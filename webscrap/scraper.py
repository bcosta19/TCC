"""
Scraper do Quadro de Horários UFF
Coleta turmas por semestre para Ciência da Computação em Niterói (currículo 31.02.003)
e conta quantas vezes cada professor ministrou cada disciplina.

Os nomes dos professores vêm do atributo title="Professor(es): NOME..."
da listagem principal — são os nomes abreviados/registrados no sistema UFF.
"""

import json
import re
import time
from pathlib import Path

import requests
import pandas as pd
from bs4 import BeautifulSoup, Tag
from playwright.sync_api import sync_playwright

BASE_URL     = "https://app.uff.br/graduacao/quadrodehorarios"
LOGIN_URL    = f"{BASE_URL}/sessions/new"
COOKIES_FILE = Path("uff_cookies.json")

SEARCH_PARAMS = {
    "utf8": "✓",
    "q[disciplina_nome_or_disciplina_codigo_cont]": "",
    "q[disciplina_cod_departamento_eq]": "",
    "q[idturno_eq]": "",
    "docente": "",
    "q[idlocalidade_eq]": "1",                               # Niterói
    "q[vagas_turma_curso_idcurso_eq]": "31",                # Ciência da Computação
    "q[disciplina_disciplinas_curriculos_idcurriculo_eq]": "3092",  # 31.02.003
    "q[curso_ferias_eq]": "false",
    "q[idturmamodalidade_eq]": "",
}

SEMESTRES = {
    "20231": "2023/1",
    "20232": "2023/2",
    "20241": "2024/1",
    "20242": "2024/2",
    "20251": "2025/1",
    "20252": "2025/2",
}

HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


# ── 1. LOGIN / COOKIES ────────────────────────────────────────────────────────

def do_login() -> dict:
    """Abre browser para login manual e salva os cookies."""
    print("Abrindo browser para login no idUFF...")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=100)
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(LOGIN_URL)
        print("Aguardando login (máx. 3 minutos)...")
        try:
            page.wait_for_url(f"{BASE_URL}/**", timeout=180_000, wait_until="networkidle")
        except Exception:
            pass
        cookies = ctx.cookies()
        browser.close()

    cookie_dict = {c.get("name", ""): c.get("value", "") for c in cookies if c.get("name")}
    COOKIES_FILE.write_text(json.dumps(cookie_dict), encoding="utf-8")
    print(f"Login OK — {len(cookie_dict)} cookies salvos em {COOKIES_FILE}")
    return cookie_dict


def load_or_login() -> dict:
    """Carrega cookies salvos se válidos; caso contrário abre o browser."""
    if COOKIES_FILE.exists():
        cookie_dict = json.loads(COOKIES_FILE.read_text(encoding="utf-8"))
        s = requests.Session()
        s.cookies.update(cookie_dict)
        r = s.get(f"{BASE_URL}/", headers=HTTP_HEADERS, timeout=15)
        # Sessão expirada se redirecionar para login
        if any(x in r.url for x in ("sessions/new", "sign_in", "openid-connect")):
            print("Sessão expirada. Abrindo browser para novo login...")
            return do_login()
        # Sessão expirada se "Login" ainda aparecer no conteúdo (sem nome do usuário)
        if 'href="/graduacao/quadrodehorarios/sessions/new">Login' in r.text:
            print("Sessão expirada. Abrindo browser para novo login...")
            return do_login()
        print(f"Sessão carregada de {COOKIES_FILE} ({len(cookie_dict)} cookies).")
        return cookie_dict
    return do_login()


# ── 2. PARSE DA LISTAGEM ──────────────────────────────────────────────────────

def extract_professors(title: str) -> list[str]:
    """
    Extrai nomes dos professores do atributo title da célula disciplina-nome.
    Formato: 'Professor(es): NOME1, NOME2<br/><br/>Curso(s) com vagas: ...'
    """
    if not title or "Professor" not in title:
        return ["(não informado)"]
    # Pega tudo antes do primeiro <br> (qualquer variante)
    part = re.split(r"<br\s*/?>", title, maxsplit=1)[0]
    part = re.sub(r"Professor(?:es)?(?:\(es\))?[:\s]+", "", part, flags=re.I).strip()
    nomes = [n.strip() for n in part.split(",") if n.strip()]
    return nomes if nomes else ["(não informado)"]


def parse_table(html: str, semestre_label: str) -> list[dict]:
    """
    Extrai todas as turmas da tabela de resultados.
    Retorna turma_url para busca posterior do nome completo do professor.
    O nome abreviado do tooltip fica em 'docente_tooltip' como fallback.
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not isinstance(table, Tag):
        print(f"  [!] Nenhuma tabela em {semestre_label}")
        return []

    tbody = table.find("tbody")
    if not isinstance(tbody, Tag):
        return []

    records = []
    for row in tbody.find_all("tr"):
        if not isinstance(row, Tag):
            continue
        cells = row.find_all("td")
        if len(cells) < 3:
            continue

        # URL da página de detalhe da turma (para buscar nome completo)
        link_tag = cells[0].find("a", href=True)
        turma_url = link_tag["href"] if link_tag else ""

        codigo = cells[0].get_text(strip=True)
        turma  = cells[2].get_text(strip=True)

        nome_cell = row.find("td", class_="disciplina-nome")
        if isinstance(nome_cell, Tag):
            disciplina = nome_cell.get_text(strip=True)
            title_val  = nome_cell.get("title")
            title_str  = title_val if isinstance(title_val, str) else ""
            tooltip_names = extract_professors(title_str)
        else:
            disciplina    = cells[1].get_text(strip=True)
            tooltip_names = ["(não informado)"]

        records.append({
            "semestre":       semestre_label,
            "codigo":         codigo,
            "disciplina":     disciplina,
            "turma":          turma,
            "turma_url":      turma_url,
            "docente_tooltip": ", ".join(tooltip_names),
        })

    return records


# ── 3. NOME COMPLETO VIA PÁGINA DE DETALHE ────────────────────────────────────

SESSION_EXPIRED_MARKER = "__SESSION_EXPIRED__"


def is_session_expired(html: str) -> bool:
    return 'href="/graduacao/quadrodehorarios/sessions/new">Login' in html


def fetch_full_names(turma_url: str, session: requests.Session) -> list[str]:
    """
    Busca nomes completos dos professores na página de detalhe da turma.
    Tabela alvo: <table id="tabela-alteracao-professores-turma">
    Retorna [SESSION_EXPIRED_MARKER] se a sessão tiver expirado.
    Retorna [] se não encontrar a tabela.
    """
    if not turma_url:
        return []
    url = f"https://app.uff.br{turma_url}" if turma_url.startswith("/") else turma_url
    try:
        r = session.get(url, headers=HTTP_HEADERS, timeout=20)
        r.raise_for_status()
    except Exception:
        return []

    if is_session_expired(r.text):
        return [SESSION_EXPIRED_MARKER]

    soup = BeautifulSoup(r.text, "html.parser")
    tabela = soup.find("table", id="tabela-alteracao-professores-turma")
    if not isinstance(tabela, Tag):
        return []

    tbody = tabela.find("tbody")
    if not isinstance(tbody, Tag):
        return []

    nomes = []
    for row in tbody.find_all("tr"):
        if not isinstance(row, Tag):
            continue
        cells = row.find_all("td")
        if cells:
            nome = cells[0].get_text(strip=True)
            if nome:
                nomes.append(nome)
    return nomes


def enrich_with_full_names(records: list[dict], session: requests.Session) -> list[dict]:
    """
    Para cada turma_url única, busca os nomes completos dos professores.
    Expande registros: um por (turma, professor).
    Se a sessão expirar (timeout de 20 min), usa o nome do tooltip como fallback.
    """
    unique_urls = {r["turma_url"] for r in records if r["turma_url"]}
    total = len(unique_urls)
    print(f"\nBuscando nomes completos em {total} páginas de turma...")
    print(f"(estimativa: ~{int(total * 0.3 / 60) + 1} min — sessão expira em 20 min)")

    url_to_names: dict[str, list[str]] = {}
    session_ok = True
    for i, url in enumerate(unique_urls, 1):
        if i % 25 == 0 or i == total:
            print(f"  {i}/{total}")
        if not session_ok:
            url_to_names[url] = []
            continue
        nomes = fetch_full_names(url, session)
        if nomes == [SESSION_EXPIRED_MARKER]:
            print(f"\n  [AVISO] Sessão expirou na turma {i}/{total}.")
            print("  Usando nomes do tooltip para as turmas restantes.")
            session_ok = False
            url_to_names[url] = []
        else:
            url_to_names[url] = nomes
        time.sleep(0.3)

    enriched = []
    for rec in records:
        nomes = url_to_names.get(rec["turma_url"], [])
        if not nomes:
            nomes = [n.strip() for n in rec["docente_tooltip"].split(",") if n.strip()]
        for nome in nomes:
            enriched.append({
                "semestre":   rec["semestre"],
                "codigo":     rec["codigo"],
                "disciplina": rec["disciplina"],
                "turma":      rec["turma"],
                "turma_url":  rec["turma_url"],
                "docente":    nome,
            })
    return enriched


# ── 3. BUSCA POR SEMESTRE ─────────────────────────────────────────────────────

def last_page_number(soup: BeautifulSoup) -> int:
    """Extrai o número da última página da paginação a partir dos hrefs."""
    pagination = soup.find(class_="pagination")
    if not isinstance(pagination, Tag):
        return 1
    max_page = 1
    for a in pagination.find_all("a", href=True):
        m = re.search(r"[?&]page=(\d+)", a["href"])
        if m:
            max_page = max(max_page, int(m.group(1)))
    return max_page


def fetch_semester(code: str, label: str, session: requests.Session) -> list[dict]:
    params = {**SEARCH_PARAMS, "q[anosemestre_eq]": code}
    resp = session.get(f"{BASE_URL}/", params=params, headers=HTTP_HEADERS, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    records = parse_table(resp.text, label)
    total_pages = last_page_number(soup)

    for p in range(2, total_pages + 1):
        time.sleep(0.5)
        r = session.get(f"{BASE_URL}/", params={**params, "page": p},
                        headers=HTTP_HEADERS, timeout=30)
        r.raise_for_status()
        records.extend(parse_table(r.text, label))

    print(f"  {label}: {len(records)} entradas em {total_pages} página(s)")
    return records


# ── 4. ANÁLISE ────────────────────────────────────────────────────────────────

def analyze(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Gera tabelas de contagem por (professor, disciplina) e por professor."""
    por_disciplina = (
        df.groupby(["docente", "codigo", "disciplina"])
        .agg(
            total_turmas=("turma", "count"),
            semestres=("semestre", lambda s: ", ".join(sorted(s.unique()))),
        )
        .reset_index()
        .sort_values(["docente", "total_turmas"], ascending=[True, False])
    )

    por_professor = (
        df.groupby("docente")
        .agg(
            total_turmas=("turma", "count"),
            disciplinas_distintas=("codigo", "nunique"),
            semestres=("semestre", lambda s: ", ".join(sorted(s.unique()))),
        )
        .reset_index()
        .sort_values("total_turmas", ascending=False)
    )

    return por_disciplina, por_professor


# ── 5. MAIN ───────────────────────────────────────────────────────────────────

def main():
    cookies = load_or_login()

    session = requests.Session()
    session.cookies.update(cookies)

    print("\nBuscando semestres...")
    all_records: list[dict] = []
    for code, label in SEMESTRES.items():
        try:
            all_records.extend(fetch_semester(code, label, session))
        except Exception as e:
            print(f"  [ERRO] {label}: {e}")
        time.sleep(1)

    if not all_records:
        print("Nenhum dado coletado. Verifique se o login foi bem-sucedido.")
        return

    # Enriquece com nomes completos via páginas de detalhe
    all_records = enrich_with_full_names(all_records, session)

    df = pd.DataFrame(all_records)
    sem_professor = (df["docente"] == "(não informado)").sum()
    if sem_professor == len(df):
        print("\n[AVISO] Todos sem professor — sessão pode ter expirado.")
        print("Delete uff_cookies.json e rode novamente.")
        return

    print(f"\n{sem_professor} turmas sem professor de {len(df)} total.")

    df.to_csv("turmas_raw.csv", index=False, encoding="utf-8-sig")
    print(f"Dados brutos: turmas_raw.csv ({len(df)} linhas)")

    df_por_disc, df_por_prof = analyze(df)

    with pd.ExcelWriter("preferencias_professores.xlsx", engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Dados Brutos", index=False)
        df_por_disc.to_excel(writer, sheet_name="Por Disciplina", index=False)
        df_por_prof.to_excel(writer, sheet_name="Totais por Professor", index=False)

    print("Análise salva: preferencias_professores.xlsx")
    print("\n=== TOP 15 professores por nº de turmas ===")
    print(df_por_prof.head(15).to_string(index=False))
    print("\n[NOTA] Nomes são os registrados no sistema UFF (podem ser abreviados).")
    print("       Professores com mesmo nome abreviado são contados juntos.")


if __name__ == "__main__":
    main()
