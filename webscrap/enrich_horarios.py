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
import time

import pandas as pd
import requests

from scraper import (
    load_or_login,
    fetch_turma_details,
    SESSION_EXPIRED_MARKER,
)

CSV = "turmas_raw.csv"


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
    session = requests.Session()
    session.cookies.update(cookies)

    print(f"\nBuscando horário/vagas em {total} turmas únicas...")
    print(f"(estimativa: ~{int(total * 0.3 / 60) + 1} min — sessão expira em 20 min)")

    cache: dict[str, dict] = {}
    for i, url in enumerate(urls, 1):
        if i % 25 == 0 or i == total:
            print(f"  {i}/{total}")
        det = fetch_turma_details(url, session)
        if det == SESSION_EXPIRED_MARKER:
            print(f"\n[ERRO] Sessão expirou na turma {i}/{total}. "
                  "Delete uff_cookies.json e rode de novo.")
            break
        cache[url] = det if isinstance(det, dict) else {}
        time.sleep(0.3)

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
