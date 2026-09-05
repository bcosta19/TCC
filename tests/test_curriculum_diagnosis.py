import copy
import unittest

from scripts.diagnose_curriculum_conflicts_2026 import diagnose
from tests.test_integrated_solver import toy_payload


class CurriculumDiagnosisTests(unittest.TestCase):
    def conflicted(self):
        payload = toy_payload()
        a, b = payload['classes']
        b['grupos_curriculares'] = a['grupos_curriculares'][:]
        b['encontros'] = copy.deepcopy(a['encontros'])
        return payload

    def test_choque_entre_ofertas_pode_ter_alternativa_cursavel(self):
        payload = self.conflicted()
        alternative = copy.deepcopy(payload['classes'][1])
        alternative['id'] = 'b-alternativa'
        alternative['encontros'][0]['dia'] = 'sexta'
        payload['classes'].append(alternative)
        conflicts, witnesses = diagnose(payload)
        self.assertEqual(len(conflicts), 1)
        self.assertTrue(witnesses[0]['escolha_sem_choque'])
        self.assertIn('b-alternativa', witnesses[0]['turmas'])

    def test_sem_alternativa_nao_existe_escolha(self):
        conflicts, witnesses = diagnose(self.conflicted())
        self.assertEqual(len(conflicts), 1)
        self.assertFalse(witnesses[0]['escolha_sem_choque'])

    def test_secoes_identicas_nao_duplicam_contador(self):
        payload = self.conflicted()
        duplicate = copy.deepcopy(payload['classes'][1])
        duplicate['id'] = 'b-outra'
        payload['classes'].append(duplicate)
        conflicts, _ = diagnose(payload)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(set(conflicts[0]['turmas_b'].split(';')), {'b', 'b-outra'})
