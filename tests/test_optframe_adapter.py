"""Testes do adaptador pyoptframe (busca nativa BasicSA).

Valida que o engine OptFrame, sobre o mesmo payload e o mesmo avaliador de
referencia, produz solucao nunca pior que a gulosa de entrada e que o
movimento de ida e reversivel (paridade com apply_move/undo da referencia).
"""

import copy
import unittest

from src.solve.direct_objective import evaluate
from src.solve.integrated import objective_key, search_energy
from src.solve.optframe_adapter import (
    NSIntegrated,
    MoveTCC,
    ProblemTimetable,
    SolutionTimetable,
    solve_sa_optframe,
)


def toy_payload():
    return {
        "min_obrigatorias_ano": 1,
        "prioridades_professores": {"Ana": 1.0, "Bruno": 1.0},
        "teachers": [
            {"name": "Ana", "incluido_h12": True},
            {"name": "Bruno", "incluido_h12": True},
        ],
        "rooms": [
            {"id": "302", "capacidade_estimada": 40, "laboratorio": False},
            {"id": "304", "capacidade_estimada": 50, "laboratorio": False},
        ],
        "classes": [
            {
                "id": "a",
                "semestre": "2026-1",
                "codigo": "TCC00001",
                "curso": "CC",
                "origem": "IC",
                "obrigatoria": True,
                "grupos_curriculares": ["CC-P1"],
                "professor": "Ana",
                "professores_alocados": ["Ana"],
                "professores_observados": ["Bruno"],
                "professores_habilitados": ["Ana", "Bruno"],
                "preferencias_professores": {"Ana": 1.0, "Bruno": 0.0},
                "capacidade_turma": 35,
                "horario_fixo": True,
                "sala_fixa": False,
                "encontros": [
                    {
                        "dia": "segunda",
                        "inicio": "20:00",
                        "fim": "22:00",
                        "sala": "302",
                        "requer_laboratorio": False,
                    }
                ],
            },
            {
                "id": "b",
                "semestre": "2026-1",
                "codigo": "TCC00002",
                "curso": "CC",
                "origem": "IC",
                "obrigatoria": True,
                "grupos_curriculares": ["CC-P2"],
                "professor": "Bruno",
                "professores_alocados": ["Bruno"],
                "professores_observados": ["Ana"],
                "professores_habilitados": ["Ana", "Bruno"],
                "preferencias_professores": {"Bruno": 1.0, "Ana": 0.0},
                "capacidade_turma": 45,
                "horario_fixo": True,
                "sala_fixa": False,
                "encontros": [
                    {
                        "dia": "terca",
                        "inicio": "20:00",
                        "fim": "22:00",
                        "sala": "304",
                        "requer_laboratorio": False,
                    }
                ],
            },
        ],
    }


class TestOptframeAdapter(unittest.TestCase):
    def test_protocolos_de_composicao(self):
        payload = toy_payload()
        p = ProblemTimetable(payload)
        sol = SolutionTimetable(payload)
        self.assertEqual(ProblemTimetable.minimize(p, sol) > 0, True)
        self.assertEqual(p.evaluations, 1)

    def test_engine_avalia_igual_referencia(self):
        payload = toy_payload()
        p = ProblemTimetable(payload, greedy_start=False)
        sol = SolutionTimetable(payload)
        energia_engine = ProblemTimetable.minimize(p, sol)
        energia_ref = search_energy(evaluate(payload))
        self.assertAlmostEqual(energia_engine, energia_ref)

    def test_random_move_reversivel(self):
        payload = toy_payload()
        p = ProblemTimetable(payload, greedy_start=False)
        p.rng.seed(7)
        sol = SolutionTimetable(payload)
        original = copy.deepcopy(sol.payload)
        for _ in range(20):
            mv = NSIntegrated.randomMove(p, sol)
            reverse = mv.apply(p, sol)
            reverse.apply(p, sol)  # desfaz: volta ao estado original
            self.assertEqual(sol.payload, original)

    def test_movimentos_desfazem_e_refazem_estado_completo(self):
        moves = [
            {'kind': 'teacher', 'class_index': 0, 'new_teacher': 'Bruno'},
            {'kind': 'room', 'class_index': 0, 'meeting_index': 0, 'new_room': '304'},
            {'kind': 'schedule', 'class_index': 0, 'pattern_index': 0},
        ]
        for move in moves:
            payload = toy_payload()
            payload['classes'][0]['dominio_horarios'] = [[
                {'dia': 'sexta', 'inicio': '08:00', 'fim': '10:00'}]]
            original = copy.deepcopy(payload)
            p = ProblemTimetable(payload, greedy_start=False)
            sol = SolutionTimetable(payload)
            with self.subTest(kind=move['kind']):
                reverse = MoveTCC(move).apply(p, sol)
                changed = copy.deepcopy(sol.payload)
                redo = reverse.apply(p, sol)
                self.assertEqual(sol.payload, original)
                redo.apply(p, sol)
                self.assertEqual(sol.payload, changed)

    def test_sa_optframe_nunca_pior_que_gulosa(self):
        payload = toy_payload()
        best_payload, evaluation, meta = solve_sa_optframe(
            payload, seed=101, seconds=2.0, greedy_start=True
        )
        from src.solve.integrated import greedy_improve

        greedy_sol, greedy_meta = greedy_improve(payload)
        greedy_eval = evaluate(greedy_sol)
        self.assertLessEqual(objective_key(evaluation), objective_key(greedy_eval))
        self.assertEqual(evaluate(best_payload), evaluation)
        self.assertIn("engine_evaluations", meta)
        self.assertGreater(meta["engine_evaluations"], 0)

    def test_rejeita_tempo_invalido_antes_do_callback_nativo(self):
        for seconds in (0, -1, float("nan"), float("inf")):
            with self.subTest(seconds=seconds), self.assertRaises(ValueError):
                solve_sa_optframe(toy_payload(), seed=1, seconds=seconds)

    def test_rejeita_h12_indisponivel_antes_do_callback_nativo(self):
        payload = toy_payload()
        payload["classes"][0]["professores_alocados"] = ["Ana", "Bruno"]
        with self.assertRaisesRegex(ValueError, "H12 indisponivel"):
            solve_sa_optframe(payload, seed=1, seconds=1)


if __name__ == "__main__":
    unittest.main()
