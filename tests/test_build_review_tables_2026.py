import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.build_review_tables_2026 import historical_counts, refresh_historical_counts


class HistoricalCountsTests(unittest.TestCase):
    def test_unknown_teacher_stays_empty_instead_of_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            pd.DataFrame([
                {"codigo": "TCC1", "professor": "Ana", "contagem": "2"},
                {"codigo": "TCC2", "professor": "Ana", "contagem": "1"},
            ]).to_csv(data / "preferencias_2025.csv", index=False)
            pd.DataFrame([
                {"codigo": "TCC1", "docente": "Ana", "frequencia_historica_2023_2025": "", "habilitado": "sim"},
                {"codigo": "TCC3", "docente": "Ana", "frequencia_historica_2023_2025": "", "habilitado": ""},
                {"codigo": "TCC1", "docente": "Novo", "frequencia_historica_2023_2025": "", "habilitado": ""},
            ]).to_csv(data / "revisao_habilitacao_docente_2026.csv", index=False)
            pd.DataFrame([
                {"nome_normalizado": "Ana", "ocorrencias_2023_2025": "", "prioridade": "1"},
                {"nome_normalizado": "Novo", "ocorrencias_2023_2025": "", "prioridade": ""},
            ]).to_csv(data / "revisao_prioridades_docentes_2026.csv", index=False)

            refresh_historical_counts(data)

            qualification = pd.read_csv(data / "revisao_habilitacao_docente_2026.csv", dtype=str).fillna("")
            self.assertEqual(qualification["frequencia_historica_2023_2025"].tolist(), ["2", "0", ""])
            self.assertEqual(qualification["habilitado"].tolist(), ["sim", "", ""])
            priorities = pd.read_csv(data / "revisao_prioridades_docentes_2026.csv", dtype=str).fillna("")
            self.assertEqual(priorities["ocorrencias_2023_2025"].tolist(), ["3", ""])

    def test_repeated_pairs_are_summed(self):
        counts, known = historical_counts(pd.DataFrame([
            {"codigo": "TCC1", "professor": "Ana", "contagem": "1"},
            {"codigo": "TCC1", "professor": "Ana", "contagem": "2"},
        ]))
        self.assertEqual(counts[("TCC1", "Ana")], 3)
        self.assertEqual(known, {"Ana"})


if __name__ == "__main__":
    unittest.main()
