"""Theorem A certificate specialized to the frozen B1 scalar AR study."""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Sequence

from protocol import HORIZONS, LOCAL_ALPHA, assert_frozen_scope, expected_scope


def _require_primitive(value: float | None, name: str, *, positive: bool = False) -> float:
    if value is None or not math.isfinite(float(value)):
        raise ValueError(f"INVALID_CERTIFICATE: missing/nonfinite {name}")
    result = float(value)
    if (positive and result <= 0.0) or (not positive and result < 0.0):
        raise ValueError(f"INVALID_CERTIFICATE: invalid {name}")
    return result


def b1_certificate(
    r: Fraction,
    *,
    eval_origins: int = 512,
    scope: Sequence[tuple[int, int, Fraction]] | None = None,
    rho: float = 0.5,
    innovation_diameter: float | None = 2.0,
    state_support: float | None = 2.0,
    alpha: Fraction = LOCAL_ALPHA,
) -> dict[str, object]:
    if Fraction(r) not in (Fraction(0), Fraction(1, 50), Fraction(1, 20)):
        raise ValueError("r is outside the frozen ladder")
    if Fraction(alpha) != LOCAL_ALPHA:
        raise ValueError("alpha differs from the frozen local level")
    if eval_origins != 512 or rho != 0.5:
        raise ValueError("B1 design changed")
    diameter = _require_primitive(innovation_diameter, "innovation diameter", positive=True)
    _require_primitive(state_support, "state support", positive=True)
    actual_scope = tuple(scope) if scope is not None else expected_scope(eval_origins)
    assert_frozen_scope(actual_scope, eval_origins)

    max_time = eval_origins - 1 + max(HORIZONS)
    c = [0.0] * max_time
    r_float = float(r)
    for origin, horizon, weight in actual_scope:
        weight_float = float(weight)
        target_time = origin + horizon
        for innovation_time in range(1, target_time + 1):
            target_gain = rho ** (target_time - innovation_time)
            forecast_gain = rho ** (target_time - innovation_time) if innovation_time <= origin else 0.0
            u = diameter * (
                (2.0 - r_float) * target_gain
                + (1.0 - r_float) * forecast_gain
                + forecast_gain
            )
            c[innovation_time - 1] += weight_float * u
    c_squared_sum = sum(value * value for value in c)
    threshold = math.sqrt(0.5 * math.log(1.0 / float(alpha)) * c_squared_sum) if c_squared_sum else 0.0
    if not all(math.isfinite(value) for value in (*c, c_squared_sum, threshold)):
        raise ValueError("INVALID_CERTIFICATE: nonfinite result")
    return {
        "status": "VALID_CERTIFICATE",
        "r": str(Fraction(r)),
        "alpha": str(Fraction(alpha)),
        "c_by_innovation_time": c,
        "c_squared_sum": c_squared_sum,
        "threshold": threshold,
        "strict_rejection": True,
        "scope_terms": len(actual_scope),
    }


def b1_scalar_reference(
    r: Fraction,
    *,
    eval_origins: int = 512,
    rho: float = 0.5,
    innovation_diameter: float = 2.0,
    alpha: Fraction = LOCAL_ALPHA,
) -> dict[str, object]:
    """Independent scalar calculation using cancellation cases explicitly."""
    scope = expected_scope(eval_origins)
    max_time = eval_origins - 1 + max(HORIZONS)
    totals = []
    multiplier = innovation_diameter * (2.0 - float(r))
    for j in range(1, max_time + 1):
        total = 0.0
        for origin, horizon, weight in scope:
            target = origin + horizon
            if j > target:
                continue
            copies = 2.0 if j <= origin else 1.0
            total += float(weight) * multiplier * copies * rho ** (target - j)
        totals.append(total)
    squared = sum(value * value for value in totals)
    threshold = math.sqrt(0.5 * math.log(1.0 / float(alpha)) * squared) if squared else 0.0
    return {"c_by_innovation_time": totals, "c_squared_sum": squared, "threshold": threshold}


def reject_b1(w_value: float, certificate: dict[str, object]) -> bool:
    if certificate.get("status") != "VALID_CERTIFICATE":
        return False
    threshold = float(certificate["threshold"])
    if not math.isfinite(float(w_value)) or not math.isfinite(threshold):
        return False
    return float(w_value) > threshold
