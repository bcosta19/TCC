import unittest

import pandas as pd

from scripts.prefill_fixed_schedules_2026 import prefill


def item(class_id, origin="IC", code="TCC00001", **courses):
    return {
        "id": class_id, "origem": origin, "codigo": code,
        "vagas_por_curso": [{"codigo_curso": key, "curso": key, "vagas": value} for key, value in courses.items()],
    }


class PrefillFixedSchedulesTests(unittest.TestCase):
    def run_rule(self, classes, rows=None):
        rows = rows or [{"turma_id": c["id"], "horario_fixo": "", "validado": ""} for c in classes]
        result = prefill(pd.DataFrame(rows), {c["id"]: c for c in classes})
        return dict(zip(result["turma_id"], result["horario_fixo"])), result

    def test_any_vacancy_outside_cc_si_fixes_schedule(self):
        decisions, result = self.run_rule([
            item("a", **{"83": 30, "15": 1}),
            item("b", **{"31": 40, "83": 10}),
            item("c", origin="externa", code="GMA00001"),
        ])
        self.assertEqual(decisions, {"a": "sim", "b": "nao", "c": "sim"})
        self.assertEqual(result.loc[result["turma_id"].eq("a"), "cursos_externos"].item(), "15 (1)")
        self.assertTrue(result["validado"].eq("sim").all())

    def test_zero_vacancies_do_not_count(self):
        decisions, _ = self.run_rule([item("a", **{"31": 40, "41": 0})])
        self.assertEqual(decisions["a"], "nao")

    def test_manual_validation_is_preserved(self):
        rows = [{"turma_id": "a", "horario_fixo": "sim", "validado": "sim", "criterio_horario": "manual"}]
        decisions, _ = self.run_rule([item("a", **{"31": 40})], rows)
        self.assertEqual(decisions["a"], "sim")


if __name__ == "__main__":
    unittest.main()
