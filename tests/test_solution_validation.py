import copy
import unittest

from src.solve.integrated import greedy_improve
from src.solve.validation import validate_solution
from tests.test_integrated_solver import toy_payload


class SolutionValidationTests(unittest.TestCase):
    def test_aceita_gulosa_sem_modificar_entrada(self):
        source = toy_payload()
        original = copy.deepcopy(source)
        solution, _ = greedy_improve(source)
        validate_solution(source, solution)
        self.assertEqual(source, original)

    def test_rejeita_sala_ausente_mesmo_com_score_calculavel(self):
        source = toy_payload()
        solution = copy.deepcopy(source)
        solution['classes'][0]['encontros'][0].pop('sala')
        with self.assertRaisesRegex(ValueError, 'sala ausente'):
            validate_solution(source, solution)

    def test_rejeita_alteracao_de_horario_fixo(self):
        source = toy_payload()
        solution = copy.deepcopy(source)
        solution['classes'][0]['encontros'][0]['inicio'] = '19:00'
        with self.assertRaisesRegex(ValueError, 'horario fixo'):
            validate_solution(source, solution)

    def test_rejeita_professor_nao_habilitado(self):
        source = toy_payload()
        solution = copy.deepcopy(source)
        solution['classes'][0]['professores_alocados'] = ['Terceiro']
        with self.assertRaisesRegex(ValueError, 'fora do dominio'):
            validate_solution(source, solution)

    def test_rejeita_remocao_de_turma_e_edicao_de_regra(self):
        source = toy_payload()
        for mutation in ('classes', 'min_obrigatorias_ano'):
            solution = copy.deepcopy(source)
            if mutation == 'classes':
                solution['classes'].pop()
            else:
                solution[mutation] = 0
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_solution(source, solution)
