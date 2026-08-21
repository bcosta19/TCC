"""Leitura das grades curriculares versionadas em Markdown."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


COURSE_CODES = {"CC": "31", "SI": "83"}
ROW_RE = re.compile(
    r"^\|\s*([A-Z]{2,4}\d{4,6})\s*\|\s*([^|]+?)\s*\|\s*(\d+)h\s*\|$"
)
PERIOD_RE = re.compile(r"^### Período (\d+)")


@dataclass(frozen=True)
class CurriculumEntry:
    course: str
    code: str
    discipline: str
    hours: int
    kind: str
    period: int | None
    source: str

    @property
    def group(self) -> str:
        return f"{self.course}-P{self.period}" if self.period is not None else f"{self.course}-OPT"


def load_curriculum_markdown(path: str | Path, course: str) -> list[CurriculumEntry]:
    """Lê disciplinas obrigatórias por período e optativas não periodizadas."""
    path = Path(path)
    course = course.upper()
    if course not in COURSE_CODES:
        raise ValueError(f"curso desconhecido: {course}")

    kind = ""
    period: int | None = None
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        period_match = PERIOD_RE.match(line)
        if period_match:
            kind = "obrigatoria"
            period = int(period_match.group(1))
            continue
        if line.startswith("## Disciplinas optativas") or line.startswith(
            "## Disciplinas não periodizadas"
        ):
            kind = "optativa"
            period = None
            continue
        match = ROW_RE.match(line)
        if not match or not kind:
            continue
        code, discipline, hours = match.groups()
        entries.append(
            CurriculumEntry(
                course=course,
                code=code,
                discipline=discipline.strip(),
                hours=int(hours),
                kind=kind,
                period=period,
                source=str(path),
            )
        )
    return entries


def load_project_curricula(root: str | Path) -> dict[str, list[CurriculumEntry]]:
    root = Path(root)
    return {
        "CC": load_curriculum_markdown(root / "dados" / "grade_cc.md", "CC"),
        "SI": load_curriculum_markdown(root / "dados" / "grade_si.md", "SI"),
    }


def entries_by_code(entries: list[CurriculumEntry]) -> dict[str, list[CurriculumEntry]]:
    result: dict[str, list[CurriculumEntry]] = {}
    for entry in entries:
        result.setdefault(entry.code, []).append(entry)
    return result


def classify_code(code: str, curricula: dict[str, list[CurriculumEntry]]) -> dict:
    """Classifica um código sem duplicar ofertas presentes nos dois cursos."""
    code = str(code or "").strip()
    memberships = {}
    for course, entries in curricula.items():
        matched = [entry for entry in entries if entry.code == code]
        if not matched:
            continue
        periods = sorted({entry.period for entry in matched if entry.period is not None})
        kinds = sorted({entry.kind for entry in matched})
        memberships[course] = {
            "course_code": COURSE_CODES[course],
            "kinds": kinds,
            "periods": periods,
            "groups": sorted({entry.group for entry in matched}),
        }
    obligatory_courses = sorted(
        course for course, value in memberships.items() if "obrigatoria" in value["kinds"]
    )
    return {
        "code": code,
        "courses": sorted(memberships),
        "memberships": memberships,
        "shared": len(memberships) > 1,
        "obligatory": bool(obligatory_courses),
        "obligatory_courses": obligatory_courses,
        "in_curricula": bool(memberships),
    }
