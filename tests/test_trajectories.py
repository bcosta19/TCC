import copy
import itertools
import random
import unittest

from src.eval.trajectories import evaluate_trajectories


def offer(code, ident=None, start='08:00', end='09:00', semester='2026-1', course='31'):
    return {'id': ident or code, 'codigo': code, 'semestre': semester,
            'vagas_por_curso': [{'codigo_curso': course, 'vagas': 10}],
            'encontros': [{'dia': 'segunda', 'inicio': start, 'fim': end}]}


def run(classes, codes=('A', 'B'), **kwargs):
    return evaluate_trajectories({'classes': classes}, {'CC-P1': codes}, ['2026-1'], **kwargs)['grupos'][0]


class TrajectoryTests(unittest.TestCase):
    def test_alternativa_sem_choque_e_fronteira_adjacente(self):
        r = run([offer('A'), offer('B'), offer('B', 'B2', '09:00', '10:00')])
        self.assertEqual(r['status'], 'trajetoria_encontrada')
        self.assertEqual({c['turma_id'] for c in r['trajetoria']}, {'A', 'B2'})

    def test_choque_com_dados_completos(self):
        self.assertEqual(run([offer('A'), offer('B')])['status'], 'sem_trajetoria')

    def test_compatibilidade_por_pares_nao_basta(self):
        offers = [offer(code, code+str(hour), f'{hour:02}:00', f'{hour+1:02}:00')
                  for code in ('A', 'B', 'C') for hour in (8, 9)]
        self.assertEqual(run(offers, ('A', 'B', 'C'))['status'], 'sem_trajetoria')

    def test_ausencia_nao_passa_silenciosamente(self):
        r = run([offer('A')])
        self.assertEqual(r['status'], 'dados_incompletos')
        self.assertEqual(r['disciplinas_ausentes'], ['B'])
        self.assertEqual(run([], ())['status'], 'dados_incompletos')

    def test_semestre_e_grupo_sem_ofertas_aparecem(self):
        r = evaluate_trajectories({'classes': [offer('A')]}, {'CC-P1': ['A'], 'SI-P1': ['A']}, ['2026-1', '2026-2'])
        self.assertEqual(len(r['grupos']), 4)
        self.assertEqual(r['resumo']['dados_incompletos'], 3)

    def test_filtra_vagas_do_curso(self):
        r = run([offer('A'), offer('B', start='09:00', end='10:00', course='83')])
        self.assertEqual(r['status'], 'dados_incompletos')
        self.assertEqual(r['disciplinas_sem_turma_utilizavel'], ['B'])

    def test_vagas_invalidas_e_horario_parcial_sao_inconclusivos(self):
        for value in (None, '', -1, float('nan'), 1.5):
            b = offer('B')
            b['vagas_por_curso'][0]['vagas'] = value
            with self.subTest(value=value):
                self.assertEqual(run([offer('A'), b])['status'], 'dados_incompletos')
        b = offer('B')
        b['encontros'].append({'dia': 'terca', 'inicio': '', 'fim': '10:00'})
        self.assertEqual(run([offer('A'), b])['status'], 'dados_incompletos')

    def test_horario_desconhecido_impede_prova_de_impossibilidade(self):
        unknown = offer('B', 'B2')
        unknown['encontros'] = []
        self.assertEqual(run([offer('A'), offer('B'), unknown])['status'], 'dados_incompletos')
        good = offer('B', 'B3', '09:00', '10:00')
        self.assertEqual(run([offer('A'), good, unknown])['status'], 'trajetoria_encontrada')

    def test_todos_os_encontros_sao_considerados(self):
        a, b = offer('A'), offer('B', start='09:00', end='10:00')
        a['encontros'].append({'dia': 'terca', 'inicio': '08:00', 'fim': '10:00'})
        b['encontros'].append({'dia': 'terca', 'inicio': '09:00', 'fim': '11:00'})
        self.assertEqual(run([a, b])['status'], 'sem_trajetoria')

    def test_limite_nao_declara_impossibilidade(self):
        r = run([offer('A'), offer('B', start='09:00', end='10:00')], max_nodes=1)
        self.assertEqual((r['status'], r['motivo']), ('dados_incompletos', 'limite_busca'))

    def test_complemento_nao_substitui_solucao_e_nao_muta_entrada(self):
        classes = [offer('A'), offer('B')]
        original = copy.deepcopy(classes)
        extra = [offer('B', 'web:B', '09:00', '10:00')]
        self.assertEqual(run(classes, supplementary=extra)['status'], 'sem_trajetoria')
        self.assertEqual(classes, original)
        r = run([offer('A')], supplementary=extra)
        self.assertEqual(r['status'], 'trajetoria_encontrada')
        self.assertEqual(r['trajetoria'][1]['origem'], 'complemento')

    def test_compara_busca_com_enumeracao_independente(self):
        rng = random.Random(13)
        for _ in range(40):
            domains = {code: rng.sample(range(8, 12), rng.randint(1, 3)) for code in ('A', 'B', 'C')}
            feasible = any(len(set(hours)) == 3 for hours in itertools.product(*domains.values()))
            classes = [offer(code, f'{code}{h}', f'{h:02}:00', f'{h+1:02}:00') for code, hours in domains.items() for h in hours]
            result = run(classes, tuple(domains))
            self.assertEqual(result['status'], 'trajetoria_encontrada' if feasible else 'sem_trajetoria')

    def test_id_duplicado_rejeitado(self):
        with self.assertRaises(ValueError):
            run([offer('A'), offer('B', 'A')])
