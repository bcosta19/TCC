"""Audita a instância CC/SI processada antes dos experimentos."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA = ROOT / "dados" / "processados"
OUT_JSON = DATA / "auditoria_2025_cc_si.json"
OUT_MD = DATA / "auditoria_2025_cc_si.md"


def main() -> None:
    t = pd.read_csv(DATA / "turmas_2025.csv", dtype=str).fillna("")
    h = pd.read_csv(DATA / "horarios_2025.csv", dtype=str).fillna("")
    r = pd.read_csv(DATA / "salas_2025.csv", dtype=str).fillna("")
    keep = t["curso"].isin({"31", "83"}) | (
        t["curso"].eq("") & t["periodo"].str.startswith(("CC-", "SI-"))
    )
    t = t[keep].copy()
    h = h[h["turma_id"].isin(set(t["id"]))].copy()

    duplicate_ids = t[t["id"].duplicated(keep=False)]["id"].unique().tolist()
    missing_meetings = sorted(set(t["id"]) - set(h["turma_id"]))
    orphan_meetings = sorted(set(h["turma_id"]) - set(t["id"]))
    invalid_time = h[~h["inicio"].str.match(r"^\d{2}:\d{2}$") | ~h["fim"].str.match(r"^\d{2}:\d{2}$")]
    no_room = h[h["sala"].eq("")]
    room_ids = set(r["id"])
    unknown_rooms = sorted(set(h["sala"]) - {""} - room_ids)
    missing_teacher = t[t["alocacao"].eq("")]["id"].tolist()
    missing_sector = t[t["setor"].eq("")]["id"].tolist()
    lab_rooms = r[r["laboratorio"].astype(str).str.lower().eq("true")]["id"].tolist()
    resource_path = DATA / "recursos_turmas_2025.csv"
    resource_classes = pd.read_csv(resource_path, dtype=str).fillna("") if resource_path.exists() else pd.DataFrame()
    lab_classes = int(resource_classes["exige_laboratorio"].eq("True").sum()) if not resource_classes.empty else 0
    unknown_resource_classes = int(resource_classes["exige_laboratorio"].eq("").sum()) if not resource_classes.empty else 0

    result = {
        "perfil": "cc_si",
        "turmas": len(t),
        "encontros": len(h),
        "salas": len(r),
        "laboratorios": lab_rooms,
        "turmas_com_laboratorio_inferido": lab_classes,
        "turmas_com_recurso_desconhecido": unknown_resource_classes,
        "ids_duplicados": duplicate_ids,
        "turmas_sem_encontro": missing_meetings,
        "encontros_sem_turma": orphan_meetings,
        "horarios_invalidos": int(len(invalid_time)),
        "encontros_sem_sala": int(len(no_room)),
        "salas_desconhecidas": unknown_rooms,
        "turmas_sem_professor": missing_teacher,
        "turmas_sem_setor": missing_sector,
    }
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Auditoria da instância CC/SI 2025",
        "",
        f"- Turmas: **{len(t)}**",
        f"- Encontros: **{len(h)}**",
        f"- Salas: **{len(r)}**",
        f"- Laboratórios inferidos: **{', '.join(lab_rooms) or 'nenhum'}**",
        f"- Turmas com laboratório inferido: **{lab_classes}**",
        f"- Turmas com recurso desconhecido: **{unknown_resource_classes}**",
        "",
        "## Verificações",
        "",
        f"- IDs de turma duplicados: **{len(duplicate_ids)}**",
        f"- Turmas sem encontro: **{len(missing_meetings)}**",
        f"- Encontros sem turma: **{len(orphan_meetings)}**",
        f"- Horários inválidos: **{len(invalid_time)}**",
        f"- Encontros sem sala: **{len(no_room)}**",
        f"- Salas desconhecidas: **{len(unknown_rooms)}**",
        f"- Turmas sem professor: **{len(missing_teacher)}**",
        f"- Turmas sem setor: **{len(missing_sector)}**",
        "",
        "## Observação",
        "",
        "A capacidade das salas é estimada pelo maior `CAP` observado na sala; isso não substitui a capacidade física oficial.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT_MD)


if __name__ == "__main__":
    main()
