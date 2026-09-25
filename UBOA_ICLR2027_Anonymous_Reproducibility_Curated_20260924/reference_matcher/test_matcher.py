#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import unittest
from fractions import Fraction
from pathlib import Path

from matcher import match, terminalize_trace


HERE = Path(__file__).resolve().parent
GOLD = HERE / "GOLD_FIXTURES.json"
GOLD_SHA256 = "62421f878913532c0a173c1b97285cf66a1ca09fd2ac8bedbae54cde7fef227c"


def deep_merge(base: dict, patch: dict) -> dict:
    out = copy.deepcopy(base)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


class GoldMatcherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        digest = hashlib.sha256(GOLD.read_bytes()).hexdigest()
        if digest != GOLD_SHA256:
            raise AssertionError(f"gold fixture digest changed: {digest}")
        cls.gold = json.loads(GOLD.read_text(encoding="utf-8"))

    def test_all_frozen_gold_cases(self) -> None:
        defaults = self.gold["defaults"]
        for case in self.gold["cases"]:
            with self.subTest(case=case["id"]):
                request = deep_merge(defaults["request"], case.get("request_patch", {}))
                if "request_metadata" in case:
                    request["metadata"] = copy.deepcopy(case["request_metadata"])
                evidence = deep_merge(defaults["evidence"], case.get("evidence_patch", {}))
                got = match(request, evidence)
                observed = {key: got[key] for key in ("status", "rule", "reasons")}
                self.assertEqual(observed, case["expected"])
                self.assertEqual(got["request"], request)

    def test_missing_information_fails_closed(self) -> None:
        request = copy.deepcopy(self.gold["defaults"]["request"])
        evidence = copy.deepcopy(self.gold["defaults"]["evidence"])
        del evidence["scientific"]["horizons"]
        got = match(request, evidence)
        self.assertEqual(got["status"], "UNSUPPORTED_REQUEST")
        self.assertEqual(got["reasons"], ["MISSING_FIELD:evidence.scientific.horizons"])
        self.assertEqual(got["request"], request)

    def test_invalid_later_node_overrides_public_promotion_but_retains_trace(self) -> None:
        trace = [
            {"ordinal": 1, "status": "VALID", "reject": True},
            {"ordinal": 2, "status": "VALID", "reject": True},
            {"ordinal": 3, "status": "INVALID", "reason": "NONPOSITIVE_NORMALIZER"},
        ]
        got = terminalize_trace(trace)
        self.assertEqual(got["public_terminal"], "UNRESOLVED")
        self.assertIsNone(got["public_positive_promotion"])
        self.assertEqual(got["internal_trace"], trace)
        self.assertEqual(got["stop_reason"], "INVALID_EVIDENCE")

    def test_random_family_composes_at_full_history_before_coarsening(self) -> None:
        request = deep_merge(
            self.gold["defaults"]["request"],
            {"conclusion_type": "fixed_sequence_error_bound", "validity": {"conditioning": "selected_label"}},
        )
        evidence = deep_merge(
            self.gold["defaults"]["evidence"],
            {
                "kind": "local_validity_family",
                "conclusion_type": "local_node_bounds",
                "validity": {"conditioning": "selected_label"},
                "premises": ["truth_events_measurable", "local_bounds_hold"],
                "verified_assumptions": ["truth_events_measurable", "local_bounds_hold"],
                "metadata": {
                    "potential_tests_defined": True,
                    "ordered_family": True,
                    "stop_at_first_valid_nonrejection": True,
                    "invalid_policy": "whole_request_unresolved",
                    "no_true_null_convention": True,
                },
            },
        )
        got = match(request, evidence)
        self.assertEqual(got["status"], "UNSUPPORTED_REQUEST")
        self.assertEqual(
            got["reasons"], ["FIXED_SEQUENCE_SIDE_CONDITION_FAILED:full_history_conditioning"]
        )


class ExactAnalyticTests(unittest.TestCase):
    def test_two_stage_probabilities(self) -> None:
        expected = {
            Fraction(1, 20): Fraction(39, 400),
            Fraction(1, 10): Fraction(19, 100),
            Fraction(1, 2): Fraction(3, 4),
        }
        for alpha, selected in expected.items():
            self.assertEqual(1 - (1 - alpha) ** 2, selected)
            self.assertGreater(selected, alpha)

    def test_first_true_null_inclusion_and_infinity_boundary(self) -> None:
        checked = 0
        infinity_cases = 0
        for truth_bits in range(8):
            truth = [bool(truth_bits & (1 << j)) for j in range(3)]
            true_indices = [j for j, is_true in enumerate(truth) if is_true]
            first_true = min(true_indices) if true_indices else None
            if first_true is None:
                infinity_cases += 1
            for reject_bits in range(8):
                potential = [bool(reject_bits & (1 << j)) for j in range(3)]
                reached = True
                false_promotion = False
                for j in range(3):
                    if not reached:
                        break
                    if potential[j] and truth[j]:
                        false_promotion = True
                    reached = reached and potential[j]
                phi_j = potential[first_true] if first_true is not None else False
                self.assertFalse(false_promotion and not phi_j)
                if first_true is None:
                    self.assertFalse(false_promotion)
                    self.assertFalse(phi_j)
                checked += 1
        self.assertEqual(checked, 64)
        self.assertEqual(infinity_cases, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
