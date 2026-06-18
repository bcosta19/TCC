"""
Probe de uma página de turma do Quadro de Horários UFF.

Objetivo: inspecionar o HTML da página de detalhe da turma para descobrir
ONDE e EM QUE FORMATO aparecem o horário e as vagas, antes de escrever o
parser definitivo em scraper.py.

Uso:
    python probe_turma.py [turma_url]

Sem argumento, usa uma turma de Análise e Projeto de Algoritmos (TCC00285)
como amostra. Reaproveita o login/cookies do scraper.py (abre o browser se
a sessão tiver expirado). Salva o HTML cru em _probe_turma.html.
"""

import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Tag

from scraper import load_or_login, HTTP_HEADERS

# Amostra padrão: TCC00285 ANÁLISE E PROJETO DE ALGORITMOS, turma A1 (2023/1)
DEFAULT_URL = "/graduacao/quadrodehorarios/turmas/100000371167"

KEYWORDS = [
    "horár", "horar", "vaga", "local", "sala", "turno",
    "segunda", "terça", "terca", "quarta", "quinta", "sexta",
]


def preview(text: str, n: int = 160) -> str:
    return " ".join(text.split())[:n]


def class_str(el: Tag) -> str:
    cls = el.get("class")
    if isinstance(cls, list):
        return " ".join(cls)
    return cls or ""


def main():
    turma_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    url = f"https://app.uff.br{turma_url}" if turma_url.startswith("/") else turma_url

    cookies = load_or_login()
    session = requests.Session()
    session.cookies.update(cookies)

    print(f"\nBuscando: {url}")
    r = session.get(url, headers=HTTP_HEADERS, timeout=20)
    r.raise_for_status()

    out = Path("_probe_turma.html")
    out.write_text(r.text, encoding="utf-8")
    print(f"HTML cru salvo em {out} ({len(r.text)} bytes)\n")

    soup = BeautifulSoup(r.text, "html.parser")

    # 1. Todas as tabelas: id, classe e prévia
    print("=" * 70)
    print("TABELAS NA PÁGINA")
    print("=" * 70)
    for i, t in enumerate(soup.find_all("table"), 1):
        if not isinstance(t, Tag):
            continue
        tid = t.get("id", "")
        print(f"\n[tabela {i}] id={tid!r} class={class_str(t)!r}")
        print(f"  prévia: {preview(t.get_text(' ', strip=True), 220)}")

    # 2. Elementos que contêm palavras-chave de horário/vagas
    print("\n" + "=" * 70)
    print("ELEMENTOS COM PALAVRAS-CHAVE (horário, vagas, dias da semana...)")
    print("=" * 70)
    seen = set()
    for el in soup.find_all(True):
        if not isinstance(el, Tag):
            continue
        # só folhas / blocos pequenos, pra não imprimir o body inteiro
        txt = el.get_text(" ", strip=True)
        if not txt or len(txt) > 200:
            continue
        low = txt.lower()
        if any(k in low for k in KEYWORDS):
            key = (el.name, txt)
            if key in seen:
                continue
            seen.add(key)
            print(f"  <{el.name} class={class_str(el)!r}> {preview(txt)}")

    print("\n[OK] Veja também _probe_turma.html para o HTML completo.")


if __name__ == "__main__":
    main()
