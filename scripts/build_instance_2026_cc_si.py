"""Gera a instância CC/SI de 2026 sem duplicar turmas compartilhadas.

As ofertas são selecionadas pelo vínculo com as buscas públicas dos currículos
de CC e SI. A grade curricular fornece períodos e obrigatoriedade; as vagas
vêm das páginas públicas de detalhe. Linhas compactadas no PDF são expandidas
quando correspondem a mais de uma turma no sistema.
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.eval.rooms import is_lab_room


DATA = ROOT / "dados" / "processados"
OUT = DATA / "instancia_2026_cc_si.json"
CLASSES_OUT = DATA / "turmas_2026_cc_si.csv"
MEETINGS_OUT = DATA / "horarios_2026_cc_si.csv"
ROOMS_OUT = DATA / "salas_2026_cc_si.csv"

DAY_MAP = {
    "Seg": "segunda",
    "Ter": "terca",
    "Qua": "quarta",
    "Qui": "quinta",
    "Sex": "sexta",
    "Sab": "sabado",
}
MEETING_RE = re.compile(r"(Seg|Ter|Qua|Qui|Sex|Sab)\s+(\d{2}:\d{2})-(\d{2}:\d{2})")


def as_bool(value: object) -> bool:
    return str(value).strip().lower() == "true"


def as_int(value: object) -> int | None:
    text = str(value or "").strip()
    return int(float(text)) if text else None


def split_values(value: object) -> list[str]:
    return sorted({item for item in str(value or "").split(";") if item})


def web_slots(value: str) -> set[tuple[str, str, str]]:
    return {
        (DAY_MAP[day], start, end)
        for day, start, end in MEETING_RE.findall(str(value or ""))
    }


def target_id(link, link_count: int) -> str:
    if link_count == 1:
        return link.turma_id
    return f"{link.semestre}-{link.codigo}-{link.turma_web}"


def main() -> None:
    pdf_classes = pd.read_csv(DATA / "turmas_2026.csv", dtype=str).fillna("")
    pdf_meetings = pd.read_csv(DATA / "horarios_2026.csv", dtype=str).fillna("")
    links = pd.read_csv(DATA / "vagas_turmas_2026.csv", dtype=str).fillna("")
    curricula = pd.read_csv(DATA / "curriculos_cc_si.csv", dtype=str).fillna("")
    pdf_by_id = pdf_classes.set_index("id")
    meetings_by_id = {
        class_id: group.to_dict("records")
        for class_id, group in pdf_meetings.groupby("turma_id")
    }
    link_counts = links.groupby("turma_id").size().to_dict()

    classes_json = []
    class_rows = []
    meeting_rows = []
    room_demands: dict[str, list[int]] = defaultdict(list)

    for link in links.itertuples():
        pdf = pdf_by_id.loc[link.turma_id]
        count = int(link_counts[link.turma_id])
        class_id = target_id(link, count)
        courses = split_values(link.curriculos) or split_values(link.cursos_busca)
        groups = split_values(link.grupos_curriculares)
        obligatory = as_bool(link.obrigatoria) if link.curriculos else None
        observed_teachers = split_values(pdf.professores)
        class_capacity = as_int(link.vagas)
        enrolled = as_int(link.inscritos)

        source_meetings = meetings_by_id.get(link.turma_id, [])
        if count > 1:
            selected_slots = web_slots(link.horario_web)
            source_meetings = [
                meeting
                for meeting in source_meetings
                if (meeting["dia"], meeting["inicio"], meeting["fim"]) in selected_slots
            ]

        instance_meetings = []
        for number, meeting in enumerate(source_meetings, start=1):
            room = meeting["sala"] or None
            observed_lab = is_lab_room(room) if room else None
            if room and class_capacity is not None:
                room_demands[room].append(class_capacity)
            instance_meetings.append(
                {
                    "dia": meeting["dia"],
                    "inicio": meeting["inicio"],
                    "fim": meeting["fim"],
                    "sala": room,
                    "horario_observado": True,
                    "sala_observada": bool(room),
                    "laboratorio_observado": observed_lab,
                    "recursos_observados": ["laboratorio"] if observed_lab else [],
                    "requer_laboratorio": None,
                    "recursos_requeridos": None,
                    "valor_original": meeting["valor_original"],
                    "pagina_pdf": int(float(meeting["pagina_pdf"])),
                }
            )
            meeting_rows.append(
                {
                    "turma_id": class_id,
                    "semestre": link.semestre,
                    "codigo": link.codigo,
                    "turma": link.turma_web,
                    "encontro": number,
                    "dia": meeting["dia"],
                    "inicio": meeting["inicio"],
                    "fim": meeting["fim"],
                    "sala": meeting["sala"],
                    "valor_original": meeting["valor_original"],
                    "requer_laboratorio": "",
                }
            )

        shared_curriculum = as_bool(link.compartilhada_curriculos_cc_si)
        shared_vacancies = as_bool(link.compartilhada_vagas_cc_si)
        allocation_type = (
            "multipla" if len(observed_teachers) > 1
            else ("simples" if observed_teachers else "ausente")
        )
        class_item = {
            "id": class_id,
            "semestre": link.semestre,
            "codigo": link.codigo,
            "disciplina": pdf.disciplina,
            "turma": link.turma_web,
            "turma_pdf": link.turma_pdf,
            "origem": "IC" if link.codigo.startswith("TCC") else "externa",
            "curso": ";".join(courses),
            "curriculos": courses,
            "grupos_curriculares": groups,
            "compartilhada_cc_si": shared_curriculum,
            "compartilhada_vagas_cc_si": shared_vacancies,
            "periodo": None,
            "obrigatoria": obligatory,
            "obrigatoria_fonte": "dados/grade_cc.md;dados/grade_si.md" if link.curriculos else None,
            "setor": None,
            "professor": observed_teachers[0] if len(observed_teachers) == 1 else None,
            "professores_observados": observed_teachers,
            "alocacao_tipo": allocation_type,
            "capacidade_turma": class_capacity,
            "inscritos": enrolled,
            "vagas_por_curso": json.loads(link.vagas_por_curso_json or "[]"),
            "capacidade_fonte": "vagas alocadas na página pública da turma",
            "horario_fixo": None,
            "sala_fixa": None,
            "encontros": instance_meetings,
            "fontes": {
                "quadro_pdf": str(pdf.arquivo_origem),
                "pagina_pdf": int(float(pdf.pagina_pdf)),
                "turma_url": link.turma_url,
                "metodo_vinculo": link.metodo_vinculo,
                "tipo": "alocacao_observada",
            },
        }
        classes_json.append(class_item)
        class_rows.append(
            {
                "id": class_id,
                "semestre": link.semestre,
                "curso": ";".join(courses),
                "periodo": "",
                "grupos_curriculares": ";".join(groups),
                "codigo": link.codigo,
                "disciplina": pdf.disciplina,
                "turma": link.turma_web,
                "turma_pdf": link.turma_pdf,
                "origem": class_item["origem"],
                "alocacao": class_item["professor"] or "",
                "professores": ";".join(observed_teachers),
                "capacidade": class_capacity or "",
                "inscritos": enrolled if enrolled is not None else "",
                "obrigatoria": obligatory if obligatory is not None else "",
                "compartilhada_cc_si": shared_curriculum,
                "compartilhada_vagas_cc_si": shared_vacancies,
                "turma_url": link.turma_url,
                "metodo_vinculo": link.metodo_vinculo,
            }
        )

    room_ids = sorted({meeting["sala"] for item in classes_json for meeting in item["encontros"] if meeting["sala"]})
    rooms = []
    room_rows = []
    for room in room_ids:
        lab = is_lab_room(room)
        minimum_observed = max(room_demands.get(room, []), default=None)
        rooms.append(
            {
                "id": room,
                "laboratorio": lab,
                "resources": ["laboratorio"] if lab else [],
                "capacity": None,
                "capacidade_estimada": None,
                "capacidade_minima_observada": minimum_observed,
                "capacidade_fonte": "capacidade física não disponível; mínimo observado calculado pelas vagas",
            }
        )
        room_rows.append(
            {
                "id": room,
                "laboratorio": lab,
                "capacidade": "",
                "capacidade_minima_observada": minimum_observed or "",
                "capacidade_fonte": "limite inferior pelas vagas das turmas observadas; não é capacidade física",
            }
        )

    curriculum_groups = []
    obligatory_curricula = curricula[curricula["tipo"].eq("obrigatoria")]
    for (course, group), values in obligatory_curricula.groupby(["curso", "grupo"]):
        curriculum_groups.append(
            {
                "curso": course,
                "periodo": group,
                "disciplinas": sorted(values["codigo"].unique()),
                "fonte": str(values["fonte"].iloc[0]),
            }
        )

    teacher_names = sorted({teacher for item in classes_json for teacher in item["professores_observados"]})
    linked_pdf_ids = set(links["turma_id"])
    excluded = pdf_classes[~pdf_classes["id"].isin(linked_pdf_ids)]
    unknown_curriculum = [item["id"] for item in classes_json if not item["grupos_curriculares"]]
    multiple_teacher = [item["id"] for item in classes_json if item["alocacao_tipo"] == "multipla"]

    instance = {
        "schema_version": "0.2",
        "source": [
            "dados/brutos/QH-2026-1.pdf",
            "dados/brutos/QH-2026-2.pdf",
            "webscrap/turmas_2026_raw.csv",
            "dados/grade_cc.md",
            "dados/grade_si.md",
        ],
        "profile": "cc_si",
        "ano": 2026,
        "pronta_para_experimento": False,
        "evaluation_readiness": {
            "vagas_turmas": True,
            "vinculo_cc_si": True,
            "turmas_compartilhadas": True,
            "conflitos_curriculares": len(unknown_curriculum) == 0,
            "conflitos_sala": True,
            "capacidade_salas": False,
            "h12": False,
            "professores_multiplos": len(multiple_teacher) == 0,
            "setores_preferencias_prioridades": False,
        },
        "notes": [
            "Cada turma_url aparece uma única vez, inclusive quando atende CC e SI.",
            "A condição compartilhada curricular é inferida pela interseção dos códigos das duas grades.",
            "Vagas compartilhadas observadas são mantidas em campo separado da interseção curricular.",
            "Duas linhas compactadas dos PDFs foram expandidas em suas turmas AA e BA conforme o sistema público.",
            "Horários, professores e salas continuam sendo alocações observadas, não domínios fixos.",
            "Capacidade física das salas não foi inferida; capacidade_minima_observada é apenas um limite inferior.",
        ],
        "rooms": rooms,
        "teachers": [
            {"name": teacher, "observado_no_qh": True, "incluido_h12": None, "prioridade": None}
            for teacher in teacher_names
        ],
        "curriculum_groups": curriculum_groups,
        "classes": classes_json,
        "pending": {
            "turmas_sem_grupo_curricular_na_grade_markdown": unknown_curriculum,
            "turmas_com_multiplos_professores": multiple_teacher,
            "capacidade_fisica_salas": room_ids,
            "universo_h12": "não definido",
        },
        "excluded_pdf_records": [
            {
                "id": row.id,
                "status": row.status,
                "categoria_observada": row.categoria_observada,
                "motivo": "não retornada nas buscas públicas pelos currículos atuais de CC/SI",
            }
            for row in excluded.itertuples()
        ],
    }

    OUT.write_text(json.dumps(instance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pd.DataFrame(class_rows).to_csv(CLASSES_OUT, index=False)
    pd.DataFrame(meeting_rows).to_csv(MEETINGS_OUT, index=False)
    pd.DataFrame(room_rows).to_csv(ROOMS_OUT, index=False)
    print(
        f"{OUT}: {len(classes_json)} turmas CC/SI, {len(meeting_rows)} encontros, "
        f"{len(teacher_names)} docentes, {len(unknown_curriculum)} sem grupo curricular"
    )


if __name__ == "__main__":
    main()
