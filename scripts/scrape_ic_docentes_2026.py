"""Coleta nome e cargo dos docentes listados na página pública do IC/UFF.

Fonte: https://www.ic.uff.br/docentes/ e a página individual de cada docente
(``/blog/pessoas/<slug>/``), em que o cargo aparece logo abaixo do nome
(ex.: "Professor Adjunto"). Saída: ``dados/brutos/docentes_ic_2026.csv``, com
a data da coleta. Usada para o universo de H12 (só permanentes), decidido em
30/09/2026.

As requisições são sequenciais, com pausa entre elas.
"""

from __future__ import annotations

import argparse
import csv
import html
import re
import time
from datetime import date
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dados" / "brutos" / "docentes_ic_2026.csv"
LISTING = "https://www.ic.uff.br/docentes/"
PERSON_RE = re.compile(r'href="(https://www\.ic\.uff\.br/blog/pessoas/[a-z0-9-]+/)"')
HEADERS = {"User-Agent": "Mozilla/5.0 (TCC IC/UFF; coleta de cargos docentes)"}


def text_lines(page: str) -> list[str]:
    page = re.sub(r"(?is)<(script|style).*?</\1>", " ", page)
    text = html.unescape(re.sub(r"(?s)<[^>]+>", "\n", page))
    return [line.strip() for line in text.splitlines() if line.strip()]


def person_urls(listing: str) -> list[str]:
    return list(dict.fromkeys(PERSON_RE.findall(listing)))


def parse_person(page: str) -> tuple[str, str]:
    """Nome (do título da página) e cargo (linha seguinte ao nome no corpo)."""
    lines = text_lines(page)
    name = lines[0].split("–")[0].strip() if lines else ""
    for index, line in enumerate(lines[1:], start=1):
        if line == name and index + 1 < len(lines):
            return name, lines[index + 1]
    return name, ""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pausa", type=float, default=1.0, help="Segundos entre requisições")
    args = parser.parse_args()
    session = requests.Session()
    session.headers.update(HEADERS)
    listing = session.get(LISTING, timeout=30)
    listing.raise_for_status()
    rows = []
    for url in person_urls(listing.text):
        time.sleep(args.pausa)
        response = session.get(url, timeout=30)
        response.raise_for_status()
        name, cargo = parse_person(response.text)
        rows.append({"nome": name, "cargo": cargo, "url": url, "coletado_em": date.today().isoformat()})
        print(f"{cargo or '(sem cargo)':<28} {name}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["nome", "cargo", "url", "coletado_em"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"{OUTPUT}: {len(rows)} docentes")


if __name__ == "__main__":
    main()
