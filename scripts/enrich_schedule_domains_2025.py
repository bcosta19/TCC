"""Adiciona domínios de padrões de horário à instância CC/SI."""

from __future__ import annotations

import copy
import csv
import json
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "dados" / "processados" / "instancia_2025_cc_si.json"
OUTPUT = ROOT / "dados" / "processados" / "instancia_2025_cc_si_flex.json"
SECTOR_DAYS_CSV = ROOT / "dados" / "processados" / "dias_por_setor_2025.csv"
DAY_ORDER = {"segunda": 0, "terca": 1, "quarta": 2, "quinta": 3, "sexta": 4, "sabado": 5}


def minutes(value: str) -> int:
    hour, minute = value.split(":")
    return int(hour) * 60 + int(minute)


def pattern_key(pattern: list[dict]) -> tuple:
    return tuple(sorted((item["dia"], item["inicio"], item["fim"]) for item in pattern))


def ordered_pattern(pattern: list[dict]) -> list[dict]:
    return sorted(
        pattern,
        key=lambda item: (
            DAY_ORDER.get(str(item.get("dia", "")), 99),
            item.get("inicio", ""),
            item.get("fim", ""),
        ),
    )


def signature(pattern: list[dict]) -> tuple:
    ordered = ordered_pattern(pattern)
    durations = tuple(minutes(item["fim"]) - minutes(item["inicio"]) for item in ordered)
    return len(pattern), durations


def day_tuple(pattern: list[dict]) -> tuple[str, ...]:
    return tuple(str(item["dia"]) for item in ordered_pattern(pattern))


def write_sector_days(rows: list[dict]) -> None:
    fieldnames = [
        "setor",
        "semestre",
        "encontros",
        "duracoes_min",
        "dias",
        "turmas_observadas",
        "codigos",
        "fonte",
    ]
    with SECTOR_DAYS_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    payload = json.loads(INPUT.read_text(encoding="utf-8"))
    slots_by_semester = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    sector_days = defaultdict(set)
    sector_patterns: dict[tuple[str, str, tuple], Counter] = defaultdict(Counter)
    sector_pattern_examples: dict[tuple[str, str, tuple, tuple[str, ...]], dict] = {}

    for item in payload["classes"]:
        pattern = item.get("encontros", [])
        if not pattern:
            continue
        for meeting in pattern:
            duration = minutes(meeting["fim"]) - minutes(meeting["inicio"])
            slots_by_semester[item["semestre"]][meeting["dia"]][duration].add(
                (meeting["inicio"], meeting["fim"])
            )
        if item.get("setor"):
            sig = signature(pattern)
            days = day_tuple(pattern)
            key = (item["semestre"], item["setor"], sig)
            sector_patterns[key][days] += 1
            example_key = (item["semestre"], item["setor"], sig, days)
            example = sector_pattern_examples.setdefault(
                example_key,
                {
                    "setor": item["setor"],
                    "semestre": item["semestre"],
                    "encontros": sig[0],
                    "duracoes_min": ";".join(str(value) for value in sig[1]),
                    "dias": ";".join(days),
                    "turmas": set(),
                    "codigos": set(),
                },
            )
            example["turmas"].add(str(item.get("id", "")))
            example["codigos"].add(str(item.get("codigo", "")))
            sector_days[item["setor"]].update(days)

    sector_day_rows = []
    for example in sorted(
        sector_pattern_examples.values(),
        key=lambda row: (row["setor"], row["semestre"], row["dias"], row["duracoes_min"]),
    ):
        sector_day_rows.append({
            "setor": example["setor"],
            "semestre": example["semestre"],
            "encontros": example["encontros"],
            "duracoes_min": example["duracoes_min"],
            "dias": example["dias"],
            "turmas_observadas": len(example["turmas"]),
            "codigos": ";".join(sorted(example["codigos"])),
            "fonte": "padroes observados na planilha QH 2025; proxy nao oficial",
        })
    write_sector_days(sector_day_rows)

    domains = 0
    fixed = 0
    source_counts = Counter()
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

        sig = signature(current)
        durations = sig[1]
        day_options_from_sector = [
            day_pattern
            for day_pattern, _count in sector_patterns[
                (item["semestre"], item.get("setor"), sig)
            ].most_common()
        ]
        if day_options_from_sector:
            day_patterns = day_options_from_sector
            source = "padroes_do_setor"
        else:
            day_patterns = [day_tuple(current)]
            source = "padrao_atual_sem_equivalente_setor"

        candidates = []
        seen = set()
        for days in day_patterns:
            if len(days) != len(durations):
                continue
            day_options = []
            for day, duration in zip(days, durations):
                options = sorted(slots_by_semester[item["semestre"]][day][duration])
                if not options:
                    day_options = []
                    break
                day_options.append([(day, start, end) for start, end in options])
            if not day_options:
                continue
            for combination in product(*day_options):
                if len(set(combination)) != len(combination):
                    continue
                pattern = [
                    {"dia": day, "inicio": start, "fim": end, "sala": ""}
                    for day, start, end in combination
                ]
                key = pattern_key(pattern)
                if key in seen:
                    continue
                candidates.append(pattern)
                seen.add(key)
                if len(candidates) >= 100:
                    break
            if len(candidates) >= 100:
                break
        if not candidates:
            candidates = [copy.deepcopy(current)]
            source = "fallback_padrao_atual"
        item["dominio_horarios"] = candidates
        item["dominio_horarios_fonte"] = source
        item["dias_setor_observados"] = sorted(sector_days.get(item.get("setor"), []))
        source_counts[source] += 1
        domains += len(candidates)

    payload["schedule_domain"] = {
        "source": "padrões observados na própria planilha QH 2025",
        "sector_days": {key: sorted(value) for key, value in sector_days.items()},
        "sector_patterns_csv": str(SECTOR_DAYS_CSV.relative_to(ROOT)),
        "fixed_classes": fixed,
        "flexible_classes": len(payload["classes"]) - fixed,
        "candidate_patterns_total": domains,
        "domain_source_counts": dict(source_counts),
        "warning": "domínios provisórios; não substituem dias oficiais de setor nem disponibilidade oficial dos docentes",
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{OUTPUT}: {len(payload['classes'])} turmas, {fixed} fixas, {len(payload['classes']) - fixed} flexíveis")


if __name__ == "__main__":
    main()
