import unittest

import pandas as pd

from src.eval.evaluator import QHEvaluator
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


if __name__ == "__main__":
    unittest.main()
