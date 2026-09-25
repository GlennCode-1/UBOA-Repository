"""Frozen scalar AR(1) dynamics on caller-supplied innovations.

Randomness is intentionally absent. The future locked entry point supplies
innovation arrays after constructing the sole authorized RNG streams.
"""

from __future__ import annotations

import numpy as np


RHO = 0.5


def evolve_scalar_ar(initial_state: float, innovations: np.ndarray) -> np.ndarray:
    eps = np.asarray(innovations)
    if eps.ndim not in (1, 2):
        raise ValueError("innovations must be a one- or two-dimensional array")
    if not np.isfinite(eps).all():
        raise ValueError("innovations must be finite")
    if eps.ndim == 1:
        states = np.empty(eps.shape[0] + 1, dtype=np.float64)
        states[0] = float(initial_state)
        for t in range(eps.shape[0]):
            states[t + 1] = RHO * states[t] + eps[t]
        return states
    states = np.empty((eps.shape[0], eps.shape[1] + 1), dtype=np.float64)
    states[:, 0] = float(initial_state)
    for t in range(eps.shape[1]):
        states[:, t + 1] = RHO * states[:, t] + eps[:, t]
    return states


def validate_b1_innovations(innovations: np.ndarray) -> None:
    values = np.asarray(innovations)
    if not np.isin(values, (-1, 1)).all():
        raise ValueError("B1 innovations must be Rademacher values {-1,+1}")


def evolve_b1(initial_state: float, innovations: np.ndarray) -> np.ndarray:
    validate_b1_innovations(innovations)
    return evolve_scalar_ar(initial_state, innovations)


def evolve_qb(initial_state: float, innovations: np.ndarray) -> np.ndarray:
    return evolve_scalar_ar(initial_state, innovations)
