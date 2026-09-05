"""Executa H8 por trajetória em paralelo ao score atual, sem mutar a instância."""
import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.eval.trajectories import evaluate_trajectories
from src.model.curricula import load_project_curricula
from src.solve.direct_objective import evaluate
from scripts.match_qh_web_2026 import MEETING_RE, web_meetings


def load_supplement(path):
    with path.open(encoding='utf-8-sig', newline='') as file:
        rows = list(csv.DictReader(file))
    offers = []
    for row in rows:
        text = row['horario']
        slots = web_meetings(text)
        # Não aceitar parsing parcial como se fosse o horário completo.
        if MEETING_RE.sub('', text).strip(' ;\t\n'):
            slots = set()
        offers.append({'id': f"web:{row['semestre']}:{row['codigo']}:{row['turma']}",
                       'codigo': row['codigo'], 'semestre': row['semestre'],
                       'vagas_por_curso': json.loads(row['vagas_por_curso_json'] or '[]'),
                       'encontros': [dict(zip(('dia', 'inicio', 'fim'), s)) for s in sorted(slots)]})
    return offers


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('instance', type=Path)
    parser.add_argument('--supplement-web', type=Path, help='Coleta local opcional para códigos ausentes')
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--max-nodes', type=int, default=100_000)
    args = parser.parse_args()
    payload = json.loads(args.instance.read_text(encoding='utf-8'))
    expected = {}
    for entries in load_project_curricula(ROOT).values():
        for entry in entries:
            if entry.kind == 'obrigatoria':
                expected.setdefault(entry.group, []).append(entry.code)
    if not payload.get('ano'):
        parser.error('A instância deve informar ano para verificar os dois semestres')
    semesters = [f"{payload['ano']}-{i}" for i in (1, 2)]
    report = evaluate_trajectories(payload, expected, semesters,
        supplementary=load_supplement(args.supplement_web) if args.supplement_web else (), max_nodes=args.max_nodes)
    report['avaliacao_atual'] = evaluate(payload)
    sources = [args.instance, ROOT/'dados/grade_cc.md', ROOT/'dados/grade_si.md', Path(__file__),
               ROOT/'src/eval/trajectories.py', ROOT/'src/model/curricula.py',
               ROOT/'src/solve/direct_objective.py', ROOT/'scripts/match_qh_web_2026.py']
    if args.supplement_web:
        sources.append(args.supplement_web)
    report['fontes_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir/'resultado.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    lines = ['# H8 por trajetória — diagnóstico paralelo', '',
             'Filtro provisório: vagas ofertadas positivas por curso. Não comprova matrícula individual nem atendimento coletivo.',
             'O score e a H8 atuais não foram alterados. Grupos incompletos não são tratados como viáveis.', '',
             f"Resumo: `{json.dumps(report['resumo'], ensure_ascii=False)}`", '',
             '| Semestre | Grupo | Estado | Disciplinas sem turma utilizável |', '|---|---|---|---|']
    for row in report['grupos']:
        lines.append(f"| {row['semestre']} | {row['grupo']} | {row['status']} | {', '.join(row['disciplinas_sem_turma_utilizavel']) or '—'} |")
    lines += ['', 'O arquivo `resultado.json` contém a trajetória e seus encontros, pendências, motivos e hashes das fontes.',
              'Complementos suprem apenas códigos ausentes por semestre, preservando as alocações da instância. Não são incorporados ao solver.', '']
    (args.output_dir/'relatorio.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(report['resumo'], ensure_ascii=False))


if __name__ == '__main__':
    main()
