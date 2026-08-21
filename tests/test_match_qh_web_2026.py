import unittest
from collections import namedtuple

from scripts.match_qh_web_2026 import (
    match_score,
    normalize_class_code,
    web_meetings,
)


PDFRow = namedtuple("PDFRow", ["turma", "codigo"])
WebRow = namedtuple("WebRow", ["turma", "horario"])


class MatchQHWeb2026Tests(unittest.TestCase):
    def test_normalize_class_code(self):
        self.assertEqual(normalize_class_code("A-1"), "A1")
        self.assertEqual(normalize_class_code("A-A / B-A"), "AAB-A".replace("-", "").replace(" ", ""))
        self.assertEqual(normalize_class_code("b1a1"), "B1A1")
        self.assertEqual(normalize_class_code(""), "")

    def test_web_meetings_parsing(self):
        slots = web_meetings("Seg 09:00-11:00; Qua 09:00-11:00")
        self.assertEqual(
            slots,
            {("segunda", "09:00", "11:00"), ("quarta", "09:00", "11:00")},
        )

    def test_exact_class_and_slots_match(self):
        pdf_row = PDFRow(turma="A1", codigo="TCC00001")
        pdf_slots = {("terca", "09:00", "11:00"), ("quinta", "09:00", "11:00")}
        web_row = WebRow(turma="A1", horario="Ter 09:00-11:00; Qui 09:00-11:00")
        score, method = match_score(pdf_row, pdf_slots, web_row)
        self.assertEqual(score, 120)
        self.assertEqual(method, "turma_e_encontros_exatos")

    def test_compressed_row_expansion_by_subset_slots(self):
        # Linha compactada A-A/B-A do PDF contendo dois encontros em dias separados
        pdf_row = PDFRow(turma="A-A/B-A", codigo="TCC00301")
        pdf_slots = {("terca", "11:00", "13:00"), ("quinta", "11:00", "13:00")}

        web_aa = WebRow(turma="AA", horario="Ter 11:00-13:00")
        score_aa, method_aa = match_score(pdf_row, pdf_slots, web_aa)
        self.assertEqual(score_aa, 100)
        self.assertEqual(method_aa, "turma_contida_e_encontros_contidos")

        web_ba = WebRow(turma="BA", horario="Qui 11:00-13:00")
        score_ba, method_ba = match_score(pdf_row, pdf_slots, web_ba)
        self.assertEqual(score_ba, 100)
        self.assertEqual(method_ba, "turma_contida_e_encontros_contidos")

    def test_schedule_mismatch_with_exact_class_name(self):
        pdf_row = PDFRow(turma="A1", codigo="CGI00004")
        pdf_slots = {("sexta", "18:00", "22:00")}
        web_row = WebRow(turma="A1", horario="Sex 18:00-20:00")
        score, method = match_score(pdf_row, pdf_slots, web_row)
        self.assertEqual(score, 110)
        self.assertEqual(method, "turma_exata")


if __name__ == "__main__":
    unittest.main()
