"""Piloto tecnico do SA nativo e da referencia; nao e comparacao estatistica.

Usa a mesma entrada gulosa, preserva solucoes e confere dois avaliadores.
O nativo para por tempo; a referencia por avaliacoes. Sementes controlam a
vizinhanca Python, mas o RNG interno do OptFrame nao esta configurado.
"""
import argparse
import copy
import csv
import json
import platform
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.solve.direct_objective import evaluate
from src.solve.integrated import greedy_improve, objective_key, solve_sa, search_energy
from src.solve.optframe_adapter import solve_sa_optframe
from src.solve.validation import validate_solution
from scripts.run_synthetic_experiments_2026 import (
    assert_reference_equivalence, flatten_result, git_revision, git_worktree_status,
    optframe_version, sha256,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('seconds', nargs='?', type=float, default=10.0)
    parser.add_argument('--instance', type=Path, default=ROOT / 'dados/processados/instancia_sintetica_2026_v1.json')
    parser.add_argument('--config', type=Path, default=ROOT / 'dados/config_sintetica_2026_v1.json')
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    if not 0 < args.seconds < float('inf'):
        parser.error('segundos deve ser positivo e finito')
    config = json.loads(args.config.read_text())
    payload = json.loads(args.instance.read_text())
    if payload.get('profile') != config['id']:
        raise ValueError('Instancia e configuracao pertencem a perfis diferentes')
    provenance = payload['synthetic_manifest']
    if provenance['config_sha256'] != sha256(args.config):
        raise ValueError('Configuracao mudou: regenere a instancia sintetica')
    if provenance['base_sha256'] != sha256(ROOT / provenance['base']):
        raise ValueError('Instancia-base mudou: regenere a instancia sintetica')
    output = args.output_dir or ROOT / 'dados/processados' / datetime.now().strftime('piloto_optframe_%Y%m%d_%H%M%S')
    output.mkdir(parents=True, exist_ok=False)
    baseline = evaluate(payload)
    validate_solution(payload, payload)
    assert_reference_equivalence(payload, baseline)
    start = time.perf_counter()
    greedy, gmeta = greedy_improve(payload, config['experimento']['maximo_candidatos_guloso'])
    greedy_time = time.perf_counter() - start
    geval = evaluate(greedy)
    validate_solution(payload, greedy)
    assert_reference_equivalence(greedy, geval)
    native_config = dict(seconds=args.seconds, alpha=0.98, iter_max=100, t0=1e8, greedy_start=False)
    # Mantem os parametros ja usados no benchmark sintetico de referencia.
    reference_config = config['experimento']['algoritmos']['sa']
    source_paths = sorted((ROOT / 'src').rglob('*.py')) + [Path(__file__), ROOT / 'scripts/run_synthetic_experiments_2026.py']
    import optframe
    library = Path(optframe.__file__).parent / 'optframe_lib.so'
    manifest = dict(executado_em=datetime.now().astimezone().isoformat(), commit=git_revision(),
        worktree=git_worktree_status(), python=platform.python_version(), sistema=platform.platform(),
        optframe=optframe_version(), optframe_binario_sha256=sha256(library),
        instancia_sha256=sha256(args.instance), configuracao_sha256=sha256(args.config),
        fontes_sha256={str(p.relative_to(ROOT)):sha256(p) for p in source_paths},
        seeds=config['experimento']['seeds'], nativo=native_config, referencia=reference_config,
        limite_reproducibilidade='Semente controla vizinhanca Python; RNG interno nativo nao configurado. Parada por tempo varia entre execucoes.',
        perfil=config['id'])
    (output / 'manifesto.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    (output / 'instancia_entrada.json').write_bytes(args.instance.read_bytes())
    rows = [flatten_result('baseline', '-', 0, baseline, {'evaluations':1}),
            flatten_result('guloso', '-', greedy_time, geval, gmeta)]
    for algorithm in ('sa_referencia', 'sa_optframe'):
        for seed in manifest['seeds']:
            start = time.perf_counter()
            if algorithm == 'sa_optframe':
                solution, ev, meta = solve_sa_optframe(copy.deepcopy(greedy), seed, **native_config)
                meta['evaluations'] = meta['engine_evaluations']
                if abs(meta['engine_best_energy'] - search_energy(ev)) > 1e-4:
                    raise AssertionError('Energia nativa diverge da solucao retornada')
            else:
                result = solve_sa(copy.deepcopy(greedy), seed, reference_config)
                solution, ev, meta = result.solution, result.evaluation, result.metadata
            elapsed = time.perf_counter() - start
            validate_solution(payload, solution)
            assert_reference_equivalence(solution, ev)
            if objective_key(ev) > objective_key(geval):
                raise AssertionError(f'{algorithm}/{seed}: pior que entrada gulosa')
            rows.append(flatten_result(algorithm, seed, elapsed, ev, meta))
            solution['experiment_result'] = dict(metadata=meta, evaluation=ev,
                instance_sha256=manifest['instancia_sha256'])
            (output / f'solucao_{algorithm}_{seed}.json').write_text(json.dumps(solution, ensure_ascii=False, indent=2)+'\n')
            print(f'{algorithm}/{seed}: hard={ev["hard_violations"]}, deficit={ev["guidance"]["deficit_carga_anual"]}, {elapsed:.2f}s', flush=True)
    with (output / 'resultados.csv').open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    lines = ['# Piloto tecnico do SA nativo no pyoptframe', '',
        f"Execucao: {manifest['executado_em']}", f"Python {manifest['python']}; OptFrame {manifest['optframe']}.", '',
        'Perfil sintetico existente, com proxies; pesos e dominios nao foram alterados.',
        'Todos os resultados passaram pela validacao estrutural, pela equivalencia entre avaliadores e pela comparacao com a mesma entrada gulosa.', '',
        '| Metodo | Seed | Hard | Deficit H12 | Score | Tempo (s) | Avaliacoes |', '|---|---:|---:|---:|---:|---:|---:|']
    for r in rows:
        lines.append(f"| {r['algoritmo']} | {r['seed']} | {r['hard_total']} | {r['deficit_h12']} | {r['score']:.2f} | {r['tempo_segundos']:.3f} | {r['avaliacoes']} |")
    lines += ['', '## Limites de interpretacao', '',
        f"SA nativo: {args.seconds}s por busca, alpha=0.98, iter_max=100, T0=1e8. SA de referencia: `{json.dumps(reference_config)}`.",
        'Os orcamentos e resfriamentos diferem; este piloto verifica integracao e nao estabelece superioridade entre implementacoes.',
        manifest['limite_reproducibilidade'],
        'O score reportado pelo avaliador difere da energia interna da busca. O manifesto e os metadados das solucoes preservam a configuracao usada.',
        'As dez sobreposicoes curriculares permanecem no perfil fixo. Consulte o diagnostico de turmas alternativas antes de interpretar isso como impossibilidade de cursar um periodo.', '',
        '## Reexecucao', '', '```bash',
        f'.venv/bin/python scripts/benchmark_optframe_sa_2026.py {args.seconds}', '```', '',
        'Cada execucao cria uma pasta nova. `manifesto.json` registra hashes e parametros; `resultados.csv` guarda todas as metricas. Instancia e solucoes JSON ficam locais e sao ignoradas pelo Git.', '']
    (output / 'relatorio.md').write_text('\n'.join(lines))
    print(output, flush=True)


if __name__ == '__main__':
    main()
