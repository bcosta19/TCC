"""
Enriquece turmas_raw.csv com HORÁRIO e VAGAS.

Para cada turma_url já presente no CSV, busca a página de detalhe e extrai
horário (dia × faixa), padrão de dias e vagas — reaproveitando os parsers de
scraper.py. NÃO refaz a resolução de nomes de professores (que já está no CSV);
só acrescenta as colunas: horario, padrao_dias, vagas, inscritos.

Uso:
    python enrich_horarios.py            # processa todas as turmas e salva
    python enrich_horarios.py --limit 8  # testa em 8 turmas, NÃO sobrescreve

O modo --limit serve para validar o parser em poucas páginas antes do run
completo (a sessão idUFF expira em ~20 min).
"""

import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests

from scraper import (
    load_or_login,
    fetch_turma_details,
    SESSION_EXPIRED_MARKER,
)

CSV = "turmas_raw.csv"
WORKERS = 8  # nº de requisições concorrentes (tarefa I/O-bound)

# requests.Session não é thread-safe para compartilhar entre threads;
# cada thread cria a sua, todas com os mesmos cookies de sessão.
_local = threading.local()


def _session(cookies: dict) -> requests.Session:
    s = getattr(_local, "session", None)
    if s is None:
        s = requests.Session()
        s.cookies.update(cookies)
        _local.session = s
    return s


def _fetch(url: str, cookies: dict):
    return url, fetch_turma_details(url, _session(cookies))


def main():
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    df = pd.read_csv(CSV, encoding="utf-8-sig")
    urls = [u for u in df["turma_url"].dropna().unique().tolist() if u]
    if limit:
        urls = urls[:limit]
    total = len(urls)

    cookies = load_or_login()

    print(f"\nBuscando horário/vagas em {total} turmas únicas "
          f"({WORKERS} em paralelo)...", flush=True)

    cache: dict[str, dict] = {}
    expirou = 0
    feito = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futuros = [executor.submit(_fetch, u, cookies) for u in urls]
        for fut in as_completed(futuros):
            url, det = fut.result()
            feito += 1
            if det == SESSION_EXPIRED_MARKER:
                expirou += 1
                cache[url] = {}
            else:
                cache[url] = det if isinstance(det, dict) else {}
            if feito % 50 == 0 or feito == total:
                print(f"  {feito}/{total}", flush=True)
    if expirou:
        print(f"\n[AVISO] Sessão expirou em {expirou} turma(s) — "
              "rode de novo para completá-las.")

    def col(campo):
        return df["turma_url"].map(lambda u: cache.get(u, {}).get(campo))

    df["horario"]     = col("horario")
    df["padrao_dias"] = col("padrao_dias")
    df["vagas"]       = pd.to_numeric(col("vagas"), errors="coerce").astype("Int64")
    df["inscritos"]   = pd.to_numeric(col("inscritos"), errors="coerce").astype("Int64")

    # ── Modo teste: mostra a amostra e NÃO sobrescreve o CSV ──
    if limit:
        sub = df[df["turma_url"].isin(urls)].drop_duplicates("turma_url")
        print("\n=== AMOSTRA (modo --limit; CSV NÃO foi sobrescrito) ===")
        print(sub[["codigo", "disciplina", "turma",
                   "padrao_dias", "horario", "vagas", "inscritos"]].to_string(index=False))
        return

    df.to_csv(CSV, index=False, encoding="utf-8-sig")
    print(f"\nOK: {CSV} atualizado (+colunas horario, padrao_dias, vagas, inscritos).")

    # ── Tabulação dos padrões de dias (1 linha por turma) ──
    turmas = df.dropna(subset=["padrao_dias"]).drop_duplicates("turma_url")
    turmas = turmas[turmas["padrao_dias"] != ""]
    print(f"\n=== Distribuição de PADRÃO DE DIAS ({len(turmas)} turmas com horário) ===")
    contagem = turmas["padrao_dias"].value_counts()
    for padrao, n in contagem.items():
        print(f"  {padrao:<20} {n:>4}  ({n / len(turmas) * 100:4.1f}%)")

    # mesma tabulação, restrita ao IC/Computação (códigos TCC*)
    ic = turmas[turmas["codigo"].astype(str).str.startswith("TCC")]
    if len(ic):
        print(f"\n=== Só IC/Computação (TCC*) — {len(ic)} turmas ===")
        for padrao, n in ic["padrao_dias"].value_counts().items():
            print(f"  {padrao:<20} {n:>4}  ({n / len(ic) * 100:4.1f}%)")

    sem_horario = df.drop_duplicates("turma_url")
    sem_horario = sem_horario[sem_horario["padrao_dias"].fillna("") == ""]
    if len(sem_horario):
        print(f"\n[nota] {len(sem_horario)} turmas sem horário cadastrado na página.")


if __name__ == "__main__":
    main()
