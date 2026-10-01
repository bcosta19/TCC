"""Constrói a instância oficial de 2026 a partir das tabelas de revisão humana.

Parte da instância observada (``instancia_2026_cc_si.json``) e aplica somente
decisões registradas nas tabelas ``dados/processados/revis*_2026.csv``,
``universo_h12_2026.csv``, ``politica_cotutoria_2026.csv`` e
``cadastro_salas_2026.csv``. Nenhum valor ausente é substituído por proxy:
campos sem decisão ficam nulos, entram em ``pendencias_aplicacao`` e mantêm
``pronta_para_experimento=false``.

Regras de aplicação (ver ``anotacoes/decisoes_modelagem_2026_09_30.md``):

- Tabelas com coluna ``validado`` só são aplicadas nas linhas com
  ``validado=sim``.
- ``horario_fixo=nao`` gera domínio de horários nos dias do setor: os dias de
  ``dias_oficiais`` (coluna opcional em ``revisao_setores_2026.csv``) ou, na
  falta deles, os padrões de dias observados para o setor em 2025.
- ``requer_laboratorio=sim`` exige laboratório em todos os encontros, exceto
  quando a disciplina alternou tipo de sala; nesse caso, só nos encontros
  observados em laboratório.
- Turmas externas da coleta web só entram quando
  ``tratamento_no_modelo=fixar_horario_e_sala``, como ocupação fixa (H8).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_synthetic_instance_2026 import (  # noqa: E402
    DAY_ORDER,
    build_schedule_domain,
    h12_matching,
    load_historical_evidence,
    minutes,
    pattern_signature,
)
from scripts.check_readiness_2026 import check_profile  # noqa: E402
from src.eval.resources import resources_from_requirement  # noqa: E402
from src.eval.rooms import is_lab_room  # noqa: E402


DATA = ROOT / "dados" / "processados"
DEFAULT_INPUT = DATA / "instancia_2026_cc_si.json"
DEFAULT_OUTPUT = DATA / "instancia_oficial_2026.json"
MIN_OBRIGATORIAS_ANO = 3
MAX_PATTERNS = 12
TRUE = {"sim", "true", "1"}
FALSE = {"nao", "não", "false", "0"}
REVIEW_FILES = (
    "revisao_classificacao_curricular_2026.csv",
    "politica_cotutoria_2026.csv",
    "universo_h12_2026.csv",
    "cadastro_salas_2026.csv",
    "revisao_recursos_disciplinas_2026.csv",
    "revisao_horarios_fixos_2026.csv",
    "revisao_setores_2026.csv",
    "revisao_habilitacao_docente_2026.csv",
    "revisao_prioridades_docentes_2026.csv",
    "revisao_turmas_externas_2026.csv",
)
DAY_MAP = {"Seg": "segunda", "Ter": "terca", "Qua": "quarta", "Qui": "quinta", "Sex": "sexta", "Sab": "sabado"}
WEB_MEETING_RE = re.compile(r"(Seg|Ter|Qua|Qui|Sex|Sab)\s+(\d{2}:\d{2})-(\d{2}:\d{2})")


def yes_no(value: object) -> bool | None:
    text = str(value or "").strip().lower()
    if text in TRUE:
        return True
    if text in FALSE:
        return False
    return None


def read_table(data: Path, name: str) -> pd.DataFrame:
    path = data / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str).fillna("")


def validated_rows(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty or "validado" not in frame.columns:
        return frame
    return frame[frame["validado"].map(yes_no).eq(True)]


def split_values(value: object, separator: str = ";") -> list[str]:
    return [item.strip() for item in str(value or "").split(separator) if item.strip()]


def sha256(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


class Pending:
    """Agrupa pendências por categoria, preservando exemplos para o relatório."""

    def __init__(self) -> None:
        self.items: dict[str, list[str]] = defaultdict(list)

    def add(self, category: str, detail: str) -> None:
        if detail not in self.items[category]:
            self.items[category].append(detail)

    def __bool__(self) -> bool:
        return any(self.items.values())

    def summary(self, examples: int = 10) -> dict:
        return {
            category: {"quantidade": len(details), "exemplos": details[:examples]}
            for category, details in sorted(self.items.items())
        }


def parse_classification(decision: str) -> tuple[str, bool | None, list[str]]:
    """Converte ``obrigatoria:SI-P7``, ``optativa:CC`` ou ``ignorar``."""
    text = decision.strip()
    if text == "ignorar":
        return "ignorar", None, []
    kind, _, target = text.partition(":")
    if kind == "obrigatoria" and re.fullmatch(r"(CC|SI)-P[1-8]", target):
        return "obrigatoria", True, [target]
    if kind == "optativa" and target in {"CC", "SI"}:
        return "optativa", False, []
    raise ValueError(f"decisão curricular inválida: {decision!r}")


def official_day_patterns(days: list[str], meetings: int) -> list[tuple[str, ...]]:
    ordered = sorted(set(days), key=lambda day: DAY_ORDER.get(day, 99))
    return [tuple(combo) for combo in combinations(ordered, meetings)]


def observed_slots(classes: list[dict]) -> dict:
    slots: dict = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    for item in classes:
        for meeting in item.get("encontros", []):
            duration = minutes(meeting["fim"]) - minutes(meeting["inicio"])
            slots[item["semestre"]][meeting["dia"]][duration].add((meeting["inicio"], meeting["fim"]))
    return slots


def external_class(row: pd.Series) -> dict:
    meetings = [
        {
            "id": f"E{index}",
            "dia": DAY_MAP[day],
            "inicio": start,
            "fim": end,
            "sala": None,
            "horario_observado": True,
            "sala_observada": False,
            "requer_laboratorio": False,
            "recursos_requeridos": [],
            "recurso_fonte": "turma externa fixa sem sala do IC",
        }
        for index, (day, start, end) in enumerate(WEB_MEETING_RE.findall(row["horarios"]), start=1)
    ]
    groups = split_values(row.get("periodo_curricular", ""))
    pattern = [{"dia": m["dia"], "inicio": m["inicio"], "fim": m["fim"]} for m in meetings]
    return {
        "id": f"{row['semestre']}-{row['codigo']}-{row['turma']}-WEB",
        "semestre": row["semestre"],
        "codigo": row["codigo"],
        "disciplina": row["disciplina"],
        "turma": row["turma"],
        "origem": "externa",
        "curso": row.get("curso", ""),
        "curriculos": split_values(row.get("curso", "")),
        "grupos_curriculares": groups,
        "obrigatoria": bool(groups),
        "setor": None,
        "professor": None,
        "professores_observados": [],
        "professores_alocados": [],
        "professor_fixo": True,
        "professores_habilitados": [],
        "capacidade_turma": None,
        "horario_fixo": True,
        "sala_fixa": True,
        "dominio_horarios": [pattern],
        "padrao_horario_observado": pattern,
        "encontros": meetings,
        "fontes": {"turma_url": row.get("turma_url", ""), "tipo": "revisao_turmas_externas_2026"},
    }


def validate(payload: dict) -> list[str]:
    errors = []
    room_ids = {room["id"] for room in payload.get("rooms", [])}
    for item in payload.get("classes", []):
        assigned = item.get("professores_alocados") or []
        internal = item.get("origem") == "IC"
        if internal and not assigned:
            errors.append(f"{item['id']}: turma IC sem professor")
        if internal and not item.get("professor_fixo") and assigned and assigned[0] not in set(item.get("professores_habilitados") or []):
            errors.append(f"{item['id']}: professor observado {assigned[0]} fora da habilitação")
        if not item.get("encontros"):
            errors.append(f"{item['id']}: turma sem encontro")
        if not item.get("dominio_horarios"):
            errors.append(f"{item['id']}: domínio de horário vazio")
        if internal:
            for meeting in item.get("encontros", []):
                if meeting.get("sala") not in room_ids:
                    errors.append(f"{item['id']}: sala inexistente {meeting.get('sala')}")
    for room in payload.get("rooms", []):
        if room.get("capacity") is None:
            errors.append(f"sala {room['id']}: sem capacidade física")
    h12_teachers = {t["name"] for t in payload.get("teachers", []) if t.get("incluido_h12") is True}
    if h12_teachers:
        matched, required = h12_matching(payload.get("classes", []), h12_teachers, int(payload["min_obrigatorias_ano"]))
        if matched != required:
            errors.append(f"H12 inviável: o matching cobre {matched} de {required} créditos necessários")
    return errors


def build(base_path: Path, data: Path = DATA, evidence: dict | None = None, max_patterns: int = MAX_PATTERNS) -> dict:
    payload = json.loads(base_path.read_text(encoding="utf-8"))
    evidence = evidence if evidence is not None else load_historical_evidence()
    pending = Pending()

    classification = {
        row.turma_id: row.decisao
        for row in read_table(data, "revisao_classificacao_curricular_2026.csv").itertuples()
        if row.decisao.strip()
    }
    cotutoria = {}
    for row in read_table(data, "politica_cotutoria_2026.csv").itertuples():
        if row.politica_h12.strip():
            entry = {"politica_h12": row.politica_h12.strip()}
            if row.professor_responsavel.strip():
                entry["professor_responsavel"] = row.professor_responsavel.strip()
            cotutoria[row.turma_id] = entry
        else:
            pending.add("cotutoria", row.turma_id)

    fixed_schedule = {
        row.turma_id: yes_no(row.horario_fixo)
        for row in validated_rows(read_table(data, "revisao_horarios_fixos_2026.csv")).itertuples()
        if yes_no(row.horario_fixo) is not None
    }
    sectors_table = validated_rows(read_table(data, "revisao_setores_2026.csv"))
    sectors = {row["codigo"]: row["setor_oficial"].strip() for _, row in sectors_table.iterrows() if row["setor_oficial"].strip()}
    sector_days = {
        row["codigo"]: split_values(row.get("dias_oficiais", ""))
        for _, row in sectors_table.iterrows()
        if split_values(row.get("dias_oficiais", ""))
    }
    qualified: dict[str, set[str]] = defaultdict(set)
    reviewed_codes: set[str] = set()
    for row in validated_rows(read_table(data, "revisao_habilitacao_docente_2026.csv")).itertuples():
        decision = yes_no(row.habilitado)
        if decision is None:
            continue
        reviewed_codes.add(row.codigo)
        if decision:
            qualified[row.codigo].add(row.docente)
    resources_table = validated_rows(read_table(data, "revisao_recursos_disciplinas_2026.csv"))
    lab_required = {}
    extra_resources = {}
    alternated = {}
    for _, row in resources_table.iterrows():
        decision = yes_no(row["requer_laboratorio"])
        if decision is not None:
            lab_required[row["codigo"]] = decision
            extra_resources[row["codigo"]] = split_values(row.get("recursos_requeridos", ""))
            alternated[row["codigo"]] = yes_no(row.get("alternou_tipo_de_sala")) is True
    rooms_table = validated_rows(read_table(data, "cadastro_salas_2026.csv"))
    room_capacity = {}
    room_resources = {}
    for _, row in rooms_table.iterrows():
        try:
            capacity = int(float(row["capacidade_fisica"]))
        except ValueError:
            continue
        if capacity > 0:
            room_capacity[row["sala"]] = capacity
            room_resources[row["sala"]] = split_values(row.get("recursos_oficiais", ""))
    priorities = {}
    for _, row in validated_rows(read_table(data, "revisao_prioridades_docentes_2026.csv")).iterrows():
        try:
            priorities[row["nome_normalizado"]] = float(row["prioridade"])
        except ValueError:
            continue
    h12_universe = {
        row.nome_normalizado: yes_no(row.incluido_h12)
        for row in read_table(data, "universo_h12_2026.csv").itertuples()
        if yes_no(row.incluido_h12) is not None
    }

    slots = observed_slots(payload.get("classes", []))
    classes = []
    for item in payload.get("classes", []):
        code = item["codigo"]
        internal = item.get("origem") == "IC"
        if item["id"] in classification:
            kind, obligatory, groups = parse_classification(classification[item["id"]])
            if kind == "ignorar":
                continue
            item["obrigatoria"] = obligatory
            item["grupos_curriculares"] = groups
            item["obrigatoria_fonte"] = "revisao_classificacao_curricular_2026.csv"
        elif item.get("obrigatoria") is None and internal:
            pending.add("classificacao_curricular", item["id"])

        observed = [str(value) for value in item.get("professores_observados") or [] if str(value)]
        item["professores_alocados"] = list(observed)
        item["professor"] = observed[0] if len(observed) == 1 else None
        item["professor_fixo"] = not internal or len(observed) != 1
        if internal and len(observed) > 1 and item["id"] not in cotutoria:
            pending.add("cotutoria", item["id"])

        item["setor"] = sectors.get(code)
        if internal and code not in reviewed_codes:
            pending.add("habilitacao_docente", code)
        enabled = sorted(qualified.get(code, set()) | (set(observed) if item["professor_fixo"] else set()))
        item["professores_habilitados"] = enabled
        item["professores_habilitados_fonte"] = "revisao_habilitacao_docente_2026.csv"
        preferences = evidence.get("preferences", {}).get(code, {})
        item["preferencias_professores"] = {teacher: float(preferences.get(teacher, 0.0)) for teacher in enabled}

        if code not in lab_required:
            pending.add("recursos_disciplina", code)
        for index, meeting in enumerate(item.get("encontros", []), start=1):
            meeting["id"] = f"E{index}"
            meeting["sala_observada_id"] = meeting.get("sala")
            if code in lab_required:
                needs_lab = lab_required[code] and (not alternated[code] or is_lab_room(meeting.get("sala") or ""))
                meeting["requer_laboratorio"] = needs_lab
                meeting["recursos_requeridos"] = (resources_from_requirement(needs_lab) or []) + extra_resources[code]
                meeting["recurso_fonte"] = "revisao_recursos_disciplinas_2026.csv"
            else:
                meeting["requer_laboratorio"] = None
                meeting["recursos_requeridos"] = None
                meeting["recurso_fonte"] = "pendente"

        current = [{"dia": m["dia"], "inicio": m["inicio"], "fim": m["fim"]} for m in item.get("encontros", [])]
        item["padrao_horario_observado"] = [dict(pattern) for pattern in current]
        fixed = fixed_schedule.get(item["id"])
        if fixed is None:
            pending.add("horario_fixo", item["id"])
            fixed = True
        domain = [current]
        source = "observado"
        if not fixed:
            if not item["setor"]:
                pending.add("setor_para_horario_flexivel", item["id"])
            else:
                parity = str(item["semestre"])[-1:]
                signature = pattern_signature(current)
                if code in sector_days:
                    patterns = {(parity, item["setor"], signature): official_day_patterns(sector_days[code], signature[0])}
                    source = "dias_oficiais_do_setor"
                else:
                    patterns = evidence.get("patterns", {})
                    source = "padroes_de_dias_do_setor_2025"
                domain = build_schedule_domain(item, slots, patterns, max_patterns)
        item["dominio_horarios"] = domain
        item["horario_fixo"] = fixed or len(domain) <= 1
        item["horario_dominio_fonte"] = source
        item["sala_fixa"] = not internal
        classes.append(item)

    for _, row in read_table(data, "revisao_turmas_externas_2026.csv").iterrows():
        if row["tratamento_no_modelo"].strip() == "fixar_horario_e_sala" and yes_no(row["vinculada_ao_pdf"]) is not True:
            classes.append(external_class(row))
    payload["classes"] = classes

    for room in payload.get("rooms", []):
        capacity = room_capacity.get(room["id"])
        if capacity is None:
            pending.add("capacidade_sala", room["id"])
        room["capacity"] = capacity
        room["capacidade_estimada"] = capacity
        room["capacidade_fonte"] = "cadastro_salas_2026.csv" if capacity is not None else "pendente"
        resources = set(room_resources.get(room["id"], [])) | ({"laboratorio"} if room.get("laboratorio") else set())
        room["resources"] = sorted(resources)
        room["laboratorio"] = "laboratorio" in resources

    names = sorted(
        {t for item in classes for t in item.get("professores_habilitados", [])}
        | {t for item in classes for t in item.get("professores_observados", [])}
    )
    teachers = []
    for name in names:
        included = h12_universe.get(name)
        if included is None:
            pending.add("universo_h12", name)
        if name not in priorities:
            pending.add("prioridade_docente", name)
        teachers.append({"name": name, "incluido_h12": included, "prioridade": priorities.get(name)})
    payload["teachers"] = teachers
    payload["prioridades_professores"] = {name: value for name, value in priorities.items() if name in names}
    payload["politica_cotutoria"] = cotutoria
    payload["min_obrigatorias_ano"] = MIN_OBRIGATORIAS_ANO
    payload["schema_version"] = "0.3-oficial"
    payload["profile"] = "oficial_2026"

    readiness_ok, readiness_pending = check_profile("completo", data, update_instance=False)
    errors = validate(payload) if not pending and readiness_ok else []
    payload["pronta_para_experimento"] = readiness_ok and not pending and not errors
    payload["pendencias_aplicacao"] = pending.summary()
    payload["pendencias_verificador"] = len(readiness_pending)
    payload["erros_validacao"] = errors
    payload["manifesto_oficial"] = {
        "base": str(base_path.relative_to(ROOT)) if base_path.is_relative_to(ROOT) else str(base_path),
        "base_sha256": sha256(base_path),
        "revisoes": {name: sha256(data / name) for name in REVIEW_FILES},
        "decisoes": "anotacoes/decisoes_modelagem_2026_09_30.md",
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Constrói a instância oficial de 2026 a partir das revisões humanas")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--data", type=Path, default=DATA, help="Diretório das tabelas de revisão")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build(args.input.resolve(), args.data.resolve())
    args.output.resolve().write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    flexible = sum(not item.get("horario_fixo", True) for item in payload["classes"])
    print(f"{args.output}: {len(payload['classes'])} turmas, {flexible} com horário flexível")
    if payload["pronta_para_experimento"]:
        print("Status: PRONTA PARA EXPERIMENTO")
        return
    print(f"Status: NÃO PRONTA ({payload['pendencias_verificador']} pendência(s) no verificador)")
    for category, info in payload["pendencias_aplicacao"].items():
        print(f"  - {category}: {info['quantidade']}")
    for error in payload["erros_validacao"][:20]:
        print(f"  - erro: {error}")


if __name__ == "__main__":
    main()
