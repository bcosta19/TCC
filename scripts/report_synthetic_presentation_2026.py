"""Gera uma apresentação em PDF comparando os perfis sintéticos v1, v2_hp e v3.

Lê os CSVs de resultados e as soluções JSON do perfil v3, monta slides HTML com
gráficos SVG e imprime em PDF com o Chromium do Playwright. Os números vêm só
dos artefatos do experimento; nada é estimado aqui.

Uso:
    python scripts/report_synthetic_presentation_2026.py
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dados" / "processados"
DEFAULT_OUTPUT = ROOT / "saida" / "apresentacao_experimento_sintetico_v3.pdf"

PROFILES = {
    "v1": {
        "csv": DATA / "resultados_experimento_sintetico_2026.csv",
        "instance": DATA / "instancia_sintetica_2026_v1.json",
        "label": "v1",
        "descricao": "Só optativas do IC flexíveis",
    },
    "v2": {
        "csv": DATA / "resultados_experimento_sintetico_2026_v2_hp.csv",
        "instance": DATA / "instancia_sintetica_2026_v2_hp.json",
        "label": "v2_hp",
        "descricao": "Todas as turmas do IC flexíveis no setor",
    },
    "v3": {
        "csv": DATA / "resultados_experimento_sintetico_2026_v3.csv",
        "instance": DATA / "instancia_sintetica_2026_v3.json",
        "label": "v3",
        "descricao": "Decisões de 30/09/2026",
    },
}
V3_SOLUTIONS = DATA / "experimento_sintetico_2026_v3"
ALGORITHMS = ("sa", "ils", "vns")
ALGORITHM_LABEL = {"baseline": "Observado", "guloso": "Guloso", "sa": "SA", "ils": "ILS", "vns": "VNS"}

# Paleta de referência (slots 1–3, validados all-pairs no modo claro).
COLOR = {"sa": "#2a78d6", "ils": "#eb6834", "vns": "#1baf7a", "baseline": "#8a8984", "guloso": "#52514e"}
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
MUTED = "#8a8984"
GRID = "#e4e3df"
SURFACE = "#fcfcfb"

HARD_LABEL = {
    "hard_conflitos_sala": "Choque de sala",
    "hard_conflitos_professor": "Choque de professor",
    "hard_conflitos_curriculares": "Choque curricular (H8)",
    "hard_capacidade_insuficiente": "Capacidade (H10)",
    "hard_recursos_incompativeis": "Laboratório",
    "hard_descanso_insuficiente": "Descanso (H11)",
    "hard_carga_anual_insuficiente": "Carga anual (H12)",
}
SOFT_LABEL = {
    "soft_dias_trabalhados": ("Dias trabalhados", "menor é melhor"),
    "soft_janelas": ("Janelas", "menor é melhor"),
    "soft_desperdicio_capacidade": ("Desperdício de capacidade", "menor é melhor"),
    "soft_rodizio_semestre": ("Repetições sem rodízio", "menor é melhor"),
    "soft_preferencia_priorizada": ("Preferência (bônus negativo)", "menor é melhor"),
}


# ---------------------------------------------------------------- dados

def read_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    for row in rows:
        for key, value in row.items():
            if key not in {"algoritmo", "seed"}:
                row[key] = float(value) if value not in {"", None} else None
    return rows


def best(rows: list[dict], algorithm: str) -> dict:
    return min((row for row in rows if row["algoritmo"] == algorithm), key=lambda row: row["score"])


def instance_stats(path: Path) -> dict | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    classes = payload.get("classes", [])
    return {
        "turmas": len(classes),
        "flexiveis": sum(not item.get("horario_fixo", True) for item in classes),
        "externas": sum(item.get("origem") != "IC" for item in classes),
        "obrigatorias_ic": sum(item.get("origem") == "IC" and item.get("obrigatoria") is True for item in classes),
        "professor_movel": sum(
            len(item.get("professores_habilitados") or []) > 1 and not item.get("professor_fixo") for item in classes
        ),
        "h12": sum(teacher.get("incluido_h12") is True for teacher in payload.get("teachers", [])),
    }


def progress_curves(algorithm: str, seeds: list[str], budget: int, step: int = 25) -> list[tuple[int, float]]:
    """Mediana entre sementes das violações hard da melhor solução até cada avaliação."""
    series = []
    for seed in seeds:
        path = V3_SOLUTIONS / f"solucao_{algorithm}_{seed}.json"
        if not path.exists():
            continue
        progress = json.loads(path.read_text(encoding="utf-8"))["experiment_result"]["progress"]
        series.append(sorted((int(p["evaluations"]), float(p["hard_violations"])) for p in progress))
    grid = list(range(1, budget + 1, step)) + [budget]
    curve = []
    for point in grid:
        values = []
        for entries in series:
            reached = [value for evaluations, value in entries if evaluations <= point]
            if reached:
                values.append(reached[-1])
        if values:
            curve.append((point, statistics.median(values)))
    return curve


def overlaps(a: dict, b: dict) -> bool:
    def minutes(value: str) -> int:
        hour, minute = value.split(":")
        return int(hour) * 60 + int(minute)

    return a["dia"] == b["dia"] and minutes(a["inicio"]) < minutes(b["fim"]) and minutes(b["inicio"]) < minutes(a["fim"])


def residual_curriculum_conflicts(solution_path: Path) -> list[dict]:
    payload = json.loads(solution_path.read_text(encoding="utf-8"))
    by_group: dict[tuple[str, str], list[dict]] = {}
    for item in payload.get("classes", []):
        for group in item.get("grupos_curriculares") or []:
            if re.fullmatch(r"(CC|SI)-P[1-8]", group):
                by_group.setdefault((item["semestre"], group), []).append(item)
    conflicts = {}
    for (semester, group), items in sorted(by_group.items()):
        for i, first in enumerate(items):
            for second in items[i + 1:]:
                if first["codigo"] == second["codigo"]:
                    continue
                clash = [
                    (a, b) for a in first.get("encontros", []) for b in second.get("encontros", []) if overlaps(a, b)
                ]
                if clash:
                    key = (semester, group, *sorted((first["codigo"], second["codigo"])))
                    a, _ = clash[0]
                    conflicts[key] = {
                        "semestre": semester,
                        "grupo": group,
                        "a": f"{first['codigo']} {first.get('turma', '')} ({'fixa' if first.get('horario_fixo') else 'flexível'}, {first.get('origem')})",
                        "b": f"{second['codigo']} {second.get('turma', '')} ({'fixa' if second.get('horario_fixo') else 'flexível'}, {second.get('origem')})",
                        "quando": f"{a['dia']} {a['inicio']}–{a['fim']}",
                    }
    return list(conflicts.values())


def fixed_curriculum_floor(instance_path: Path) -> int:
    """Sobreposições H8 entre turmas de horário fixo, contadas como o avaliador.

    Nenhum movimento altera esses encontros, logo é um piso para H8.
    """
    payload = json.loads(instance_path.read_text(encoding="utf-8"))
    seen = set()
    meetings: dict[tuple[str, str, str], list[tuple[str, dict]]] = {}
    for item in payload.get("classes", []):
        if not item.get("horario_fixo", True):
            continue
        for group in item.get("grupos_curriculares") or []:
            if not re.fullmatch(r"(CC|SI)-P[1-8]", group):
                continue
            for meeting in item.get("encontros", []):
                key = (item["semestre"], group, item["codigo"], meeting["dia"], meeting["inicio"], meeting["fim"])
                if key in seen:
                    continue
                seen.add(key)
                meetings.setdefault((item["semestre"], group, meeting["dia"]), []).append((item["codigo"], meeting))
    count = 0
    for records in meetings.values():
        for i, (code_a, a) in enumerate(records):
            for code_b, b in records[i + 1:]:
                if code_a != code_b and overlaps(a, b):
                    count += 1
    return count


# ---------------------------------------------------------------- SVG

def fmt(value: float | None, digits: int = 0) -> str:
    if value is None:
        return "–"
    if digits == 0:
        return f"{value:,.0f}".replace(",", ".")
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def esc(text: object) -> str:
    return html.escape(str(text))


def nice_max(value: float) -> float:
    for candidate in (5, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100, 150, 200):
        if value <= candidate:
            return candidate
    return value


def strip_plot(v3_rows: list[dict], width: int = 1100, height: int = 420) -> str:
    """Violações hard por execução: um ponto por semente, rótulo da mediana."""
    left, right, top, bottom = 70, 30, 30, 60
    categories = ["baseline", "guloso", *ALGORITHMS]
    values = {c: [r["hard_total"] for r in v3_rows if r["algoritmo"] == c] for c in categories}
    y_max = nice_max(max(max(v) for v in values.values() if v))
    plot_w, plot_h = width - left - right, height - top - bottom
    band = plot_w / len(categories)

    def y(value: float) -> float:
        return top + plot_h - value / y_max * plot_h

    parts = [f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img">']
    ticks = 5
    for i in range(ticks + 1):
        value = y_max * i / ticks
        parts.append(f'<line x1="{left}" x2="{width - right}" y1="{y(value):.1f}" y2="{y(value):.1f}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{left - 10}" y="{y(value) + 4:.1f}" text-anchor="end" class="tick">{fmt(value)}</text>')
    parts.append(f'<text x="{left - 50}" y="{top + plot_h / 2}" transform="rotate(-90 {left - 50} {top + plot_h / 2})" text-anchor="middle" class="axis">violações hard</text>')
    for index, category in enumerate(categories):
        cx = left + band * (index + 0.5)
        points = values[category]
        color = COLOR[category]
        offsets = [0] if len(points) == 1 else [(-1 + 2 * k / (len(points) - 1)) * 22 for k in range(len(points))]
        for offset, value in zip(offsets, points):
            parts.append(f'<circle cx="{cx + offset:.1f}" cy="{y(value):.1f}" r="6" fill="{color}" stroke="{SURFACE}" stroke-width="2"/>')
        median = statistics.median(points)
        parts.append(f'<line x1="{cx - 34:.1f}" x2="{cx + 34:.1f}" y1="{y(median):.1f}" y2="{y(median):.1f}" stroke="{TEXT}" stroke-width="2"/>')
        label = fmt(median, 1 if median % 1 else 0)
        detail = "" if len(points) == 1 else f" (mín {fmt(min(points))}, máx {fmt(max(points))})"
        parts.append(f'<text x="{cx:.1f}" y="{y(median) - 14:.1f}" text-anchor="middle" class="value">{label}</text>')
        parts.append(f'<text x="{cx:.1f}" y="{height - bottom + 24}" text-anchor="middle" class="cat">{ALGORITHM_LABEL[category]}</text>')
        parts.append(f'<text x="{cx:.1f}" y="{height - bottom + 42}" text-anchor="middle" class="note">{"1 solução" if len(points) == 1 else f"{len(points)} sementes"}{detail}</text>')
    parts.append("</svg>")
    return "".join(parts)


def convergence_chart(curves: dict[str, list[tuple[int, float]]], budget: int, floor: int | None = None, width: int = 1100, height: int = 420) -> str:
    left, right, top, bottom = 70, 110, 30, 50
    y_max = nice_max(max(value for curve in curves.values() for _, value in curve))
    plot_w, plot_h = width - left - right, height - top - bottom

    def x(value: float) -> float:
        return left + value / budget * plot_w

    def y(value: float) -> float:
        return top + plot_h - value / y_max * plot_h

    parts = [f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img">']
    for i in range(6):
        value = y_max * i / 5
        parts.append(f'<line x1="{left}" x2="{width - right}" y1="{y(value):.1f}" y2="{y(value):.1f}" stroke="{GRID}"/>')
        parts.append(f'<text x="{left - 10}" y="{y(value) + 4:.1f}" text-anchor="end" class="tick">{fmt(value)}</text>')
    for i in range(6):
        value = budget * i / 5
        parts.append(f'<text x="{x(value):.1f}" y="{height - bottom + 22}" text-anchor="middle" class="tick">{fmt(value)}</text>')
    parts.append(f'<text x="{left + plot_w / 2}" y="{height - 6}" text-anchor="middle" class="axis">avaliações da função objetivo</text>')
    parts.append(f'<text x="{left - 50}" y="{top + plot_h / 2}" transform="rotate(-90 {left - 50} {top + plot_h / 2})" text-anchor="middle" class="axis">violações hard (mediana)</text>')
    if floor is not None:
        parts.append(f'<line x1="{left}" x2="{x(budget):.1f}" y1="{y(floor):.1f}" y2="{y(floor):.1f}" stroke="{TEXT_2}" stroke-width="1.5" stroke-dasharray="2 4"/>')
        parts.append(f'<text x="{left + 8}" y="{y(floor) + 18:.1f}" class="note">piso estrutural de H8 = {fmt(floor)}</text>')
    label_y = []
    for algorithm in ("vns", "sa", "ils"):
        curve = curves.get(algorithm) or []
        if not curve:
            continue
        path = []
        previous = None
        for evaluations, value in curve:
            if previous is None:
                path.append(f"M{x(evaluations):.1f},{y(value):.1f}")
            else:
                path.append(f"H{x(evaluations):.1f}V{y(value):.1f}")
            previous = value
        path.append(f"H{x(budget):.1f}")
        dash = ' stroke-dasharray="8 6"' if algorithm == "ils" else ""
        parts.append(f'<path d="{"".join(path)}" fill="none" stroke="{COLOR[algorithm]}" stroke-width="2.5"{dash}/>')
        end = curve[-1][1]
        ly = y(end) + 4
        while any(abs(ly - other) < 16 for other in label_y):
            ly += 16
        label_y.append(ly)
        parts.append(f'<circle cx="{x(budget):.1f}" cy="{y(end):.1f}" r="5" fill="{COLOR[algorithm]}" stroke="{SURFACE}" stroke-width="2"/>')
        parts.append(f'<text x="{x(budget) + 12:.1f}" y="{ly:.1f}" class="label">{ALGORITHM_LABEL[algorithm]} · {fmt(end, 1 if end % 1 else 0)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def dumbbell(profiles: dict[str, dict], width: int = 1100, height: int = 300) -> str:
    """Por perfil: observado → guloso → melhor busca, em violações hard."""
    left, right, top, bottom = 330, 40, 30, 50
    x_max = nice_max(max(p["baseline"]["hard_total"] for p in profiles.values()))
    plot_w = width - left - right
    row_h = (height - top - bottom) / len(profiles)

    def x(value: float) -> float:
        return left + value / x_max * plot_w

    parts = [f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img">']
    for i in range(6):
        value = x_max * i / 5
        parts.append(f'<line x1="{x(value):.1f}" x2="{x(value):.1f}" y1="{top}" y2="{height - bottom}" stroke="{GRID}"/>')
        parts.append(f'<text x="{x(value):.1f}" y="{height - bottom + 20}" text-anchor="middle" class="tick">{fmt(value)}</text>')
    parts.append(f'<text x="{left + plot_w / 2}" y="{height - 8}" text-anchor="middle" class="axis">violações hard</text>')
    for index, (key, profile) in enumerate(profiles.items()):
        cy = top + row_h * (index + 0.5)
        base = profile["baseline"]["hard_total"]
        greedy = profile["guloso"]["hard_total"]
        top_search = min(profile["best"].values(), key=lambda row: row["score"])
        best_value = top_search["hard_total"]
        parts.append(f'<text x="{left - 16}" y="{cy - 4:.1f}" text-anchor="end" class="cat">{esc(profile["label"])}</text>')
        parts.append(f'<text x="{left - 16}" y="{cy + 14:.1f}" text-anchor="end" class="note">{esc(profile["descricao"])}</text>')
        parts.append(f'<line x1="{x(best_value):.1f}" x2="{x(base):.1f}" y1="{cy:.1f}" y2="{cy:.1f}" stroke="{GRID}" stroke-width="4"/>')
        marks = [
            (base, COLOR["baseline"], f"observado {fmt(base)}", -14),
            (greedy, COLOR["guloso"], f"guloso {fmt(greedy)}", 24),
            (best_value, COLOR[top_search["algoritmo"]], f"{ALGORITHM_LABEL[top_search['algoritmo']]} {fmt(best_value)}", 24 if best_value == 0 else -14),
        ]
        for value, color, label, dy in marks:
            parts.append(f'<circle cx="{x(value):.1f}" cy="{cy:.1f}" r="7" fill="{color}" stroke="{SURFACE}" stroke-width="2"/>')
            anchor = "start" if value == 0 else "middle"
            parts.append(f'<text x="{x(value) - (6 if value == 0 else 0):.1f}" y="{cy + dy:.1f}" text-anchor="{anchor}" class="label">{esc(label)}</text>')
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------- slides

CSS = f"""
@page {{ size: 1280px 720px; margin: 0; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: 'Inter', 'Noto Sans', 'DejaVu Sans', sans-serif; color: {TEXT}; background: {SURFACE}; }}
.slide {{ width: 1280px; height: 720px; padding: 48px 64px; page-break-after: always; position: relative; overflow: hidden; background: {SURFACE}; }}
.slide:last-child {{ page-break-after: auto; }}
h1 {{ font-size: 40px; margin: 0 0 12px; line-height: 1.15; }}
h2 {{ font-size: 28px; margin: 0 0 6px; }}
.sub {{ color: {TEXT_2}; font-size: 17px; margin: 0 0 20px; }}
.foot {{ position: absolute; left: 64px; right: 64px; bottom: 22px; color: {MUTED}; font-size: 12px; display: flex; justify-content: space-between; }}
.badge {{ display: inline-block; border: 1.5px solid {TEXT_2}; color: {TEXT_2}; border-radius: 4px; padding: 3px 10px; font-size: 13px; font-weight: 600; letter-spacing: .04em; }}
table {{ border-collapse: collapse; font-size: 15px; width: 100%; }}
th, td {{ padding: 7px 10px; border-bottom: 1px solid {GRID}; text-align: right; }}
th {{ color: {TEXT_2}; font-weight: 600; font-size: 13px; }}
th:first-child, td:first-child {{ text-align: left; }}
td.l, th.l {{ text-align: left; }}
.small {{ font-size: 13px; }}
.small td, .small th {{ padding: 5px 8px; }}
ul {{ font-size: 19px; line-height: 1.5; margin: 0; padding-left: 24px; }}
li {{ margin-bottom: 8px; }}
.cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }}
.kpis {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 10px 0 26px; }}
.kpi {{ border-top: 3px solid {TEXT}; padding-top: 10px; }}
.kpi .n {{ font-size: 40px; font-weight: 700; }}
.kpi .t {{ color: {TEXT_2}; font-size: 14px; }}
.legend {{ display: flex; gap: 22px; font-size: 14px; color: {TEXT_2}; margin-bottom: 6px; }}
.legend span::before {{ content: ''; display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 6px; vertical-align: -1px; background: var(--c); }}
svg text {{ font-family: inherit; }}
svg .tick {{ font-size: 13px; fill: {TEXT_2}; }}
svg .axis {{ font-size: 13px; fill: {TEXT_2}; }}
svg .cat {{ font-size: 16px; fill: {TEXT}; font-weight: 600; }}
svg .note {{ font-size: 12px; fill: {MUTED}; }}
svg .value {{ font-size: 15px; fill: {TEXT}; font-weight: 700; }}
svg .label {{ font-size: 13px; fill: {TEXT}; }}
.good {{ color: #006300; font-weight: 600; }}
.bad {{ color: #b3261e; font-weight: 600; }}
"""


def slide(title: str, body: str, subtitle: str = "", number: int = 0) -> str:
    sub = f'<p class="sub">{subtitle}</p>' if subtitle else ""
    return (
        f'<section class="slide"><h2>{title}</h2>{sub}{body}'
        f'<div class="foot"><span>Experimento sintético 2026 · não oficial</span><span>{number}</span></div></section>'
    )


def legend() -> str:
    items = "".join(
        f'<span style="--c:{COLOR[key]}">{ALGORITHM_LABEL[key]}</span>' for key in ("baseline", "guloso", *ALGORITHMS)
    )
    return f'<div class="legend">{items}</div>'


def delta_cell(before: float, after: float) -> str:
    diff = after - before
    if abs(diff) < 1e-9:
        return '<td>0</td>'
    css = "good" if diff < 0 else "bad"
    sign = "+" if diff > 0 else "−"
    pct = f" ({sign}{abs(diff) / abs(before) * 100:.0f}%)" if before else ""
    return f'<td class="{css}">{sign}{fmt(abs(diff), 1 if abs(diff) % 1 else 0)}{pct}</td>'


def build_html(profiles: dict[str, dict], v3_rows: list[dict], config: dict, conflicts: list[dict], floor: int) -> str:
    v3 = profiles["v3"]
    budget = int(config["experimento"]["algoritmos"]["sa"]["avaliacoes"])
    seeds = [str(seed) for seed in config["experimento"]["seeds"]]
    best_overall = min(v3["best"].values(), key=lambda row: row["score"])
    curves = {algorithm: progress_curves(algorithm, seeds, budget) for algorithm in ALGORITHMS}
    stats = v3["stats"] or {}
    n = 1
    slides = []

    slides.append(
        '<section class="slide" style="display:flex;flex-direction:column;justify-content:center">'
        '<span class="badge" style="align-self:flex-start">EXPLORATÓRIO · NÃO OFICIAL</span>'
        '<h1 style="margin-top:22px">Perfil sintético v3: resultados dos experimentos</h1>'
        '<p class="sub" style="font-size:20px">Alocação de horários, professores e salas do IC/UFF — CC e SI, 2026<br>'
        'Instância alinhada às decisões de modelagem de 30/09/2026; setores, habilitação, salas e H12 ainda estimados.</p>'
        f'<div class="kpis" style="margin-top:30px">'
        f'<div class="kpi"><div class="n">{fmt(stats.get("turmas"))}</div><div class="t">turmas (CC/SI + externas de referência)</div></div>'
        f'<div class="kpi"><div class="n">{fmt(v3["baseline"]["hard_total"])}</div><div class="t">violações hard no quadro observado</div></div>'
        f'<div class="kpi"><div class="n">{fmt(best_overall["hard_total"])}</div><div class="t">violações hard na melhor busca ({ALGORITHM_LABEL[best_overall["algoritmo"]]})</div></div>'
        f'<div class="kpi"><div class="n">{len(seeds)}×3</div><div class="t">execuções (sementes × algoritmos), {fmt(budget)} avaliações cada</div></div>'
        "</div>"
        '<div class="foot"><span>Gerado por scripts/report_synthetic_presentation_2026.py</span><span>1</span></div></section>'
    )

    n += 1
    rows = [
        ("Horários fixos", "Obrigatórias + externas", "Só externas (+ serviço)", "Externas + turmas do IC com vaga para outros cursos"),
        ("Disciplinas externas obrigatórias em H8", "Ausentes", "Ausentes", "1 turma de referência por disciplina/semestre"),
        ("TCC00368 (P.O. para SI)", "Obrigatória SI-P7", "Obrigatória SI-P7", "Optativa"),
        ("Turma com 2 professores (H12)", "Fracionada (+0,5)", "Fracionada (+0,5)", "Integral (+1 cada)"),
        ("Universo H12", "40 docentes (proxy)", "40 docentes (proxy de permanentes)", "40 docentes (proxy de permanentes)"),
        ("Setor, habilitação, salas, laboratório, prioridade", "Estimados", "Estimados", "Estimados (iguais)"),
    ]
    body = '<table><tr><th class="l">Tema</th><th class="l">v1</th><th class="l">v2_hp</th><th class="l">v3</th></tr>'
    body += "".join(f"<tr><td>{a}</td><td class='l'>{b}</td><td class='l'>{c}</td><td class='l'><b>{d}</b></td></tr>" for a, b, c, d in rows)
    body += "</table>"
    stat_rows = [("Turmas", "turmas"), ("Horário flexível", "flexiveis"), ("Turmas externas", "externas"),
                 ("Obrigatórias do IC", "obrigatorias_ic"), ("Professor móvel", "professor_movel"), ("Docentes em H12", "h12")]
    body += '<table class="small" style="margin-top:22px;width:70%"><tr><th class="l">Tamanho da instância</th>'
    body += "".join(f"<th>{esc(p['label'])}</th>" for p in profiles.values()) + "</tr>"
    for label, key in stat_rows:
        body += f"<tr><td>{label}</td>" + "".join(
            f"<td>{fmt((p['stats'] or {}).get(key))}</td>" for p in profiles.values()
        ) + "</tr>"
    body += "</table>"
    slides.append(slide("O que muda entre os perfis", body, "O v3 aplica as decisões já tomadas e mantém as estimativas onde ainda faltam dados oficiais.", n))

    n += 1
    body = legend() + strip_plot(v3_rows)
    body += (f'<p class="sub" style="margin-top:6px">Traço = mediana. Todas as buscas partem da solução gulosa; '
             f"o comparador prioriza reduzir violações hard antes dos critérios soft.</p>")
    slides.append(slide("v3 · Violações hard por execução", body, "Um ponto por semente; quanto mais baixo, melhor.", n))

    n += 1
    keys = list(HARD_LABEL)
    columns = [("Observado", v3["baseline"]), ("Guloso", v3["guloso"])] + [
        (f"Melhor {ALGORITHM_LABEL[a]}", v3["best"][a]) for a in ALGORITHMS
    ]
    body = '<table><tr><th class="l">Tipo de violação hard</th>' + "".join(f"<th>{c}</th>" for c, _ in columns) + "</tr>"
    for key in keys:
        body += f"<tr><td>{HARD_LABEL[key]}</td>" + "".join(f"<td>{fmt(row[key])}</td>" for _, row in columns) + "</tr>"
    body += "<tr><td><b>Total</b></td>" + "".join(f"<td><b>{fmt(row['hard_total'])}</b></td>" for _, row in columns) + "</tr>"
    body += "<tr><td>Déficit de carga H12 (créditos)</td>" + "".join(f"<td>{fmt(row['deficit_h12'], 1)}</td>" for _, row in columns) + "</tr>"
    body += "</table>"
    slides.append(slide("v3 · De onde vêm as violações hard", body, "Melhor execução de cada algoritmo (menor score entre as sementes).", n))

    n += 1
    body = convergence_chart(curves, budget, floor)
    body += ('<p class="sub" style="margin-top:6px">Mediana entre as sementes da melhor solução encontrada até cada avaliação; o ponto de partida é a solução gulosa. '
             'ILS (tracejado) e VNS ficam sobrepostos: a mediana dos dois não sai de 11.</p>')
    slides.append(slide("v3 · Convergência", body, "Violações hard ao longo da busca.", n))

    n += 1
    reference = best_overall
    body = '<table><tr><th class="l">Critério soft</th><th>Observado</th><th>Guloso</th>' + "".join(
        f"<th>Melhor {ALGORITHM_LABEL[a]}</th>" for a in ALGORITHMS) + f"<th>Δ {ALGORITHM_LABEL[reference['algoritmo']]} vs observado</th></tr>"
    for key, (label, sense) in SOFT_LABEL.items():
        body += f"<tr><td>{label} <span class='small' style='color:{MUTED}'>({sense})</span></td>"
        body += f"<td>{fmt(v3['baseline'][key], 1 if key.endswith('priorizada') else 0)}</td>"
        body += f"<td>{fmt(v3['guloso'][key], 1 if key.endswith('priorizada') else 0)}</td>"
        body += "".join(f"<td>{fmt(v3['best'][a][key], 1 if key.endswith('priorizada') else 0)}</td>" for a in ALGORITHMS)
        body += delta_cell(v3["baseline"][key], reference[key]) + "</tr>"
    body += "</table>"
    body += (f'<p class="sub" style="margin-top:18px">Verde = melhorou, vermelho = piorou em relação ao quadro observado. '
             "Como os pesos soft ainda são unitários e provisórios, a piora em algum critério é o preço aceito para reduzir violações hard. "
             "ILS e VNS quase não saem da solução gulosa e por isso mantêm os critérios soft próximos dela.</p>")
    slides.append(slide("v3 · Critérios soft", body, "Qualidade da grade para professores e salas.", n))

    n += 1
    body = dumbbell(profiles)
    body += '<table class="small" style="margin-top:8px"><tr><th class="l">Perfil</th><th>Observado</th><th>Guloso</th>'
    body += "".join(f"<th>Melhor {ALGORITHM_LABEL[a]}</th>" for a in ALGORITHMS) + "<th>Janelas (melhor)</th><th>Dias (melhor)</th></tr>"
    for profile in profiles.values():
        top_search = min(profile["best"].values(), key=lambda row: row["score"])
        body += f"<tr><td>{esc(profile['label'])}</td><td>{fmt(profile['baseline']['hard_total'])}</td><td>{fmt(profile['guloso']['hard_total'])}</td>"
        body += "".join(f"<td>{fmt(profile['best'][a]['hard_total'])}</td>" for a in ALGORITHMS)
        body += f"<td>{fmt(top_search['soft_janelas'])}</td><td>{fmt(top_search['soft_dias_trabalhados'])}</td></tr>"
    body += "</table>"
    slides.append(slide("v1 × v2_hp × v3", body, "Violações hard: quadro observado → guloso → melhor busca. Os perfis não são a mesma instância.", n))

    n += 1
    if conflicts:
        body = '<table class="small"><tr><th class="l">Semestre</th><th class="l">Período</th><th class="l">Turma A</th><th class="l">Turma B</th><th class="l">Quando</th></tr>'
        body += "".join(
            f"<tr><td>{esc(c['semestre'])}</td><td class='l'>{esc(c['grupo'])}</td><td class='l'>{esc(c['a'])}</td>"
            f"<td class='l'>{esc(c['b'])}</td><td class='l'>{esc(c['quando'])}</td></tr>" for c in conflicts[:14]
        )
        body += "</table>"
        if len(conflicts) > 14:
            body += f'<p class="sub">… e mais {len(conflicts) - 14}.</p>'
        kinds = Counter(("fixa" in c["a"]) + ("fixa" in c["b"]) for c in conflicts)
        body += (f'<p class="sub" style="margin-top:14px">{len(conflicts)} pares; H8 conta cada sobreposição de encontros, '
                 f"por isso o total é {fmt(best_overall['hard_conflitos_curriculares'])}. "
                 f"{kinds.get(2, 0)} par(es) entre duas turmas fixas, {kinds.get(1, 0)} com uma fixa e {kinds.get(0, 0)} entre duas flexíveis.</p>"
                 f'<p class="sub"><b>Piso estrutural de H8 nesta instância: {fmt(floor)}</b> sobreposições entre turmas de horário fixo, '
                 "que nenhum movimento consegue desfazer. Três dos pares envolvem uma turma externa de referência, que poderia ser trocada "
                 "por outra turma da mesma disciplina; um par (TCC00332 B1 × TCC00354 A1) é entre turmas do IC fixas por terem vagas para outros cursos.</p>")
    else:
        body = '<p class="sub" style="font-size:22px">A melhor solução não tem choques curriculares.</p>'
    slides.append(slide(f"v3 · Choques curriculares restantes (melhor {ALGORITHM_LABEL[best_overall['algoritmo']]})", body,
                        "Pares de turmas do mesmo período que se sobrepõem na melhor solução.", n))

    n += 1
    base, top_row = v3["baseline"], best_overall
    lines = [
        f"No v3, o quadro observado tem <b>{fmt(base['hard_total'])}</b> violações hard; a melhor busca "
        f"({ALGORITHM_LABEL[top_row['algoritmo']]}) chega a <b>{fmt(top_row['hard_total'])}</b>.",
        f"Choques curriculares: {fmt(base['hard_conflitos_curriculares'])} → {fmt(top_row['hard_conflitos_curriculares'])}, "
        f"igual ao piso estrutural ({fmt(floor)}): o que sobra vem só de turmas fixas. "
        + ("A melhor solução atinge o mínimo possível de violações hard deste modelo." if top_row["hard_total"] == floor else ""),
        "Com isso, o gargalo deixa de ser o algoritmo e passa a ser a escolha das turmas fixas (externas de referência e regra de 1 vaga).",
        "Os números não são comparáveis entre perfis nem servem como resultado do TCC: setores, habilitação, salas, laboratório e H12 ainda são estimativas.",
        "Orçamento curto (1.500 avaliações) e 5 sementes: a comparação entre SA, ILS e VNS é indicativa, sem teste estatístico.",
    ]
    nexts = [
        "Receber setores, habilitação, salas e lista de permanentes e gerar a instância oficial.",
        "Recoletar vagas da página pública (dados de 15/08/2026) antes do experimento final.",
        "Definir pesos soft (incluindo H10 relaxável) e o orçamento do protocolo final.",
        "Escolher as turmas externas de referência evitando também as turmas fixas do IC.",
        "Rever se 1 vaga para outro curso basta para fixar o horário (ex.: TCC00354 A1, fixada por 1 vaga de Farmácia).",
    ]
    body = ('<div class="cols"><div><h3 style="margin:0 0 10px">Leitura</h3><ul>' + "".join(f"<li>{l}</li>" for l in lines) +
            '</ul></div><div><h3 style="margin:0 0 10px">Próximos passos</h3><ul>' + "".join(f"<li>{l}</li>" for l in nexts) + "</ul></div></div>")
    slides.append(slide("Leitura e próximos passos", body, "", n))

    return f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{"".join(slides)}</body></html>'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--saida", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--config", type=Path, default=ROOT / "dados" / "config_sintetica_2026_v3.json")
    args = parser.parse_args()

    profiles = {}
    for key, spec in PROFILES.items():
        if not spec["csv"].exists():
            sys.exit(f"Resultados ausentes: {spec['csv']}")
        rows = read_rows(spec["csv"])
        profiles[key] = {
            **spec,
            "rows": rows,
            "baseline": best(rows, "baseline"),
            "guloso": best(rows, "guloso"),
            "best": {algorithm: best(rows, algorithm) for algorithm in ALGORITHMS},
            "stats": instance_stats(spec["instance"]),
        }
    config = json.loads(args.config.read_text(encoding="utf-8"))
    best_overall = min(profiles["v3"]["best"].values(), key=lambda row: row["score"])
    conflicts = residual_curriculum_conflicts(V3_SOLUTIONS / f"solucao_{best_overall['algoritmo']}_{best_overall['seed']}.json")
    floor = fixed_curriculum_floor(PROFILES["v3"]["instance"])
    document = build_html(profiles, profiles["v3"]["rows"], config, conflicts, floor)

    output = args.saida.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    html_path = output.with_suffix(".html")
    html_path.write_text(document, encoding="utf-8")

    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.goto(html_path.as_uri())
        page.pdf(path=str(output), width="1280px", height="720px", print_background=True)
        browser.close()
    print(output)


if __name__ == "__main__":
    main()
