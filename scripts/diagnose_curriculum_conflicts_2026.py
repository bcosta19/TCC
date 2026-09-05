"""Audita choques entre ofertas e existencia de escolhas sem choque por periodo.

A escolha de uma turma por codigo e apenas um diagnostico temporal: nao
substitui H8 nem considera demanda, vagas, pre-requisitos ou elegibilidade.
"""
import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.solve.direct_objective import evaluate, groups_for_item
from scripts.match_qh_web_2026 import web_meetings


def slots(item):
    return {(m['dia'], m['inicio'], m['fim']) for m in item['encontros']}


def collide(a, b):
    return any(da == db and max(sa, sb) < min(ea, eb)
               for da, sa, ea in slots(a) for db, sb, eb in slots(b))


def choose_sections(by_code):
    """Busca exaustiva com poda; retorna uma testemunha ou None."""
    choices = sorted(by_code.values(), key=len)
    def visit(index, selected):
        if index == len(choices):
            return selected
        for item in choices[index]:
            if all(not collide(item, previous) for previous in selected):
                found = visit(index + 1, selected + [item])
                if found is not None:
                    return found
        return None
    return visit(0, [])


def diagnose(payload):
    groups = defaultdict(list)
    for item in payload['classes']:
        for group in groups_for_item(item):
            groups[item['semestre'], group].append(item)
    conflicts, witnesses = [], []
    for (semester, group), items in sorted(groups.items()):
        entries = defaultdict(list)
        by_code = defaultdict(list)
        for item in items:
            by_code[item['codigo']].append(item)
            for day, start, end in slots(item):
                entries[item['codigo'], day, start, end].append(item)
        for (a, ai), (b, bi) in combinations(sorted(entries.items()), 2):
            if a[0] != b[0] and a[1] == b[1] and max(a[2], b[2]) < min(a[3], b[3]):
                conflicts.append(dict(semestre=semester, grupo=group, dia=a[1],
                    codigo_a=a[0], horario_a=f'{a[2]}-{a[3]}', turmas_a=';'.join(i['id'] for i in ai),
                    codigo_b=b[0], horario_b=f'{b[2]}-{b[3]}', turmas_b=';'.join(i['id'] for i in bi),
                    todos_fixos=all(i.get('horario_fixo') is True for i in ai + bi)))
        selection = choose_sections(by_code)
        witnesses.append(dict(semestre=semester, grupo=group, codigos=len(by_code),
            escolha_sem_choque=selection is not None,
            turmas=';'.join(i['id'] for i in selection) if selection is not None else ''))
    assert len(conflicts) == evaluate(payload)['hard']['conflitos_curriculares']
    return conflicts, witnesses


def write_csv(path, rows):
    if not rows:
        path.write_text('', encoding='utf-8')
        return
    with path.open('w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--instance', type=Path, default=ROOT / 'dados/processados/instancia_sintetica_2026_v1.json')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'dados/processados/diagnostico_curricular_2026')
    args = parser.parse_args()
    payload = json.loads(args.instance.read_text())
    conflicts, witnesses = diagnose(payload)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / 'conflitos.csv', conflicts)
    write_csv(args.output_dir / 'escolhas_por_grupo.csv', witnesses)
    affected = {c for row in conflicts for side in ('a', 'b') for c in row[f'turmas_{side}'].split(';')}
    with (ROOT / 'dados/processados/vagas_turmas_2026.csv').open() as file:
        links = list(csv.DictReader(file))
    evidence = []
    for item in payload['classes']:
        if item['id'] not in affected:
            continue
        matches = [r for r in links if r['semestre'] == item['semestre'] and r['codigo'] == item['codigo'] and r['turma_web'] == item['turma']]
        for link in matches:
            # Reusa apenas o parser de horarios da coleta, sem consulta de rede.
            web = web_meetings(link['horario_web'])
            evidence.append(dict(turma_id=item['id'], grupo=';'.join(groups_for_item(item)),
                fonte_pdf=item['fontes']['quadro_pdf'], pagina_pdf=item['fontes']['pagina_pdf'],
                horario_pdf=';'.join(f'{d} {s}-{e}' for d,s,e in sorted(slots(item))),
                horario_web=link['horario_web'], horarios_conferem=slots(item) == set(web)))
    write_csv(args.output_dir / 'fontes.csv', evidence)
    affected_groups = {(r['semestre'], r['grupo']) for r in conflicts}
    lines = ['# Diagnóstico dos conflitos curriculares de 2026', '',
        f"SHA-256 da instância: `{hashlib.sha256(args.instance.read_bytes()).hexdigest()}`", '',
        f'{len(conflicts)} sobreposições contadas pelo avaliador; {len(affected)} ofertas envolvidas.', '',
        '| Semestre | Grupo | Códigos no recorte | Existe escolha sem choque? |', '|---|---|---:|---|']
    for row in witnesses:
        if (row['semestre'], row['grupo']) in affected_groups:
            lines.append(f"| {row['semestre']} | {row['grupo']} | {row['codigos']} | {'Sim' if row['escolha_sem_choque'] else 'Não'} |")
    lines += ['', 'As sobreposições são reais nos horários coletados, mas o contador atual exige ausência de choque entre todas as ofertas de códigos distintos do grupo. Ele ignora choques entre seções do mesmo código; não escolhe uma seção por disciplina.', '',
        'O diagnóstico adicional busca uma turma por código do grupo. Uma escolha sem choque comprova apenas compatibilidade temporal individual no recorte. Não comprova atendimento de todos os alunos, suficiência de vagas, elegibilidade das seções ou viabilidade global da instância.', '',
        'Não foi alterado H8 nem liberado horário obrigatório. Antes de flexibilizar horários, aluno e orientador devem decidir se H8 protege todas as ofertas ou trajetórias permitidas entre seções. A segunda interpretação exige modelar elegibilidade e, para atendimento coletivo, demanda/capacidade.', '',
        'Evidências: `conflitos.csv` detalha as unidades contadas; `escolhas_por_grupo.csv` fornece testemunhas; `fontes.csv` confronta horários PDF e coleta web local. Grupos sem ofertas no recorte não são avaliados.', '']
    (args.output_dir / 'relatorio.md').write_text('\n'.join(lines), encoding='utf-8')
    print(f'{len(conflicts)} conflitos; {len(evidence)} ofertas conferidas; {args.output_dir}')


if __name__ == '__main__':
    main()
