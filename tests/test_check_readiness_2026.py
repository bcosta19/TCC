import unittest
from scripts.check_readiness_2026 import (
    check_cotutoria_policy,
    check_curricular_classification,
    check_h12_universe,
    check_profile,
)


class CheckReadiness2026Tests(unittest.TestCase):
    def test_curricular_classification_detects_empty_decision(self):
        pendencias = check_curricular_classification()
        # In baseline state without human decisions, 4 entries must be pending
        self.assertGreaterEqual(len(pendencias), 4)

    def test_cotutoria_policy_detects_empty_policy(self):
        pendencias = check_cotutoria_policy()
        # In baseline state, 2 co-teaching entries must be pending
        self.assertGreaterEqual(len(pendencias), 2)

    def test_h12_universe_detects_unmarked_teachers(self):
        pendencias = check_h12_universe()
        self.assertTrue(any("incluido_h12" in p for p in pendencias))

    def test_baseline_profile_is_not_ready_by_default(self):
        is_ready, pendencias = check_profile("baseline")
        self.assertFalse(is_ready)
        self.assertGreater(len(pendencias), 0)


if __name__ == "__main__":
    unittest.main()
