"""Pré-preenche o tratamento das turmas externas obrigatórias de CC/SI.

Regra decidida em 30/09/2026 (opção 1 de
``anotacoes/decisoes_modelagem_2026_09_30.md``): para cada disciplina externa
obrigatória de um período de CC ou SI, fixa-se em H8 uma única turma de
referência por semestre, a com mais alunos do curso inscritos (desempate por
vagas e pelo nome da turma) entre as que não chocam com as referências já
escolhidas para o mesmo período. Os inscritos vêm da página pública da turma
("Vagas Alocadas"), já coletada em ``vagas_por_curso``. A coluna
``inscritos_curso_pct`` registra a fração dos inscritos do curso na turma de
referência: valores baixos indicam alunos espalhados entre várias turmas. As demais turmas da mesma disciplina ficam
como ``alternativa_nao_modelada``.

Só linhas com ``tratamento_no_modelo`` vazio são alteradas, salvo com
``--sobrescrever``. Ofertas que não são obrigatórias externas de CC/SI ficam
para decisão manual.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dados" / "processados"
TABLE = DATA / "revisao_turmas_externas_2026.csv"
INSTANCE = DATA / "instancia_2026_cc_si.json"
COURSE_CODES = {"CC": "31", "SI": "83"}
REFERENCE = "fixar_horario_e_sala"
ALTERNATIVE = "alternativa_nao_modelada"
CRITERION = "turma de referência: mais inscritos do curso sem choque com as demais referências do período (regra de 30/09/2026)"
MEETING_RE = re.compile(r"(Seg|Ter|Qua|Qui|Sex|Sab)\s+(\d{2}:\d{2})-(\d{2}:\d{2})")


def course_offer(vacancies_json: str, course_code: str) -> tuple[int, int]:
    try:
        entries = json.loads(vacancies_json or "[]")
    except json.JSONDecodeError:
        return 0, 0
    vacancies = sum(int(entry.get("vagas") or 0) for entry in entries if str(entry.get("codigo_curso")) == course_code)
    enrolled = sum(int(entry.get("inscritos") or 0) for entry in entries if str(entry.get("codigo_curso")) == course_code)
    return vacancies, enrolled


def external_groups(instance: dict) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for group in instance.get("curriculum_groups", []):
        for code in group.get("disciplinas", []):
            if not code.startswith("TCC"):
                groups.setdefault(code, []).append(group["periodo"])
    return groups


def meetings(schedule: str) -> list[tuple[str, int, int]]:
    result = []
    for day, start, end in MEETING_RE.findall(schedule or ""):
        to_minutes = lambda value: int(value[:2]) * 60 + int(value[3:])
        result.append((day, to_minutes(start), to_minutes(end)))
    return result


def overlaps(first: str, second: str) -> bool:
    return any(
        day_a == day_b and start_a < end_b and start_b < end_a
        for day_a, start_a, end_a in meetings(first)
        for day_b, start_b, end_b in meetings(second)
    )


def prefill(table: pd.DataFrame, groups: dict[str, list[str]], overwrite: bool = False) -> pd.DataFrame:
    """Escolhe uma turma de referência por disciplina, semestre e período.

    As disciplinas de cada período são tratadas da que tem menos turmas para a
    que tem mais; para cada uma, escolhe-se a turma de mais vagas para o curso
    que não choque com as referências já escolhidas no mesmo período. Se todas
    chocarem, fica a de mais vagas e o choque é registrado no critério.
    """
    table = table.copy()
    for column in ("criterio_referencia", "inscritos_curso_pct"):
        if column not in table.columns:
            table[column] = ""
    editable = table["tratamento_no_modelo"].str.strip().eq("") | overwrite

    codes_by_group: dict[str, list[str]] = {}
    for code, code_groups in groups.items():
        for group in code_groups:
            codes_by_group.setdefault(group, []).append(code)

    for group, codes in sorted(codes_by_group.items()):
        course_code = COURSE_CODES[group.split("-")[0]]
        for semester in sorted(table["semestre"].unique()):
            chosen: list[int] = []
            candidates_by_code = {
                code: table[table["codigo"].eq(code) & table["semestre"].eq(semester)].index.tolist()
                for code in codes
            }
            for code in sorted(codes, key=lambda value: (len(candidates_by_code[value]), value)):
                offered = [
                    index for index in candidates_by_code[code]
                    if course_offer(table.at[index, "vagas_por_curso"], course_code)[0] > 0
                ]
                ranked = sorted(
                    offered,
                    key=lambda index: (
                        -course_offer(table.at[index, "vagas_por_curso"], course_code)[1],
                        -course_offer(table.at[index, "vagas_por_curso"], course_code)[0],
                        table.at[index, "turma"],
                    ),
                )
                if not ranked:
                    continue
                compatible = [
                    index for index in ranked
                    if not any(overlaps(table.at[index, "horarios"], table.at[other, "horarios"]) for other in chosen)
                ]
                reference = (compatible or ranked)[0]
                chosen.append(reference)
                criterion = CRITERION if compatible else CRITERION + "; choca com outra referência do período"
                enrolled = sum(course_offer(table.at[index, "vagas_por_curso"], course_code)[1] for index in offered)
                share = course_offer(table.at[reference, "vagas_por_curso"], course_code)[1] / enrolled if enrolled else 0.0
                if editable[reference]:
                    table.at[reference, "inscritos_curso_pct"] = f"{100 * share:.0f}"
                    current = [value for value in table.at[reference, "periodo_curricular"].split(";") if value]
                    table.at[reference, "periodo_curricular"] = ";".join(sorted(set(current) | {group}))
                    table.at[reference, "tratamento_no_modelo"] = REFERENCE
                    table.at[reference, "criterio_referencia"] = criterion
                for index in candidates_by_code[code]:
                    if index != reference and editable[index] and table.at[index, "tratamento_no_modelo"] != REFERENCE:
                        table.at[index, "tratamento_no_modelo"] = ALTERNATIVE
                        table.at[index, "criterio_referencia"] = f"alternativa à turma {table.at[reference, 'turma']}"
    return table


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sobrescrever", action="store_true", help="Reaplica a regra mesmo em linhas já preenchidas")
    args = parser.parse_args()
    table = pd.read_csv(TABLE, dtype=str).fillna("")
    groups = external_groups(json.loads(INSTANCE.read_text(encoding="utf-8")))
    result = prefill(table, groups, overwrite=args.sobrescrever)
    result.to_csv(TABLE, index=False)
    counts = result["tratamento_no_modelo"].replace("", "(vazio)").value_counts()
    print(f"{TABLE}:")
    for value, count in counts.items():
        print(f"  - {value}: {count}")


if __name__ == "__main__":
    main()
