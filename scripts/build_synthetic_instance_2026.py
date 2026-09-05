"""Constroi o benchmark nao oficial ``sintetica_2026_v1``.

O script nunca altera as tabelas de revisao humana. Todas as inferencias sao
registradas no payload e derivadas de arquivos versionados no repositorio.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.eval.resources import infer_lab_requirement, lab_evidence_by_code, resources_from_requirement  # noqa: E402


DATA = ROOT / "dados" / "processados"
DEFAULT_CONFIG = ROOT / "dados" / "config_sintetica_2026_v1.json"
DEFAULT_INPUT = DATA / "instancia_2026_cc_si.json"
DEFAULT_OUTPUT = DATA / "instancia_sintetica_2026_v1.json"
DAY_ORDER = {"segunda": 0, "terca": 1, "quarta": 2, "quinta": 3, "sexta": 4, "sabado": 5}


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def minutes(value: str) -> int:
    hour, minute = value.split(":")
    return int(hour) * 60 + int(minute)


def pattern_key(pattern: list[dict]) -> tuple:
    return tuple(sorted((item["dia"], item["inicio"], item["fim"]) for item in pattern))


def ordered_pattern(pattern: list[dict]) -> list[dict]:
    return sorted(pattern, key=lambda item: (DAY_ORDER.get(item["dia"], 99), item["inicio"], item["fim"]))


def pattern_signature(pattern: list[dict]) -> tuple[int, tuple[int, ...]]:
    ordered = ordered_pattern(pattern)
    return len(ordered), tuple(minutes(item["fim"]) - minutes(item["inicio"]) for item in ordered)


def load_historical_evidence() -> dict:
    classes_2025 = read_csv(DATA / "turmas_2025.csv")
    sectors_by_code: dict[str, set[str]] = defaultdict(set)
    for row in classes_2025:
        code = row.get("codigo", "").strip()
        sector = row.get("setor", "").strip()
        if code and sector:
            sectors_by_code[code].add(sector)
    unique_sector = {
        code: next(iter(sectors))
        for code, sectors in sectors_by_code.items()
        if len(sectors) == 1
    }

    teachers_by_sector: dict[str, list[str]] = defaultdict(list)
    for row in read_csv(DATA / "professores_por_setor_2025.csv"):
        sector = row.get("setor", "").strip()
        teacher = row.get("professor", "").strip()
        if sector and teacher:
            teachers_by_sector[sector].append(teacher)

    preferences: dict[str, dict[str, float]] = defaultdict(dict)
    historical_load: Counter = Counter()
    for row in read_csv(DATA / "preferencias_2025.csv"):
        code = row.get("codigo", "").strip()
        teacher = row.get("professor", "").strip()
        if not code or not teacher:
            continue
        preferences[code][teacher] = float(row.get("preferencia") or 0)
        historical_load[teacher] += int(float(row.get("contagem") or 0))

    patterns: dict[tuple[str, str, tuple[int, tuple[int, ...]]], list[tuple[str, ...]]] = defaultdict(list)
    for row in read_csv(DATA / "dias_por_setor_2025.csv"):
        parity = str(row.get("semestre", ""))[-1:]
        durations = tuple(int(value) for value in str(row.get("duracoes_min", "")).split(";") if value)
        key = (parity, row.get("setor", ""), (int(row.get("encontros") or 0), durations))
        days = tuple(value for value in str(row.get("dias", "")).split(";") if value)
        if days and days not in patterns[key]:
            patterns[key].append(days)

    capacities_2025 = {}
    for row in read_csv(DATA / "salas_2025.csv"):
        value = row.get("capacidade_estimada", "").strip()
        if value:
            capacities_2025[row["id"]] = int(float(value))

    return {
        "unique_sector": unique_sector,
        "teachers_by_sector": {key: sorted(set(value)) for key, value in teachers_by_sector.items()},
        "preferences": dict(preferences),
        "historical_load": historical_load,
        "patterns": patterns,
        "capacities_2025": capacities_2025,
    }


def build_schedule_domain(item: dict, slots: dict, patterns: dict, limit: int) -> list[list[dict]]:
    current = [
        {"dia": meeting["dia"], "inicio": meeting["inicio"], "fim": meeting["fim"]}
        for meeting in item.get("encontros", [])
    ]
    if not current:
        return []
    signature = pattern_signature(current)
    parity = str(item.get("semestre", ""))[-1:]
    day_patterns = patterns.get((parity, item.get("setor", ""), signature), [])
    if not day_patterns:
        day_patterns = [tuple(meeting["dia"] for meeting in ordered_pattern(current))]

    candidates = [current]
    seen = {pattern_key(current)}
    durations = signature[1]
    for days in day_patterns:
        if len(days) != len(durations):
            continue
        options_by_meeting = []
        for day, duration in zip(days, durations):
            options = sorted(slots[item["semestre"]][day][duration])
            if not options:
                options_by_meeting = []
                break
            options_by_meeting.append([
                {"dia": day, "inicio": start, "fim": end}
                for start, end in options
            ])
        for combination in product(*options_by_meeting) if options_by_meeting else []:
            pattern = list(combination)
            key = pattern_key(pattern)
            if key in seen:
                continue
            seen.add(key)
            candidates.append(pattern)
            if len(candidates) >= limit:
                return candidates
    return candidates


def h12_matching(classes: list[dict], teachers: set[str], minimum: int) -> tuple[int, int]:
    """Retorna (creditos casados, creditos necessarios) para o universo H12."""
    fixed_credits: Counter = Counter()
    movable_classes: dict[str, set[str]] = {}
    for item in classes:
        if item.get("origem") != "IC" or item.get("obrigatoria") is not True:
            continue
        assigned = item.get("professores_alocados") or []
        if item.get("professor_fixo", False):
            share = 1.0 / len(assigned) if assigned else 0.0
            for teacher in assigned:
                if teacher in teachers:
                    fixed_credits[teacher] += share
        else:
            candidates = teachers & set(item.get("professores_habilitados") or [])
            if candidates:
                movable_classes[item["id"]] = candidates

    slots = []
    classes_by_teacher: dict[str, list[str]] = defaultdict(list)
    for class_id, candidates in movable_classes.items():
        for teacher in candidates:
            classes_by_teacher[teacher].append(class_id)
    for teacher in sorted(teachers):
        needed = max(0, math.ceil(minimum - float(fixed_credits[teacher]) - 1e-9))
        slots.extend((teacher, index) for index in range(needed))
    slots.sort(key=lambda slot: (len(classes_by_teacher[slot[0]]), slot[0], slot[1]))

    matched_class: dict[str, tuple[str, int]] = {}

    def augment(slot: tuple[str, int], visited: set[str]) -> bool:
        teacher = slot[0]
        for class_id in sorted(classes_by_teacher[teacher]):
            if class_id in visited:
                continue
            visited.add(class_id)
            previous = matched_class.get(class_id)
            if previous is None or augment(previous, visited):
                matched_class[class_id] = slot
                return True
        return False

    matched = sum(augment(slot, set()) for slot in slots)
    return matched, len(slots)


def validate(payload: dict) -> list[str]:
    errors = []
    room_ids = {room["id"] for room in payload.get("rooms", [])}
    for item in payload.get("classes", []):
        assigned = item.get("professores_alocados") or []
        if item.get("origem") == "IC" and not assigned:
            errors.append(f"{item['id']}: turma IC sem professor")
        if len(assigned) == 1 and assigned[0] not in set(item.get("professores_habilitados") or []):
            errors.append(f"{item['id']}: professor atual fora do dominio")
        if not item.get("encontros"):
            errors.append(f"{item['id']}: turma sem encontro")
        for meeting in item.get("encontros", []):
            if meeting.get("sala") not in room_ids:
                errors.append(f"{item['id']}: sala inexistente {meeting.get('sala')}")
        if not item.get("dominio_horarios"):
            errors.append(f"{item['id']}: dominio de horario vazio")
    h12_count = sum(teacher.get("incluido_h12") is True for teacher in payload.get("teachers", []))
    h12_teachers = {
        teacher["name"] for teacher in payload.get("teachers", [])
        if teacher.get("incluido_h12") is True
    }
    obligatory = sum(item.get("origem") == "IC" and item.get("obrigatoria") is True for item in payload.get("classes", []))
    if obligatory < h12_count * int(payload.get("min_obrigatorias_ano", 3)):
        errors.append("universo H12 sinteticamente inviavel")
    minimum = int(payload.get("min_obrigatorias_ano", 3))
    matched, required = h12_matching(payload.get("classes", []), h12_teachers, minimum)
    if matched != required:
        errors.append(f"universo H12: matching conjunto cobre {matched} de {required} creditos necessarios")
    return errors


def build(config_path: Path, input_path: Path) -> dict:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("laboratorio_por_prefixo_l") is not True or config.get("uso_estrito_de_laboratorio") is not True:
        raise ValueError("O perfil v1 suporta somente compatibilidade estrita de laboratorio pelo prefixo L")
    objective = config.get("objetivo", {})
    if objective.get("penalidade_hard") != 1_000_000 or objective.get("pesos_soft") != "unitarios_provisorios":
        raise ValueError("O perfil v1 suporta penalidade hard 1e6 e pesos soft unitarios")
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    evidence = load_historical_evidence()

    for room in payload.get("rooms", []):
        observed_2026 = int(room.get("capacidade_minima_observada") or 0)
        observed_2025 = int(evidence["capacities_2025"].get(room["id"], 0))
        capacity = max(observed_2025, observed_2026)
        room["capacity"] = capacity
        room["capacidade_estimada"] = capacity
        room["capacidade_fonte"] = "proxy sintetica: maximo de demanda observado em 2025 e 2026"

    slots = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    lab_rows = []
    for item in payload.get("classes", []):
        for meeting in item.get("encontros", []):
            duration = minutes(meeting["fim"]) - minutes(meeting["inicio"])
            slots[item["semestre"]][meeting["dia"]][duration].add((meeting["inicio"], meeting["fim"]))
            lab_rows.append({"codigo": item["codigo"], "sala": meeting.get("sala", "")})
    lab_evidence = lab_evidence_by_code(lab_rows)

    classification = config["classificacoes_sinteticas"]
    observed_names = set()
    mandatory_counts: Counter = Counter()
    cotutoria_policy = {}
    for item in payload.get("classes", []):
        if item["codigo"] in classification:
            override = classification[item["codigo"]]
            item["obrigatoria"] = bool(override["obrigatoria"])
            if override["grupos_curriculares"]:
                item["grupos_curriculares"] = list(override["grupos_curriculares"])

        observed = [str(value) for value in item.get("professores_observados") or [] if str(value)]
        observed_names.update(observed)
        item["professores_alocados"] = list(observed)
        item["professor"] = observed[0] if len(observed) == 1 else None
        item["professor_fixo"] = item.get("origem") != "IC" or len(observed) != 1
        if len(observed) > 1:
            cotutoria_policy[item["id"]] = {"politica_h12": config["cotutoria_h12"]}
        if item.get("origem") == "IC" and item.get("obrigatoria") is True:
            share = 1.0 / len(observed) if observed else 0
            for teacher in observed:
                mandatory_counts[teacher] += share

        sector = evidence["unique_sector"].get(item["codigo"])
        item["setor"] = sector
        candidates = list(evidence["teachers_by_sector"].get(sector, []))
        candidates.extend(observed)
        preferences = evidence["preferences"].get(item["codigo"], {})
        candidates = sorted(
            set(value for value in candidates if value),
            key=lambda teacher: (-float(preferences.get(teacher, 0.0)), teacher),
        )
        limit = int(config["professores"]["maximo_candidatos_por_turma"])
        selected = candidates[:limit]
        for teacher in observed:
            if teacher not in selected:
                selected.append(teacher)
        item["professores_habilitados"] = sorted(set(selected))
        item["professores_habilitados_fonte"] = config["professores"]["dominio"]
        item["preferencias_professores"] = {
            teacher: float(preferences.get(teacher, 0.0))
            for teacher in item["professores_habilitados"]
        }

        for index, meeting in enumerate(item.get("encontros", []), start=1):
            meeting["id"] = f"E{index}"
            required, source = infer_lab_requirement(meeting.get("sala", ""), item["codigo"], lab_evidence)
            meeting["requer_laboratorio"] = bool(required) if required is not None else False
            meeting["recursos_requeridos"] = resources_from_requirement(meeting["requer_laboratorio"])
            meeting["recurso_fonte"] = source
            meeting["sala_observada_id"] = meeting.get("sala")

        current_pattern = [
            {"dia": meeting["dia"], "inicio": meeting["inicio"], "fim": meeting["fim"]}
            for meeting in item.get("encontros", [])
        ]
        item["padrao_horario_observado"] = copy.deepcopy(current_pattern)
        flexible = (
            item.get("origem") == "IC"
            and item.get("obrigatoria") is False
            and not str(item.get("setor", "")).startswith("PROJ.FINAL")
        )
        domain = build_schedule_domain(
            item,
            slots,
            evidence["patterns"],
            int(config["horarios"]["maximo_padroes_por_turma"]),
        ) if flexible else [current_pattern]
        item["dominio_horarios"] = domain
        item["horario_fixo"] = not flexible or len(domain) <= 1
        item["horario_dominio_fonte"] = config["horarios"]["modo"]
        item["sala_fixa"] = item.get("origem") != "IC"

    all_names = sorted({
        teacher
        for item in payload.get("classes", [])
        for teacher in item.get("professores_habilitados") or []
    } | observed_names)
    h12_size = int(config["h12_universo_tamanho"])
    potential: Counter = Counter()
    for item in payload.get("classes", []):
        if item.get("origem") != "IC" or item.get("obrigatoria") is not True:
            continue
        assigned = item.get("professores_alocados") or []
        if item.get("professor_fixo", False):
            share = 1.0 / len(assigned) if assigned else 0.0
            for teacher in assigned:
                potential[teacher] += share
        else:
            for teacher in item.get("professores_habilitados") or []:
                potential[teacher] += 1.0
    eligible_h12 = {
        teacher for teacher in observed_names
        if potential[teacher] >= int(config["h12_minimo"])
    }
    ranked_candidates = sorted(
        eligible_h12,
        key=lambda teacher: (
            -float(mandatory_counts.get(teacher, 0)),
            -int(evidence["historical_load"].get(teacher, 0)),
            teacher,
        ),
    )
    ranked_h12 = []
    for teacher in ranked_candidates:
        candidate_set = set(ranked_h12) | {teacher}
        matched, required = h12_matching(payload.get("classes", []), candidate_set, int(config["h12_minimo"]))
        if matched == required:
            ranked_h12.append(teacher)
        if len(ranked_h12) == h12_size:
            break
    if len(ranked_h12) != h12_size:
        raise ValueError(
            f"Somente {len(ranked_h12)} docentes observados possuem dominio potencial para H12; "
            f"a configuracao exige {h12_size}"
        )
    h12_set = set(ranked_h12)
    payload["teachers"] = [
        {
            "name": teacher,
            "observado_no_qh": teacher in observed_names,
            "incluido_h12": teacher in h12_set,
            "prioridade": float(config["prioridade_docente_neutra"]),
        }
        for teacher in all_names
    ]
    payload["prioridades_professores"] = {
        teacher: float(config["prioridade_docente_neutra"])
        for teacher in all_names
    }
    payload["politica_cotutoria"] = cotutoria_policy
    payload["min_obrigatorias_ano"] = int(config["h12_minimo"])
    payload["schema_version"] = "0.3-sintetica"
    payload["profile"] = config["id"]
    payload["pronta_para_experimento"] = True
    payload["evaluation_readiness"] = {
        "perfil_sintetico": True,
        "dados_oficiais": False,
        "capacidade_salas_proxy": True,
        "recursos_proxy": True,
        "dominios_professores_proxy": True,
        "dominios_horarios_proxy": True,
        "h12_sintetico": True,
    }
    payload["synthetic_manifest"] = {
        "config": str(config_path.relative_to(ROOT)),
        "config_sha256": sha256(config_path),
        "base": str(input_path.relative_to(ROOT)),
        "base_sha256": sha256(input_path),
        "status": config["status"],
        "descricao": config["descricao"],
        "hipoteses": {
            "capacidade_sala": config["capacidade_sala"],
            "laboratorio_por_prefixo_l": config["laboratorio_por_prefixo_l"],
            "prioridade_docente": config["prioridade_docente_neutra"],
            "h12_universo": config["h12_universo_sintetico"],
            "cotutoria_h12": config["cotutoria_h12"],
            "horarios": config["horarios"]["modo"],
            "habilitacao": config["professores"]["dominio"],
        },
        "h12_matching": {
            "docentes": len(h12_set),
            "creditos_necessarios": h12_matching(payload["classes"], h12_set, int(config["h12_minimo"]))[1],
            "creditos_cobertos": h12_matching(payload["classes"], h12_set, int(config["h12_minimo"]))[0],
        },
    }
    errors = validate(payload)
    if errors:
        raise ValueError("Instancia sintetica invalida:\n- " + "\n- ".join(errors[:20]))
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera a instancia sintetica reprodutivel de 2026")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build(args.config.resolve(), args.input.resolve())
    args.output.resolve().write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    flexible = sum(not item.get("horario_fixo", True) for item in payload["classes"])
    movable = sum(len(item.get("professores_habilitados") or []) > 1 and not item.get("professor_fixo") for item in payload["classes"])
    h12 = sum(teacher["incluido_h12"] for teacher in payload["teachers"])
    print(f"{args.output}: {len(payload['classes'])} turmas, {flexible} horarios flexiveis, {movable} turmas com professor movel, {h12} docentes H12")


if __name__ == "__main__":
    main()
