"""Simulated Annealing experimental para atribuição de professores.

O movimento usa ``professores_habilitados`` da turma quando esse domínio foi
fornecido. ``allow_unrestricted=True`` fica restrito a testes de estresse,
pois ignora o domínio histórico por setor.
"""

from __future__ import annotations

import copy
import json
import math
import random
from pathlib import Path

from src.eval.evaluator import QHEvaluator
from src.solve.direct_objective import evaluate as fast_evaluate
from src.solve.room_sa import frames_from_payload


def teacher_candidates(item: dict, payload: dict, allow_unrestricted: bool = False) -> list[str]:
    explicit = item.get("professores_habilitados")
    if explicit:
        return sorted({str(value) for value in explicit if str(value)})
    if allow_unrestricted:
        return sorted({
            str(value.get("name", ""))
            for value in payload.get("teachers", [])
            if str(value.get("name", ""))
        })
    current = str(item.get("professor", "") or "")
    return [current] if current else []


def solve(
    payload: dict,
    iterations: int = 5000,
    seed: int = 2025,
    initial_temperature: float = 1_000_000.0,
    allow_unrestricted: bool = False,
) -> tuple[dict, dict]:
    rng = random.Random(seed)
    current = copy.deepcopy(payload)
    initial = fast_evaluate(current)
    current_score = float(initial["score"])
    best = copy.deepcopy(current)
    best_score = current_score
    movable = [
        item for item in current.get("classes", [])
        if len(teacher_candidates(item, current, allow_unrestricted)) > 1
    ]
    attempted = 0
    accepted = 0

    for iteration in range(iterations):
        if not movable:
            break
        item = rng.choice(movable)
        current_teacher = str(item.get("professor", "") or "")
        options = [
            teacher for teacher in teacher_candidates(item, current, allow_unrestricted)
            if teacher != current_teacher
        ]
        if not options:
            continue
        old_teacher = item.get("professor")
        item["professor"] = rng.choice(options)
        attempted += 1
        new_score = float(fast_evaluate(current)["score"])
        delta = new_score - current_score
        temperature = max(
            1.0, initial_temperature * (1.0 - iteration / max(1, iterations))
        )
        accept = delta <= 0 or rng.random() < math.exp(-delta / temperature)
        if accept:
            accepted += 1
            current_score = new_score
            if new_score < best_score:
                best = copy.deepcopy(current)
                best_score = new_score
        else:
            item["professor"] = old_teacher

    classes, meetings, rooms = frames_from_payload(best)
    exact = QHEvaluator(classes, meetings, rooms).evaluate().as_dict()
    metadata = {
        "algorithm": "Simulated Annealing — professores",
        "seed": seed,
        "iterations": iterations,
        "attempted_moves": attempted,
        "accepted_moves": accepted,
        "movable_classes": len(movable),
        "allow_unrestricted": allow_unrestricted,
        "initial": initial,
        "best": exact,
    }
    return best, metadata


def solve_file(
    input_path: str | Path,
    output_path: str | Path,
    iterations: int = 5000,
    seed: int = 2025,
    allow_unrestricted: bool = False,
) -> dict:
    input_path = Path(input_path)
    output_path = Path(output_path)
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    best, metadata = solve(
        payload,
        iterations=iterations,
        seed=seed,
        allow_unrestricted=allow_unrestricted,
    )
    best["solution"] = metadata
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(best, ensure_ascii=False, indent=2), encoding="utf-8")
    return metadata
