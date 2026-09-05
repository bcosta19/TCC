"""Busca integrada e reprodutivel sobre o payload JSON do TCC.

Os algoritmos deste modulo sao implementacoes de referencia em Python. Todos
usam o mesmo avaliador e as mesmas vizinhancas; um adaptador OptFrame pode
reutilizar essas funcoes sem alterar a representacao da solucao.
"""

from __future__ import annotations

import copy
import math
import random
from dataclasses import dataclass
from typing import Iterable

from src.eval.rooms import is_lab_room
from src.solve.direct_objective import evaluate


MOVE_KINDS = ("teacher", "schedule", "room")


def annual_deficit(result: dict) -> float:
    value = (result.get("guidance") or {}).get("deficit_carga_anual")
    return float(value) if value is not None else math.inf


def objective_key(result: dict) -> tuple[float, float, float]:
    """Compara hard, déficit H12 e, por fim, os demais critérios soft."""
    return (
        float(result["hard_violations"]),
        annual_deficit(result),
        float(sum(result["soft"].values())),
    )


def search_energy(result: dict) -> float:
    """Escalar lexicográfico usado somente na aceitação probabilística do SA."""
    deficit = annual_deficit(result)
    if not math.isfinite(deficit):
        raise ValueError("H12 indisponivel; defina universo docente e politica de cotutoria antes da busca")
    return (
        float(result["hard_violations"]) * 1_000_000_000
        + deficit * 1_000_000
        + float(sum(result["soft"].values()))
    )


def is_better(candidate: dict, reference: dict) -> bool:
    return objective_key(candidate) < objective_key(reference)


def assigned_teachers(item: dict) -> list[str]:
    values = item.get("professores_alocados")
    if isinstance(values, list) and values:
        return [str(value) for value in values if str(value)]
    teacher = str(item.get("professor", "") or "")
    return [teacher] if teacher else []


def _number(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def candidate_rooms(item: dict, payload: dict, meeting_index: int) -> list[str]:
    meeting = item["encontros"][meeting_index]
    required_lab = meeting.get("requer_laboratorio")
    capacity = _number(item.get("capacidade_turma"))
    candidates = []
    for room in payload.get("rooms", []):
        room_id = str(room.get("id", ""))
        room_capacity = _number(room.get("capacidade_estimada", room.get("capacity")))
        room_is_lab = bool(room.get("laboratorio", is_lab_room(room_id)))
        if required_lab is not None and room_is_lab != bool(required_lab):
            continue
        if capacity is not None and room_capacity is not None and capacity > room_capacity:
            continue
        if room_id:
            waste = room_capacity - capacity if room_capacity is not None and capacity is not None else 0
            candidates.append((waste, room_id))
    return [room_id for _waste, room_id in sorted(candidates)]


def _pattern_signature(pattern: Iterable[dict]) -> tuple:
    return tuple((str(m.get("dia", "")), str(m.get("inicio", "")), str(m.get("fim", ""))) for m in pattern)


def available_move_kinds(payload: dict) -> list[str]:
    kinds = []
    if any(
        item.get("origem") == "IC"
        and not item.get("professor_fixo", False)
        and len(assigned_teachers(item)) == 1
        and len(item.get("professores_habilitados") or []) > 1
        for item in payload.get("classes", [])
    ):
        kinds.append("teacher")
    if any(
        not item.get("horario_fixo", True) and len(item.get("dominio_horarios") or []) > 1
        for item in payload.get("classes", [])
    ):
        kinds.append("schedule")
    if any(
        item.get("origem") == "IC" and not item.get("sala_fixa", False) and item.get("encontros")
        for item in payload.get("classes", [])
    ):
        kinds.append("room")
    return kinds


def propose_move(payload: dict, rng: random.Random, kinds: Iterable[str] = MOVE_KINDS) -> dict | None:
    allowed = [kind for kind in kinds if kind in available_move_kinds(payload)]
    if not allowed:
        return None
    classes = payload.get("classes", [])
    for _ in range(50):
        kind = rng.choice(allowed)
        if kind == "teacher":
            indices = [
                index for index, item in enumerate(classes)
                if item.get("origem") == "IC"
                and not item.get("professor_fixo", False)
                and len(assigned_teachers(item)) == 1
                and len(item.get("professores_habilitados") or []) > 1
            ]
            if not indices:
                continue
            class_index = rng.choice(indices)
            item = classes[class_index]
            current = assigned_teachers(item)[0]
            options = [str(value) for value in item["professores_habilitados"] if str(value) != current]
            if options:
                return {"kind": kind, "class_index": class_index, "new_teacher": rng.choice(options)}
        elif kind == "schedule":
            indices = [
                index for index, item in enumerate(classes)
                if not item.get("horario_fixo", True)
                and len(item.get("dominio_horarios") or []) > 1
            ]
            if not indices:
                continue
            class_index = rng.choice(indices)
            item = classes[class_index]
            current = _pattern_signature(item.get("encontros", []))
            options = [
                index for index, pattern in enumerate(item["dominio_horarios"])
                if _pattern_signature(pattern) != current and len(pattern) == len(item.get("encontros", []))
            ]
            if options:
                return {"kind": kind, "class_index": class_index, "pattern_index": rng.choice(options)}
        else:
            indices = [
                index for index, item in enumerate(classes)
                if item.get("origem") == "IC" and not item.get("sala_fixa", False) and item.get("encontros")
            ]
            if not indices:
                continue
            class_index = rng.choice(indices)
            item = classes[class_index]
            meeting_index = rng.randrange(len(item["encontros"]))
            current = str(item["encontros"][meeting_index].get("sala", "") or "")
            options = [room for room in candidate_rooms(item, payload, meeting_index) if room != current]
            if options:
                return {
                    "kind": kind,
                    "class_index": class_index,
                    "meeting_index": meeting_index,
                    "new_room": rng.choice(options),
                }
    return None


def apply_move(payload: dict, move: dict) -> dict:
    item = payload["classes"][move["class_index"]]
    kind = move["kind"]
    if kind == "teacher":
        undo = {
            "kind": "teacher_restore",
            "class_index": move["class_index"],
            "had_professor": "professor" in item,
            "professor": item.get("professor"),
            "had_allocated": "professores_alocados" in item,
            "allocated": copy.deepcopy(item.get("professores_alocados")),
        }
        item["professor"] = move["new_teacher"]
        item["professores_alocados"] = [move["new_teacher"]]
        return undo
    if kind == "teacher_restore":
        reverse = {
            "kind": "teacher_restore",
            "class_index": move["class_index"],
            "had_professor": "professor" in item,
            "professor": item.get("professor"),
            "had_allocated": "professores_alocados" in item,
            "allocated": copy.deepcopy(item.get("professores_alocados")),
        }
        if move["had_professor"]:
            item["professor"] = move["professor"]
        else:
            item.pop("professor", None)
        if move["had_allocated"]:
            item["professores_alocados"] = copy.deepcopy(move["allocated"])
        else:
            item.pop("professores_alocados", None)
        return reverse
    if kind == "schedule":
        previous = [
            {key: meeting[key] for key in ("dia", "inicio", "fim") if key in meeting}
            for meeting in item["encontros"]
        ]
        pattern = item["dominio_horarios"][move["pattern_index"]]
        for meeting, slot in zip(item["encontros"], pattern):
            meeting.update({"dia": slot["dia"], "inicio": slot["inicio"], "fim": slot["fim"]})
        return {"kind": "schedule_restore", "class_index": move["class_index"], "pattern": previous}
    if kind == "schedule_restore":
        previous = [
            {key: meeting[key] for key in ("dia", "inicio", "fim") if key in meeting}
            for meeting in item["encontros"]
        ]
        for meeting, slot in zip(item["encontros"], move["pattern"]):
            for key in ("dia", "inicio", "fim"):
                meeting.pop(key, None)
            meeting.update(slot)
        return {"kind": "schedule_restore", "class_index": move["class_index"], "pattern": previous}
    meeting = item["encontros"][move["meeting_index"]]
    undo = {
        "kind": "room",
        "class_index": move["class_index"],
        "meeting_index": move["meeting_index"],
        "new_room": meeting.get("sala", ""),
    }
    meeting["sala"] = move["new_room"]
    return undo


def greedy_improve(payload: dict, max_candidates: int = 6) -> tuple[dict, dict]:
    """Executa uma passagem gulosa sobre professor, horario e sala."""
    solution = copy.deepcopy(payload)
    current_result = evaluate(solution)
    evaluations = 1
    improvements = {kind: 0 for kind in MOVE_KINDS}

    for class_index, item in enumerate(solution.get("classes", [])):
        if (
            item.get("origem") == "IC"
            and not item.get("professor_fixo", False)
            and len(assigned_teachers(item)) == 1
        ):
            current = assigned_teachers(item)[0]
            preferences = item.get("preferencias_professores") or {}
            options = sorted(
                {str(value) for value in item.get("professores_habilitados") or [] if str(value)},
                key=lambda teacher: (-float(preferences.get(teacher, 0.0)), teacher),
            )[:max_candidates]
            best_teacher = current
            best_result = current_result
            for teacher in options:
                if teacher == current:
                    continue
                undo = apply_move(solution, {"kind": "teacher", "class_index": class_index, "new_teacher": teacher})
                candidate = evaluate(solution)
                evaluations += 1
                if is_better(candidate, best_result):
                    best_teacher, best_result = teacher, candidate
                apply_move(solution, undo)
            if best_teacher != current:
                apply_move(solution, {"kind": "teacher", "class_index": class_index, "new_teacher": best_teacher})
                current_result = best_result
                improvements["teacher"] += 1

        if not item.get("horario_fixo", True):
            current_signature = _pattern_signature(item.get("encontros", []))
            best_index = None
            best_result = current_result
            for pattern_index, pattern in enumerate((item.get("dominio_horarios") or [])[:max_candidates]):
                if len(pattern) != len(item.get("encontros", [])) or _pattern_signature(pattern) == current_signature:
                    continue
                undo = apply_move(solution, {"kind": "schedule", "class_index": class_index, "pattern_index": pattern_index})
                candidate = evaluate(solution)
                evaluations += 1
                if is_better(candidate, best_result):
                    best_index, best_result = pattern_index, candidate
                apply_move(solution, undo)
            if best_index is not None:
                apply_move(solution, {"kind": "schedule", "class_index": class_index, "pattern_index": best_index})
                current_result = best_result
                improvements["schedule"] += 1

        if item.get("origem") == "IC" and not item.get("sala_fixa", False):
            for meeting_index, meeting in enumerate(item.get("encontros", [])):
                current_room = str(meeting.get("sala", "") or "")
                best_room = current_room
                best_result = current_result
                for room in candidate_rooms(item, solution, meeting_index)[:max_candidates]:
                    if room == current_room:
                        continue
                    undo = apply_move(solution, {
                        "kind": "room",
                        "class_index": class_index,
                        "meeting_index": meeting_index,
                        "new_room": room,
                    })
                    candidate = evaluate(solution)
                    evaluations += 1
                    if is_better(candidate, best_result):
                        best_room, best_result = room, candidate
                    apply_move(solution, undo)
                if best_room != current_room:
                    apply_move(solution, {
                        "kind": "room",
                        "class_index": class_index,
                        "meeting_index": meeting_index,
                        "new_room": best_room,
                    })
                    current_result = best_result
                    improvements["room"] += 1

    return solution, {
        "algorithm": "guloso_integrado",
        "evaluations": evaluations,
        "improvements": improvements,
        "best": current_result,
    }


@dataclass
class SearchResult:
    solution: dict
    evaluation: dict
    metadata: dict


def _progress_entry(evaluations: int, result: dict) -> dict:
    return {
        "evaluations": evaluations,
        "score": result["score"],
        "hard_violations": result["hard_violations"],
        "deficit_carga_anual": annual_deficit(result),
    }


def solve_sa(payload: dict, seed: int, config: dict) -> SearchResult:
    rng = random.Random(seed)
    current = copy.deepcopy(payload)
    current_result = evaluate(current)
    best = copy.deepcopy(current)
    best_result = current_result
    budget = int(config["avaliacoes"])
    temperature = float(config["temperatura_inicial"])
    cooling = float(config["resfriamento"])
    evaluations = 1
    attempted = accepted = 0
    progress = [_progress_entry(evaluations, best_result)]
    checkpoint = max(1, budget // 20)

    while evaluations < budget:
        move = propose_move(current, rng)
        if move is None:
            break
        attempted += 1
        undo = apply_move(current, move)
        candidate = evaluate(current)
        evaluations += 1
        delta = search_energy(candidate) - search_energy(current_result)
        accept = delta <= 0 or rng.random() < math.exp(-delta / max(temperature, 1e-9))
        if accept:
            accepted += 1
            current_result = candidate
            if is_better(candidate, best_result):
                best, best_result = copy.deepcopy(current), candidate
        else:
            apply_move(current, undo)
        temperature *= cooling
        if evaluations % checkpoint == 0:
            progress.append(_progress_entry(evaluations, best_result))

    return SearchResult(best, best_result, {
        "algorithm": "sa",
        "seed": seed,
        "evaluations": evaluations,
        "attempted_moves": attempted,
        "accepted_moves": accepted,
        "progress": progress,
    })


def _random_local_search(solution: dict, result: dict, rng: random.Random, attempts: int, budget_left: int) -> tuple[dict, dict, int]:
    evaluations = 0
    for _ in range(min(attempts, budget_left)):
        move = propose_move(solution, rng)
        if move is None:
            break
        undo = apply_move(solution, move)
        candidate = evaluate(solution)
        evaluations += 1
        if is_better(candidate, result):
            result = candidate
        else:
            apply_move(solution, undo)
    return solution, result, evaluations


def solve_ils(payload: dict, seed: int, config: dict) -> SearchResult:
    rng = random.Random(seed)
    best = copy.deepcopy(payload)
    best_result = evaluate(best)
    budget = int(config["avaliacoes"])
    strength = int(config["forca_perturbacao"])
    local_attempts = int(config["tentativas_busca_local"])
    evaluations = 1
    perturbations = 0
    progress = [_progress_entry(evaluations, best_result)]
    checkpoint = max(1, budget // 20)

    while evaluations < budget:
        candidate_solution = copy.deepcopy(best)
        applied = 0
        for _ in range(strength):
            move = propose_move(candidate_solution, rng)
            if move is not None:
                apply_move(candidate_solution, move)
                applied += 1
        if not applied:
            break
        candidate_result = evaluate(candidate_solution)
        evaluations += 1
        perturbations += 1
        candidate_solution, candidate_result, used = _random_local_search(
            candidate_solution,
            candidate_result,
            rng,
            local_attempts,
            budget - evaluations,
        )
        evaluations += used
        if is_better(candidate_result, best_result):
            best, best_result = candidate_solution, candidate_result
        if evaluations // checkpoint > len(progress) - 1:
            progress.append(_progress_entry(evaluations, best_result))

    return SearchResult(best, best_result, {
        "algorithm": "ils",
        "seed": seed,
        "evaluations": evaluations,
        "perturbations": perturbations,
        "progress": progress,
    })


def solve_vns(payload: dict, seed: int, config: dict) -> SearchResult:
    rng = random.Random(seed)
    best = copy.deepcopy(payload)
    best_result = evaluate(best)
    neighborhoods = [kind for kind in MOVE_KINDS if kind in available_move_kinds(best)]
    budget = int(config["avaliacoes"])
    local_attempts = int(config["tentativas_busca_local"])
    evaluations = 1
    k = 0
    failed_shakes = 0
    progress = [_progress_entry(evaluations, best_result)]
    checkpoint = max(1, budget // 20)

    while neighborhoods and evaluations < budget:
        kind = neighborhoods[k]
        candidate_solution = copy.deepcopy(best)
        applied = 0
        for _ in range(k + 1):
            move = propose_move(candidate_solution, rng, [kind])
            if move is not None:
                apply_move(candidate_solution, move)
                applied += 1
        if not applied:
            failed_shakes += 1
            if failed_shakes >= len(neighborhoods):
                break
            k = (k + 1) % len(neighborhoods)
            continue
        failed_shakes = 0
        candidate_result = evaluate(candidate_solution)
        evaluations += 1
        candidate_solution, candidate_result, used = _random_local_search(
            candidate_solution,
            candidate_result,
            rng,
            local_attempts,
            budget - evaluations,
        )
        evaluations += used
        if is_better(candidate_result, best_result):
            best, best_result, k = candidate_solution, candidate_result, 0
        else:
            k = (k + 1) % len(neighborhoods)
        if evaluations // checkpoint > len(progress) - 1:
            progress.append(_progress_entry(evaluations, best_result))

    return SearchResult(best, best_result, {
        "algorithm": "vns",
        "seed": seed,
        "evaluations": evaluations,
        "neighborhoods": neighborhoods,
        "progress": progress,
    })


ALGORITHMS = {
    "sa": solve_sa,
    "ils": solve_ils,
    "vns": solve_vns,
}
