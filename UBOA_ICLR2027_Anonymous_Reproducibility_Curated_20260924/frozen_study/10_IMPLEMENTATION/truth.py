"""Independent truth calculations for B1-MAE and QB-MSE."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Iterable

from protocol import HORIZONS, LADDER, RHO, first_true_null


SELECTED_SHIFT = Fraction(1, 10)


def b1_eta_values(horizon: int) -> tuple[Fraction, ...]:
    return tuple(
        sum((RHO ** (horizon - j)) * sign for j, sign in enumerate(signs, start=1))
        for signs in product((-1, 1), repeat=horizon)
    )


def b1_horizon_mae_risk(delta: Fraction, horizon: int) -> Fraction:
    values = b1_eta_values(horizon)
    return sum(abs(value - delta) for value in values) / len(values)


def b1_mae_risk(delta: Fraction) -> Fraction:
    return sum(b1_horizon_mae_risk(delta, horizon) for horizon in HORIZONS) / len(HORIZONS)


def b1_theta(comparator_delta: Fraction) -> Fraction:
    baseline = b1_mae_risk(Fraction(comparator_delta))
    if baseline <= 0:
        raise ValueError("baseline risk must be positive")
    return Fraction(1) - b1_mae_risk(SELECTED_SHIFT) / baseline


def b1_truth_vector(comparator_delta: Fraction) -> tuple[bool, ...]:
    theta = b1_theta(comparator_delta)
    return tuple(theta <= r for r in LADDER)


def b1_first_true_null(comparator_delta: Fraction) -> int | None:
    return first_true_null(b1_truth_vector(comparator_delta))


def qb_m2(origin_offset: int, y0: float) -> float:
    if origin_offset < 0:
        raise ValueError("origin offset must be nonnegative")
    rho2k = 0.5 ** (2 * origin_offset)
    return rho2k * float(y0) ** 2 + (1.0 - rho2k) / (1.0 - 0.25)


def qb_q(horizon: int) -> float:
    if horizon not in HORIZONS:
        raise ValueError("horizon is outside frozen scope")
    return (1.0 - 0.5 ** (2 * horizon)) / (1.0 - 0.25)


def qb_mse_risk(gamma: float, y0: float, eval_origins: int = 256) -> float:
    if eval_origins != 256:
        raise ValueError("QB evaluation origins changed")
    return sum(qb_q(h) + float(gamma) ** 2 * qb_m2(k, y0) for k in range(eval_origins) for h in HORIZONS) / (eval_origins * len(HORIZONS))


def qb_truth(comparator_gamma: float, selected_gamma: float, y0: float) -> dict[str, object]:
    baseline = qb_mse_risk(comparator_gamma, y0)
    selected = qb_mse_risk(selected_gamma, y0)
    if baseline <= 0:
        raise ValueError("baseline risk must be positive")
    theta = 1.0 - selected / baseline
    means = tuple((1.0 - float(r)) * baseline - selected for r in LADDER)
    truths = tuple(value <= 0.0 for value in means)
    return {
        "baseline_risk": baseline,
        "selected_risk": selected,
        "theta": theta,
        "mu_by_node": means,
        "truth_by_node": truths,
        "first_true_null": first_true_null(truths),
    }


def serialize_fraction(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"
