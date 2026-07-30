"""Gera uma instância JSON inicial para CC/SI a partir dos CSVs processados."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.eval.rooms import estimated_room_distance, room_metadata
from src.eval.resources import infer_lab_requirement, lab_evidence_by_code, resources_from_requirement


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dados" / "processados"
OUT = DATA / "instancia_2025_cc_si.json"


def main() -> None:
    turmas = pd.read_csv(DATA / "turmas_2025.csv", dtype=str).fillna("")
    horarios = pd.read_csv(DATA / "horarios_2025.csv", dtype=str).fillna("")
    keep = turmas["curso"].isin({"31", "83"}) | (
        turmas["curso"].eq("") & turmas["periodo"].str.startswith(("CC-", "SI-"))
    )
    turmas = turmas[keep].copy()
    horarios = horarios[horarios["turma_id"].isin(set(turmas["id"]))].copy()

    evidence = lab_evidence_by_code(horarios.to_dict("records"))
    encontros = {}
    for turma_id, group in horarios.groupby("turma_id"):
        code = str(group["codigo"].iloc[0])
        values = []
        for _, meeting in group.iterrows():
            required_lab, source = infer_lab_requirement(meeting["sala"], code, evidence)
            values.append({
                "dia": meeting["dia"],
                "inicio": meeting["inicio"],
                "fim": meeting["fim"],
                "sala": meeting["sala"],
                "requer_laboratorio": required_lab,
                "recursos_requeridos": resources_from_requirement(required_lab),
                "recurso_fonte": source,
            })
        encontros[turma_id] = values

    def class_resource_summary(meetings: list[dict]) -> tuple[bool | None, list[str], list[str]]:
        requirements = [meeting.get("requer_laboratorio") for meeting in meetings]
        sources = sorted({str(meeting.get("recurso_fonte", "")) for meeting in meetings if meeting.get("recurso_fonte")})
        if any(value is True for value in requirements):
            return True, ["laboratorio"], sources
        if requirements and all(value is False for value in requirements):
            return False, [], sources
        return None, [], sources

    classes = []
    for _, row in turmas.iterrows():
        class_meetings = encontros.get(row["id"], [])
        requires_lab, class_resources, resource_sources = class_resource_summary(class_meetings)
        classes.append({
            "id": row["id"],
            "semestre": row["semestre"],
            "curso": row["curso"] or ("SI" if row["periodo"].startswith("SI-") else "CC"),
            "periodo": row["periodo"],
            "codigo": row["codigo"],
            "disciplina": row["disciplina"],
            "turma": row["turma"],
            "origem": "IC" if row["codigo"].startswith("TCC") else "externa",
            "setor": row["setor"] or None,
            "professor": row["alocacao"] or None,
            "capacidade_turma": int(float(row["capacidade"])) if row["capacidade"] else None,
            "exige_laboratorio": requires_lab,
            "recursos_requeridos": class_resources,
            "recurso_fontes": resource_sources,
            "horario_fixo": True,
            "sala_fixa": False,
            "encontros": class_meetings,
        })

    rooms = sorted({e["sala"] for values in encontros.values() for e in values if e["sala"]})
    capacity_by_room = {}
    linked = horarios.merge(turmas[["id", "capacidade"]], left_on="turma_id", right_on="id", how="left")
    linked["capacidade_num"] = pd.to_numeric(linked["capacidade"], errors="coerce")
    for room, group in linked[linked["sala"].ne("")].groupby("sala"):
        values = group["capacidade_num"].dropna()
        if not values.empty:
            capacity_by_room[room] = int(values.max())
    teachers = sorted({c["professor"] for c in classes if c["professor"]})
    sectors = sorted({c["setor"] for c in classes if c["setor"]})
    groups: dict[str, dict] = {}
    for c in classes:
        if not c["periodo"]:
            continue
        key = f"{c['semestre']}|{c['curso']}|{c['periodo']}"
        groups.setdefault(key, {"semestre": c["semestre"], "curso": c["curso"], "periodo": c["periodo"], "disciplinas": []})
        if c["codigo"] not in groups[key]["disciplinas"]:
            groups[key]["disciplinas"].append(c["codigo"])

    instance = {
        "schema_version": "0.1",
        "source": "dados/brutos/QH-2025-1-2.xlsx",
        "profile": "cc_si",
        "notes": [
            "Instância inicial baseada na solução real da planilha.",
            "Horários são fixos nesta versão.",
            "O prefixo L identifica laboratório e também o prédio dos laboratórios.",
            "A exigência de laboratório é inferida por encontro a partir do histórico do código e da sala observada.",
            "Capacidade e distância ainda são estimadas; recursos de laboratório são uma inferência provisória.",
            "Professores são nomes abreviados conforme a coluna ALOCAÇÃO da planilha.",
        ],
        "rooms": [
            {
                **room_metadata(room),
                "capacity": None,
                "capacidade_estimada": capacity_by_room.get(room),
                "capacidade_fonte": "max(CAP) das turmas observadas na sala",
                "resources": ["laboratorio"] if room_metadata(room)["laboratorio"] else [],
                "position": None,
            }
            for room in rooms
        ],
        "distance_rule": {
            "same_room": 0,
            "same_building_different_floor": "absolute floor difference",
            "different_floor": "absolute floor difference",
            "same_floor_same_parity": 1,
            "same_floor_different_parity": 2,
            "different_building": "building change distance plus absolute floor difference",
            "building_change_distance": 3,
            "vertical_distance": "ignored",
            "horizontal_distance": "ignored",
        },
        "teachers": [{"name": teacher} for teacher in teachers],
        "sectors": sectors,
        "curriculum_groups": list(groups.values()),
        "classes": classes,
    }
    OUT.write_text(json.dumps(instance, ensure_ascii=False, indent=2), encoding="utf-8")
    resource_class_rows = []
    resource_meeting_rows = []
    for item in classes:
        resource_class_rows.append({
            "turma_id": item["id"],
            "semestre": item["semestre"],
            "codigo": item["codigo"],
            "disciplina": item["disciplina"],
            "periodo": item["periodo"],
            "exige_laboratorio": item["exige_laboratorio"],
            "recursos_requeridos": ",".join(item["recursos_requeridos"]),
            "fontes": ";".join(item["recurso_fontes"]),
        })
        for meeting in item["encontros"]:
            resource_meeting_rows.append({
                "turma_id": item["id"],
                "semestre": item["semestre"],
                "codigo": item["codigo"],
                "disciplina": item["disciplina"],
                "dia": meeting["dia"],
                "inicio": meeting["inicio"],
                "fim": meeting["fim"],
                "sala_observada": meeting["sala"],
                "requer_laboratorio": meeting["requer_laboratorio"],
                "recursos_requeridos": ",".join(meeting["recursos_requeridos"] or []),
                "fonte": meeting["recurso_fonte"],
            })
    pd.DataFrame(resource_class_rows).to_csv(DATA / "recursos_turmas_2025.csv", index=False)
    pd.DataFrame(resource_meeting_rows).to_csv(DATA / "recursos_encontros_2025.csv", index=False)
    room_table = pd.DataFrame([room_metadata(room) for room in rooms])
    room_table["capacidade_estimada"] = room_table["id"].map(capacity_by_room)
    room_table["capacidade_fonte"] = "max(CAP) das turmas observadas na sala"
    room_table["recursos"] = room_table["laboratorio"].map(lambda x: "laboratorio" if x else "")
    room_table.to_csv(DATA / "salas_2025.csv", index=False)
    distance_rows = []
    for room_a in rooms:
        for room_b in rooms:
            distance_rows.append({"sala_origem": room_a, "sala_destino": room_b, "distancia": estimated_room_distance(room_a, room_b)})
    pd.DataFrame(distance_rows).to_csv(DATA / "distancias_salas_2025.csv", index=False)
    print(f"{OUT}: {len(classes)} turmas, {len(rooms)} salas, {len(teachers)} professores")


if __name__ == "__main__":
    main()
