"""Validation-only deterministic selection for the two frozen branches."""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np

from protocol import HORIZONS, VALIDATION_ORIGINS


def _mean_validation_loss(
    states: Sequence[float], parameter: float, loss: str, forecast: Callable[[int, int, float], float]
) -> float:
    path = np.asarray(states, dtype=np.float64)
    if path.ndim != 1 or path.shape[0] <= max(VALIDATION_ORIGINS) + max(HORIZONS):
        raise ValueError("history must include every validation target through state 325")
    total = 0.0
    count = 0
    for origin in VALIDATION_ORIGINS:
        for horizon in HORIZONS:
            error = path[origin + horizon] - forecast(origin, horizon, parameter)
            total += abs(error) if loss == "mae" else error * error
            count += 1
    return total / count


def select_b1_delta(states: Sequence[float]) -> tuple[float, dict[str, float]]:
    def forecast(origin: int, horizon: int, delta: float) -> float:
        return (0.5**horizon) * float(states[origin]) + delta

    scores = {
        "-0.1": _mean_validation_loss(states, -0.1, "mae", forecast),
        "+0.1": _mean_validation_loss(states, +0.1, "mae", forecast),
    }
    selected = -0.1 if scores["-0.1"] <= scores["+0.1"] else +0.1
    return selected, scores


def select_qb_gamma(states: Sequence[float]) -> tuple[float, dict[str, float]]:
    def forecast(origin: int, horizon: int, gamma: float) -> float:
        return ((0.5**horizon) + gamma) * float(states[origin])

    scores = {
        "-0.1": _mean_validation_loss(states, -0.1, "mse", forecast),
        "+0.1": _mean_validation_loss(states, +0.1, "mse", forecast),
    }
    selected = -0.1 if scores["-0.1"] <= scores["+0.1"] else +0.1
    return selected, scores
