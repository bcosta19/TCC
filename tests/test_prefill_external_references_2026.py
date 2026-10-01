import json
import unittest

import pandas as pd

from scripts.prefill_external_references_2026 import ALTERNATIVE, REFERENCE, prefill


def offer(code, turma, schedule, vacancies, course="31", treatment="", enrolled=0):
    return {
        "semestre": "2026-1", "codigo": code, "turma": turma, "horarios": schedule,
        "periodo_curricular": "", "tratamento_no_modelo": treatment,
        "vagas_por_curso": json.dumps([{"codigo_curso": course, "vagas": vacancies, "inscritos": enrolled}]),
    }


class PrefillExternalReferencesTests(unittest.TestCase):
    def treatments(self, table):
        return dict(zip(table["codigo"] + "-" + table["turma"], table["tratamento_no_modelo"]))

    def test_picks_largest_offer_for_the_course(self):
        table = pd.DataFrame([
            offer("GMA1", "A1", "Seg 07:00-09:00", 10),
            offer("GMA1", "B1", "Ter 07:00-09:00", 50),
            offer("GMA1", "C1", "Qua 07:00-09:00", 90, course="99"),
        ])
        result = self.treatments(prefill(table, {"GMA1": ["CC-P1"]}))
        self.assertEqual(result, {"GMA1-A1": ALTERNATIVE, "GMA1-B1": REFERENCE, "GMA1-C1": ALTERNATIVE})

    def test_avoids_clash_between_references_of_the_same_period(self):
        table = pd.DataFrame([
            offer("GAN1", "A1", "Ter 14:00-16:00", 40),
            offer("GMA2", "A1", "Ter 14:00-16:00", 60),
            offer("GMA2", "B1", "Qui 14:00-16:00", 30),
        ])
        result = prefill(table, {"GAN1": ["CC-P3"], "GMA2": ["CC-P3"]})
        self.assertEqual(self.treatments(result)["GMA2-B1"], REFERENCE)
        self.assertEqual(self.treatments(result)["GMA2-A1"], ALTERNATIVE)
        self.assertEqual(set(result.loc[result["tratamento_no_modelo"].eq(REFERENCE), "periodo_curricular"]), {"CC-P3"})

    def test_enrollment_beats_offered_vacancies(self):
        table = pd.DataFrame([
            offer("GMA1", "A1", "Seg 07:00-09:00", 60, enrolled=10),
            offer("GMA1", "B1", "Ter 07:00-09:00", 40, enrolled=30),
        ])
        result = prefill(table, {"GMA1": ["CC-P1"]})
        self.assertEqual(self.treatments(result)["GMA1-B1"], REFERENCE)
        self.assertEqual(result.loc[result["turma"].eq("B1"), "inscritos_curso_pct"].item(), "75")

    def test_keeps_human_decisions(self):
        table = pd.DataFrame([
            offer("GMA1", "A1", "Seg 07:00-09:00", 10, treatment="ignorar_fora_do_ic"),
            offer("GMA1", "B1", "Ter 07:00-09:00", 50),
        ])
        result = self.treatments(prefill(table, {"GMA1": ["CC-P1"]}))
        self.assertEqual(result["GMA1-A1"], "ignorar_fora_do_ic")


if __name__ == "__main__":
    unittest.main()
