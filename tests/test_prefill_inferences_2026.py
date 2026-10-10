import unittest

import pandas as pd

from scripts.prefill_inferences_2026 import (
    prefill_external,
    prefill_priorities,
    prefill_qualifications,
    prefill_resources,
    prefill_rooms,
    prefill_sectors,
)


class PrefillRoomsTests(unittest.TestCase):
    def test_capacity_is_largest_observed_vacancy(self):
        result = prefill_rooms(pd.DataFrame([
            {"sala": "202", "capacidade_minima_observada": "61", "capacidade_fisica": "", "validado": ""},
            {"sala": "999", "capacidade_minima_observada": "", "capacidade_fisica": "", "validado": ""},
        ]))
        self.assertEqual(result["capacidade_fisica"].tolist(), ["61", ""])
        self.assertEqual(result["validado"].tolist(), ["sim", ""])
        self.assertTrue(result.loc[0, "criterio_capacidade"].startswith("HP3"))

    def test_manual_capacity_is_preserved(self):
        result = prefill_rooms(pd.DataFrame([
            {"sala": "202", "capacidade_minima_observada": "61", "capacidade_fisica": "80", "validado": "sim"},
        ]))
        self.assertEqual(result.loc[0, "capacidade_fisica"], "80")


class PrefillResourcesTests(unittest.TestCase):
    def row(self, code, common, lab, **extra):
        return {"codigo": code, "usou_sala_comum": common, "usou_laboratorio": lab,
                "requer_laboratorio": "", "validado": "", **extra}

    def test_lab_usage_is_decided_per_code(self):
        result = prefill_resources(pd.DataFrame([
            self.row("TCC1", "False", "True"),
            self.row("TCC2", "False", "True"),
            self.row("TCC2", "True", "False"),
            self.row("TCC3", "True", "False"),
        ]))
        self.assertEqual(result["requer_laboratorio"].tolist(), ["sim", "sim", "sim", "nao"])
        self.assertIn("alternou", result.loc[2, "criterio_laboratorio"])
        self.assertTrue(result["validado"].eq("sim").all())

    def test_manual_decision_is_preserved(self):
        result = prefill_resources(pd.DataFrame([
            self.row("TCC1", "False", "True", requer_laboratorio="nao", validado="sim", criterio_laboratorio="orientador"),
        ]))
        self.assertEqual(result.loc[0, "requer_laboratorio"], "nao")


class PrefillSectorsTests(unittest.TestCase):
    def row(self, code, historical="", **extra):
        return {"codigo": code, "setor_historico_2025": historical, "setor_oficial": "", "validado": "", **extra}

    def test_historical_sector_wins_and_spreads_to_rows_of_same_code(self):
        result = prefill_sectors(pd.DataFrame([
            self.row("TCC00313", "REDES"),
            self.row("TCC00313"),
            self.row("TCC00259"),
            self.row("TCC99999"),
        ]))
        self.assertEqual(result["setor_oficial"].tolist(), ["REDES", "REDES", "IA", ""])
        self.assertIn("planilha QH 2025", result.loc[1, "criterio_setor"])
        self.assertIn("afinidade", result.loc[2, "criterio_setor"])
        self.assertEqual(result.loc[3, "validado"], "")

    def test_previous_inference_is_refreshed_but_manual_is_kept(self):
        result = prefill_sectors(pd.DataFrame([
            self.row("TCC00259", setor_oficial="ARQ.SO.", validado="sim", criterio_setor="HP5 antigo"),
            self.row("TCC00260", setor_oficial="ALG.CPX.", validado="sim", criterio_setor="orientador"),
        ]))
        self.assertEqual(result["setor_oficial"].tolist(), ["IA", "ALG.CPX."])


class PrefillQualificationsTests(unittest.TestCase):
    def test_taught_pairs_are_enabled_and_artifacts_are_not(self):
        result = prefill_qualifications(pd.DataFrame([
            {"codigo": "TCC1", "docente": "Ana", "observado_2026": "True", "habilitado": "", "validado": ""},
            {"codigo": "TCC1", "docente": "Bia", "observado_2026": "False", "habilitado": "", "validado": ""},
            {"codigo": "TCC1", "docente": "FECHADA", "observado_2026": "False", "habilitado": "", "validado": ""},
            {"codigo": "TCC2", "docente": "Ana", "observado_2026": "False", "habilitado": "nao", "validado": "sim",
             "criterio_habilitacao": "orientador"},
        ]), roster={"Ana", "Bia"})
        self.assertEqual(result["habilitado"].tolist(), ["sim", "sim", "nao", "nao"])
        self.assertIn("2026", result.loc[0, "criterio_habilitacao"])
        self.assertIn("2025", result.loc[1, "criterio_habilitacao"])
        self.assertIn("fora do cadastro", result.loc[2, "criterio_habilitacao"])


class PrefillPrioritiesTests(unittest.TestCase):
    def test_uniform_priority(self):
        result = prefill_priorities(pd.DataFrame([
            {"nome_normalizado": "Ana", "prioridade": "", "validado": ""},
            {"nome_normalizado": "Bia", "prioridade": "3", "validado": "sim", "criterio_prioridade": "lista oficial"},
        ]))
        self.assertEqual(result["prioridade"].tolist(), ["1", "3"])
        self.assertTrue(result.loc[0, "criterio_prioridade"].startswith("decisão"))


class PrefillExternalTests(unittest.TestCase):
    def test_only_untreated_offers_from_other_departments_are_ignored(self):
        result = prefill_external(pd.DataFrame([
            {"codigo": "TEP00006", "tratamento_no_modelo": "", "criterio_referencia": ""},
            {"codigo": "TCC00240", "tratamento_no_modelo": "", "criterio_referencia": ""},
            {"codigo": "GMA00155", "tratamento_no_modelo": "fixar_horario_e_sala", "criterio_referencia": "turma de referência"},
        ]))
        self.assertEqual(result["tratamento_no_modelo"].tolist(), ["ignorar_fora_do_ic", "", "fixar_horario_e_sala"])


if __name__ == "__main__":
    unittest.main()
