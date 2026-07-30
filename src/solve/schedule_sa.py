"""Simulated Annealing para salas e horários flexíveis."""

from __future__ import annotations

import copy
import json
import math
import random
from pathlib import Path

from src.eval.evaluator import QHEvaluator
from src.solve.direct_objective import evaluate as fast_evaluate
from src.solve.room_sa import candidate_rooms, frames_from_payload


def flexible_classes(payload: dict) -> list[dict]:
    return [
        item for item in payload.get("classes", [])
        if not item.get("horario_fixo", True) and item.get("dominio_horarios")
    ]


def assign_pattern(item: dict, pattern: list[dict]) -> None:
    old_meetings = item.get("encontros", [])
    item["encontros"] = []
    for index, meeting in enumerate(pattern):
        updated = copy.deepcopy(meeting)
        if index < len(old_meetings):
            previous = old_meetings[index]
            updated["sala"] = previous.get("sala", "")
            for key in ("requer_laboratorio", "recursos_requeridos", "recurso_fonte"):
                if key in previous:
                    updated[key] = copy.deepcopy(previous[key])
        else:
            updated["sala"] = ""
        item["encontros"].append(updated)


def assign_room(item: dict, room: str, meeting_index: int) -> None:
    item["encontros"][meeting_index]["sala"] = room


def solve(payload: dict, iterations: int = 1000, seed: int = 2025, initial_temperature: float = 100_000.0):
    rng = random.Random(seed)
    current = copy.deepcopy(payload)
    initial_fast = fast_evaluate(current)
    current_score = initial_fast["score"]
    best = copy.deepcopy(current)
    best_score = current_score
    classes = flexible_classes(current)
    attempted = 0
    accepted = 0

    for iteration in range(iterations):
        if not classes:
            break
        item = rng.choice(classes)
        move_type = "schedule" if rng.random() < 0.6 else "room"
        old_state = copy.deepcopy(item.get("encontros", []))
        if move_type == "schedule":
            current_pattern = tuple((m.get("dia"), m.get("inicio"), m.get("fim")) for m in item.get("encontros", []))
            options = [
                pattern for pattern in item.get("dominio_horarios", [])
                if tuple((m.get("dia"), m.get("inicio"), m.get("fim")) for m in pattern) != current_pattern
            ]
            if not options:
                continue
            assign_pattern(item, rng.choice(options))
        else:
            meeting_index = rng.randrange(len(item.get("encontros", [])))
            current_room = str(item["encontros"][meeting_index].get("sala", ""))
            options = [
                room for room in candidate_rooms(item, current, meeting_index)
                if room != current_room
            ]
            if not options:
                continue
            assign_room(item, rng.choice(options), meeting_index)

        attempted += 1
        new_fast = fast_evaluate(current)
        delta = new_fast["score"] - current_score
        temperature = max(1.0, initial_temperature * (1.0 - iteration / max(1, iterations)))
        accept = delta <= 0 or rng.random() < math.exp(-delta / temperature)
        if accept:
            accepted += 1
            current_score = new_fast["score"]
            if current_score < best_score:
                best = copy.deepcopy(current)
                best_score = current_score
        else:
            item["encontros"] = old_state

    classes_df, meetings_df, rooms_df = frames_from_payload(best)
    exact = QHEvaluator(classes_df, meetings_df, rooms_df).evaluate().as_dict()
    metadata = {
        "algorithm": "Simulated Annealing — salas e horários",
        "seed": seed,
        "iterations": iterations,
        "attempted_moves": attempted,
        "accepted_moves": accepted,
        "flexible_classes": len(classes),
        "initial": initial_fast,
        "best": exact,
    }
    return best, metadata


def solve_file(input_path: str | Path, output_path: str | Path, iterations: int = 1000, seed: int = 2025):
    input_path = Path(input_path)
    output_path = Path(output_path)
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    best, metadata = solve(payload, iterations=iterations, seed=seed)
    best["solution"] = metadata
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(best, ensure_ascii=False, indent=2), encoding="utf-8")
    return metadata
