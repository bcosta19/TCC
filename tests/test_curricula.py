import unittest
from pathlib import Path

from src.model.curricula import classify_code, load_project_curricula


ROOT = Path(__file__).resolve().parents[1]


class CurriculaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.curricula = load_project_curricula(ROOT)

    def test_project_curricula_are_loaded(self):
        self.assertEqual(len({entry.code for entry in self.curricula["CC"]}), 137)
        self.assertEqual(len({entry.code for entry in self.curricula["SI"]}), 107)

    def test_intersection_creates_one_shared_classification(self):
        classification = classify_code("TCC00301", self.curricula)
        self.assertTrue(classification["shared"])
        self.assertEqual(classification["courses"], ["CC", "SI"])
        self.assertIn("CC-P2", classification["memberships"]["CC"]["groups"])
        self.assertIn("SI-OPT", classification["memberships"]["SI"]["groups"])

    def test_mandatory_si_class_has_period(self):
        classification = classify_code("TCC00332", self.curricula)
        self.assertTrue(classification["obligatory"])
        self.assertEqual(classification["obligatory_courses"], ["SI"])
    def test_intersection_has_64_codes(self):
        cc_codes = {entry.code for entry in self.curricula["CC"]}
        si_codes = {entry.code for entry in self.curricula["SI"]}
        intersection = cc_codes & si_codes
        self.assertEqual(len(intersection), 64)

    def test_distinct_codes_with_same_name_are_not_merged(self):
        # TCC00318 (CC) vs TCC00368 (SI) têm códigos distintos e classificações independentes
        cc_class = classify_code("TCC00318", self.curricula)
        si_class = classify_code("TCC00368", self.curricula)
        self.assertEqual(cc_class["courses"], ["CC"])
        self.assertFalse(cc_class["shared"])
        self.assertFalse(si_class["in_curricula"])  # TCC00368 não está nas grades Markdown

    def test_mandatory_by_curriculum_is_recorded(self):
        # TCC00301 é obrigatória em CC (CC-P2) e optativa em SI (SI-OPT)
        classification = classify_code("TCC00301", self.curricula)
        self.assertTrue(classification["obligatory"])
        self.assertEqual(classification["obligatory_courses"], ["CC"])
        self.assertIn("obrigatoria", classification["memberships"]["CC"]["kinds"])
        self.assertIn("optativa", classification["memberships"]["SI"]["kinds"])


if __name__ == "__main__":
    unittest.main()
