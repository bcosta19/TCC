"""Avaliação leve, sem pandas, para a busca de salas e horários."""

from __future__ import annotations

from collections import defaultdict

from src.eval.rooms import estimated_room_distance, is_lab_room


DAY_ORDER = {"segunda": 0, "terca": 1, "quarta": 2, "quinta": 3, "sexta": 4, "sabado": 5}


def minutes(value: str) -> int:
    hour, minute = str(value).split(":")
    return int(hour) * 60 + int(minute)


def course_name(item: dict) -> str:
    course = str(item.get("curso", ""))
    if course == "31":
        return "CC"
    if course == "83":
        return "SI"
    return course


def period_group(item: dict) -> str | None:
    period = str(item.get("periodo", ""))
    if "-P" not in period:
        return None
    return f"{course_name(item)}|{period.split('-P', 1)[1].split('-', 1)[0]}"


def evaluate(payload: dict, min_rest_hours: int = 11) -> dict:
    classes = payload.get("classes", [])
    rooms = {
        str(item.get("id")): item.get("capacidade_estimada")
        for item in payload.get("rooms", [])
    }
    meetings = []
    for item in classes:
        for meeting in item.get("encontros", []):
            meetings.append((item, meeting))

    room_keys = defaultdict(int)
    teacher_keys = defaultdict(int)
    curriculum_slots: dict[tuple, set[str]] = defaultdict(set)
    room_capacity_violations = 0
    resource_violations = 0
    capacity_waste = 0.0
    seen_class_rooms = set()
    teacher_days = set()
    teacher_day_slots: dict[tuple, list[tuple[int, int]]] = defaultdict(list)
    curriculum_rooms: dict[tuple, dict[tuple[int, int], set[str]]] = defaultdict(lambda: defaultdict(set))

    for item, meeting in meetings:
        semester = item.get("semestre", "")
        day = meeting.get("dia", "")
        start = meeting.get("inicio", "")
        end = meeting.get("fim", "")
        room = str(meeting.get("sala", ""))
        teacher = str(item.get("professor", "") or "")
        start_min = minutes(start) if start else None
        end_min = minutes(end) if end else None

        if room:
            room_keys[(semester, day, start, end, room)] += 1
            required_lab = meeting.get("requer_laboratorio")
            if required_lab is None and "exige_laboratorio" in item:
                required_lab = item.get("exige_laboratorio")
            if required_lab is not None and is_lab_room(room) != bool(required_lab):
                resource_violations += 1
            room_capacity = _number(rooms.get(room))
            class_capacity = _number(item.get("capacidade_turma"))
            if room_capacity is not None and class_capacity is not None:
                if class_capacity > room_capacity:
                    room_capacity_violations += 1
                class_room = (item.get("id", ""), room)
                if class_room not in seen_class_rooms:
                    capacity_waste += max(0.0, room_capacity - class_capacity)
                    seen_class_rooms.add(class_room)

        if teacher:
            teacher_keys[(semester, day, start, end, teacher)] += 1
            teacher_days.add((semester, teacher, day))
            if start_min is not None and end_min is not None:
                teacher_day_slots[(semester, teacher, day)].append((start_min, end_min))

        group = period_group(item)
        if group and group.endswith(tuple(f"|{i}" for i in range(1, 9))):
            curriculum_slots[(semester, group, day, start, end)].add(str(item.get("codigo", "")))
            if room:
                curriculum_rooms[(semester, group, day)][(start_min, end_min)].add(room)

    room_conflicts = sum(max(0, value - 1) for value in room_keys.values())
    teacher_conflicts = sum(max(0, value - 1) for value in teacher_keys.values())
    curriculum_conflicts = sum(max(0, len(codes) - 1) for codes in curriculum_slots.values())
    windows = 0
    for slots in teacher_day_slots.values():
        for (_, end), (start, _) in zip(sorted(slots), sorted(slots)[1:]):
            windows += max(0, (start - end) // 120)

    daily_bounds = {}
    for (semester, teacher, day), slots in teacher_day_slots.items():
        daily_bounds[(semester, teacher, day)] = (min(start for start, _ in slots), max(end for _, end in slots))
    rest_violations = 0
    teachers = {(semester, teacher) for semester, teacher, _ in daily_bounds}
    for semester, teacher in teachers:
        days = sorted(
            [day for sem, prof, day in daily_bounds if sem == semester and prof == teacher],
            key=lambda day: DAY_ORDER.get(day, 99),
        )
        for current_day, next_day in zip(days, days[1:]):
            current_end = daily_bounds[(semester, teacher, current_day)][1]
            next_start = daily_bounds[(semester, teacher, next_day)][0]
            if next_start + 24 * 60 - current_end < min_rest_hours * 60:
                rest_violations += 1

    rotation = 0
    by_course_code = defaultdict(list)
    for item in classes:
        by_course_code[(course_name(item), item.get("codigo", ""))].append(item)
    for group in by_course_code.values():
        odd = list(dict.fromkeys(str(item.get("professor", "")) for item in group if item.get("semestre") == "2025-1" and item.get("professor")))
        even = list(dict.fromkeys(str(item.get("professor", "")) for item in group if item.get("semestre") == "2025-2" and item.get("professor")))
        if odd and even and odd[0] == even[0]:
            rotation += 1

    distance = 0
    for slots in curriculum_rooms.values():
        ordered = sorted(
            slots.items(),
            key=lambda pair: (pair[0][0], pair[0][1]),
        )
        for ((_, end), previous_rooms), ((next_start, _), next_rooms) in zip(ordered, ordered[1:]):
            if next_start < end:
                continue
            values = [
                estimated_room_distance(a, b)
                for a in previous_rooms
                for b in next_rooms
            ]
            values = [value for value in values if value is not None]
            if values:
                distance += min(values)

    hard = {
        "conflitos_sala": room_conflicts,
        "conflitos_professor": teacher_conflicts,
        "conflitos_curriculares": curriculum_conflicts,
        "capacidade_insuficiente": room_capacity_violations,
        "recursos_incompativeis": resource_violations,
        "descanso_insuficiente": rest_violations,
    }
    soft = {
        "dias_trabalhados": len(teacher_days),
        "janelas": windows,
        "desperdicio_capacidade": capacity_waste,
        "rodizio_semestre": rotation,
        "distancia": distance,
    }
    hard_count = sum(hard.values())
    score = hard_count * 1_000_000 + sum(soft.values())
    return {"score": score, "hard_violations": hard_count, "hard": hard, "soft": soft}


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
