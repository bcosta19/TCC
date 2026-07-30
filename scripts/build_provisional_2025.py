"""Constrói uma variante de teste com salas ausentes reparadas heurísticamente."""

from __future__ import annotations

import shutil
from pathlib import Path
import json

import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.eval.rooms import is_lab_room


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dados" / "processados"
OUT = DATA / "provisoria_2025"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    turmas = pd.read_csv(DATA / "turmas_2025.csv", dtype=str).fillna("")
    horarios = pd.read_csv(DATA / "horarios_2025.csv", dtype=str).fillna("")
    salas = pd.read_csv(DATA / "salas_2025.csv", dtype=str).fillna("")

    keep = turmas["curso"].isin({"31", "83"}) | (
        turmas["curso"].eq("") & turmas["periodo"].str.startswith(("CC-", "SI-"))
    )
    turmas = turmas[keep].copy()
    horarios = horarios[horarios["turma_id"].isin(set(turmas["id"]))].copy()
    horarios["sala_fonte"] = horarios["sala"].map(lambda x: "original" if x else "nao_informada")
    base_instance = json.loads((DATA / "instancia_2025_cc_si.json").read_text(encoding="utf-8"))
    base_meetings = {item["id"]: item.get("encontros", []) for item in base_instance["classes"]}

    capacity = dict(zip(salas["id"], pd.to_numeric(salas["capacidade_estimada"], errors="coerce")))
    room_assignments = {}
    repair_rows = []

    for turma_id, group in horarios.groupby("turma_id"):
        missing = group["sala"].eq("").any()
        if not missing:
            continue
        turma = turmas[turmas["id"].eq(turma_id)].iloc[0]
        code = turma["codigo"]
        if not code.startswith("TCC"):
            repair_rows.append({"turma_id": turma_id, "codigo": code, "status": "externa_sem_sala", "sala": "", "fonte": "mantida_nula"})
            continue
        if code == "TCC00311" or not turma["periodo"]:
            repair_rows.append({"turma_id": turma_id, "codigo": code, "status": "projeto_ou_sem_periodo", "sala": "", "fonte": "mantida_nula"})
            continue

        historical = sorted(set(horarios[(horarios["codigo"].eq(code)) & horarios["sala"].ne("")]["sala"]))
        class_capacity = pd.to_numeric(pd.Series([turma["capacidade"]]), errors="coerce").iloc[0]
        candidates = [room for room in historical if pd.isna(class_capacity) or capacity.get(room, 0) >= class_capacity]
        candidates += [room for room in salas["id"] if room not in candidates and (pd.isna(class_capacity) or capacity.get(room, 0) >= class_capacity)]

        missing_positions = [position for position, (_, meeting) in enumerate(group.iterrows()) if not meeting["sala"]]
        required_values = [
            base_meetings.get(turma_id, [])[position].get("requer_laboratorio")
            for position in missing_positions
            if position < len(base_meetings.get(turma_id, []))
        ]
        if required_values and all(value is not None for value in required_values) and len(set(required_values)) == 1:
            required_lab = bool(required_values[0])
            candidates = [room for room in candidates if is_lab_room(room) == required_lab]

        chosen = ""
        for room in candidates:
            conflict = False
            for position, (_, meeting) in enumerate(group.iterrows()):
                if not meeting["sala"]:
                    requirement = None
                    if position < len(base_meetings.get(turma_id, [])):
                        requirement = base_meetings[turma_id][position].get("requer_laboratorio")
                    if requirement is not None and is_lab_room(room) != bool(requirement):
                        conflict = True
                        break
                    same_time = horarios[
                        (horarios["semestre"].eq(meeting["semestre"]))
                        & (horarios["dia"].eq(meeting["dia"]))
                        & (horarios["inicio"].eq(meeting["inicio"]))
                        & (horarios["fim"].eq(meeting["fim"]))
                        & (horarios["sala"].eq(room))
                    ]
                    if not same_time.empty:
                        conflict = True
                        break
            if not conflict:
                chosen = room
                break

        if chosen:
            room_assignments[turma_id] = chosen
            repair_rows.append({"turma_id": turma_id, "codigo": code, "status": "sala_atribuida_provisoriamente", "sala": chosen, "fonte": "historico_ou_compatibilidade"})
            mask = (horarios["turma_id"].eq(turma_id)) & horarios["sala"].eq("")
            horarios.loc[mask, "sala"] = chosen
            horarios.loc[mask, "sala_fonte"] = "provisoria"
        else:
            repair_rows.append({"turma_id": turma_id, "codigo": code, "status": "sem_candidato", "sala": "", "fonte": "mantida_nula"})

    turmas.to_csv(OUT / "turmas_2025.csv", index=False)
    horarios.to_csv(OUT / "horarios_2025.csv", index=False)
    salas.to_csv(OUT / "salas_2025.csv", index=False)
    pd.DataFrame(repair_rows).to_csv(OUT / "reparos_salas.csv", index=False)
    shutil.copyfile(DATA / "carga_docente_2025.csv", OUT / "carga_docente_2025.csv")
    meeting_map = {
        turma_id: [
            {
                "dia": row["dia"],
                "inicio": row["inicio"],
                "fim": row["fim"],
                "sala": row["sala"],
                **{
                    key: base_meetings.get(turma_id, [])[position].get(key)
                    for key in ("requer_laboratorio", "recursos_requeridos", "recurso_fonte")
                    if position < len(base_meetings.get(turma_id, []))
                },
            }
            for position, (_, row) in enumerate(group.iterrows())
        ]
        for turma_id, group in horarios.groupby("turma_id")
    }
    for item in base_instance["classes"]:
        item["encontros"] = meeting_map.get(item["id"], [])
    (OUT / "instancia_2025_cc_si.json").write_text(
        json.dumps(base_instance, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"{OUT}: {len(room_assignments)} turmas receberam sala provisória")


if __name__ == "__main__":
    main()
