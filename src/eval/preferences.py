"""Construção da matriz histórica de preferência professor×disciplina.

As frequências vêm do webscrap e são apenas uma proxy de preferência. A
prioridade do professor permanece um parâmetro separado da instância.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd


def normalize_name(value: object) -> str:
    """Normaliza nomes para permitir o vínculo entre fontes com abreviações."""
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.upper().replace(", 20H", "")
    return re.sub(r"[^A-Z0-9]+", " ", text).strip()


def _teacher_aliases(carga: pd.DataFrame) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for _, row in carga.iterrows():
        alias = str(row.get("Nome Planilha", "")).strip()
        full_name = str(row.get("Docente", "")).strip()
        if alias:
            aliases[normalize_name(alias)] = alias
        if full_name and alias:
            aliases[normalize_name(full_name)] = alias
    return aliases


def _map_historical_teacher(name: object, aliases: dict[str, str]) -> str:
    normalized = normalize_name(name)
    if normalized in aliases:
        return aliases[normalized]
    candidates = [
        (key, value)
        for key, value in aliases.items()
        if key and (key in normalized or normalized in key)
    ]
    if candidates:
        return max(candidates, key=lambda item: len(item[0]))[1]
    return str(name or "").strip()


def load_preference_lookup(
    workbook_path: str | Path,
    carga_path: str | Path,
    teachers: list[str],
) -> tuple[dict[str, dict[str, float]], pd.DataFrame]:
    """Retorna ``codigo -> professor -> preferência normalizada``.

    Para cada disciplina, a maior frequência histórica observada recebe 1.0;
    códigos sem histórico recebem 0.0. A tabela longa retornada é útil para
    auditoria e relatório do experimento.
    """
    workbook_path = Path(workbook_path)
    carga_path = Path(carga_path)
    empty_columns = ["codigo", "professor", "contagem", "max_codigo", "preferencia"]
    if not workbook_path.exists() or not carga_path.exists():
        empty = pd.DataFrame(columns=empty_columns)
        return {}, empty

    historical = pd.read_excel(workbook_path, sheet_name="Por Disciplina")
    carga = pd.read_csv(carga_path, dtype=str).fillna("")
    aliases = _teacher_aliases(carga)
    historical["professor"] = historical["docente"].map(
        lambda value: _map_historical_teacher(value, aliases)
    )
    historical["codigo"] = historical["codigo"].astype(str)
    historical["contagem"] = pd.to_numeric(
        historical["total_turmas"], errors="coerce"
    ).fillna(0.0)
    historical = historical[["codigo", "professor", "contagem"]]
    historical = historical.groupby(["codigo", "professor"], as_index=False)["contagem"].sum()
    historical["max_codigo"] = historical.groupby("codigo")["contagem"].transform("max")
    historical["preferencia"] = historical["contagem"].where(
        historical["max_codigo"].eq(0), historical["contagem"] / historical["max_codigo"]
    )

    teacher_set = set(teachers)
    lookup = {code: {teacher: 0.0 for teacher in teachers} for code in historical["codigo"].unique()}
    for row in historical.itertuples(index=False):
        if row.codigo in lookup and row.professor in teacher_set:
            lookup[row.codigo][row.professor] = float(row.preferencia)
    return lookup, historical
