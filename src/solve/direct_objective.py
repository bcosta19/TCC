"""Avaliação leve, sem pandas, para a busca de salas e horários."""

from __future__ import annotations

import re
from collections import defaultdict

from src.eval.rooms import is_lab_room


DAY_ORDER = {"segunda": 0, "terca": 1, "quarta": 2, "quinta": 3, "sexta": 4, "sabado": 5}
YEAR_RE = re.compile(r"^(\d{4})-")


def minutes(value: str) -> int:
    hour, minute = str(value).split(":")
    return int(hour) * 60 + int(minute)


def overlaps(start_a: int, end_a: int, start_b: int, end_b: int) -> bool:
    return max(start_a, start_b) < min(end_a, end_b)


def teachers_for_item(item: dict) -> list[str]:
    explicit = item.get("professores_observados")
    if isinstance(explicit, (list, set, tuple)):
        names = [str(p).strip() for p in explicit if str(p).strip()]
        if names:
            return names
    single = str(item.get("professor", "") or "").strip()
    return [single] if single else []


def groups_for_item(item: dict) -> list[str]:
    explicit = item.get("grupos_curriculares")
    if isinstance(explicit, (list, set, tuple)):
        valid = [str(g).strip() for g in explicit if re.match(r"^(?:CC|SI)-P[1-8]$", str(g).strip())]
        if valid:
            return valid
    period = str(item.get("periodo", ""))
    if "-P" in period:
        course = str(item.get("curso", ""))
        c_name = "CC" if course == "31" else ("SI" if course == "83" else course)
        p_num = period.split("-P", 1)[1].split("-", 1)[0]
        if p_num in {str(i) for i in range(1, 9)}:
            return [f"{c_name}-P{p_num}"]
    return []


def evaluate(payload: dict, min_rest_hours: int = 11) -> dict:
    classes = payload.get("classes", [])
    rooms = {
        str(item.get("id")): item.get("capacidade_estimada")
        for item in payload.get("rooms", [])
    }
    policy_map = payload.get("politica_cotutoria", {})

    room_meetings: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    teacher_meetings: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    curriculum_meetings: dict[tuple[str, str, str], list[dict]] = defaultdict(list)

    room_capacity_violations = 0
    resource_violations = 0
    capacity_waste = 0.0
    seen_class_rooms = set()
    teacher_days = set()
    teacher_day_slots: dict[tuple[str, str, str], list[tuple[int, int]]] = defaultdict(list)

    ic_teachers: set[str] = {
        str(teacher.get("name", ""))
        for teacher in payload.get("teachers", [])
        if str(teacher.get("name", "")) and teacher.get("incluido_h12", True) is not False
    }
    obligatory_classes = []
    preference_bonus = 0.0
    preference_observations = 0
    priorities = payload.get("prioridades_professores", {})

    for item in classes:
        code = str(item.get("codigo", ""))
        is_internal = item.get("origem") == "IC" or code.startswith("TCC")
        class_teachers = teachers_for_item(item)
        for t in class_teachers:
            if is_internal:
                ic_teachers.add(t)

        if is_internal and bool(item.get("obrigatoria", False)):
            obligatory_classes.append(item)

        assigned_teacher = str(item.get("professor", "") or "")
        if is_internal and assigned_teacher:
            preference = (item.get("preferencias_professores") or {}).get(assigned_teacher)
            priority = priorities.get(assigned_teacher)
            pref_num = _number(preference)
            prio_num = _number(priority)
            if pref_num is not None and prio_num is not None:
                preference_bonus -= pref_num * prio_num
                preference_observations += 1

        class_id = str(item.get("id", ""))
        class_capacity = _number(item.get("capacidade_turma"))
        semester = str(item.get("semestre", ""))
        c_groups = groups_for_item(item)

        for meeting in item.get("encontros", []):
            day = str(meeting.get("dia", ""))
            start_str = str(meeting.get("inicio", ""))
            end_str = str(meeting.get("fim", ""))
            room = str(meeting.get("sala", "") or "")
            if not start_str or not end_str or not day:
                continue
            start_min = minutes(start_str)
            end_min = minutes(end_str)

            entry = {
                "class_id": class_id,
                "codigo": code,
                "start": start_min,
                "end": end_min,
                "room": room,
            }

            if room:
                room_meetings[(semester, day, room)].append(entry)
                required_lab = meeting.get("requer_laboratorio")
                if required_lab is None and "exige_laboratorio" in item:
                    required_lab = item.get("exige_laboratorio")
                if required_lab is not None and is_lab_room(room) != bool(required_lab):
                    resource_violations += 1
                room_capacity = _number(rooms.get(room))
                if room_capacity is not None and class_capacity is not None:
                    if class_capacity > room_capacity:
                        room_capacity_violations += 1
                    class_room = (class_id, room)
                    if class_room not in seen_class_rooms:
                        capacity_waste += max(0.0, room_capacity - class_capacity)
                        seen_class_rooms.add(class_room)

            for t in class_teachers:
                teacher_meetings[(semester, day, t)].append(entry)
                teacher_days.add((semester, t, day))
                teacher_day_slots[(semester, t, day)].append((start_min, end_min))

            for g in c_groups:
                curriculum_meetings[(semester, g, day)].append(entry)

    # Room conflicts
    room_conflicts = 0
    for meeting_list in room_meetings.values():
        for i in range(len(meeting_list)):
            for j in range(i + 1, len(meeting_list)):
                if meeting_list[i]["class_id"] != meeting_list[j]["class_id"] and overlaps(
                    meeting_list[i]["start"], meeting_list[i]["end"],
                    meeting_list[j]["start"], meeting_list[j]["end"],
                ):
                    room_conflicts += 1

    # Teacher conflicts
    teacher_conflicts = 0
    for meeting_list in teacher_meetings.values():
        for i in range(len(meeting_list)):
            for j in range(i + 1, len(meeting_list)):
                if meeting_list[i]["class_id"] != meeting_list[j]["class_id"] and overlaps(
                    meeting_list[i]["start"], meeting_list[i]["end"],
                    meeting_list[j]["start"], meeting_list[j]["end"],
                ):
                    teacher_conflicts += 1

    # Curriculum conflicts (parallel sections of same discipline code do not conflict)
    curriculum_conflicts = 0
    for meeting_list in curriculum_meetings.values():
        dedup = {}
        for entry in meeting_list:
            key = (entry["codigo"], entry["start"], entry["end"])
            dedup[key] = entry
        unique_entries = list(dedup.values())
        for i in range(len(unique_entries)):
            for j in range(i + 1, len(unique_entries)):
                if unique_entries[i]["codigo"] != unique_entries[j]["codigo"] and overlaps(
                    unique_entries[i]["start"], unique_entries[i]["end"],
                    unique_entries[j]["start"], unique_entries[j]["end"],
                ):
                    curriculum_conflicts += 1

    # Windows
    windows = 0
    for slots in teacher_day_slots.values():
        slots_sorted = sorted(set(slots))
        if len(slots_sorted) < 2:
            continue
        merged = []
        for s, e in slots_sorted:
            if not merged:
                merged.append([s, e])
            else:
                if s <= merged[-1][1]:
                    merged[-1][1] = max(merged[-1][1], e)
                else:
                    merged.append([s, e])
        for (s1, e1), (s2, e2) in zip(merged, merged[1:]):
            windows += max(0, (s2 - e1) // 120)

    # Rest violations
    daily_bounds = {}
    for (semester, teacher, day), slots in teacher_day_slots.items():
        daily_bounds[(semester, teacher, day)] = (
            min(s for s, _ in slots),
            max(e for _, e in slots),
        )
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

    # Rotation across semesters of the same year
    rotation = 0
    by_year_course_code = defaultdict(list)
    for item in classes:
        semester = str(item.get("semestre", ""))
        match = YEAR_RE.match(semester)
        ano = match.group(1) if match else ""
        course = str(item.get("curso", ""))
        c_name = "CC" if course == "31" else ("SI" if course == "83" else course)
        by_year_course_code[(ano, c_name, str(item.get("codigo", "")))].append(item)

    for group in by_year_course_code.values():
        impar = {
            t
            for item in group
            if str(item.get("semestre", "")).endswith("-1")
            for t in teachers_for_item(item)
            if t
        }
        par = {
            t
            for item in group
            if str(item.get("semestre", "")).endswith("-2")
            for t in teachers_for_item(item)
            if t
        }
        if impar and par and (impar & par):
            rotation += len(impar & par)

    # H12
    h12_violations = 0
    min_h12 = int(payload.get("min_obrigatorias_ano", 3))
    teacher_counts: dict[str, float] = defaultdict(float)
    h12_available = True

    for item in obligatory_classes:
        profs = teachers_for_item(item)
        if not profs:
            continue
        if len(profs) == 1:
            teacher_counts[profs[0]] += 1.0
        else:
            p_entry = policy_map.get(item.get("id", "")) or {}
            p_name = p_entry.get("politica_h12") if isinstance(p_entry, dict) else str(p_entry or "")
            p_name = str(p_name or "").strip()
            if not p_name:
                h12_available = False
                break
            if p_name == "integral_para_cada_docente":
                for p in profs:
                    teacher_counts[p] += 1.0
            elif p_name == "fracionada":
                for p in profs:
                    teacher_counts[p] += 1.0 / len(profs)
            elif p_name == "contar_para_um_responsavel":
                resp = p_entry.get("professor_responsavel") if isinstance(p_entry, dict) else None
                if resp and resp in profs:
                    teacher_counts[resp] += 1.0
                else:
                    h12_available = False
                    break
            elif p_name == "nao_contabilizar_em_h12":
                pass
            else:
                h12_available = False
                break

    if h12_available:
        if ic_teachers:
            for t in ic_teachers:
                teacher_counts.setdefault(t, 0.0)
            h12_violations = sum(1 for t in ic_teachers if teacher_counts[t] < min_h12)
        elif teacher_counts:
            h12_violations = sum(1 for count in teacher_counts.values() if count < min_h12)

    hard = {
        "conflitos_sala": room_conflicts,
        "conflitos_professor": teacher_conflicts,
        "conflitos_curriculares": curriculum_conflicts,
        "capacidade_insuficiente": room_capacity_violations,
        "recursos_incompativeis": resource_violations,
        "descanso_insuficiente": rest_violations,
        "carga_anual_insuficiente": h12_violations if h12_available else 0,
    }
    soft = {
        "dias_trabalhados": len(teacher_days),
        "janelas": windows,
        "desperdicio_capacidade": capacity_waste,
        "rodizio_semestre": rotation,
    }
    if preference_observations:
        soft["preferencia_priorizada"] = preference_bonus

    hard_count = sum(hard.values())
    soft_count = sum(soft.values())
    score = hard_count * 1_000_000 + soft_count
    return {"score": score, "hard_violations": hard_count, "hard": hard, "soft": soft}


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
