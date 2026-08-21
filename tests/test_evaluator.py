import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.eval.evaluator import QHEvaluator, evaluate_json
from src.eval.rooms import room_metadata


def class_row(class_id, semester, code, name, course, period, teacher, capacity="40"):
    return {
        "id": class_id,
        "semestre": semester,
        "curso": course,
        "periodo": period,
        "codigo": code,
        "disciplina": name,
        "turma": "A1",
        "setor": "TESTE",
        "alocacao": teacher,
        "capacidade": capacity,
    }


def meeting(class_id, semester, day="terca", start="09:00", end="11:00", room="302", code="TESTE"):
    return {
        "turma_id": class_id,
        "semestre": semester,
        "codigo": code,
        "turma": "A1",
        "dia": day,
        "inicio": start,
        "fim": end,
        "sala": room,
        "valor_original": f"{start}-{end} {room}",
    }


def evaluate(classes, meetings, rooms=None):
    room_frame = pd.DataFrame(rooms or [])
    return QHEvaluator(pd.DataFrame(classes), pd.DataFrame(meetings), room_frame).evaluate()


class EvaluatorTests(unittest.TestCase):
    def test_room_conflict(self):
        classes = [
            class_row("a", "2025-1", "TCC00001", "A", "31", "CC-P1", "Ana"),
            class_row("b", "2025-1", "TCC00002", "B", "31", "CC-P2", "Bruno"),
        ]
        result = evaluate(classes, [meeting("a", "2025-1"), meeting("b", "2025-1")])
        self.assertEqual(result.hard["conflitos_sala"], 1)

    def test_teacher_conflict(self):
        classes = [
            class_row("a", "2025-1", "TCC00001", "A", "31", "CC-P1", "Ana"),
            class_row("b", "2025-1", "TCC00002", "B", "31", "CC-P2", "Ana"),
        ]
        result = evaluate(classes, [meeting("a", "2025-1", room="302"), meeting("b", "2025-1", room="304")])
        self.assertEqual(result.hard["conflitos_professor"], 1)

    def test_curriculum_conflict(self):
        classes = [
            class_row("a", "2025-1", "TCC00001", "A", "31", "CC-P1", "Ana"),
            class_row("b", "2025-1", "TCC00002", "B", "31", "CC-P1", "Bruno"),
        ]
        result = evaluate(classes, [meeting("a", "2025-1", code="TCC00001"), meeting("b", "2025-1", room="304", code="TCC00002")])
        self.assertEqual(result.hard["conflitos_curriculares"], 1)

    def test_parallel_sections_do_not_create_curriculum_conflict(self):
        classes = [
            class_row("a", "2025-1", "TCC00001", "A", "31", "CC-P1-A", "Ana"),
            class_row("b", "2025-1", "TCC00001", "A", "31", "CC-P1-B", "Bruno"),
        ]
        result = evaluate(classes, [meeting("a", "2025-1", code="TCC00001"), meeting("b", "2025-1", room="304", code="TCC00001")])
        self.assertEqual(result.hard["conflitos_curriculares"], 0)

    def test_shared_class_participates_in_both_curriculum_groups(self):
        classes = [
            class_row("shared", "2026-1", "TCC00001", "A", "CC;SI", "", "Ana"),
            class_row("cc", "2026-1", "TCC00002", "B", "CC", "", "Bruno"),
            class_row("si", "2026-1", "TCC00003", "C", "SI", "", "Carla"),
        ]
        classes[0]["grupos_curriculares"] = ["CC-P1", "SI-P2"]
        classes[1]["grupos_curriculares"] = ["CC-P1"]
        classes[2]["grupos_curriculares"] = ["SI-P2"]
        meetings = [
            meeting("shared", "2026-1", code="TCC00001"),
            meeting("cc", "2026-1", room="304", code="TCC00002"),
            meeting("si", "2026-1", room="306", code="TCC00003"),
        ]
        result = evaluate(classes, meetings)
        self.assertEqual(result.hard["conflitos_curriculares"], 2)

    def test_capacity_and_waste(self):
        classes = [class_row("a", "2025-1", "TCC00001", "A", "31", "CC-P1", "Ana", "60")]
        rooms = [{"id": "302", "capacidade_estimada": "50"}]
        result = evaluate(classes, [meeting("a", "2025-1")], rooms)
        self.assertEqual(result.hard["capacidade_insuficiente"], 1)
        self.assertEqual(result.soft["desperdicio_capacidade"], 0.0)

    def test_window(self):
        classes = [class_row("a", "2025-1", "TCC00001", "A", "31", "CC-P1", "Ana")]
        meetings = [
            meeting("a", "2025-1", start="07:00", end="09:00"),
            meeting("a", "2025-1", start="11:00", end="13:00", room="304"),
        ]
        result = evaluate(classes, meetings)
        self.assertEqual(result.soft["janelas"], 1)

    def test_rotation(self):
        classes = [
            class_row("a", "2025-1", "TCC00001", "A", "31", "CC-P1", "Ana"),
            class_row("b", "2025-2", "TCC00001", "A", "31", "CC-P1", "Ana"),
        ]
        meetings = [meeting("a", "2025-1"), meeting("b", "2025-2")]
        result = evaluate(classes, meetings)
        self.assertEqual(result.soft["rodizio_semestre"], 1)

    def test_rotation_is_not_hardcoded_to_2025(self):
        classes = [
            class_row("a", "2026-1", "TCC00001", "A", "31", "CC-P1", "Ana"),
            class_row("b", "2026-2", "TCC00001", "A", "31", "CC-P1", "Ana"),
        ]
        meetings = [meeting("a", "2026-1"), meeting("b", "2026-2")]
        result = evaluate(classes, meetings)
        self.assertEqual(result.soft["rodizio_semestre"], 1)

    def test_annual_obligatory_load(self):
        classes = [
            class_row("a", "2025-1", "TCC00001", "A", "31", "CC-P1", "Ana"),
            class_row("b", "2025-1", "TCC00002", "B", "31", "CC-P1", "Ana"),
            class_row("c", "2025-2", "TCC00003", "C", "31", "CC-P2", "Ana"),
            class_row("d", "2025-1", "TCC00004", "D", "31", "CC-P2", "Bruno"),
            class_row("e", "2025-2", "TCC00005", "E", "31", "CC-P3", "Bruno"),
        ]
        for row in classes:
            row["obrigatoria"] = True
        meetings = [
            meeting("a", "2025-1", start="07:00", end="09:00", room="302"),
            meeting("b", "2025-1", start="09:00", end="11:00", room="304"),
            meeting("c", "2025-2", start="07:00", end="09:00", room="302"),
            meeting("d", "2025-1", start="11:00", end="13:00", room="304"),
            meeting("e", "2025-2", start="09:00", end="11:00", room="304"),
        ]
        result = evaluate(classes, meetings)
        self.assertEqual(result.hard["carga_anual_insuficiente"], 1)

    def test_annual_load_includes_unassigned_teacher(self):
        classes = [
            class_row("a", "2025-1", "TCC00001", "A", "31", "CC-P1", "Ana"),
            class_row("b", "2025-1", "TCC00002", "B", "31", "CC-P1", "Ana"),
            class_row("c", "2025-2", "TCC00003", "C", "31", "CC-P2", "Ana"),
        ]
        for row in classes:
            row["obrigatoria"] = True
        class_frame = pd.DataFrame(classes)
        class_frame.attrs["professores_ic"] = ["Ana", "Bruno"]
        result = QHEvaluator(
            class_frame,
            pd.DataFrame([meeting("a", "2025-1"), meeting("b", "2025-1", room="304"), meeting("c", "2025-2")]),
        ).evaluate()
        self.assertEqual(result.hard["carga_anual_insuficiente"], 1)

    def test_weighted_preference_is_a_bonus(self):
        classes = [class_row("a", "2025-1", "TCC00001", "A", "31", "CC-P1", "Ana")]
        classes[0]["preferencia"] = 0.75
        classes[0]["prioridade"] = 0.8
        result = evaluate(classes, [meeting("a", "2025-1")])
        self.assertAlmostEqual(result.soft["preferencia_priorizada"], -0.6)

    def test_distance_is_not_an_evaluation_criterion(self):
        classes = [class_row("a", "2025-1", "TCC00001", "A", "31", "CC-P1", "Ana")]
        result = evaluate(classes, [meeting("a", "2025-1")])
        self.assertNotIn("distancia", result.soft)

    def test_lab_resource_mismatch(self):
        classes = [class_row("a", "2025-1", "TCC00001", "A", "31", "CC-P1", "Ana")]
        meetings = [meeting("a", "2025-1", room="308")]
        meetings[0]["requer_laboratorio"] = True
        result = evaluate(classes, meetings)
        self.assertEqual(result.hard["recursos_incompativeis"], 1)

    def test_lab_room_matches_lab_resource(self):
        classes = [class_row("a", "2025-1", "TCC00001", "A", "31", "CC-P1", "Ana")]
        meetings = [meeting("a", "2025-1", room="L307")]
        meetings[0]["requer_laboratorio"] = True
        result = evaluate(classes, meetings)
        self.assertEqual(result.hard["recursos_incompativeis"], 0)

    def test_lab_room_metadata(self):
        metadata = room_metadata("L307")
        self.assertTrue(metadata["laboratorio"])
        self.assertEqual(metadata["recursos"], ["laboratorio"])

    def test_partially_overlapping_intervals_trigger_room_conflict(self):
        classes = [
            class_row("a", "2026-1", "TCC00001", "A", "31", "CC-P1", "Ana"),
            class_row("b", "2026-1", "TCC00002", "B", "31", "CC-P2", "Bruno"),
        ]
        meetings = [
            meeting("a", "2026-1", start="08:00", end="10:00", room="302"),
            meeting("b", "2026-1", start="09:00", end="11:00", room="302"),
        ]
        result = evaluate(classes, meetings)
        self.assertEqual(result.hard["conflitos_sala"], 1)

    def test_adjacent_intervals_do_not_trigger_room_conflict(self):
        classes = [
            class_row("a", "2026-1", "TCC00001", "A", "31", "CC-P1", "Ana"),
            class_row("b", "2026-1", "TCC00002", "B", "31", "CC-P2", "Bruno"),
        ]
        meetings = [
            meeting("a", "2026-1", start="08:00", end="10:00", room="302"),
            meeting("b", "2026-1", start="10:00", end="12:00", room="302"),
        ]
        result = evaluate(classes, meetings)
        self.assertEqual(result.hard["conflitos_sala"], 0)

    def test_partially_overlapping_intervals_trigger_teacher_conflict(self):
        classes = [
            class_row("a", "2026-1", "TCC00001", "A", "31", "CC-P1", "Ana"),
            class_row("b", "2026-1", "TCC00002", "B", "31", "CC-P2", "Ana"),
        ]
        meetings = [
            meeting("a", "2026-1", start="08:00", end="10:00", room="302"),
            meeting("b", "2026-1", start="09:00", end="11:00", room="304"),
        ]
        result = evaluate(classes, meetings)
        self.assertEqual(result.hard["conflitos_professor"], 1)

    def test_adjacent_intervals_do_not_trigger_teacher_conflict(self):
        classes = [
            class_row("a", "2026-1", "TCC00001", "A", "31", "CC-P1", "Ana"),
            class_row("b", "2026-1", "TCC00002", "B", "31", "CC-P2", "Ana"),
        ]
        meetings = [
            meeting("a", "2026-1", start="08:00", end="10:00", room="302"),
            meeting("b", "2026-1", start="10:00", end="12:00", room="304"),
        ]
        result = evaluate(classes, meetings)
        self.assertEqual(result.hard["conflitos_professor"], 0)

    def test_co_teaching_conflict_for_both_teachers(self):
        classes = [
            class_row("a", "2026-1", "TCC00001", "A", "31", "CC-P1", ""),
            class_row("b", "2026-1", "TCC00002", "B", "31", "CC-P2", ""),
        ]
        classes[0]["professores_observados"] = ["Ana", "Bruno"]
        classes[1]["professores_observados"] = ["Ana", "Bruno"]
        meetings = [
            meeting("a", "2026-1", start="08:00", end="10:00", room="302"),
            meeting("b", "2026-1", start="09:00", end="11:00", room="304"),
        ]
        result = evaluate(classes, meetings)
        self.assertEqual(result.hard["conflitos_professor"], 2)

    def test_co_teaching_conflict_for_single_teacher(self):
        classes = [
            class_row("a", "2026-1", "TCC00001", "A", "31", "CC-P1", ""),
            class_row("b", "2026-1", "TCC00002", "B", "31", "CC-P2", "Ana"),
        ]
        classes[0]["professores_observados"] = ["Ana", "Bruno"]
        meetings = [
            meeting("a", "2026-1", start="08:00", end="10:00", room="302"),
            meeting("b", "2026-1", start="09:00", end="11:00", room="304"),
        ]
        result = evaluate(classes, meetings)
        self.assertEqual(result.hard["conflitos_professor"], 1)

    def test_co_teaching_does_not_double_count_physical_classes(self):
        classes = [class_row("a", "2026-1", "TCC00001", "A", "31", "CC-P1", "")]
        classes[0]["professores_observados"] = ["Ana", "Bruno"]
        meetings = [meeting("a", "2026-1", start="08:00", end="10:00", room="302")]
        result = evaluate(classes, meetings)
        self.assertEqual(result.hard["conflitos_sala"], 0)
        self.assertEqual(result.hard["conflitos_professor"], 0)
        self.assertEqual(result.soft["dias_trabalhados"], 2)

    def test_co_teaching_working_days_and_windows(self):
        classes = [
            class_row("a", "2026-1", "TCC00001", "A", "31", "CC-P1", ""),
            class_row("b", "2026-1", "TCC00002", "B", "31", "CC-P2", "Ana"),
        ]
        classes[0]["professores_observados"] = ["Ana", "Bruno"]
        meetings = [
            meeting("a", "2026-1", start="08:00", end="10:00", room="302"),
            meeting("b", "2026-1", start="14:00", end="16:00", room="304"),
        ]
        result = evaluate(classes, meetings)
        # Ana works Monday, Bruno works Monday -> total 2 working days
        self.assertEqual(result.soft["dias_trabalhados"], 2)
        # Ana has 10:00 to 14:00 gap (4h = 2 windows of 2h)
        self.assertEqual(result.soft["janelas"], 2)

    def test_cotutoria_without_policy_makes_h12_unavailable(self):
        classes = [
            class_row("a", "2026-1", "TCC00001", "A", "31", "CC-P1", ""),
            class_row("b", "2026-1", "TCC00002", "B", "31", "CC-P2", "Carla"),
            class_row("c", "2026-2", "TCC00003", "C", "31", "CC-P1", "Carla"),
            class_row("d", "2026-2", "TCC00004", "D", "31", "CC-P2", "Carla"),
        ]
        classes[0]["professores_observados"] = ["Ana", "Bruno"]
        for row in classes:
            row["obrigatoria"] = True
        class_frame = pd.DataFrame(classes)
        class_frame.attrs["professores_ic"] = ["Ana", "Bruno", "Carla"]
        # Without policy attribute
        result = QHEvaluator(
            class_frame,
            pd.DataFrame([meeting("a", "2026-1"), meeting("b", "2026-1"), meeting("c", "2026-2"), meeting("d", "2026-2")]),
        ).evaluate()
        self.assertIsNone(result.hard["carga_anual_insuficiente"])

    def test_cotutoria_with_integral_policy(self):
        classes = [
            class_row("a", "2026-1", "TCC00001", "A", "31", "CC-P1", ""),
            class_row("b", "2026-1", "TCC00002", "B", "31", "CC-P2", "Ana"),
            class_row("c", "2026-2", "TCC00003", "C", "31", "CC-P1", "Ana"),
            class_row("d", "2026-1", "TCC00004", "D", "31", "CC-P2", "Bruno"),
            class_row("e", "2026-2", "TCC00005", "E", "31", "CC-P3", "Bruno"),
        ]
        classes[0]["professores_observados"] = ["Ana", "Bruno"]
        for row in classes:
            row["obrigatoria"] = True
        class_frame = pd.DataFrame(classes)
        class_frame.attrs["professores_ic"] = ["Ana", "Bruno"]
        class_frame.attrs["politica_cotutoria"] = {
            "a": {"politica_h12": "integral_para_cada_docente"}
        }
        result = QHEvaluator(
            class_frame,
            pd.DataFrame([
                meeting("a", "2026-1"), meeting("b", "2026-1", room="304"),
                meeting("c", "2026-2"), meeting("d", "2026-1", room="306"),
                meeting("e", "2026-2", room="308")
            ]),
        ).evaluate()
        # Ana has 1+1+1=3, Bruno has 1+1+1=3 -> 0 violations
        self.assertEqual(result.hard["carga_anual_insuficiente"], 0)

    def test_cotutoria_with_single_responsible_policy(self):
        classes = [
            class_row("a", "2026-1", "TCC00001", "A", "31", "CC-P1", ""),
            class_row("b", "2026-1", "TCC00002", "B", "31", "CC-P2", "Ana"),
            class_row("c", "2026-2", "TCC00003", "C", "31", "CC-P1", "Ana"),
            class_row("d", "2026-1", "TCC00004", "D", "31", "CC-P2", "Bruno"),
            class_row("e", "2026-2", "TCC00005", "E", "31", "CC-P3", "Bruno"),
        ]
        classes[0]["professores_observados"] = ["Ana", "Bruno"]
        for row in classes:
            row["obrigatoria"] = True
        class_frame = pd.DataFrame(classes)
        class_frame.attrs["professores_ic"] = ["Ana", "Bruno"]
        class_frame.attrs["politica_cotutoria"] = {
            "a": {
                "politica_h12": "contar_para_um_responsavel",
                "professor_responsavel": "Ana"
            }
        }
        result = QHEvaluator(
            class_frame,
            pd.DataFrame([
                meeting("a", "2026-1"), meeting("b", "2026-1", room="304"),
                meeting("c", "2026-2"), meeting("d", "2026-1", room="306"),
                meeting("e", "2026-2", room="308")
            ]),
        ).evaluate()
        # Ana has 1+1+1=3, Bruno has 0+1+1=2 (< 3) -> 1 violation
        self.assertEqual(result.hard["carga_anual_insuficiente"], 1)


    def test_incomplete_instance_is_not_evaluated_as_experimental(self):
        payload = {
            "pronta_para_experimento": False,
            "profile": "dados_observados_incompletos",
            "classes": [],
            "rooms": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "instance.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "pronta_para_experimento=false"):
                evaluate_json(path)


if __name__ == "__main__":
    unittest.main()
