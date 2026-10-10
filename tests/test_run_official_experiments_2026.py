import unittest

from scripts.run_official_experiments_2026 import wilcoxon_exact


class WilcoxonExactTests(unittest.TestCase):
    def test_known_values(self):
        self.assertAlmostEqual(wilcoxon_exact(list(range(1, 11)))[1], 2 / 1024)
        self.assertAlmostEqual(wilcoxon_exact([1, -2, 3, -4, 5, -6, 7, -8, 9, -10])[1], 866 / 1024)
        self.assertEqual(wilcoxon_exact([0.0, 0.0]), (0.0, 1.0))


if __name__ == "__main__":
    unittest.main()
