import unittest

import pandas as pd

from scripts.refresh_review_evidence_2026 import merge


class RefreshReviewEvidenceTests(unittest.TestCase):
    def test_evidence_is_updated_and_decisions_are_kept(self):
        current = pd.DataFrame([
            {"sala": "202", "capacidade_minima_observada": "61", "capacidade_fisica": "61", "validado": "sim", "criterio_capacidade": "HP3"},
            {"sala": "999", "capacidade_minima_observada": "10", "capacidade_fisica": "10", "validado": "sim", "criterio_capacidade": "HP3"},
        ])
        fresh = pd.DataFrame([
            {"sala": "202", "capacidade_minima_observada": "65", "capacidade_fisica": "", "validado": ""},
            {"sala": "L1", "capacidade_minima_observada": "30", "capacidade_fisica": "", "validado": ""},
        ])
        merged, report = merge(current, fresh, ["sala"], ["capacidade_fisica", "validado", "criterio_capacidade"])
        rows = merged.set_index("sala")
        self.assertEqual(rows.loc["202", "capacidade_minima_observada"], "65")
        self.assertEqual(rows.loc["202", "capacidade_fisica"], "61")
        self.assertEqual(rows.loc["202", "criterio_capacidade"], "HP3")
        self.assertEqual(rows.loc["L1", "validado"], "")
        self.assertEqual(report, {"novas": [("L1",)], "removidas": [("999",)]})
        self.assertEqual(list(merged.columns), list(current.columns))


if __name__ == "__main__":
    unittest.main()
