import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.check_readiness_2026 import (
    check_cotutoria_policy,
    check_curricular_classification,
    check_h12_universe,
    check_profile,
)


class CheckReadiness2026Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = Path(self.tmp.name)
        pd.DataFrame([
            {"turma_id": "2026-1-TCC00368-A1", "codigo": "TCC00368", "decisao": ""},
            {"turma_id": "2026-1-TCC00371-A1", "codigo": "TCC00371", "decisao": "optativa:CC"},
        ]).to_csv(self.data / "revisao_classificacao_curricular_2026.csv", index=False)
        pd.DataFrame([
            {"turma_id": "2026-2-TCC00285-A1", "professores": "A;B", "politica_h12": "", "professor_responsavel": ""},
            {"turma_id": "2026-2-TCC00354-A1", "professores": "A;B", "politica_h12": "contar_para_um_responsavel",
             "professor_responsavel": "C"},
        ]).to_csv(self.data / "politica_cotutoria_2026.csv", index=False)
        pd.DataFrame([
            {"nome_normalizado": "A", "incluido_h12": "sim"},
            {"nome_normalizado": "B", "incluido_h12": ""},
        ]).to_csv(self.data / "universo_h12_2026.csv", index=False)

    def tearDown(self):
        self.tmp.cleanup()

    def test_curricular_classification_detects_empty_decision(self):
        pendencias = check_curricular_classification(self.data)
        self.assertEqual(len(pendencias), 1)
        self.assertIn("TCC00368", pendencias[0])

    def test_cotutoria_policy_detects_empty_policy_and_invalid_responsible(self):
        pendencias = check_cotutoria_policy(self.data)
        self.assertEqual(len(pendencias), 2)
        self.assertTrue(any("professor_responsavel" in p for p in pendencias))

    def test_h12_universe_detects_unmarked_teachers(self):
        pendencias = check_h12_universe(self.data)
        self.assertTrue(any("incluido_h12" in p for p in pendencias))

    def test_missing_review_files_keep_profile_not_ready(self):
        is_ready, pendencias = check_profile("baseline", self.data, update_instance=False)
        self.assertFalse(is_ready)
        self.assertTrue(any("Arquivo ausente" in p for p in pendencias))


if __name__ == "__main__":
    unittest.main()
