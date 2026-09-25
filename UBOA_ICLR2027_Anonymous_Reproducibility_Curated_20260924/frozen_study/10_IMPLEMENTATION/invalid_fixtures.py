"""Five mandatory deterministic invalid-certificate fixtures."""

from __future__ import annotations

from fractions import Fraction

from certificate_b1 import b1_certificate
from certificate_qb import GAUSSIAN_MOMENTS, quadratic_certificate
from fixed_sequence import potential_local_tests, run_fixed_sequence
from protocol import expected_scope


def _invalid_without_promotion(callable_) -> dict[str, object]:
    try:
        callable_()
    except (ValueError, TypeError, KeyError) as exc:
        operational = run_fixed_sequence(
            potential_local_tests((1.0, 1.0, 1.0), (None, None, None)),
            (True, True, True),
        )
        return {
            "status": "INVALID_CERTIFICATE_HOLD",
            "exception": type(exc).__name__,
            "message": str(exc),
            "positive_terminal_promotion": bool(operational["false_promotion"]),
            "operational_status": operational["terminal_report"],
        }
    return {"status": "UNEXPECTED_ACCEPT", "positive_terminal_promotion": True}


def run_invalid_fixtures() -> dict[str, dict[str, object]]:
    mutated_scope = tuple(item for item in expected_scope(512) if item[1] != 3)
    no_m4 = {key: value for key, value in GAUSSIAN_MOMENTS.items() if key != "m4"}
    fixtures = {
        "B1_MISSING_SUPPORT": lambda: b1_certificate(Fraction(0), state_support=None),
        "QB_MISSING_M4": lambda: quadratic_certificate(0.2, -0.1, 0.0, Fraction(0), moments=no_m4),
        "QB_CORRELATED_SCALAR_COORDS": lambda: quadratic_certificate(
            0.2, -0.1, 0.0, Fraction(0), independent_scalar_coordinates=False
        ),
        "SCOPE_MUTATION": lambda: b1_certificate(Fraction(0), scope=mutated_scope),
        "NONFINITE_CERTIFICATE": lambda: b1_certificate(Fraction(0), innovation_diameter=float("inf")),
    }
    return {name: _invalid_without_promotion(function) for name, function in fixtures.items()}


def fixtures_pass(results: dict[str, dict[str, object]]) -> bool:
    return set(results) == {
        "B1_MISSING_SUPPORT",
        "QB_MISSING_M4",
        "QB_CORRELATED_SCALAR_COORDS",
        "SCOPE_MUTATION",
        "NONFINITE_CERTIFICATE",
    } and all(
        result["status"] == "INVALID_CERTIFICATE_HOLD"
        and result["positive_terminal_promotion"] is False
        for result in results.values()
    )
