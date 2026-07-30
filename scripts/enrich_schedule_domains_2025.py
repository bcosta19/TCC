"""Adiciona domínios de padrões de horário à instância CC/SI."""

from __future__ import annotations

import copy
import json
from collections import defaultdict
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "dados" / "processados" / "instancia_2025_cc_si.json"
OUTPUT = ROOT / "dados" / "processados" / "instancia_2025_cc_si_flex.json"


def minutes(value: str) -> int:
    hour, minute = value.split(":")
    return int(hour) * 60 + int(minute)


def pattern_key(pattern: list[dict]) -> tuple:
    return tuple(sorted((item["dia"], item["inicio"], item["fim"]) for item in pattern))


def signature(pattern: list[dict]) -> tuple:
    ordered = sorted(pattern, key=lambda item: (item["inicio"], item["dia"]))
    durations = tuple(minutes(item["fim"]) - minutes(item["inicio"]) for item in ordered)
    return len(pattern), durations


def main() -> None:
    payload = json.loads(INPUT.read_text(encoding="utf-8"))
    patterns_by_semester = defaultdict(dict)
    slots_by_semester = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    sector_days = defaultdict(set)

    for item in payload["classes"]:
        pattern = item.get("encontros", [])
        if not pattern:
            continue
        key = pattern_key(pattern)
        patterns_by_semester[item["semestre"]][key] = copy.deepcopy(pattern)
        for meeting in pattern:
            duration = minutes(meeting["fim"]) - minutes(meeting["inicio"])
            slots_by_semester[item["semestre"]][meeting["dia"]][duration].add(
                (meeting["inicio"], meeting["fim"])
            )
        if item.get("setor"):
            sector_days[item["setor"]].update(meeting["dia"] for meeting in pattern)

    domains = 0
    fixed = 0
    for item in payload["classes"]:
        current = item.get("encontros", [])
        is_internal = item.get("origem") == "IC"
        is_flexible = is_internal and bool(item.get("periodo")) and not str(item.get("setor", "")).startswith("PROJ.FINAL")
        item["horario_fixo"] = not is_flexible
        item["padrao_horario_atual"] = copy.deepcopy(current)
        if not is_flexible or not current:
            item["dominio_horarios"] = [copy.deepcopy(current)] if current else []
            fixed += 1
            continue

        current_by_day = {
            meeting["dia"]: minutes(meeting["fim"]) - minutes(meeting["inicio"])
            for meeting in current
        }
        day_options = []
        for day, duration in current_by_day.items():
            options = sorted(slots_by_semester[item["semestre"]][day][duration])
            day_options.append([(day, start, end) for start, end in options])
        candidates = []
        for combination in product(*day_options):
            pattern = [
                {"dia": day, "inicio": start, "fim": end, "sala": ""}
                for day, start, end in combination
            ]
            candidates.append(pattern)
            if len(candidates) >= 100:
                break
        if not candidates:
            candidates = [copy.deepcopy(current)]
        item["dominio_horarios"] = candidates
        domains += len(candidates)

    payload["schedule_domain"] = {
        "source": "padrões observados na própria planilha QH 2025",
        "sector_days": {key: sorted(value) for key, value in sector_days.items()},
        "fixed_classes": fixed,
        "flexible_classes": len(payload["classes"]) - fixed,
        "candidate_patterns_total": domains,
        "warning": "domínios provisórios; não substituem disponibilidade oficial dos docentes",
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{OUTPUT}: {len(payload['classes'])} turmas, {fixed} fixas, {len(payload['classes']) - fixed} flexíveis")


if __name__ == "__main__":
    main()
