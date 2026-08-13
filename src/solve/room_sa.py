"""Simulated Annealing inicial para realocação de salas.

Professores e horários permanecem fixos. O objetivo desta primeira versão é
validar o ciclo solução -> movimento -> avaliação -> solução melhorada.
"""

from __future__ import annotations

import copy
import json
import math
import random
from pathlib import Path

import pandas as pd

from src.eval.evaluator import QHEvaluator
from src.eval.rooms import is_lab_room


def frames_from_payload(payload: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    class_rows = []
    meeting_rows = []
    priorities = payload.get("prioridades_professores", {})
    for item in payload.get("classes", []):
        professor = item.get("professor") or ""
        class_rows.append({
            "id": item.get("id", ""),
            "semestre": item.get("semestre", ""),
            "curso": item.get("curso", ""),
            "periodo": item.get("periodo", ""),
            "codigo": item.get("codigo", ""),
            "disciplina": item.get("disciplina", ""),
            "turma": item.get("turma", ""),
            "setor": item.get("setor") or "",
            "alocacao": professor,
            "origem": item.get("origem", ""),
            "capacidade": item.get("capacidade_turma") or "",
            "obrigatoria": item.get("obrigatoria", False),
            "preferencia": (item.get("preferencias_professores") or {}).get(professor),
            "prioridade": priorities.get(professor),
            "exige_laboratorio": item.get("exige_laboratorio"),
            "recursos_requeridos": item.get("recursos_requeridos") or [],
        })
        for meeting in item.get("encontros", []):
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
                "requer_laboratorio": meeting.get("requer_laboratorio"),
                "recursos_requeridos": meeting.get("recursos_requeridos"),
                "recurso_fonte": meeting.get("recurso_fonte", ""),
            })
    rooms = pd.DataFrame([
        {
            "id": room.get("id", ""),
            "capacidade_estimada": room.get("capacidade_estimada", ""),
            "laboratorio": room.get("laboratorio", is_lab_room(room.get("id", ""))),
            "predio": room.get("predio", ""),
        }
        for room in payload.get("rooms", [])
    ])
    classes = pd.DataFrame(class_rows).fillna("")
    classes.attrs["min_obrigatorias_ano"] = payload.get("min_obrigatorias_ano", 3)
    classes.attrs["professores_ic"] = sorted({
        str(teacher.get("name", ""))
        for teacher in payload.get("teachers", [])
        if str(teacher.get("name", ""))
    })
    return classes, pd.DataFrame(meeting_rows).fillna(""), rooms.fillna("")


def evaluate_payload(payload: dict):
    classes, meetings, rooms = frames_from_payload(payload)
    return QHEvaluator(classes, meetings, rooms).evaluate()


def mutable_classes(payload: dict) -> list[dict]:
    return [
        item for item in payload.get("classes", [])
        if item.get("origem") == "IC" and item.get("periodo") and item.get("encontros")
    ]


def candidate_rooms(item: dict, payload: dict, meeting_index: int | None = None) -> list[str]:
    capacity = item.get("capacidade_turma")
    try:
        capacity = float(capacity)
    except (TypeError, ValueError):
        capacity = None
    meetings = item.get("encontros", [])
    if meeting_index is None:
        target_meetings = meetings
    elif 0 <= meeting_index < len(meetings):
        target_meetings = [meetings[meeting_index]]
    else:
        return []
    required_values = []
    for meeting in target_meetings:
        value = meeting.get("requer_laboratorio")
        if value is None and "exige_laboratorio" in item:
            value = item.get("exige_laboratorio")
        required_values.append(value)
    requires_lab = required_values[0] if required_values and all(value == required_values[0] for value in required_values) else None
    rooms = []
    for room in payload.get("rooms", []):
        room_id = str(room.get("id", ""))
        room_capacity = room.get("capacidade_estimada")
        try:
            room_capacity = float(room_capacity)
        except (TypeError, ValueError):
            room_capacity = None
        is_lab = bool(room.get("laboratorio", is_lab_room(room_id)))
        if requires_lab is not None and is_lab != bool(requires_lab):
            continue
        if capacity is not None and room_capacity is not None and room_capacity < capacity:
            continue
        if room_id:
            rooms.append(room_id)
    return rooms


def assign_room(item: dict, room: str, meeting_index: int | None = None) -> None:
    if meeting_index is None:
        for meeting in item.get("encontros", []):
            meeting["sala"] = room
        return
    item["encontros"][meeting_index]["sala"] = room


class RoomObjective:
    """Objetivo incremental para movimentos que só alteram salas."""

    def __init__(self, payload: dict):
        initial = evaluate_payload(payload)
        self.static_hard = sum(value for key, value in initial.hard.items() if key not in {"conflitos_sala", "capacidade_insuficiente", "recursos_incompativeis"})
        self.static_soft = sum(value for key, value in initial.soft.items() if key != "desperdicio_capacidade" and value is not None)
        self.room_capacity = {
            str(room.get("id")): room.get("capacidade_estimada")
            for room in payload.get("rooms", [])
        }

    @staticmethod
    def _number(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def dynamic(self, payload: dict) -> dict:
        occupied = {}
        capacity_violations = 0
        resource_violations = 0
        capacity_waste = 0.0

        for item in payload.get("classes", []):
            class_capacity = self._number(item.get("capacidade_turma"))
            seen_class_rooms = set()
            for meeting in item.get("encontros", []):
                room = str(meeting.get("sala", ""))
                if room:
                    key = (
                        item.get("semestre", ""), meeting.get("dia", ""),
                        meeting.get("inicio", ""), meeting.get("fim", ""), room,
                    )
                    occupied[key] = occupied.get(key, 0) + 1
                    required_lab = meeting.get("requer_laboratorio")
                    if required_lab is None and "exige_laboratorio" in item:
                        required_lab = item.get("exige_laboratorio")
                    if required_lab is not None and is_lab_room(room) != bool(required_lab):
                        resource_violations += 1
                    room_capacity = self._number(self.room_capacity.get(room))
                    if class_capacity is not None and room_capacity is not None:
                        if class_capacity > room_capacity:
                            capacity_violations += 1
                        room_key = (item.get("id", ""), room)
                        if room_key not in seen_class_rooms:
                            capacity_waste += max(0.0, room_capacity - class_capacity)
                            seen_class_rooms.add(room_key)
        room_conflicts = sum(max(0, count - 1) for count in occupied.values())
        return {
            "room_conflicts": room_conflicts,
            "capacity_violations": capacity_violations,
            "resource_violations": resource_violations,
            "capacity_waste": capacity_waste,
        }

    def score(self, payload: dict) -> float:
        dynamic = self.dynamic(payload)
        hard = (
            self.static_hard
            + dynamic["room_conflicts"]
            + dynamic["capacity_violations"]
            + dynamic["resource_violations"]
        )
        soft = self.static_soft + dynamic["capacity_waste"]
        return hard * 1_000_000 + soft


def solve(payload: dict, iterations: int = 3000, seed: int = 2025, initial_temperature: float = 100_000.0) -> tuple[dict, dict]:
    rng = random.Random(seed)
    current = copy.deepcopy(payload)
    initial = evaluate_payload(current)
    objective = RoomObjective(current)
    current_score = objective.score(current)
    best = copy.deepcopy(current)
    best_eval = initial
    classes = mutable_classes(current)
    accepted = 0
    attempted = 0

    for iteration in range(iterations):
        if not classes:
            break
        item = rng.choice(classes)
        meeting_index = rng.randrange(len(item.get("encontros", [])))
        current_room = str(item["encontros"][meeting_index].get("sala", ""))
        options = [room for room in candidate_rooms(item, current, meeting_index) if room != current_room]
        if not options:
            continue
        attempted += 1
        old_room = item["encontros"][meeting_index].get("sala", "")
        new_room = rng.choice(options)
        assign_room(item, new_room, meeting_index)
        new_score = objective.score(current)
        delta = new_score - current_score
        temperature = max(1.0, initial_temperature * (1.0 - iteration / max(1, iterations)))
        accept = delta <= 0 or rng.random() < math.exp(-delta / temperature)
        if accept:
            accepted += 1
            current_score = new_score
            if new_score < objective.score(best):
                best = copy.deepcopy(current)
                # A conferência completa ocorre ao final; esta avaliação evita
                # chamar pandas em cada movimento.
        else:
            item["encontros"][meeting_index]["sala"] = old_room

    best_eval = evaluate_payload(best)
    metadata = {
        "algorithm": "Simulated Annealing — salas",
        "seed": seed,
        "iterations": iterations,
        "attempted_moves": attempted,
        "accepted_moves": accepted,
        "mutable_classes": len(classes),
        "initial": initial.as_dict(),
        "best": best_eval.as_dict(),
    }
    return best, metadata


def solve_file(input_path: str | Path, output_path: str | Path, iterations: int = 3000, seed: int = 2025) -> dict:
    input_path = Path(input_path)
    output_path = Path(output_path)
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    best, metadata = solve(payload, iterations=iterations, seed=seed)
    best["solution"] = metadata
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(best, ensure_ascii=False, indent=2), encoding="utf-8")
    return metadata
