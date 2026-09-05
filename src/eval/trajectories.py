"""H8 experimental por trajetória, sem alterar o score ou as turmas ofertadas.

Vagas positivas por curso são uma hipótese de elegibilidade, não matrícula
individual nem atendimento coletivo. A grade esperada é entrada independente.
"""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from itertools import combinations

from src.model.curricula import COURSE_CODES

DAYS = {'segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo'}
TIME = re.compile(r'^(?:[01]\d|2[0-3]):[0-5]\d$')
STATES = ('trajetoria_encontrada', 'sem_trajetoria', 'dados_incompletos')


def _schedule(item):
    meetings = item.get('encontros')
    if not isinstance(meetings, list) or not meetings:
        return None
    slots = []
    for meeting in meetings:
        day, start, end = (meeting.get(k) for k in ('dia', 'inicio', 'fim'))
        if day not in DAYS or not isinstance(start, str) or not isinstance(end, str):
            return None
        if not TIME.fullmatch(start) or not TIME.fullmatch(end) or start >= end:
            return None
        slots.append((day, start, end))
    # Sobreposição dentro da própria turma também não é uma trajetória válida.
    if any(_overlap(a, b) for a, b in combinations(slots, 2)):
        return None
    return tuple(sorted(slots))


def _overlap(a, b):
    return a[0] == b[0] and max(a[1], b[1]) < min(a[2], b[2])


def _eligible(item, course):
    rows = item.get('vagas_por_curso')
    if not isinstance(rows, list) or not rows:
        return None
    matches = [r for r in rows if str(r.get('codigo_curso')) == COURSE_CODES[course]]
    if not matches:
        return False
    values = []
    for row in matches:
        value = row.get('vagas')
        try:
            number = float(value)
        except (ValueError, TypeError):
            return None
        if isinstance(value, bool) or not math.isfinite(number) or number < 0 or not number.is_integer():
            return None
        values.append(number)
    return sum(values) > 0


def _search(domains, max_nodes):
    nodes = 0
    ordered = sorted(domains, key=lambda code: (len(domains[code]), code))

    def visit(index, selected):
        nonlocal nodes
        if index == len(ordered):
            return selected
        for candidate in domains[ordered[index]]:
            if nodes >= max_nodes:
                raise TimeoutError
            nodes += 1
            if all(not any(_overlap(a, b) for a in candidate['slots'] for b in other['slots'])
                   for other in selected):
                found = visit(index + 1, selected + [candidate])
                if found is not None:
                    return found
        return None

    try:
        return visit(0, []), nodes, False
    except TimeoutError:
        return None, nodes, True


def evaluate_trajectories(payload, expected_groups, semesters, *, supplementary=(), max_nodes=100_000):
    """Retorna um diagnóstico por grupo/semestre, incluindo grupos sem ofertas.

    supplementary só supre códigos ausentes no semestre da instância. Nunca
    substitui horários de uma solução pela alocação observada na coleta.
    O limite de nós vale por grupo; interrupção é inconclusiva.
    """
    if not isinstance(max_nodes, int) or isinstance(max_nodes, bool) or max_nodes < 1:
        raise ValueError('max_nodes deve ser inteiro positivo')
    semesters = sorted(set(semesters))
    if not semesters or not expected_groups:
        raise ValueError('Informe os semestres e os grupos esperados')
    offers = defaultdict(list)
    seen = set()
    for origin, items in (('instancia', payload.get('classes', [])), ('complemento', supplementary)):
        primary_keys = set(offers) if origin == 'complemento' else set()
        for item in items:
            key = (item.get('semestre'), item.get('codigo'))
            if origin == 'complemento' and key in primary_keys:
                continue
            ident = item.get('id')
            if not ident or ident in seen:
                raise ValueError('Identificador de turma ausente ou duplicado')
            seen.add(ident)
            offers[key].append((item, origin))
    results = []
    for semester in semesters:
        for group, expected in sorted(expected_groups.items()):
            if not re.fullmatch(r'(CC|SI)-P[1-8]', group):
                raise ValueError(f'Grupo inválido: {group}')
            course = group.split('-')[0]
            codes = sorted(set(expected))
            domains = {code: [] for code in codes}
            missing, issues = [], []
            for code in codes:
                items = offers.get((semester, code), [])
                if not items:
                    missing.append(code)
                for item, origin in sorted(items, key=lambda pair: pair[0]['id']):
                    eligibility = _eligible(item, course)
                    if eligibility is False:
                        continue
                    slots = _schedule(item)
                    if eligibility is None or slots is None:
                        issues.append({'codigo': code, 'turma_id': item['id'],
                                       'motivo': 'vagas_desconhecidas' if eligibility is None else 'horario_invalido_ou_ausente'})
                        continue
                    domains[code].append({'codigo': code, 'turma_id': item['id'], 'origem': origin, 'slots': slots})
            empty = [code for code in codes if not domains[code]]
            selection, nodes, limited = (None, 0, False)
            if codes and not empty:
                selection, nodes, limited = _search(domains, max_nodes)
            if selection is not None:
                status, reason = 'trajetoria_encontrada', 'testemunha_verificada'
            elif not codes or empty or issues or limited:
                status = 'dados_incompletos'
                reason = 'limite_busca' if limited else 'cobertura_ou_dados_insuficientes'
            else:
                status, reason = 'sem_trajetoria', 'busca_exaustiva_sem_combinacao'
            results.append({'semestre': semester, 'grupo': group, 'status': status, 'motivo': reason,
                            'disciplinas_esperadas': codes, 'disciplinas_ausentes': missing,
                            'disciplinas_sem_turma_utilizavel': empty, 'pendencias': issues,
                            'nos_explorados': nodes,
                            'trajetoria': [{'codigo': c['codigo'], 'turma_id': c['turma_id'], 'origem': c['origem'],
                                           'encontros': [dict(zip(('dia', 'inicio', 'fim'), slot)) for slot in c['slots']]}
                                          for c in (selection or [])]})
    counts = Counter(r['status'] for r in results)
    return {'modo': 'diagnostico_paralelo_h8_opcao2',
            'elegibilidade': 'proxy_vagas_ofertadas_positivas_por_curso',
            'max_nos_por_grupo': max_nodes, 'resumo': {state: counts[state] for state in STATES}, 'grupos': results}
