"""Audita o recorte CC/SI de 2026 após o vínculo PDF × sistema público."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dados" / "processados"
OUT_JSON = DATA / "auditoria_2026_cc_si.json"
OUT_MD = DATA / "auditoria_2026_cc_si.md"
CONFLICTS_OUT = DATA / "conflitos_candidatos_2026_cc_si.csv"


def minute(value: str) -> int:
    hour, minutes = str(value).split(":")
    return int(hour) * 60 + int(minutes)


def overlaps(first: dict, second: dict) -> bool:
    return max(minute(first["inicio"]), minute(second["inicio"])) < min(
        minute(first["fim"]), minute(second["fim"])
    )


def conflict_pairs(classes: pd.DataFrame, meetings: pd.DataFrame) -> pd.DataFrame:
    lookup = classes.set_index("id")
    values = meetings.copy()
    values["professores"] = values["turma_id"].map(lookup["professores"]).fillna("")
    values["disciplina"] = values["turma_id"].map(lookup["disciplina"]).fillna("")
    rows = []

    def compare(frame: pd.DataFrame, keys: list[str], kind: str) -> None:
        for key, group in frame.groupby(keys):
            records = group.to_dict("records")
            for index, first in enumerate(records):
                for second in records[index + 1 :]:
                    if first["turma_id"] == second["turma_id"] or not overlaps(first, second):
                        continue
                    resource = key[-1] if isinstance(key, tuple) else key
                    rows.append(
                        {
                            "tipo": kind,
                            "semestre": first["semestre"],
                            "dia": first["dia"],
                            "recurso": resource,
                            "turma_id_a": first["turma_id"],
                            "codigo_a": first["codigo"],
                            "disciplina_a": first["disciplina"],
                            "inicio_a": first["inicio"],
                            "fim_a": first["fim"],
                            "turma_id_b": second["turma_id"],
                            "codigo_b": second["codigo"],
                            "disciplina_b": second["disciplina"],
                            "inicio_b": second["inicio"],
                            "fim_b": second["fim"],
                            "mesmo_codigo": bool(first["codigo"] == second["codigo"]),
                        }
                    )

    compare(values[values["sala"].ne("")], ["semestre", "dia", "sala"], "sala")
    teachers = values.assign(professor=values["professores"].str.split(";")).explode("professor")
    teachers["professor"] = teachers["professor"].fillna("").str.strip()
    compare(
        teachers[teachers["professor"].ne("")],
        ["semestre", "dia", "professor"],
        "professor",
    )
    return pd.DataFrame(rows)


def curriculum_conflicts(classes: pd.DataFrame, meetings: pd.DataFrame) -> pd.DataFrame:
    lookup = classes.set_index("id")
    values = meetings.copy()
    values["grupos"] = values["turma_id"].map(lookup["grupos_curriculares"]).fillna("")
    values["grupo"] = values["grupos"].str.split(";")
    values = values.explode("grupo")
    values = values[values["grupo"].str.match(r"^(?:CC|SI)-P[1-8]$")]
    values = values.drop_duplicates(
        ["semestre", "grupo", "codigo", "dia", "inicio", "fim"]
    )
    groups = values.groupby(["semestre", "grupo", "dia", "inicio", "fim"])
    rows = []
    for key, group in groups:
        codes = sorted(group["codigo"].unique())
        if len(codes) > 1:
            rows.append(
                {
                    "semestre": key[0],
                    "grupo": key[1],
                    "dia": key[2],
                    "inicio": key[3],
                    "fim": key[4],
                    "codigos": ";".join(codes),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    classes = pd.read_csv(DATA / "turmas_2026_cc_si.csv", dtype=str).fillna("")
    meetings = pd.read_csv(DATA / "horarios_2026_cc_si.csv", dtype=str).fillna("")
    rooms = pd.read_csv(DATA / "salas_2026_cc_si.csv", dtype=str).fillna("")
    links = pd.read_csv(DATA / "vagas_turmas_2026.csv", dtype=str).fillna("")
    intersection = pd.read_csv(DATA / "intersecao_curriculos_cc_si.csv", dtype=str).fillna("")

    conflicts = conflict_pairs(classes, meetings)
    conflicts.to_csv(CONFLICTS_OUT, index=False)
    curricular = curriculum_conflicts(classes, meetings)

    obligatory = classes[classes["obrigatoria"].str.lower().eq("true")]
    obligatory_counts = obligatory.assign(
        professor=obligatory["professores"].str.split(";")
    ).explode("professor")
    obligatory_counts = obligatory_counts[obligatory_counts["professor"].ne("")]
    counts = obligatory_counts.groupby("professor")["id"].nunique().sort_values(ascending=False)
    unknown_groups = classes[classes["grupos_curriculares"].eq("")]
    multiple_teachers = classes[classes["professores"].str.contains(";", regex=False)]
    no_room = meetings[meetings["sala"].eq("")]
    room_conflicts = conflicts[conflicts["tipo"].eq("sala")] if not conflicts.empty else conflicts
    teacher_conflicts = conflicts[conflicts["tipo"].eq("professor")] if not conflicts.empty else conflicts
    schedule_mismatches = links[links["metodo_vinculo"].eq("turma_exata")]

    result = {
        "turmas": len(classes),
        "encontros": len(meetings),
        "docentes_observados": int(
            classes.assign(professor=classes["professores"].str.split(";"))
            .explode("professor")["professor"].replace("", pd.NA).dropna().nunique()
        ),
        "salas": len(rooms),
        "turmas_com_vagas": int(classes["capacidade"].ne("").sum()),
        "turmas_obrigatorias": len(obligatory),
        "turmas_com_obrigatoriedade_desconhecida": int(classes["obrigatoria"].eq("").sum()),
        "codigos_na_intersecao_curricular": len(intersection),
        "turmas_compartilhadas_por_intersecao": int(
            classes["compartilhada_cc_si"].str.lower().eq("true").sum()
        ),
        "turmas_com_vagas_cc_e_si": int(
            classes["compartilhada_vagas_cc_si"].str.lower().eq("true").sum()
        ),
        "turmas_com_multiplos_professores": len(multiple_teachers),
        "turmas_sem_grupo_curricular": unknown_groups["id"].tolist(),
        "encontros_sem_sala": len(no_room),
        "sobreposicoes_sala": len(room_conflicts),
        "sobreposicoes_professor": len(teacher_conflicts),
        "conflitos_curriculares_observados": len(curricular),
        "divergencias_horario_pdf_web": schedule_mismatches["turma_id"].tolist(),
        "h12": {
            "obrigatorias_disponiveis": len(obligatory),
            "maximo_docentes_que_podem_receber_tres": len(obligatory) // 3,
            "docentes_com_contagem_observada": len(counts),
            "calculavel_como_restricao": False,
            "motivos": [
                "universo oficial de docentes H12 ainda ausente",
                "duas turmas do recorte têm alocação docente múltipla",
            ],
        },
        "capacidade": {
            "vagas_turmas_disponiveis": True,
            "capacidades_fisicas_salas_disponiveis": False,
            "capacidade_minima_observada_nao_e_capacidade_fisica": True,
        },
    }
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Auditoria da instância CC/SI observada em 2026",
        "",
        "> Auditoria de dados; as sobreposições não são resultados experimentais.",
        "",
        "## Cobertura obtida",
        "",
        f"- Turmas físicas após consolidar/expandir os registros: **{len(classes)}**.",
        f"- Encontros semanais: **{len(meetings)}**.",
        f"- Docentes observados: **{result['docentes_observados']}**.",
        f"- Salas observadas: **{len(rooms)}**.",
        f"- Turmas com vagas e inscritos disponíveis: **{result['turmas_com_vagas']}**.",
        f"- Turmas classificadas como obrigatórias: **{len(obligatory)}**.",
        f"- Turmas com obrigatoriedade ainda desconhecida: **{result['turmas_com_obrigatoriedade_desconhecida']}**.",
        "",
        "## Turmas compartilhadas",
        "",
        f"- Códigos na interseção das grades completas: **{len(intersection)}**.",
        f"- Turmas de 2026 compartilhadas pela interseção curricular: **{result['turmas_compartilhadas_por_intersecao']}**.",
        f"- Turmas com vagas simultaneamente alocadas a CC e SI: **{result['turmas_com_vagas_cc_e_si']}**.",
        "",
        "Os dois indicadores são diferentes: a interseção descreve a grade; as vagas",
        "descrevem a alocação observada da turma no semestre.",
        "",
        "## Pendências remanescentes",
        "",
        f"- Sem grupo curricular nas grades Markdown: **{len(unknown_groups)}** — "
        + ", ".join(f"`{value}`" for value in unknown_groups["id"]) + ".",
        f"- Turmas com múltiplos professores: **{len(multiple_teachers)}**.",
        f"- Encontros sem sala: **{len(no_room)}**.",
        "- Capacidades físicas das salas: ausentes; `capacidade_minima_observada`",
        "  é somente um limite inferior derivado das vagas.",
        "- Universo oficial de docentes submetidos a H12: ausente.",
        "",
        "## Verificações da alocação observada",
        "",
        f"- Sobreposições candidatas de sala: **{len(room_conflicts)}**.",
        f"- Sobreposições candidatas de professor: **{len(teacher_conflicts)}**.",
        f"- Conflitos curriculares observados: **{len(curricular)}**.",
        f"- Divergências de horário PDF × página pública: **{len(schedule_mismatches)}**.",
        "",
        "Os pares de sala/professor estão em `conflitos_candidatos_2026_cc_si.csv`.",
        "",
        "## Condição estrutural de H12",
        "",
        f"Há **{len(obligatory)}** turmas obrigatórias classificadas. Sem contar",
        f"alocações múltiplas, esse total comporta no máximo **{len(obligatory) // 3}**",
        "docentes recebendo três obrigatórias. A violação de H12 só pode ser calculada",
        "após definir quais docentes compõem seu universo.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT_MD)


if __name__ == "__main__":
    main()
