"""Leitura da instância JSON para o avaliador."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def load_instance_json(path: str | Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    path = Path(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    classes = payload.get("classes", [])
    rooms = payload.get("rooms", [])
    priorities = payload.get("prioridades_professores", {})

    class_rows = []
    meeting_rows = []
    for item in classes:
        class_rows.append({
            "id": item.get("id", ""),
            "semestre": item.get("semestre", ""),
            "curso": item.get("curso", ""),
            "periodo": item.get("periodo", ""),
            "codigo": item.get("codigo", ""),
            "disciplina": item.get("disciplina", ""),
            "turma": item.get("turma", ""),
            "setor": item.get("setor") or "",
            "alocacao": item.get("professor") or "",
            "origem": item.get("origem", ""),
            "capacidade": item.get("capacidade_turma") or "",
            "exige_laboratorio": item.get("exige_laboratorio"),
            "recursos_requeridos": item.get("recursos_requeridos") or [],
            "obrigatoria": item.get("obrigatoria", False),
            "preferencia": (item.get("preferencias_professores") or {}).get(
                item.get("professor", "")
            ),
            "prioridade": priorities.get(item.get("professor", "")),
        })
        for meeting in item.get("encontros", []):
            required_lab = meeting.get("requer_laboratorio")
            if required_lab is None and "exige_laboratorio" in item:
                required_lab = item.get("exige_laboratorio")
            meeting_rows.append({
                "turma_id": item.get("id", ""),
                "semestre": item.get("semestre", ""),
                "codigo": item.get("codigo", ""),
                "turma": item.get("turma", ""),
                "dia": meeting.get("dia", ""),
                "inicio": meeting.get("inicio", ""),
                "fim": meeting.get("fim", ""),
                "sala": meeting.get("sala", "") or "",
                "valor_original": meeting.get("valor_original", ""),
                "requer_laboratorio": required_lab,
                "recursos_requeridos": meeting.get("recursos_requeridos"),
                "recurso_fonte": meeting.get("recurso_fonte", ""),
            })

    room_rows = []
    for room in rooms:
        room_rows.append({
            "id": room.get("id", ""),
            "capacidade_estimada": room.get("capacidade_estimada", ""),
            "laboratorio": room.get("laboratorio", False),
            "predio": room.get("predio", ""),
        })
    classes_frame = pd.DataFrame(class_rows).fillna("")
    classes_frame.attrs["min_obrigatorias_ano"] = payload.get("min_obrigatorias_ano", 3)
    classes_frame.attrs["professores_ic"] = sorted({
        str(teacher.get("name", ""))
        for teacher in payload.get("teachers", [])
        if str(teacher.get("name", ""))
    })
    return (
        classes_frame,
        pd.DataFrame(meeting_rows).fillna(""),
        pd.DataFrame(room_rows).fillna(""),
    )
