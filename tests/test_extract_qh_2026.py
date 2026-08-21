import unittest

from scripts.extract_qh_2026 import (
    TeacherNormalizer,
    normalize_room,
    parse_time,
    split_teachers,
)


class ExtractQH2026Tests(unittest.TestCase):
    def test_time_formats_are_normalized(self):
        self.assertEqual(parse_time("07:00-09:00", "2026-1"), ("07:00", "09:00"))
        self.assertEqual(parse_time("09/13", "2026-2"), ("09:00", "13:00"))
        self.assertIsNone(parse_time("-", "2026-2"))

    def test_room_formats_are_normalized_without_merging_lab_and_classroom(self):
        self.assertEqual(normalize_room("SALA 302"), "302")
        self.assertEqual(normalize_room("LAB. 302"), "L302")
        self.assertEqual(normalize_room("L. 307"), "L307")

    def test_multiple_teachers_are_preserved(self):
        self.assertEqual(split_teachers("Raquel / Martinhon"), ["Raquel", "Martinhon"])
        self.assertEqual(split_teachers("Martinhon/Loana"), ["Martinhon", "Loana"])
        self.assertEqual(split_teachers("----"), [])

    def test_teacher_normalization_uses_unique_reference_matches(self):
        normalizer = TeacherNormalizer()
        self.assertEqual(normalizer.match("IGOR COELHO").normalized, "Igor Machado")
        self.assertEqual(normalizer.match("LEONARDO GRESTA MURTA").normalized, "Leo Murta")
        self.assertEqual(normalizer.match("REBECA CAMPOS MOTTA").normalized, "Rebeca")
        self.assertFalse(normalizer.match("Miguel").verified)


if __name__ == "__main__":
    unittest.main()
