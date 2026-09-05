import copy
import random
import unittest

from src.solve.direct_objective import evaluate, teachers_for_item
from src.solve.integrated import (
    apply_move,
    greedy_improve,
    objective_key,
    propose_move,
    search_energy,
    solve_sa,
    solve_vns,
)
from scripts.build_synthetic_instance_2026 import h12_matching


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
                "professores_observados": ["Bruno"],
                "professores_habilitados": ["Ana", "Bruno"],
                "preferencias_professores": {"Ana": 0.0, "Bruno": 1.0},
                "capacidade_turma": 35,
                "horario_fixo": True,
                "sala_fixa": False,
                "encontros": [
                    {
                        "dia": "quarta",
                        "inicio": "07:00",
                        "fim": "09:00",
                        "sala": "302",
                        "requer_laboratorio": False,
                    }
                ],
            },
        ],
    }


class IntegratedSolverTests(unittest.TestCase):
    def test_current_assignment_precedes_observed_assignment(self):
        item = toy_payload()["classes"][0]
        self.assertEqual(teachers_for_item(item), ["Ana"])

    def test_non_consecutive_days_use_real_rest_interval(self):
        result = evaluate(toy_payload())
        self.assertEqual(result["hard"]["descanso_insuficiente"], 0)

    def test_explicit_h12_universe_does_not_expand_from_assignments(self):
        payload = toy_payload()
        payload["teachers"][1]["incluido_h12"] = False
        result = evaluate(payload)
        self.assertEqual(result["hard"]["carga_anual_insuficiente"], 0)
        self.assertEqual(result["guidance"]["deficit_carga_anual"], 0.0)

    def test_greedy_uses_h12_deficit_as_progress(self):
        payload = {
            "min_obrigatorias_ano": 3,
            "prioridades_professores": {"Ana": 1.0, "Bruno": 1.0},
            "teachers": [
                {"name": "Ana", "incluido_h12": True},
                {"name": "Bruno", "incluido_h12": True},
            ],
            "rooms": [],
            "classes": [],
        }
        for index in range(6):
            payload["classes"].append({
                "id": f"c{index}",
                "semestre": "2026-1",
                "codigo": f"TCC{index:05d}",
                "curso": "CC",
                "origem": "IC",
                "obrigatoria": True,
                "professor": "Bruno",
                "professores_alocados": ["Bruno"],
                "professores_habilitados": ["Ana", "Bruno"],
                "preferencias_professores": {"Ana": 0.0, "Bruno": 0.0},
                "horario_fixo": True,
                "sala_fixa": True,
                "encontros": [],
            })
        initial = evaluate(payload)
        self.assertEqual(initial["hard"]["carga_anual_insuficiente"], 1)
        self.assertEqual(initial["guidance"]["deficit_carga_anual"], 3.0)
        _solution, metadata = greedy_improve(payload, max_candidates=2)
        self.assertEqual(metadata["best"]["hard"]["carga_anual_insuficiente"], 0)
        self.assertEqual(metadata["best"]["guidance"]["deficit_carga_anual"], 0.0)

    def test_implicit_h12_universe_uses_obligatory_teachers_only(self):
        payload = toy_payload()
        payload["teachers"] = []
        payload["min_obrigatorias_ano"] = 3
        payload["classes"][1]["obrigatoria"] = False
        result = evaluate(payload)
        self.assertEqual(result["hard"]["carga_anual_insuficiente"], 1)
        self.assertEqual(result["guidance"]["deficit_carga_anual"], 2.0)

    def test_search_rejects_unavailable_h12(self):
        result = evaluate(toy_payload())
        result["guidance"]["deficit_carga_anual"] = None
        with self.assertRaisesRegex(ValueError, "H12 indisponivel"):
            search_energy(result)

    def test_move_and_reverse_restore_payload(self):
        payload = toy_payload()
        original = copy.deepcopy(payload)
        move = {
            "kind": "room",
            "class_index": 0,
            "meeting_index": 0,
            "new_room": "304",
        }
        undo = apply_move(payload, move)
        apply_move(payload, undo)
        self.assertEqual(payload, original)

    def test_teacher_move_and_reverse_restore_payload(self):
        payload = toy_payload()
        original = copy.deepcopy(payload)
        undo = apply_move(payload, {"kind": "teacher", "class_index": 0, "new_teacher": "Bruno"})
        apply_move(payload, undo)
        self.assertEqual(payload, original)

    def test_schedule_move_and_reverse_restore_payload(self):
        payload = toy_payload()
        payload["classes"][0]["horario_fixo"] = False
        payload["classes"][0]["dominio_horarios"] = [
            [{"dia": "segunda", "inicio": "20:00", "fim": "22:00"}],
            [{"dia": "terca", "inicio": "18:00", "fim": "20:00"}],
        ]
        original = copy.deepcopy(payload)
        undo = apply_move(payload, {"kind": "schedule", "class_index": 0, "pattern_index": 1})
        apply_move(payload, undo)
        self.assertEqual(payload, original)

    def test_random_move_is_reproducible(self):
        first = propose_move(toy_payload(), random.Random(7))
        second = propose_move(toy_payload(), random.Random(7))
        self.assertEqual(first, second)

    def test_greedy_never_worsens_objective(self):
        payload = toy_payload()
        initial = evaluate(payload)
        _solution, metadata = greedy_improve(payload, max_candidates=2)
        self.assertLessEqual(objective_key(metadata["best"]), objective_key(initial))

    def test_sa_is_deterministic_for_same_seed(self):
        payload = toy_payload()
        config = {"avaliacoes": 30, "temperatura_inicial": 1000.0, "resfriamento": 0.99}
        first = solve_sa(payload, 42, config)
        second = solve_sa(payload, 42, config)
        self.assertEqual(first.evaluation, second.evaluation)
        self.assertEqual(first.solution, second.solution)

    def test_vns_terminates_when_room_has_no_alternative(self):
        payload = toy_payload()
        payload["rooms"] = [payload["rooms"][0]]
        for item in payload["classes"]:
            item["professor_fixo"] = True
        config = {"avaliacoes": 30, "tentativas_busca_local": 5}
        result = solve_vns(payload, 42, config)
        self.assertEqual(result.metadata["evaluations"], 1)

    def test_capacity_violation_is_counted_once_per_class_and_room(self):
        payload = toy_payload()
        payload["rooms"][0]["capacidade_estimada"] = 20
        payload["classes"][1]["encontros"][0]["sala"] = "304"
        payload["classes"][0]["encontros"].append({
            "dia": "terca",
            "inicio": "20:00",
            "fim": "22:00",
            "sala": "302",
            "requer_laboratorio": False,
        })
        result = evaluate(payload)
        self.assertEqual(result["hard"]["capacidade_insuficiente"], 1)

    def test_h12_matching_detects_competing_teacher_domains(self):
        classes = []
        for index in range(3):
            classes.append({
                "id": f"c{index}",
                "origem": "IC",
                "obrigatoria": True,
                "professor_fixo": False,
                "professores_habilitados": ["Ana", "Bruno"],
            })
        matched, required = h12_matching(classes, {"Ana", "Bruno"}, 2)
        self.assertEqual((matched, required), (3, 4))
        classes.append({
            "id": "c3",
            "origem": "IC",
            "obrigatoria": True,
            "professor_fixo": False,
            "professores_habilitados": ["Ana", "Bruno"],
        })
        matched, required = h12_matching(classes, {"Ana", "Bruno"}, 2)
        self.assertEqual((matched, required), (4, 4))


if __name__ == "__main__":
    unittest.main()
