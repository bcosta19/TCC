"""Cruza as ofertas de 2026 com as grades curriculares de CC e SI.

A interseção é feita pelo código da disciplina. Uma oferta presente nas duas
grades permanece uma única turma e recebe os dois vínculos curriculares.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.model.curricula import classify_code, load_project_curricula


DATA = ROOT / "dados" / "processados"
CURRICULA_OUT = DATA / "curriculos_cc_si.csv"
INTERSECTION_OUT = DATA / "intersecao_curriculos_cc_si.csv"
CLASSIFICATION_OUT = DATA / "classificacao_curricular_2026.csv"


def joined(values: list[object]) -> str:
    return ";".join(str(value) for value in values)


def main() -> None:
    curricula = load_project_curricula(ROOT)
    class_rows = pd.read_csv(DATA / "turmas_2026.csv", dtype=str).fillna("")

    curriculum_rows = []
    codes_by_course = {}
    for course, entries in curricula.items():
        codes_by_course[course] = {entry.code for entry in entries}
        for entry in entries:
            curriculum_rows.append(
                {
                    "curso": course,
                    "codigo_curso": "31" if course == "CC" else "83",
                    "codigo": entry.code,
                    "disciplina": entry.discipline,
                    "tipo": entry.kind,
                    "periodo": entry.period or "",
                    "grupo": entry.group,
                    "ch": entry.hours,
                    "fonte": str(Path(entry.source).relative_to(ROOT)),
                }
            )
    pd.DataFrame(curriculum_rows).to_csv(CURRICULA_OUT, index=False)

    intersection_rows = []
    for code in sorted(codes_by_course["CC"] & codes_by_course["SI"]):
        classification = classify_code(code, curricula)
        cc = classification["memberships"]["CC"]
        si = classification["memberships"]["SI"]
        intersection_rows.append(
            {
                "codigo": code,
                "tipos_cc": joined(cc["kinds"]),
                "periodos_cc": joined(cc["periods"]),
                "grupos_cc": joined(cc["groups"]),
                "tipos_si": joined(si["kinds"]),
                "periodos_si": joined(si["periods"]),
                "grupos_si": joined(si["groups"]),
                "oferta_compartilhada_inferida": True,
                "criterio": "interseção dos códigos em dados/grade_cc.md e dados/grade_si.md",
            }
        )
    pd.DataFrame(intersection_rows).to_csv(INTERSECTION_OUT, index=False)

    classified_rows = []
    for row in class_rows.itertuples():
        classification = classify_code(row.codigo, curricula)
        memberships = classification["memberships"]
        groups = sorted(
            group
            for membership in memberships.values()
            for group in membership["groups"]
        )
        classified_rows.append(
            {
                "turma_id": row.id,
                "semestre": row.semestre,
                "codigo": row.codigo,
                "disciplina": row.disciplina,
                "turma": row.turma,
                "nos_curriculos": classification["in_curricula"],
                "curriculos": joined(classification["courses"]),
                "grupos_curriculares": joined(groups),
                "periodos_cc": joined(memberships.get("CC", {}).get("periods", [])),
                "tipos_cc": joined(memberships.get("CC", {}).get("kinds", [])),
                "periodos_si": joined(memberships.get("SI", {}).get("periods", [])),
                "tipos_si": joined(memberships.get("SI", {}).get("kinds", [])),
                "obrigatoria": classification["obligatory"],
                "obrigatoria_nos_curriculos": joined(classification["obligatory_courses"]),
                "compartilhada_cc_si": classification["shared"],
                "status_classificacao": (
                    "classificada_por_codigo"
                    if classification["in_curricula"]
                    else ("sem_codigo" if not row.codigo else "fora_dos_curriculos")
                ),
                "fonte": "dados/grade_cc.md;dados/grade_si.md",
            }
        )
    classified = pd.DataFrame(classified_rows)
    classified.to_csv(CLASSIFICATION_OUT, index=False)

    summary = {
        "codigos_cc": len(codes_by_course["CC"]),
        "codigos_si": len(codes_by_course["SI"]),
        "intersecao": len(intersection_rows),
        "ofertas_2026_classificadas": int(classified["nos_curriculos"].sum()),
        "ofertas_2026_compartilhadas": int(classified["compartilhada_cc_si"].sum()),
        "ofertas_2026_obrigatorias": int(classified["obrigatoria"].sum()),
        "ofertas_2026_fora_dos_curriculos": int(classified["status_classificacao"].eq("fora_dos_curriculos").sum()),
        "ofertas_2026_sem_codigo": int(classified["status_classificacao"].eq("sem_codigo").sum()),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
