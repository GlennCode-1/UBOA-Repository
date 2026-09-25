"""Independent C2 reference implementation.

This module intentionally does not import or call the old production implementation.
It implements the Shao mean-case self-normalized statistic and a frozen Brownian
functional reference approximation for an upper one-sided test.
"""
from __future__ import annotations

import math
import numpy as np


def statistic(x: np.ndarray, mu0: float = 0.0) -> tuple[float, float]:
    x = np.asarray(x, dtype=float)
    if x.ndim != 1 or x.size < 2 or not np.all(np.isfinite(x)):
        raise ValueError("C2 input must be a finite one-dimensional vector with n >= 2")
    n = x.size
    mean = float(np.mean(x))
    centered = x - mean
    partial = np.cumsum(centered)
    k = np.arange(1, n + 1, dtype=float)
    # W_n = n^-2 sum_t [sum_{j<=t}(X_j - Xbar)]^2.
    w = float(np.sum((partial - (k / n) * partial[-1]) ** 2) / (n * n))
    if not math.isfinite(w) or w <= 0.0:
        raise ValueError("C2 self-normalizer is nonpositive or nonfinite")
    return math.sqrt(n) * (mean - mu0) / math.sqrt(w), math.sqrt(w)


def reference_draws(paths: int = 200_000, grid: int = 2048, seed: int = 2027090801) -> np.ndarray:
    if paths < 1000 or grid < 128:
        raise ValueError("reference approximation grid is below the frozen minimum")
    rng = np.random.default_rng(seed)
    out = np.empty(paths, dtype=float)
    dt = 1.0 / grid
    k = np.arange(1, grid + 1, dtype=float)
    for start in range(0, paths, 2000):
        m = min(2000, paths - start)
        increments = rng.normal(size=(m, grid)) * math.sqrt(dt)
        brownian = np.cumsum(increments, axis=1)
        terminal = brownian[:, -1]
        bridge = brownian - k[None, :] * terminal[:, None] / grid
        denom = np.sqrt(np.sum(bridge * bridge, axis=1) * dt)
        out[start:start + m] = terminal / denom
    return out


def upper_critical_value(alpha: float = 0.05, **kwargs: int) -> float:
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0,1)")
    return float(np.quantile(reference_draws(**kwargs), 1.0 - alpha, method="linear"))


if __name__ == "__main__":
    print(f"q95={upper_critical_value():.8f}")
