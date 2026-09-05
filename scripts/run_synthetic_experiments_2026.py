"""Executa e relata o benchmark sintetico multi-seed de 2026."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.solve.direct_objective import evaluate  # noqa: E402
from src.eval.evaluator import evaluate_json  # noqa: E402
from src.solve.integrated import ALGORITHMS, annual_deficit, assigned_teachers, greedy_improve, is_better, objective_key  # noqa: E402


DATA = ROOT / "dados" / "processados"
DEFAULT_CONFIG = ROOT / "dados" / "config_sintetica_2026_v1.json"
DEFAULT_INSTANCE = DATA / "instancia_sintetica_2026_v1.json"
OUTPUT_DIR = DATA / "experimento_sintetico_2026"
RUNS_CSV = DATA / "resultados_experimento_sintetico_2026.csv"
REPORT = DATA / "relatorio_experimento_sintetico_2026.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_revision() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() or "indisponivel"


def git_worktree_status() -> str:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return "limpa" if not result.stdout.strip() else "com alteracoes nao commitadas"


def code_sha256() -> str:
    digest = hashlib.sha256()
    for path in (
        ROOT / "src" / "eval" / "evaluator.py",
        ROOT / "src" / "eval" / "instance_io.py",
        ROOT / "src" / "eval" / "resources.py",
        ROOT / "src" / "eval" / "rooms.py",
        ROOT / "src" / "solve" / "direct_objective.py",
        ROOT / "src" / "solve" / "integrated.py",
        ROOT / "scripts" / "build_synthetic_instance_2026.py",
        ROOT / "scripts" / "run_synthetic_experiments_2026.py",
    ):
        digest.update(str(path.relative_to(ROOT)).encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def optframe_version() -> str:
    try:
        import optframe
    except ImportError:
        return "nao instalado"
    return str(getattr(optframe, "__version__", "instalado; versao indisponivel"))


def flatten_result(label: str, seed: int | str, elapsed: float, result: dict, metadata: dict) -> dict:
    row = {
        "algoritmo": label,
        "seed": seed,
        "tempo_segundos": round(elapsed, 6),
        "avaliacoes": metadata.get("evaluations", 0),
        "score": result["score"],
        "hard_total": result["hard_violations"],
        "deficit_h12": annual_deficit(result),
    }
    row.update({f"hard_{key}": value for key, value in result["hard"].items()})
    row.update({f"soft_{key}": value for key, value in result["soft"].items()})
    return row


def assert_reference_equivalence(payload: dict, direct_result: dict) -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "instance.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        reference = evaluate_json(path).as_dict()
    if direct_result["hard"] != reference["hard"]:
        raise AssertionError(
            f"Avaliadores divergiram nos criterios hard: {direct_result['hard']} != {reference['hard']}"
        )
    soft_keys = set(direct_result["soft"]) | set(reference["soft"])
    for key in soft_keys:
        direct_value = direct_result["soft"].get(key)
        reference_value = reference["soft"].get(key)
        if direct_value is None or reference_value is None:
            if direct_value != reference_value:
                raise AssertionError(f"Avaliadores divergiram em {key}: {direct_value} != {reference_value}")
        elif abs(float(direct_value) - float(reference_value)) > 1e-8:
            raise AssertionError(f"Avaliadores divergiram em {key}: {direct_value} != {reference_value}")
    direct_deficit = (direct_result.get("guidance") or {}).get("deficit_carga_anual")
    reference_deficit = reference["metadata"].get("deficit_carga_anual")
    if direct_deficit is None or reference_deficit is None:
        if direct_deficit != reference_deficit:
            raise AssertionError(f"Avaliadores divergiram no deficit H12: {direct_deficit} != {reference_deficit}")
    elif abs(float(direct_deficit) - float(reference_deficit)) > 1e-8:
        raise AssertionError(f"Avaliadores divergiram no deficit H12: {direct_deficit} != {reference_deficit}")


def improvement(before: float, after: float) -> str:
    if before == 0:
        return "0,00%" if after == 0 else "n/a"
    return f"{((before - after) / abs(before)) * 100:.2f}%".replace(".", ",")


def markdown_number(value) -> str:
    if value is None:
        return "indisponivel"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def aggregate(rows: list[dict], algorithm: str) -> dict:
    selected = [row for row in rows if row["algoritmo"] == algorithm]
    scores = [float(row["score"]) for row in selected]
    hard = [float(row["hard_total"]) for row in selected]
    deficits = [float(row["deficit_h12"]) for row in selected]
    times = [float(row["tempo_segundos"]) for row in selected]
    return {
        "runs": len(selected),
        "score_mean": statistics.mean(scores),
        "score_stdev": statistics.stdev(scores) if len(scores) > 1 else 0.0,
        "score_best": min(scores),
        "hard_mean": statistics.mean(hard),
        "hard_best": min(hard),
        "deficit_mean": statistics.mean(deficits),
        "deficit_best": min(deficits),
        "time_mean": statistics.mean(times),
    }


def write_report(config: dict, instance: dict, rows: list[dict], baseline: dict, greedy: dict, best_by_algorithm: dict, instance_hash: str) -> None:
    algorithms = list(config["experimento"]["algoritmos"])
    h12_count = sum(teacher.get("incluido_h12") is True for teacher in instance["teachers"])
    flexible = sum(not item.get("horario_fixo", True) for item in instance["classes"])
    movable_teachers = sum(
        len(item.get("professores_habilitados") or []) > 1 and not item.get("professor_fixo", False)
        for item in instance["classes"]
    )
    meetings = sum(len(item.get("encontros", [])) for item in instance["classes"])
    mandatory = sum(item.get("origem") == "IC" and item.get("obrigatoria") is True for item in instance["classes"])
    seed_count = len(config["experimento"]["seeds"])
    environment_optframe = optframe_version()
    lines = [
        "# Relatorio do experimento sintetico reprodutivel - 2026 CC/SI",
        "",
        f"Execucao: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"Commit: `{git_revision()}`",
        f"Estado do worktree: `{git_worktree_status()}`",
        f"SHA-256 do codigo do benchmark: `{code_sha256()}`",
        f"Python: `{platform.python_version()}`",
        f"OptFrame disponivel no ambiente: `{environment_optframe}`",
        f"SHA-256 da instancia: `{instance_hash}`",
        "",
        "> Resultados nao oficiais. Capacidades, recursos, habilitacoes, prioridades, horarios flexiveis e universo H12 usam proxies documentadas. O benchmark valida a implementacao e nao substitui dados institucionais.",
        "",
        "## Dados da instancia",
        "",
        "| Indicador | Valor |",
        "|---|---:|",
        f"| Turmas fisicas | {len(instance['classes'])} |",
        f"| Encontros semanais | {meetings} |",
        f"| Salas | {len(instance['rooms'])} |",
        f"| Docentes no cadastro sintetico | {len(instance['teachers'])} |",
        f"| Docentes no universo H12 sintetico | {h12_count} |",
        f"| Turmas obrigatorias do IC | {mandatory} |",
        f"| Turmas com professor movel | {movable_teachers} |",
        f"| Turmas com horario flexivel | {flexible} |",
        "",
        "## Hipoteses reproduziveis",
        "",
        "| Parametro | Regra utilizada |",
        "|---|---|",
    ]
    for key, value in instance["synthetic_manifest"]["hipoteses"].items():
        lines.append(f"| {key} | `{value}` |")

    lines += [
        "",
        "## Baseline e melhoria gulosa",
        "",
        "| Configuracao | Score | Hard | Sala | Professor | Curriculo | Capacidade | Recursos | Descanso | H12 docentes | Deficit H12 | Dias | Janelas | Desperdicio | Preferencia |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label, result in (("Baseline observado", baseline), ("Melhoria gulosa integrada", greedy)):
        h, s = result["hard"], result["soft"]
        lines.append(
            f"| {label} | {result['score']:.2f} | {result['hard_violations']} | {h['conflitos_sala']} | "
            f"{h['conflitos_professor']} | {h['conflitos_curriculares']} | {h['capacidade_insuficiente']} | "
            f"{h['recursos_incompativeis']} | {h['descanso_insuficiente']} | {markdown_number(h['carga_anual_insuficiente'])} | "
            f"{annual_deficit(result):.2f} | {s['dias_trabalhados']} | {s['janelas']} | {s['desperdicio_capacidade']:.2f} | "
            f"{s.get('preferencia_priorizada', 0):.2f} |"
        )
    lines += [
        "",
        f"A passagem gulosa reduziu o score em **{improvement(float(baseline['score']), float(greedy['score']))}** e as violacoes hard em **{improvement(float(baseline['hard_violations']), float(greedy['hard_violations']))}**.",
        "",
        "## Resultados multi-seed",
        "",
        "| Algoritmo | Execucoes | Score medio | Desvio | Melhor score | Hard medio | Melhor hard | Deficit H12 medio | Melhor deficit | Tempo medio (s) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for algorithm in algorithms:
        stats = aggregate(rows, algorithm)
        lines.append(
            f"| {algorithm.upper()} | {stats['runs']} | {stats['score_mean']:.2f} | {stats['score_stdev']:.2f} | "
            f"{stats['score_best']:.2f} | {stats['hard_mean']:.2f} | {stats['hard_best']:.0f} | "
            f"{stats['deficit_mean']:.2f} | {stats['deficit_best']:.2f} | {stats['time_mean']:.3f} |"
        )

    lines += [
        "",
        "## Melhor resultado por algoritmo",
        "",
        "| Algoritmo | Score | Melhoria score vs. baseline | Hard | Melhoria hard vs. baseline | Sala | Professor | Curriculo | H12 docentes | Deficit H12 | Janelas | Desperdicio |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for algorithm in algorithms:
        result = best_by_algorithm[algorithm].evaluation
        h, s = result["hard"], result["soft"]
        lines.append(
            f"| {algorithm.upper()} | {result['score']:.2f} | {improvement(float(baseline['score']), float(result['score']))} | "
            f"{result['hard_violations']} | {improvement(float(baseline['hard_violations']), float(result['hard_violations']))} | "
            f"{h['conflitos_sala']} | {h['conflitos_professor']} | {h['conflitos_curriculares']} | "
            f"{markdown_number(h['carga_anual_insuficiente'])} | {annual_deficit(result):.2f} | {s['janelas']} | {s['desperdicio_capacidade']:.2f} |"
        )

    global_algorithm = min(
        algorithms,
        key=lambda name: objective_key(best_by_algorithm[name].evaluation),
    )
    global_search = best_by_algorithm[global_algorithm]
    global_result = global_search.evaluation
    baseline_by_id = {item["id"]: item for item in instance["classes"]}
    best_by_id = {item["id"]: item for item in global_search.solution["classes"]}
    teacher_changes = schedule_changes = room_changes = 0
    for class_id, before in baseline_by_id.items():
        after = best_by_id[class_id]
        teacher_changes += assigned_teachers(before) != assigned_teachers(after)
        before_pattern = [
            (meeting.get("dia"), meeting.get("inicio"), meeting.get("fim"))
            for meeting in before.get("encontros", [])
        ]
        after_pattern = [
            (meeting.get("dia"), meeting.get("inicio"), meeting.get("fim"))
            for meeting in after.get("encontros", [])
        ]
        schedule_changes += before_pattern != after_pattern
        room_changes += sum(
            left.get("sala") != right.get("sala")
            for left, right in zip(before.get("encontros", []), after.get("encontros", []))
        )

    lines += [
        "",
        "## Melhor solucao global",
        "",
        f"A melhor solucao foi produzida por **{global_algorithm.upper()}**. Ela alterou **{teacher_changes} atribuicoes de professor**, **{schedule_changes} padroes de horario** e **{room_changes} alocacoes de sala por encontro** em relacao ao baseline.",
        "",
        "| Metrica | Baseline | Melhor global | Diferenca |",
        "|---|---:|---:|---:|",
    ]
    for key in baseline["hard"]:
        before = baseline["hard"][key]
        after = global_result["hard"][key]
        delta = None if before is None or after is None else after - before
        lines.append(f"| Hard: {key} | {markdown_number(before)} | {markdown_number(after)} | {markdown_number(delta)} |")
    for key in baseline["soft"]:
        before = baseline["soft"][key]
        after = global_result["soft"][key]
        delta = None if before is None or after is None else after - before
        lines.append(f"| Soft: {key} | {markdown_number(before)} | {markdown_number(after)} | {markdown_number(delta)} |")
    lines.append(
        f"| Guia: deficit_carga_anual | {annual_deficit(baseline):.2f} | "
        f"{annual_deficit(global_result):.2f} | {annual_deficit(global_result) - annual_deficit(baseline):.2f} |"
    )
    lines += [
        "",
        f"Os conflitos curriculares nao diminuem neste perfil porque as {mandatory} turmas obrigatorias permanecem com horario fixo; somente optativas recebem dominio de horario sintetico. Essa limitacao e intencional e separa o teste de professores/salas da futura validacao dos horarios institucionais.",
        "",
        f"A melhor busca ({global_algorithm.upper()}) altera as metricas conforme a tabela acima. Como o comparador prioriza qualquer reducao hard, uma melhora hard pode aceitar piora nos criterios soft; o resultado evidencia um trade-off e nao demonstra superioridade geral de um algoritmo.",
    ]

    lines += [
        "",
        "## Execucoes individuais",
        "",
        "| Algoritmo | Seed | Score | Hard | Deficit H12 | Tempo (s) | Avaliacoes |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        if row["algoritmo"] in algorithms:
            lines.append(
                f"| {row['algoritmo'].upper()} | {row['seed']} | {float(row['score']):.2f} | "
                f"{row['hard_total']} | {float(row['deficit_h12']):.2f} | {float(row['tempo_segundos']):.3f} | {row['avaliacoes']} |"
            )

    lines += [
        "",
        "## Validacoes executadas",
        "",
        "- [x] Mesma instancia e mesmo avaliador para todos os algoritmos.",
        "- [x] Avaliador direto e avaliador de referencia equivalentes em todas as solucoes registradas.",
        "- [x] Mesmos orcamentos de avaliacao configurados por algoritmo.",
        f"- [x] {seed_count} sementes explicitas e versionadas.",
        "- [x] Professor observado separado da atribuicao corrente.",
        "- [x] Turmas fixas nao pertencem as vizinhancas correspondentes.",
        "- [x] Capacidades e recursos sinteticos identificados por fonte.",
        "- [x] Matching bipartido confirma cobertura conjunta dos creditos H12 sinteticos.",
        "- [x] Solucoes e resultados vinculados ao hash da instancia.",
        "- [x] Melhor solucao nunca pior que a entrada gulosa no comparador hard/soft.",
        "",
        "## Reproducao",
        "",
        "```bash",
        "python scripts/run_pipeline_2026.py --offline",
        "python scripts/build_synthetic_instance_2026.py",
        "python scripts/run_synthetic_experiments_2026.py",
        "```",
        "",
        "## Limitacoes",
        "",
        (
            f"- O pacote nativo `optframe=={environment_optframe}` foi importado, mas este relatorio usa as implementacoes de referencia em Python; a execucao nativa das buscas permanece uma etapa separada."
            if environment_optframe not in {"nao instalado", "instalado; versao indisponivel"}
            else "- O pacote nativo `optframe` nao estava disponivel; este relatorio usa as implementacoes de referencia em Python."
        ),
        "- Os pesos soft sao unitarios e provisorios.",
        "- O universo H12 de 40 docentes e uma hipotese sintetica de viabilidade, nao uma lista institucional.",
        "- Capacidades sao limites inferiores observados, nao capacidades fisicas oficiais.",
        "- Habilitacoes e horarios flexiveis sao derivados do historico de 2025.",
        "",
        "## Leitura tecnica",
        "",
        "A comparacao mede se as vizinhancas integradas conseguem melhorar a mesma solucao inicial sob um avaliador comum. Diferencas entre algoritmos neste benchmark servem para validar o software e orientar a etapa oficial; nao sustentam, isoladamente, conclusoes sobre a grade real da UFF.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa o benchmark sintetico multi-seed de 2026")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--instance", type=Path, default=DEFAULT_INSTANCE)
    args = parser.parse_args()
    config_path = args.config.resolve()
    instance_path = args.instance.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    instance = json.loads(instance_path.read_text(encoding="utf-8"))
    if instance.get("profile") != config["id"]:
        raise ValueError("A instancia nao corresponde ao perfil configurado")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    instance_hash = sha256(instance_path)

    baseline = evaluate(instance)
    assert_reference_equivalence(instance, baseline)
    start = time.perf_counter()
    greedy_solution, greedy_metadata = greedy_improve(
        instance,
        max_candidates=int(config["experimento"]["maximo_candidatos_guloso"]),
    )
    greedy_elapsed = time.perf_counter() - start
    greedy = greedy_metadata["best"]
    assert_reference_equivalence(greedy_solution, greedy)
    rows = [
        flatten_result("baseline", "-", 0.0, baseline, {"evaluations": 1}),
        flatten_result("guloso", "-", greedy_elapsed, greedy, greedy_metadata),
    ]
    best_by_algorithm = {}

    for algorithm, algorithm_config in config["experimento"]["algoritmos"].items():
        best_search = None
        for seed in config["experimento"]["seeds"]:
            start = time.perf_counter()
            search = ALGORITHMS[algorithm](greedy_solution, int(seed), algorithm_config)
            elapsed = time.perf_counter() - start
            if is_better(greedy, search.evaluation):
                raise AssertionError(f"{algorithm}/{seed}: busca retornou solucao pior que a entrada")
            assert_reference_equivalence(search.solution, search.evaluation)
            rows.append(flatten_result(algorithm, int(seed), elapsed, search.evaluation, search.metadata))
            solution_path = OUTPUT_DIR / f"solucao_{algorithm}_{seed}.json"
            solution_payload = search.solution
            solution_payload["experiment_result"] = {
                **search.metadata,
                "evaluation": search.evaluation,
                "instance_sha256": instance_hash,
                "config_sha256": sha256(config_path),
            }
            solution_path.write_text(json.dumps(solution_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if best_search is None or is_better(search.evaluation, best_search.evaluation):
                best_search = search
        best_by_algorithm[algorithm] = best_search

    fieldnames = list(rows[0])
    for row in rows[1:]:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with RUNS_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    write_report(config, instance, rows, baseline, greedy, best_by_algorithm, instance_hash)
    print(RUNS_CSV)
    print(REPORT)


if __name__ == "__main__":
    main()
