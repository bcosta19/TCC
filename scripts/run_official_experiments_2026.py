"""Executa o protocolo experimental na instância oficial de 2026.

Configuração: ``dados/config_oficial_2026.json``. Todos os algoritmos partem
da mesma solução gulosa (calculada uma vez) e têm o mesmo orçamento de
avaliações. Saída em ``dados/processados/experimento_oficial_2026/<rótulo>/``:
``resultados.csv`` (uma linha por execução), ``execucoes.json`` (metadados e
progresso) e ``resumo.md`` (medianas, distância aos pisos e Wilcoxon pareado
exato contra o ``sa2``).

Exemplos:

    # verificação curta nas sementes de calibração
    python scripts/run_official_experiments_2026.py --sementes calibracao \\
        --avaliacoes 20000 --algoritmos sa2,ils,vns,sa --rotulo verificacao_inicial

    # experimento completo nas sementes de avaliação
    python scripts/run_official_experiments_2026.py --sementes avaliacao --rotulo e3_completo
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.report_synthetic_presentation_2026 import fixed_curriculum_floor  # noqa: E402
from src.solve.direct_objective import evaluate  # noqa: E402
from src.solve.integrated import ALGORITHMS, greedy_improve, objective_key  # noqa: E402

CONFIG = ROOT / "dados" / "config_oficial_2026.json"
OUTPUT = ROOT / "dados" / "processados" / "experimento_oficial_2026"
SOFT_TERMS = ("dias_trabalhados", "janelas", "desperdicio_capacidade", "rodizio_semestre", "preferencia_priorizada")


def row_from_result(algorithm: str, seed: int, result: dict, seconds: float, evaluations: int) -> dict:
    guidance = result.get("guidance") or {}
    row = {
        "algoritmo": algorithm,
        "semente": seed,
        "hard": result["hard_violations"],
        "conflitos_curriculares": result["hard"].get("conflitos_curriculares"),
        "conflitos_sala": result["hard"].get("conflitos_sala"),
        "conflitos_professor": result["hard"].get("conflitos_professor"),
        "deficit_carga_anual": guidance.get("deficit_carga_anual"),
        "excesso_capacidade": guidance.get("excesso_capacidade"),
        "soft_total": round(float(result.get("soft_total", 0.0)), 6),
        "avaliacoes": evaluations,
        "segundos": round(seconds, 1),
    }
    row.update({term: result["soft"].get(term) for term in SOFT_TERMS})
    return row


def run_one(task: tuple[str, int, dict, dict]) -> tuple[dict, dict]:
    algorithm, seed, settings, start = task
    began = time.time()
    search = ALGORITHMS[algorithm](start, seed, settings)
    seconds = time.time() - began
    metadata = {key: value for key, value in search.metadata.items()}
    return row_from_result(algorithm, seed, search.evaluation, seconds, metadata.get("evaluations", 0)), metadata


def wilcoxon_exact(differences: list[float]) -> tuple[float, float]:
    """Wilcoxon pareado bilateral exato: (W+, p). Diferenças nulas são descartadas."""
    values = [d for d in differences if abs(d) > 1e-12]
    n = len(values)
    if n == 0:
        return 0.0, 1.0
    order = sorted(range(n), key=lambda i: abs(values[i]))
    ranks = [0.0] * n
    position = 0
    while position < n:
        end = position
        while end + 1 < n and abs(abs(values[order[end + 1]]) - abs(values[order[position]])) < 1e-12:
            end += 1
        for k in range(position, end + 1):
            ranks[order[k]] = (position + end) / 2 + 1
        position = end + 1
    w_plus = sum(rank for rank, value in zip(ranks, values) if value > 0)
    total = sum(ranks)
    observed = min(w_plus, total - w_plus)
    extreme = 0
    for signs in itertools.product((0, 1), repeat=n):
        w = sum(rank for rank, sign in zip(ranks, signs) if sign)
        if min(w, total - w) <= observed + 1e-9:
            extreme += 1
    return w_plus, extreme / 2 ** n


def summarize(rows: list[dict], floors: dict, baseline: dict, start: dict, reference: str = "sa2") -> str:
    by_algorithm: dict[str, list[dict]] = {}
    for row in rows:
        by_algorithm.setdefault(row["algoritmo"], []).append(row)
    lines = [
        "| Algoritmo | Execuções | Hard (mediana) | Acima do piso | Déficit H12 | Excesso H10 | Soft total (mediana) | Segundos |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for name, items in sorted(by_algorithm.items()):
        med = lambda key: statistics.median(float(item[key]) for item in items)
        lines.append(
            f"| {name} | {len(items)} | {med('hard'):g} | {med('hard') - floors['hard']:g} | "
            f"{med('deficit_carga_anual'):g} (piso {floors['deficit_carga_anual']}) | {med('excesso_capacidade'):g} | "
            f"{med('soft_total'):.3f} | {med('segundos'):.0f} |"
        )
    lines += [
        "",
        f"Horário real: hard {baseline['hard_violations']}, déficit {baseline['guidance']['deficit_carga_anual']:g}, "
        f"soft {baseline['soft_total']:.3f}. Partida gulosa: hard {start['hard_violations']}, "
        f"déficit {start['guidance']['deficit_carga_anual']:g}, soft {start['soft_total']:.3f}.",
        "",
    ]
    if reference in by_algorithm:
        lines += [f"Comparação pareada por semente contra `{reference}` (lexicográfica e Wilcoxon exato por nível):", ""]
        ref = {item["semente"]: item for item in by_algorithm[reference]}
        for name, items in sorted(by_algorithm.items()):
            if name == reference:
                continue
            pairs = [(ref[item["semente"]], item) for item in items if item["semente"] in ref]
            if not pairs:
                continue
            key = lambda row: tuple(float(row[k]) for k in ("hard", "deficit_carga_anual", "excesso_capacidade", "soft_total"))
            wins = sum(1 for a, b in pairs if key(a) < key(b))
            losses = sum(1 for a, b in pairs if key(a) > key(b))
            parts = []
            for level in ("hard", "deficit_carga_anual", "soft_total"):
                _, p = wilcoxon_exact([float(b[level]) - float(a[level]) for a, b in pairs])
                parts.append(f"{level} p={p:.3f}")
            lines.append(
                f"- `{name}`: `{reference}` melhor em {wins}, pior em {losses}, empate em {len(pairs) - wins - losses} "
                f"de {len(pairs)}; " + ", ".join(parts)
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sementes", choices=["calibracao", "avaliacao"], default="avaliacao")
    parser.add_argument("--algoritmos", help="Lista separada por vírgula (padrão: os do protocolo)")
    parser.add_argument("--avaliacoes", type=int, help="Sobrescreve o orçamento (verificações curtas)")
    parser.add_argument("--rotulo", required=True)
    parser.add_argument("--processos", type=int, default=6)
    parser.add_argument("--resumir", action="store_true", help="Só refaz o resumo.md a partir do resultados.csv existente")
    args = parser.parse_args()

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    instance_path = ROOT / config["instancia"]
    payload = json.loads(instance_path.read_text(encoding="utf-8"))
    if not payload.get("pronta_para_experimento"):
        sys.exit("Instância oficial não está pronta para experimento.")
    # Pisos estruturais lidos da própria instância: sobreposições H8 entre turmas
    # fixas e cobertura máxima de H12 pelo matching.
    floors = {
        "hard": fixed_curriculum_floor(instance_path),
        "deficit_carga_anual": (payload.get("h12_cobertura") or {}).get("piso_deficit", 0),
    }
    out = OUTPUT / args.rotulo
    if args.resumir:
        with (out / "resultados.csv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        start, _ = greedy_improve(payload, max_candidates=int(config["maximo_candidatos_guloso"]))
        summary = summarize(rows, floors, evaluate(payload), evaluate(start))
        (out / "resumo.md").write_text(f"# Experimento oficial 2026 — {args.rotulo}\n\n{summary}", encoding="utf-8")
        print(summary)
        return
    settings_by_name = {**config.get("referencias", {}), **config["algoritmos"]}
    names = args.algoritmos.split(",") if args.algoritmos else list(config["algoritmos"])
    seeds = config["sementes"][args.sementes]

    baseline = evaluate(payload)
    start, greedy_metadata = greedy_improve(payload, max_candidates=int(config["maximo_candidatos_guloso"]))
    start_result = evaluate(start)
    tasks = []
    for name in names:
        settings = dict(settings_by_name[name])
        if args.avaliacoes:
            settings["avaliacoes"] = args.avaliacoes
        tasks += [(name, seed, settings, start) for seed in seeds]

    rows, runs = [], []
    with ProcessPoolExecutor(max_workers=args.processos) as executor:
        futures = [executor.submit(run_one, task) for task in tasks]
        for future in as_completed(futures):
            row, metadata = future.result()
            rows.append(row)
            runs.append(metadata)
            print(f"{row['algoritmo']:>4}/{row['semente']:<5} hard={row['hard']} déficit={row['deficit_carga_anual']} "
                  f"excesso={row['excesso_capacidade']} soft={row['soft_total']:.3f} ({row['segundos']:.0f}s)", flush=True)
    rows.sort(key=lambda row: (row["algoritmo"], row["semente"]))

    out.mkdir(parents=True, exist_ok=True)
    with (out / "resultados.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (out / "execucoes.json").write_text(json.dumps({
        "config": config["id"], "sementes": args.sementes, "avaliacoes": args.avaliacoes,
        "guloso": {"avaliacoes": greedy_metadata.get("evaluations"), "objetivo": list(objective_key(start_result))},
        "execucoes": runs,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    summary = summarize(rows, floors, baseline, start_result)
    (out / "resumo.md").write_text(f"# Experimento oficial 2026 — {args.rotulo}\n\n{summary}", encoding="utf-8")
    print("\n" + summary)
    print(f"Saída: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
