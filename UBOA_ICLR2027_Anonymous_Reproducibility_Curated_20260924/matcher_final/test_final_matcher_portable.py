#!/usr/bin/env python3
"""Deterministic regressions for the FINAL_MATCHER candidate.

V2 is already-exposed development evidence.  Its use here is regression-only.
No test calls an RNG or reads scientific outcomes.
"""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from matcher import match


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
V2 = HERE / "test_inputs" / "CHALLENGE_V2_FROZEN.jsonl"
LEGACY_GOLD = ROOT / "reference_matcher_original" / "GOLD_FIXTURES.json"
DEV_REGRESSIONS = ROOT / "reference_matcher" / "DEVELOPMENT_REGRESSIONS.json"


def deep_merge(base: dict, patch: dict) -> dict:
    out = copy.deepcopy(base)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def load_v2() -> dict[str, dict]:
    return {
        record["case_id"]: record
        for record in (
            json.loads(line) for line in V2.read_text(encoding="utf-8").splitlines() if line.strip()
        )
    }


class TargetedV2RegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = load_v2()

    def assert_case(self, case_id: str, status: str, reason: str | None = None) -> None:
        case = self.cases[case_id]
        got = match(case["request"], case["evidence"])
        self.assertEqual(got["status"], status)
        self.assertEqual(got["request"], case["request"])
        if reason is not None:
            self.assertEqual(got["reasons"], [reason])

    def test_m2_requires_nonempty_string_provenance(self) -> None:
        self.assert_case(
            "F08_C4", "UNSUPPORTED_REQUEST", "OBSERVED_COPY_PROVENANCE_MISSING"
        )
        self.assert_case("F08_C1", "ESTABLISHED")

        case = copy.deepcopy(self.cases["F08_C1"])
        case["evidence"]["metadata"]["provenance"] = "  "
        got = match(case["request"], case["evidence"])
        self.assertEqual(got["reasons"], ["OBSERVED_COPY_PROVENANCE_MISSING"])

    def test_m4_requires_at_least_one_declared_premise(self) -> None:
        self.assert_case("F28_C4", "UNSUPPORTED_REQUEST", "THEOREM_PREMISES_EMPTY")
        self.assert_case("F28_C1", "ESTABLISHED")

    def test_existing_conclusion_type_guards_remain(self) -> None:
        self.assert_case("F05_C4", "UNSUPPORTED_REQUEST", "CONCLUSION_TYPE_MISMATCH")
        self.assert_case("F24_C3", "UNSUPPORTED_REQUEST", "CONCLUSION_TYPE_MISMATCH")

    def test_existing_validity_coordinate_guards_remain(self) -> None:
        self.assert_case(
            "F25_C3", "UNSUPPORTED_REQUEST", "VALIDITY_SCOPE_MISMATCH:coverage_unit"
        )
        self.assert_case(
            "F29_C3", "UNSUPPORTED_REQUEST", "VALIDITY_SCOPE_MISMATCH:selection_mechanism"
        )


class LegacyCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gold = json.loads(LEGACY_GOLD.read_text(encoding="utf-8"))

    def materialize(self, case: dict) -> tuple[dict, dict]:
        defaults = self.gold["defaults"]
        request = deep_merge(defaults["request"], case.get("request_patch", {}))
        if "request_metadata" in case:
            request["metadata"] = copy.deepcopy(case["request_metadata"])
        evidence = deep_merge(defaults["evidence"], case.get("evidence_patch", {}))
        return request, evidence

    def test_legacy_cases_other_than_superseded_m2_fixture_are_unchanged(self) -> None:
        checked = 0
        for case in self.gold["cases"]:
            if case["id"] == "observed_decision_copy":
                continue
            with self.subTest(case=case["id"]):
                request, evidence = self.materialize(case)
                got = match(request, evidence)
                observed = {key: got[key] for key in ("status", "rule", "reasons")}
                self.assertEqual(observed, case["expected"])
                self.assertEqual(got["request"], request)
                checked += 1
        self.assertEqual(checked, 22)

    def test_incomplete_legacy_m2_fixture_is_now_rejected(self) -> None:
        case = next(x for x in self.gold["cases"] if x["id"] == "observed_decision_copy")
        request, evidence = self.materialize(case)
        self.assertNotIn("provenance", evidence["metadata"])
        got = match(request, evidence)
        self.assertEqual(got["status"], "UNSUPPORTED_REQUEST")
        self.assertEqual(got["reasons"], ["OBSERVED_COPY_PROVENANCE_MISSING"])

    def test_contract_complete_legacy_m2_positive_control(self) -> None:
        case = next(x for x in self.gold["cases"] if x["id"] == "observed_decision_copy")
        request, evidence = self.materialize(case)
        evidence["metadata"]["provenance"] = "fixture:observed_decision_copy"
        got = match(request, evidence)
        self.assertEqual(got["status"], "ESTABLISHED")
        self.assertEqual(got["rule"], "M2_OBSERVED_COPY")

    def test_revised_development_regressions_remain_unchanged(self) -> None:
        cases = json.loads(DEV_REGRESSIONS.read_text(encoding="utf-8"))
        self.assertEqual(len(cases), 18)
        for case in cases:
            with self.subTest(case=case["id"]):
                got = match(case["request"], case["evidence"])
                self.assertEqual(got["status"], case["expected_status"])
                self.assertEqual(got["request"], case["request"])


class V2PostExposureRegressionTests(unittest.TestCase):
    def test_full_v2_regression_counts_are_frozen_and_labeled(self) -> None:
        counts = {
            "cases": 0,
            "ambiguous": 0,
            "false_accepts": 0,
            "valid_not_licensed": 0,
            "exceptions": 0,
        }
        for case in load_v2().values():
            counts["cases"] += 1
            if case["expected_disposition"] == "ambiguous":
                counts["ambiguous"] += 1
                continue
            try:
                got = match(case["request"], case["evidence"])
            except Exception:
                counts["exceptions"] += 1
                continue
            predicted_permissible = got["status"] == "ESTABLISHED"
            if case["expected_disposition"] == "impermissible" and predicted_permissible:
                counts["false_accepts"] += 1
            if case["expected_disposition"] == "permissible" and not predicted_permissible:
                counts["valid_not_licensed"] += 1

        self.assertEqual(
            counts,
            {
                "cases": 160,
                "ambiguous": 3,
                "false_accepts": 0,
                "valid_not_licensed": 10,
                "exceptions": 0,
            },
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
