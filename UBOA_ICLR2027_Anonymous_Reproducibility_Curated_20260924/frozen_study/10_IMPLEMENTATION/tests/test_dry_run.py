from __future__ import annotations

import ast
import hashlib
import json
import math
import unittest
from fractions import Fraction
from itertools import product
from pathlib import Path

import numpy as np

from analyze_confirmatory import decide_study_status, holm_step_down, one_sided_binomial_pvalue
from certificate_b1 import b1_certificate, b1_scalar_reference
from certificate_qb import gaussian_variance_identity, quadratic_certificate, quadratic_value
from fixed_sequence import potential_local_tests, run_fixed_sequence
from generators import evolve_qb
from invalid_fixtures import fixtures_pass, run_invalid_fixtures
from protocol import H_END, HORIZONS, LADDER, MASTER_SEED, ROOT, load_cells
from seed_schedule import derive_seed
from selection import select_b1_delta, select_qb_gamma
from truth import b1_mae_risk, b1_theta, b1_truth_vector, qb_truth
from verify_outputs import verify_scientific_freeze


IMPLEMENTATION = Path(__file__).resolve().parents[1]


class FrozenProtocolTests(unittest.TestCase):
    def test_scientific_freeze_and_cells(self) -> None:
        self.assertEqual(verify_scientific_freeze(), [])
        cells = load_cells()
        self.assertEqual(len(cells), 10)
        self.assertEqual(sum(cell.branch.startswith("B1_") for cell in cells), 5)
        self.assertEqual(sum(cell.branch.startswith("QB_") for cell in cells), 5)
        self.assertEqual(H_END, 325)
        self.assertEqual(HORIZONS, (1, 3, 6))
        self.assertEqual(LADDER, (Fraction(0), Fraction(1, 50), Fraction(1, 20)))

    def test_seed_derivation_is_pure_sha256(self) -> None:
        key = f"{MASTER_SEED}|B1_MAE_NEG|outer|0".encode()
        expected = int.from_bytes(hashlib.sha256(key).digest()[:16], "big", signed=False)
        self.assertEqual(derive_seed("B1_MAE_NEG", "outer", 0), expected)
        with self.assertRaises(ValueError):
            derive_seed("B1_MAE_NEG", "retry", 0)


class ExactTruthTests(unittest.TestCase):
    EXPECTED = {
        "B1_MAE_NEG": (Fraction(0), Fraction(-1, 1280), 0),
        "B1_MAE_B02": (Fraction(289, 784), Fraction(1, 50), 1),
        "B1_MAE_B05": (Fraction(5875, 10336), Fraction(1, 20), 2),
        "B1_MAE_ALT08": (Fraction(2747, 3680), Fraction(2, 25), None),
        "B1_MAE_STR40": (Fraction(541, 328), Fraction(2, 5), None),
    }

    def test_b1_exact_rational_truth_and_boundaries(self) -> None:
        for cell_id, (delta, theta, first) in self.EXPECTED.items():
            self.assertEqual(b1_theta(delta), theta, cell_id)
            truths = b1_truth_vector(delta)
            self.assertEqual(next((i for i, value in enumerate(truths) if value), None), first)
        self.assertEqual(b1_truth_vector(Fraction(289, 784)), (False, True, True))
        self.assertEqual(b1_truth_vector(Fraction(5875, 10336)), (False, False, True))

    def test_b1_independent_float_enumeration(self) -> None:
        def float_risk(delta: float) -> float:
            risks = []
            for horizon in HORIZONS:
                errors = []
                for signs in product((-1.0, 1.0), repeat=horizon):
                    eta = sum((0.5 ** (horizon - j)) * sign for j, sign in enumerate(signs, start=1))
                    errors.append(abs(eta - delta))
                risks.append(sum(errors) / len(errors))
            return sum(risks) / len(risks)

        for cell_id, (delta, _, _) in self.EXPECTED.items():
            self.assertLessEqual(abs(float(b1_mae_risk(delta)) - float_risk(float(delta))), 1e-12, cell_id)

    def test_validation_tie_break_is_negative(self) -> None:
        states = np.zeros(326, dtype=np.float64)
        self.assertEqual(select_b1_delta(states)[0], -0.1)
        self.assertEqual(select_qb_gamma(states)[0], -0.1)

    def test_qb_direct_truth_matches_quadratic_expectation(self) -> None:
        qb_cells = [cell for cell in load_cells() if cell.branch.startswith("QB_")]
        for y0 in (-1.25, 0.0, 0.75):
            for cell in qb_cells:
                direct = qb_truth(cell.comparator_gamma, -0.1, y0)
                for node, r in enumerate(LADDER):
                    cert = quadratic_certificate(cell.comparator_gamma, -0.1, y0, r)
                    expected = float(direct["mu_by_node"][node])
                    self.assertTrue(math.isclose(expected, float(cert["conditional_mean"]), rel_tol=1e-10, abs_tol=1e-10 * (1 + abs(expected))))
                    independent_variance = gaussian_variance_identity(cert["A"], cert["g"])
                    self.assertTrue(math.isclose(float(cert["conditional_variance"]), independent_variance, rel_tol=1e-10, abs_tol=1e-10))

    def test_qb_agk_matches_direct_hardcoded_path(self) -> None:
        y0, baseline, selected, r = 0.375, 0.24185434428325728, -0.1, Fraction(1, 50)
        cert = quadratic_certificate(baseline, selected, y0, r)
        innovations = np.linspace(-0.75, 0.75, 261, dtype=np.float64)
        states = evolve_qb(y0, innovations)
        b_total = 0.0
        s_total = 0.0
        for origin in range(256):
            for horizon in HORIZONS:
                target = states[origin + horizon]
                b_error = target - (0.5**horizon + baseline) * states[origin]
                s_error = target - (0.5**horizon + selected) * states[origin]
                b_total += b_error * b_error
                s_total += s_error * s_error
        direct_w = (1.0 - float(r)) * b_total / 768 - s_total / 768
        quadratic_w = float(quadratic_value(innovations, cert["A"], cert["g"], cert["k"]))
        self.assertTrue(math.isclose(direct_w, quadratic_w, rel_tol=1e-10, abs_tol=1e-10))


class CertificateAndSequenceTests(unittest.TestCase):
    def test_b1_general_and_scalar_reference(self) -> None:
        for r in LADDER:
            general = b1_certificate(r)
            independent = b1_scalar_reference(r)
            self.assertEqual(general["scope_terms"], 1536)
            self.assertTrue(math.isclose(float(general["c_squared_sum"]), float(independent["c_squared_sum"]), rel_tol=1e-10, abs_tol=1e-10))
            self.assertTrue(math.isclose(float(general["threshold"]), float(independent["threshold"]), rel_tol=1e-10, abs_tol=1e-10))

    def test_strict_endpoint_and_fixed_sequence_inclusion(self) -> None:
        potential = potential_local_tests((1.0, 2.0001, 3.0), (1.0, 2.0, 3.0))
        self.assertEqual(potential, (False, True, False))
        stopped = run_fixed_sequence(potential, (False, False, True))
        self.assertEqual(stopped["reached"], (True, False, False))
        self.assertFalse(stopped["false_promotion"])
        promoted = run_fixed_sequence((True, True, True), (False, False, True))
        self.assertTrue(promoted["false_promotion"])
        self.assertTrue(promoted["first_true_null_inclusion_ok"])

    def test_all_five_invalid_fixtures_hold_without_promotion(self) -> None:
        results = run_invalid_fixtures()
        self.assertTrue(fixtures_pass(results), json.dumps(results, indent=2))

    def test_binomial_and_holm_invariants(self) -> None:
        self.assertEqual(one_sided_binomial_pvalue(0), 1.0)
        result = holm_step_down({"h1": 0.0001, "h2": 0.006, "h3": 0.5})
        self.assertIn("h1", result["rejected_history_ids"])
        self.assertNotIn("h2", result["rejected_history_ids"])

    def test_reached_invalid_forces_hold(self) -> None:
        analysis = {
            "pathwise_invariant_violations": 0,
            "invalid_count": 1,
            "primary_holm_audit": {"status": "NO_CALIBRATION_RED_FLAG_OBSERVED"},
        }
        self.assertEqual(
            decide_study_status(
                protocol_conformant=True,
                fixtures_pass=True,
                crosschecks_pass=True,
                analysis=analysis,
            ),
            "IMPLEMENTATION_HOLD",
        )


class StaticSafetyTests(unittest.TestCase):
    def test_sources_compile_without_execution(self) -> None:
        for path in IMPLEMENTATION.rglob("*.py"):
            compile(path.read_text(encoding="utf-8"), str(path), "exec")

    def test_rng_calls_exist_only_in_locked_entry(self) -> None:
        banned_attributes = {"Generator", "PCG64DXSM", "choice", "standard_normal", "normal", "integers", "default_rng"}
        violations = []
        calls_in_entry = 0
        for path in IMPLEMENTATION.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in banned_attributes:
                    if path.name == "run_confirmatory.py":
                        calls_in_entry += 1
                    else:
                        violations.append(f"{path.relative_to(IMPLEMENTATION)}:{node.lineno}:{node.func.attr}")
        self.assertEqual(violations, [])
        self.assertGreater(calls_in_entry, 0)

    def test_schemas_parse(self) -> None:
        schemas = sorted((IMPLEMENTATION / "schemas").glob("*.json"))
        self.assertEqual(len(schemas), 4)
        for path in schemas:
            self.assertEqual(json.loads(path.read_text())["$schema"], "https://json-schema.org/draft/2020-12/schema")


if __name__ == "__main__":
    unittest.main()
