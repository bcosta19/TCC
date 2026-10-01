"""Pré-preenche ``revisao_horarios_fixos_2026.csv`` pela regra de 30/09/2026.

Regra (``anotacoes/decisoes_modelagem_2026_09_30.md``):

- turma de outro departamento → horário fixo;
- turma do IC com ao menos uma vaga alocada para curso que não seja CC (31)
  nem SI (83) na página pública da turma ("Vagas Alocadas") → disciplina
  oferecida a outros cursos, horário fixo;
- código listado como disciplina-serviço → horário fixo;
- demais turmas do IC → horário flexível dentro do setor.

Como a decisão é a aplicação de uma regra aprovada pelo aluno, as linhas
recebem ``validado=sim`` e a evidência fica em ``cursos_externos`` e
``criterio_horario``. Linhas já validadas com outro valor não são alteradas,
salvo com ``--sobrescrever``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dados" / "processados"
TABLE = DATA / "revisao_horarios_fixos_2026.csv"
INSTANCE = DATA / "instancia_2026_cc_si.json"
INTERNAL_COURSES = {"31", "83"}
SERVICE_CODES = {"TCC00319"}
RULE_DATE = "30/09/2026"


def external_courses(item: dict) -> list[str]:
    return [
        f"{entry.get('curso')} ({int(entry.get('vagas') or 0)})"
        for entry in item.get("vagas_por_curso") or []
        if str(entry.get("codigo_curso")) not in INTERNAL_COURSES and int(entry.get("vagas") or 0) > 0
    ]


def decide(item: dict) -> tuple[bool, str, list[str]]:
    courses = external_courses(item)
    if item.get("origem") != "IC":
        return True, "turma de outro departamento", courses
    if item.get("codigo") in SERVICE_CODES:
        return True, "disciplina-serviço", courses
    if courses:
        return True, "oferecida a cursos fora de CC/SI", courses
    return False, "turma do IC só para CC/SI: flexível no setor", courses


def prefill(table: pd.DataFrame, classes: dict[str, dict], overwrite: bool = False) -> pd.DataFrame:
    table = table.copy()
    for column in ("cursos_externos", "criterio_horario"):
        if column not in table.columns:
            table[column] = ""
    for index, row in table.iterrows():
        item = classes.get(row["turma_id"])
        if item is None:
            continue
        human = str(row.get("validado", "")).strip().lower() == "sim" and not str(row.get("criterio_horario", "")).startswith("regra")
        if human and not overwrite:
            continue
        fixed, reason, courses = decide(item)
        table.at[index, "horario_fixo"] = "sim" if fixed else "nao"
        table.at[index, "cursos_externos"] = "; ".join(courses)
        table.at[index, "criterio_horario"] = f"regra {RULE_DATE}: {reason}"
        table.at[index, "validado"] = "sim"
    return table


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sobrescrever", action="store_true", help="Reaplica a regra também em linhas validadas manualmente")
    args = parser.parse_args()
    instance = json.loads(INSTANCE.read_text(encoding="utf-8"))
    classes = {item["id"]: item for item in instance.get("classes", [])}
    table = pd.read_csv(TABLE, dtype=str).fillna("")
    result = prefill(table, classes, overwrite=args.sobrescrever)
    result.to_csv(TABLE, index=False)
    print(f"{TABLE}:")
    for value, count in result["criterio_horario"].value_counts().items():
        print(f"  - {value}: {count}")


if __name__ == "__main__":
    main()
