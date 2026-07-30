"""Extrai os quadros QH-2025-1/2 para CSVs normalizados."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "dados" / "brutos" / "QH-2025-1-2.xlsx"
OUTPUT = ROOT / "dados" / "processados"

DAY_COLUMNS = {
    "2ª": "segunda",
    "3ª": "terca",
    "4ª": "quarta",
    "5ª": "quinta",
    "6ª": "sexta",
    "Sáb.": "sabado",
}


def clean(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).replace("\r", "").strip()


def parse_slot(value: str) -> tuple[str, str, str] | None:
    """Extrai inicio, fim e sala de células como '09/11\\n321'."""
    value = clean(value)
    if not value or value in {"-", "EXTERNA"}:
        return None
    match = re.search(r"(\d{1,2})\s*/\s*(\d{1,2})", value)
    if not match:
        return None
    start, end = match.groups()
    rest = value[match.end():].strip()
    room = re.sub(r"\s+", "", rest).strip("-;,")
    if room.lower() == "sala":
        room = ""
    return f"{int(start):02d}:00", f"{int(end):02d}:00", room


def parse_sheet(sheet: str) -> tuple[list[dict], list[dict]]:
    frame = pd.read_excel(INPUT, sheet_name=sheet, header=0)
    semester = sheet.removeprefix("QH-")
    turma_rows: list[dict] = []
    horario_rows: list[dict] = []

    for row_number, row in frame.iterrows():
        code = clean(row.get("Código"))
        name = clean(row.get("Disciplina"))
        turma = clean(row.get("Código Turma"))
        if not code or not name or code == "nan" or name.startswith("SEÇÃO:"):
            continue
        if not re.match(r"^[A-Z]{2,4}\d{4,6}$", code):
            continue

        turma_id = f"{semester.replace('/', '.')}-{code}-{turma}"
        record = {
            "id": turma_id,
            "semestre": semester,
            "curso": clean(row.get("Curso")).replace(".0", ""),
            "periodo": clean(row.get("PERIODO")),
            "ch_ob": clean(row.get("CH-OB")),
            "ch_op": clean(row.get("CH-OP")),
            "capacidade": clean(row.get("CAP")).replace(".0", ""),
            "codigo": code,
            "disciplina": name,
            "turma": turma,
            "setor": clean(row.get("Setor")),
            "alocacao": clean(row.get("ALOCAÇÃO 2025.1")) or clean(row.get("ALOCAÇÃO 2025.2")),
            "codigo_horario": clean(row.get("Código Horario")),
            "origem": "IC" if code.startswith("TCC") else "externa",
            "linha_planilha": int(row_number) + 2,
        }
        turma_rows.append(record)

        for column, day in DAY_COLUMNS.items():
            parsed = parse_slot(row.get(column, ""))
            if parsed is None:
                continue
            start, end, room = parsed
            horario_rows.append({
                "turma_id": turma_id,
                "semestre": semester,
                "codigo": code,
                "turma": turma,
                "dia": day,
                "inicio": start,
                "fim": end,
                "sala": room,
                "valor_original": clean(row.get(column)),
            })
    return turma_rows, horario_rows


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    all_turmas: list[dict] = []
    all_horarios: list[dict] = []
    for sheet in ("QH-2025-1", "QH-2025-2"):
        turmas, horarios = parse_sheet(sheet)
        all_turmas.extend(turmas)
        all_horarios.extend(horarios)

    turmas = pd.DataFrame(all_turmas)
    horarios = pd.DataFrame(all_horarios)
    turmas.to_csv(OUTPUT / "turmas_2025.csv", index=False)
    horarios.to_csv(OUTPUT / "horarios_2025.csv", index=False)

    docente = pd.read_excel(INPUT, sheet_name="CH Docente", header=1)
    docente = docente.dropna(how="all")
    docente.to_csv(OUTPUT / "carga_docente_2025.csv", index=False)

    resumo = {
        "arquivo_origem": str(INPUT.relative_to(ROOT)),
        "abas_processadas": ["QH-2025-1", "QH-2025-2", "CH Docente"],
        "turmas": int(len(turmas)),
        "horarios": int(len(horarios)),
        "por_semestre": turmas.groupby("semestre").size().to_dict(),
        "por_origem": turmas.groupby("origem").size().to_dict(),
        "por_setor": turmas["setor"].replace("", "SEM_SETOR").value_counts().to_dict(),
        "salas": sorted(x for x in horarios["sala"].dropna().unique() if x),
        "disciplinas": int(turmas["codigo"].nunique()),
    }
    (OUTPUT / "resumo_2025.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(resumo, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
