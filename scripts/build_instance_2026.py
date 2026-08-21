"""Constrói uma instância anual observada a partir dos QHs de 2026.

A saída não é chamada de instância CC/SI porque os PDFs não informam curso,
período curricular ou obrigatoriedade. Esses campos permanecem nulos. Uma
tabela separada registra correspondências históricas com o QH 2025 sem
incorporá-las como fatos de 2026.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.eval.rooms import is_lab_room


DATA = ROOT / "dados" / "processados"
OUT = DATA / "instancia_2026_ic_observada.json"
CURRICULAR_PROXY = DATA / "classificacao_curricular_proxy_2026.csv"
RESOURCE_CLASSES = DATA / "recursos_turmas_2026.csv"
RESOURCE_MEETINGS = DATA / "recursos_encontros_2026.csv"


def historical_curriculum_proxy(classes: pd.DataFrame) -> pd.DataFrame:
    historical_path = DATA / "turmas_2025.csv"
    mapping: dict[str, dict] = defaultdict(
        lambda: {
            "cursos": set(),
            "periodos": set(),
            "obrigatoria": False,
            "registros": 0,
        }
    )
    if historical_path.exists():
        historical = pd.read_csv(historical_path, dtype=str).fillna("")
        target = historical[historical["curso"].isin({"31", "83"}) | (
            historical["curso"].eq("") & historical["periodo"].str.startswith(("CC-", "SI-"))
        )]
        for row in target.itertuples():
            item = mapping[row.codigo]
            if row.curso:
                item["cursos"].add(row.curso)
            if row.periodo:
                item["periodos"].add(row.periodo)
            ch_ob = pd.to_numeric(pd.Series([row.ch_ob]), errors="coerce").iloc[0]
            item["obrigatoria"] = item["obrigatoria"] or bool(pd.notna(ch_ob) and ch_ob > 0)
            item["registros"] += 1

    rows = []
    for row in classes.itertuples():
        item = mapping.get(row.codigo)
        rows.append(
            {
                "turma_id": row.id,
                "semestre": row.semestre,
                "codigo": row.codigo,
                "disciplina": row.disciplina,
                "turma": row.turma,
                "correspondencia_2025": bool(item),
                "cursos_observados_2025": ";".join(sorted(item["cursos"])) if item else "",
                "periodos_observados_2025": ";".join(sorted(item["periodos"])) if item else "",
                "obrigatoria_em_algum_registro_2025": item["obrigatoria"] if item else "",
                "registros_correspondentes_2025": item["registros"] if item else 0,
                "incorporado_como_fato_2026": False,
                "fonte": "proxy histórico de turmas_2025.csv; requer validação curricular para 2026",
            }
        )
    return pd.DataFrame(rows)


def observed_room_resources(room: str) -> tuple[bool | None, list[str] | None, str]:
    """Descreve a sala observada sem convertê-la em requisito da turma."""
    room = str(room or "").strip()
    if not room:
        return None, None, "sala_ausente_no_pdf"
    observed_lab = is_lab_room(room)
    return (
        observed_lab,
        ["laboratorio"] if observed_lab else [],
        "tipo_da_sala_inferido_exclusivamente_do_prefixo_observado",
    )


def class_resource_summary(meetings: list[dict]) -> tuple[bool | None, list[str], list[str]]:
    observations = [meeting["laboratorio_observado"] for meeting in meetings]
    sources = sorted({meeting["recurso_observado_fonte"] for meeting in meetings})
    uses_lab = True if any(value is True for value in observations) else (False if observations and all(value is False for value in observations) else None)
    observed_resources = ["laboratorio"] if uses_lab else []
    return uses_lab, observed_resources, sources


def main() -> None:
    classes = pd.read_csv(DATA / "turmas_2026.csv", dtype=str).fillna("")
    meetings = pd.read_csv(DATA / "horarios_2026.csv", dtype=str).fillna("")
    teacher_review = pd.read_csv(DATA / "normalizacao_docentes_2026.csv", dtype=str).fillna("")
    rooms_table = pd.read_csv(DATA / "salas_2026.csv", dtype=str).fillna("")

    proxy = historical_curriculum_proxy(classes)
    proxy.to_csv(CURRICULAR_PROXY, index=False)

    excluded = classes[classes["status"].ne("ativa")].copy()
    active = classes[classes["status"].eq("ativa")].copy()
    active_meetings = meetings[meetings["turma_id"].isin(set(active["id"]))].copy()

    meetings_by_class: dict[str, list[dict]] = defaultdict(list)
    resource_meeting_rows = []
    for row in active_meetings.itertuples():
        observed_lab, observed_resources, source = observed_room_resources(row.sala)
        record = {
            "dia": row.dia,
            "inicio": row.inicio,
            "fim": row.fim,
            "sala": row.sala or None,
            "horario_observado": True,
            "sala_observada": bool(row.sala),
            "laboratorio_observado": observed_lab,
            "recursos_observados": observed_resources,
            "recurso_observado_fonte": source,
            "requer_laboratorio": None,
            "recursos_requeridos": None,
            "recurso_fonte": "requisito não disponível nos PDFs",
            "valor_original": row.valor_original,
            "pagina_pdf": int(float(row.pagina_pdf)),
        }
        meetings_by_class[row.turma_id].append(record)
        resource_meeting_rows.append(
            {
                "turma_id": row.turma_id,
                "semestre": row.semestre,
                "codigo": row.codigo,
                "dia": row.dia,
                "inicio": row.inicio,
                "fim": row.fim,
                "sala_observada": row.sala,
                "laboratorio_observado": observed_lab,
                "recursos_observados": ";".join(observed_resources or []),
                "observacao_fonte": source,
                "requer_laboratorio": "",
                "recursos_requeridos": "",
                "requisito_fonte": "não disponível nos PDFs",
            }
        )

    instance_classes = []
    resource_class_rows = []
    for row in active.itertuples():
        class_meetings = meetings_by_class[row.id]
        uses_lab, observed_resources, resource_sources = class_resource_summary(class_meetings)
        observed_teachers = [value for value in row.professores.split(";") if value]
        allocation_type = "multipla" if len(observed_teachers) > 1 else ("simples" if observed_teachers else "ausente")
        instance_classes.append(
            {
                "id": row.id,
                "semestre": row.semestre,
                "codigo": row.codigo or None,
                "codigo_interno": row.codigo_interno,
                "disciplina": row.disciplina,
                "turma": row.turma or None,
                "origem_codigo": row.origem_codigo,
                "categoria_observada": row.categoria_observada,
                "curso": None,
                "periodo": None,
                "obrigatoria": None,
                "setor": None,
                "capacidade_turma": None,
                "professor": observed_teachers[0] if len(observed_teachers) == 1 else None,
                "professores_observados": observed_teachers,
                "alocacao_tipo": allocation_type,
                "alocacao_observada_original": row.alocacao_original or None,
                "usa_laboratorio_observado": uses_lab,
                "recursos_observados": observed_resources,
                "recurso_observado_fontes": resource_sources,
                "exige_laboratorio": None,
                "recursos_requeridos": None,
                "recurso_fontes": ["requisito não disponível nos PDFs"],
                "horario_fixo": None,
                "sala_fixa": None,
                "encontros": class_meetings,
                "fonte": {
                    "arquivo": row.arquivo_origem,
                    "pagina": int(float(row.pagina_pdf)),
                    "tipo": "alocacao_observada",
                },
            }
        )
        resource_class_rows.append(
            {
                "turma_id": row.id,
                "semestre": row.semestre,
                "codigo": row.codigo,
                "disciplina": row.disciplina,
                "usa_laboratorio_observado": uses_lab,
                "recursos_observados": ";".join(observed_resources),
                "observacao_fontes": ";".join(resource_sources),
                "exige_laboratorio": "",
                "recursos_requeridos": "",
                "requisito_fonte": "não disponível nos PDFs",
            }
        )

    teacher_verification = {
        row.nome_normalizado: str(row.verificada).lower() == "true"
        for row in teacher_review.itertuples()
    }
    observed_teacher_names = sorted({
        teacher
        for value in active["professores"]
        for teacher in value.split(";")
        if teacher
    })

    rooms = []
    for row in rooms_table.itertuples():
        is_lab = str(row.laboratorio_inferido).lower() == "true"
        rooms.append(
            {
                "id": row.id,
                "laboratorio": is_lab,
                "resources": ["laboratorio"] if is_lab else [],
                "capacity": None,
                "capacidade_estimada": None,
                "recurso_fonte": row.fonte_tipo,
                "capacidade_fonte": row.capacidade_fonte,
            }
        )

    instance = {
        "schema_version": "0.2-observada",
        "source": ["dados/brutos/QH-2026-1.pdf", "dados/brutos/QH-2026-2.pdf"],
        "profile": "ic_observado_nao_classificado_cc_si",
        "ano": 2026,
        "pronta_para_experimento": False,
        "evaluation_readiness": {
            "conflitos_sala": True,
            "conflitos_professor": "requer decisão para as quatro alocações múltiplas",
            "dias_janelas_descanso": "requer decisão para as quatro alocações múltiplas",
            "h12": False,
            "conflitos_curriculares": False,
            "capacidade": False,
            "setores_preferencias_prioridades": False,
        },
        "classificacao_ausente": [
            "curso CC/SI",
            "período curricular",
            "obrigatória/optativa para cada currículo",
            "setor",
            "capacidade da turma",
            "universo H12",
        ],
        "notes": [
            "Horários, salas e professores são alocações observadas nos PDFs; não são declarados como parâmetros fixos.",
            "Registros incompletos e cancelados foram preservados nos CSVs, mas excluídos desta instância operacional.",
            "Curso, período, obrigatoriedade, setor e capacidades permanecem nulos em vez de serem inferidos.",
            "A tabela classificacao_curricular_proxy_2026.csv é somente apoio de revisão e não foi incorporada como fato.",
            "O prefixo L descreve uso observado de laboratório; não é convertido em requisito da turma.",
            "Turmas com mais de um professor preservam a lista observada e deixam o campo professor singular nulo.",
        ],
        "rooms": rooms,
        "teachers": [
            {
                "name": teacher,
                "observado_no_qh": True,
                "normalizacao_verificada": teacher_verification.get(teacher, False),
                "incluido_h12": None,
                "prioridade": None,
            }
            for teacher in observed_teacher_names
        ],
        "classes": instance_classes,
        "excluded_records": [
            {
                "id": row.id,
                "status": row.status,
                "pendencias": row.pendencias.split(";") if row.pendencias else [],
            }
            for row in excluded.itertuples()
        ],
    }
    OUT.write_text(json.dumps(instance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pd.DataFrame(resource_class_rows).to_csv(RESOURCE_CLASSES, index=False)
    pd.DataFrame(resource_meeting_rows).to_csv(RESOURCE_MEETINGS, index=False)
    print(
        f"{OUT}: {len(instance_classes)} registros ativos, {len(rooms)} salas, "
        f"{len(observed_teacher_names)} docentes observados; pronta_para_experimento=false"
    )


if __name__ == "__main__":
    main()
