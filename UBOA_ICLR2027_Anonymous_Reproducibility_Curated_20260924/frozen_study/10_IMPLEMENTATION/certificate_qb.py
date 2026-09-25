"""Exact full-overlap quadratic certificate for the frozen QB-MSE branch."""

from __future__ import annotations

import math
from fractions import Fraction
from functools import lru_cache
from typing import Mapping, Sequence

import numpy as np

from protocol import HORIZONS, LOCAL_ALPHA, assert_frozen_scope, expected_scope


GAUSSIAN_MOMENTS = {"mean": 0.0, "s2": 1.0, "m3": 0.0, "m4": 3.0}


def _finite_number(value: object, name: str) -> float:
    if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ValueError(f"INVALID_CERTIFICATE: missing/nonfinite {name}")
    return float(value)


def error_affine(gamma: float, y0: float, origin: int, horizon: int, n_innovations: int) -> tuple[float, np.ndarray]:
    """Return d,v for error = d + v'e in relative evaluation time."""
    d = -float(gamma) * (0.5**origin) * float(y0)
    v = np.zeros(n_innovations, dtype=np.float64)
    for j in range(1, origin + 1):
        v[j - 1] = -float(gamma) * (0.5 ** (origin - j))
    for j in range(origin + 1, origin + horizon + 1):
        v[j - 1] = 0.5 ** (origin + horizon - j)
    return d, v


@lru_cache(maxsize=1)
def _frozen_design_components() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    """Precompute full-overlap Gram objects for the one frozen QB scope."""
    scope = expected_scope(256)
    n = 256 - 1 + max(HORIZONS)
    eta = np.zeros((len(scope), n), dtype=np.float64)
    state = np.zeros((len(scope), n), dtype=np.float64)
    initial_gain = np.zeros(len(scope), dtype=np.float64)
    weight = float(scope[0][2])
    for row, (origin, horizon, _) in enumerate(scope):
        initial_gain[row] = 0.5**origin
        for j in range(1, origin + 1):
            state[row, j - 1] = 0.5 ** (origin - j)
        for j in range(origin + 1, origin + horizon + 1):
            eta[row, j - 1] = 0.5 ** (origin + horizon - j)
    ee = weight * (eta.T @ eta)
    ex_symmetric = weight * (eta.T @ state + state.T @ eta)
    xx = weight * (state.T @ state)
    eta_initial = weight * (eta.T @ initial_gain)
    state_initial = weight * (state.T @ initial_gain)
    initial_squared = weight * float(initial_gain @ initial_gain)
    return ee, ex_symmetric, xx, eta_initial, state_initial, initial_squared


def build_agk(
    comparator_gamma: float,
    selected_gamma: float,
    y0: float,
    r: Fraction,
    *,
    eval_origins: int = 256,
    scope: Sequence[tuple[int, int, Fraction]] | None = None,
) -> tuple[np.ndarray, np.ndarray, float]:
    if eval_origins != 256:
        raise ValueError("QB evaluation-origin count changed")
    if Fraction(r) not in (Fraction(0), Fraction(1, 50), Fraction(1, 20)):
        raise ValueError("r is outside the frozen ladder")
    for name, value in (("comparator_gamma", comparator_gamma), ("selected_gamma", selected_gamma), ("y0", y0)):
        _finite_number(value, name)
    actual_scope = tuple(scope) if scope is not None else expected_scope(eval_origins)
    assert_frozen_scope(actual_scope, eval_origins)
    ee, ex_symmetric, xx, eta_initial, state_initial, initial_squared = _frozen_design_components()
    one_minus_r = 1.0 - float(r)
    def second_moment_matrix(gamma: float) -> np.ndarray:
        return ee - gamma * ex_symmetric + gamma * gamma * xx

    def first_moment_vector(gamma: float) -> np.ndarray:
        return -gamma * float(y0) * eta_initial + gamma * gamma * float(y0) * state_initial

    def constant(gamma: float) -> float:
        return gamma * gamma * float(y0) * float(y0) * initial_squared

    A = one_minus_r * second_moment_matrix(float(comparator_gamma)) - second_moment_matrix(float(selected_gamma))
    g = one_minus_r * first_moment_vector(float(comparator_gamma)) - first_moment_vector(float(selected_gamma))
    k_const = one_minus_r * constant(float(comparator_gamma)) - constant(float(selected_gamma))
    return A, g, k_const


def quadratic_certificate(
    comparator_gamma: float,
    selected_gamma: float,
    y0: float,
    r: Fraction,
    *,
    moments: Mapping[str, float] | None = GAUSSIAN_MOMENTS,
    independent_scalar_coordinates: bool = True,
    eval_origins: int = 256,
    scope: Sequence[tuple[int, int, Fraction]] | None = None,
    alpha: Fraction = LOCAL_ALPHA,
) -> dict[str, object]:
    if not independent_scalar_coordinates:
        raise ValueError("INVALID_CERTIFICATE: scalar innovation coordinates are correlated")
    if moments is None or "m4" not in moments:
        raise ValueError("INVALID_CERTIFICATE: fourth moment m4 is required")
    if Fraction(alpha) != LOCAL_ALPHA:
        raise ValueError("alpha differs from the frozen local level")
    mean_e = _finite_number(moments.get("mean"), "innovation mean")
    s2 = _finite_number(moments.get("s2"), "s2")
    m3 = _finite_number(moments.get("m3"), "m3")
    m4 = _finite_number(moments.get("m4"), "m4")
    if mean_e != 0.0 or s2 < 0.0 or m4 < s2 * s2:
        raise ValueError("INVALID_CERTIFICATE: moment premises fail")
    A, g, k_const = build_agk(
        comparator_gamma, selected_gamma, y0, r, eval_origins=eval_origins, scope=scope
    )
    diagonal = np.diag(A)
    conditional_mean = k_const + s2 * float(np.trace(A))
    diagonal_variance = float(np.sum(diagonal * diagonal)) * (m4 - s2 * s2)
    off_diagonal = float(np.sum(np.triu(A, 1) ** 2))
    variance = (
        diagonal_variance
        + 4.0 * off_diagonal * s2 * s2
        + 4.0 * float(np.dot(g, g)) * s2
        + 4.0 * float(np.dot(diagonal, g)) * m3
    )
    if variance < -1e-10 or not math.isfinite(variance):
        raise ValueError("INVALID_CERTIFICATE: nonfinite/negative variance")
    variance = max(0.0, variance)
    threshold = math.sqrt(variance * (1.0 - float(alpha)) / float(alpha)) if variance else 0.0
    if not all(np.isfinite(A).flat) or not all(np.isfinite(g)) or not math.isfinite(conditional_mean + threshold):
        raise ValueError("INVALID_CERTIFICATE: nonfinite A/g/k/threshold")
    return {
        "status": "VALID_CERTIFICATE",
        "r": str(Fraction(r)),
        "alpha": str(Fraction(alpha)),
        "A": A,
        "g": g,
        "k": k_const,
        "conditional_mean": conditional_mean,
        "conditional_variance": variance,
        "threshold": threshold,
        "strict_rejection": True,
        "scope_terms": eval_origins * len(HORIZONS),
    }


def gaussian_variance_identity(A: np.ndarray, g: np.ndarray) -> float:
    matrix = np.asarray(A, dtype=np.float64)
    vector = np.asarray(g, dtype=np.float64)
    return 2.0 * float(np.sum(matrix * matrix.T)) + 4.0 * float(np.dot(vector, vector))


def quadratic_value(innovations: np.ndarray, A: np.ndarray, g: np.ndarray, k_const: float) -> np.ndarray:
    e = np.asarray(innovations, dtype=np.float64)
    if e.ndim == 1:
        return np.asarray(float(e @ A @ e + 2.0 * g @ e + k_const))
    return np.einsum("bi,ij,bj->b", e, A, e) + 2.0 * (e @ g) + k_const


def reject_qb(w_value: float, certificate: dict[str, object]) -> bool:
    if certificate.get("status") != "VALID_CERTIFICATE":
        return False
    threshold = float(certificate["threshold"])
    if not math.isfinite(float(w_value)) or not math.isfinite(threshold):
        return False
    return float(w_value) > threshold
