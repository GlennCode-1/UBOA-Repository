"""Pure finite-lag certificate algebra for Route 1.

The module accepts only explicit numeric dictionaries/lists.  It has no file,
network, data, fitting, or random-generation entry point.  The dynamic law is

    Y_t = c_t + sum_l A[t,l] Y_{t-l} + epsilon_t,

with vector-valued member state and a conditionally independent innovation
block at each time.  Forecast maps are frozen affine maps on explicit lag
coordinates; a ridge class is represented by an l2 coefficient radius, not by
refitting from H.  Seasonal naive is a declared one-hot affine map.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


Number = float


def _finite(x: Number) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(float(x))


def _as_matrix(x: Sequence[Sequence[Number]], m: int) -> List[List[float]]:
    if len(x) != m or any(len(row) != m for row in x):
        raise ValueError("matrix dimension does not match member_count")
    out = [[float(v) for v in row] for row in x]
    if not all(_finite(v) for row in out for v in row):
        raise ValueError("matrix contains non-finite coefficient")
    return out


def _zeros(m: int) -> List[List[float]]:
    return [[0.0 for _ in range(m)] for _ in range(m)]


def _eye(m: int) -> List[List[float]]:
    out = _zeros(m)
    for i in range(m):
        out[i][i] = 1.0
    return out


def _mat_add(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
    return [[a[i][j] + b[i][j] for j in range(len(a[i]))] for i in range(len(a))]


def _mat_mul(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
    n = len(a)
    k = len(b)
    p = len(b[0]) if b else 0
    return [[sum(a[i][u] * b[u][j] for u in range(k)) for j in range(p)] for i in range(n)]


def _mat_abs(x: List[List[float]]) -> List[List[float]]:
    return [[abs(v) for v in row] for row in x]


def _mat_row_sum(x: List[List[float]], row: int) -> float:
    return sum(x[row])


def _vec(values: Sequence[Number], m: int) -> List[float]:
    if len(values) != m:
        raise ValueError("vector dimension does not match member_count")
    out = [float(v) for v in values]
    if not all(_finite(v) for v in out):
        raise ValueError("non-finite vector")
    return out


def _key(mapping: Mapping[Any, Any], key: int) -> Any:
    if key in mapping:
        return mapping[key]
    if str(key) in mapping:
        return mapping[str(key)]
    raise KeyError(key)


def _initial_value(dynamics: Mapping[str, Any], t: int, m: int) -> float:
    values = dynamics.get("initial_values", {})
    return float(_vec(_key(values, t), int(dynamics["member_count"]))[m])


def _initial_range(dynamics: Mapping[str, Any], t: int, m: int) -> float:
    ranges = dynamics.get("initial_ranges", {})
    out = float(_vec(_key(ranges, t), int(dynamics["member_count"]))[m])
    if out < 0 or not _finite(out):
        raise ValueError("initial_ranges must be finite and nonnegative")
    return out


def _innovation_vec(dynamics: Mapping[str, Any], field: str, t: int, m: int) -> float:
    values = dynamics[field]
    value = _key(values, t)
    if isinstance(value, (int, float)):
        out = float(value)
    else:
        out = float(_vec(value, int(dynamics["member_count"]))[m])
    if not _finite(out):
        raise ValueError(f"{field}[{t}] must be finite")
    return out


def _innovation_block_value(dynamics: Mapping[str, Any], field: str, t: int) -> float:
    """Return a scalar l-infinity block diameter/radius bound.

    A scalar entry is a common bound for every member.  A vector entry is
    reduced to its maximum coordinate bound; this is conservative when a time
    block contains shared innovations and keeps the certificate block-valid.
    """
    value = _key(dynamics[field], t)
    if isinstance(value, (int, float)):
        out = float(value)
    else:
        entries = _vec(value, int(dynamics["member_count"]))
        out = max(entries)
    if out < 0 or not _finite(out):
        raise ValueError(f"{field}[{t}] must be finite and nonnegative")
    return out


def _validate_dynamics(dynamics: Mapping[str, Any]) -> Tuple[int, int]:
    m = int(dynamics["member_count"])
    T = int(dynamics["max_time"])
    if m <= 0 or T < 0:
        raise ValueError("member_count must be positive and max_time nonnegative")
    for t in range(1, T + 1):
        _vec(_key(dynamics["intercepts"], t), m)
        _innovation_vec(dynamics, "innovation_diameter", t, 0)
        _innovation_vec(dynamics, "innovation_radius", t, 0)
        if _innovation_vec(dynamics, "innovation_diameter", t, 0) < 0:
            raise ValueError("innovation diameters must be nonnegative")
        if _innovation_vec(dynamics, "innovation_radius", t, 0) < 0:
            raise ValueError("innovation radii must be nonnegative")
        lag_map = _key(dynamics["coefficients"], t)
        for lag, matrix in lag_map.items():
            lag_i = int(lag)
            if lag_i <= 0:
                raise ValueError("dynamic lags must be positive")
            _as_matrix(matrix, m)
    for t in range(0, 1):
        _vec(_key(dynamics["initial_values"], t), m)
        _vec(_key(dynamics["initial_ranges"], t), m)
    return m, T


def state_certificate(dynamics: Mapping[str, Any]) -> Dict[str, Any]:
    """Return direct finite-lag transfer, base path, and range bounds.

    `transfer[t][j][m][q]` is an absolute coefficient bound from innovation
    coordinate q at time j to state member m at time t.  It is obtained by
    direct lag recursion; no shift-augmented Euclidean contraction is used.
    """
    m, T = _validate_dynamics(dynamics)
    transfer: Dict[int, Dict[int, List[List[float]]]] = {}
    base: Dict[int, List[float]] = {0: [_initial_value(dynamics, 0, q) for q in range(m)]}
    state_range: Dict[int, List[float]] = {0: [_initial_range(dynamics, 0, q) for q in range(m)]}
    history_base = {int(t): list(_vec(v, m)) for t, v in dynamics.get("initial_values", {}).items()}
    history_range = {int(t): list(_vec(v, m)) for t, v in dynamics.get("initial_ranges", {}).items()}
    if any(value < 0.0 for values in history_range.values() for value in values):
        raise ValueError("initial_ranges must be finite absolute envelopes")

    for t in range(1, T + 1):
        intercept = _vec(_key(dynamics["intercepts"], t), m)
        lag_map = _key(dynamics["coefficients"], t)
        base_t = list(intercept)
        range_t = [abs(v) for v in intercept]
        for lag, matrix_raw in lag_map.items():
            lag_i = int(lag)
            matrix = _as_matrix(matrix_raw, m)
            source_t = t - lag_i
            source_base = base[source_t] if source_t >= 0 else [_initial_value(dynamics, source_t, q) for q in range(m)]
            source_range = state_range[source_t] if source_t >= 0 else [_initial_range(dynamics, source_t, q) for q in range(m)]
            for row in range(m):
                base_t[row] += sum(matrix[row][col] * source_base[col] for col in range(m))
                range_t[row] += sum(abs(matrix[row][col]) * source_range[col] for col in range(m))
        radius = [_innovation_vec(dynamics, "innovation_radius", t, q) for q in range(m)]
        base[t] = base_t
        state_range[t] = [range_t[q] + radius[q] for q in range(m)]

        transfer[t] = {}
        for j in range(1, t + 1):
            current = _eye(m) if j == t else _zeros(m)
            if j < t:
                current = _zeros(m)
                for lag, matrix_raw in lag_map.items():
                    source_t = t - int(lag)
                    if source_t < j or source_t not in transfer or j not in transfer[source_t]:
                        continue
                    current = _mat_add(current, _mat_mul(_mat_abs(_as_matrix(matrix_raw, m)), transfer[source_t][j]))
            transfer[t][j] = current

    return {
        "member_count": m,
        "max_time": T,
        "transfer_abs": transfer,
        "base_path": base,
        "state_range": state_range,
        "history_base": history_base,
        "history_range": history_range,
    }


def seasonal_naive_spec(member: int, period: int, horizon: int) -> Dict[str, Any]:
    """Declare direct seasonal repetition for any positive horizon.

    q=period*ceil(horizon/period); forecast at origin o is Y[o+horizon-q].
    Thus the lag coordinate is q-horizon in {0,...,period-1}; this is explicit
    even when horizon exceeds one season and never uses an unknown future value.
    """
    if period <= 0 or horizon <= 0 or member < 0:
        raise ValueError("period, horizon, and member must be valid")
    q = period * ((horizon + period - 1) // period)
    return {"kind": "affine", "intercept": 0.0, "coefficients": [{"member": member, "lag": q - horizon, "value": 1.0}]}


def _mapping_stats(
    spec: Mapping[str, Any],
    origin: int,
    transfer_info: Mapping[str, Any],
) -> Dict[str, Any]:
    """Return range, base, influence, and innovation coefficient vectors."""
    m = int(transfer_info["member_count"])
    T = int(transfer_info["max_time"])
    transfer = transfer_info["transfer_abs"]
    base = transfer_info["base_path"]
    state_range = transfer_info["state_range"]
    history_base = transfer_info.get("history_base", {})
    history_range = transfer_info.get("history_range", {})

    def base_at(t: int, member: int) -> float:
        return float(base[t][member]) if t >= 0 else float(_vec(_key(history_base, t), m)[member])

    def range_at(t: int, member: int) -> float:
        return float(state_range[t][member]) if t >= 0 else float(_vec(_key(history_range, t), m)[member])
    kind = spec.get("kind", "affine")
    if kind == "affine":
        intercept = float(spec.get("intercept", 0.0))
        coeffs = [(int(c["member"]), int(c["lag"]), float(c["value"])) for c in spec.get("coefficients", [])]
        if not _finite(intercept) or any(member < 0 or member >= m or lag < 0 or not _finite(beta) for member, lag, beta in coeffs):
            raise ValueError("affine coefficient coordinate is out of range")
        base_value = intercept
        range_value = abs(intercept)
        influence = [0.0 for _ in range(T + 1)]
        coeff_vector: Dict[Tuple[int, int], float] = {}
        for member, lag, beta in coeffs:
            t = origin - lag
            if t > T:
                raise ValueError("mapping time exceeds max_time")
            base_value += beta * base_at(t, member)
            range_value += abs(beta) * range_at(t, member)
            if t > 0:
                for j in range(1, t + 1):
                    row_sum = _mat_row_sum(transfer[t][j], member)
                    influence[j] += abs(beta) * row_sum
                for j in range(1, t + 1):
                    for q in range(m):
                        coeff_vector[(j, q)] = coeff_vector.get((j, q), 0.0) + beta * transfer[t][j][member][q]
        return {"base": base_value, "range": range_value, "influence": influence, "coeff_vector": coeff_vector}
    if kind == "ridge_class":
        intercept_abs = float(spec.get("intercept_abs", 0.0))
        radius = float(spec["l2_radius"])
        features = [(int(c["member"]), int(c["lag"])) for c in spec.get("features", [])]
        if not _finite(intercept_abs) or not _finite(radius) or intercept_abs < 0 or radius < 0 or any(member < 0 or member >= m or lag < 0 for member, lag in features):
            raise ValueError("invalid ridge class")
        feature_ranges = []
        feature_gains = [[] for _ in range(T + 1)]
        for member, lag in features:
            t = origin - lag
            if t > T:
                raise ValueError("ridge feature time exceeds max_time")
            feature_ranges.append(range_at(t, member))
            if t > 0:
                for j in range(1, t + 1):
                    feature_gains[j].append(_mat_row_sum(transfer[t][j], member))
        range_value = intercept_abs + radius * math.sqrt(sum(v * v for v in feature_ranges))
        influence = [0.0 for _ in range(T + 1)]
        for j in range(1, T + 1):
            influence[j] = radius * math.sqrt(sum(v * v for v in feature_gains[j]))
        # A class certificate is uniform, so no exact affine coefficient vector exists.
        return {"base": 0.0, "range": range_value, "influence": influence, "coeff_vector": None}
    raise ValueError(f"unknown mapping kind: {kind}")


def _validate_scope(scope: Sequence[Mapping[str, Any]], T: int, member_count: int | None = None) -> None:
    if not scope:
        raise ValueError("scope must retain at least one origin/horizon/member term")
    total = 0.0
    for term in scope:
        o = int(term["origin"])
        h = int(term["horizon"])
        member = int(term["target_member"])
        weight = float(term["weight"])
        if o < 0 or h <= 0 or member < 0 or (member_count is not None and member >= member_count) or weight < 0 or not _finite(weight):
            raise ValueError("invalid scope term")
        if o + h > T:
            raise ValueError("scope target exceeds max_time")
        total += weight
    if total <= 0 or not math.isfinite(total):
        raise ValueError("scope weights must have positive finite total")


def build_influence_certificate(
    dynamics: Mapping[str, Any],
    scope: Sequence[Mapping[str, Any]],
    baseline_specs: Sequence[Mapping[str, Any]],
    selected_specs: Sequence[Mapping[str, Any]],
    r: float,
    alpha: float,
    loss: str,
) -> Dict[str, Any]:
    """Compute c_j, Efron--Stein V, and raw-loss range certificates."""
    if not (0.0 < alpha < 1.0 and 0.0 <= r < 1.0):
        raise ValueError("alpha must be in (0,1), r in [0,1)")
    if len(scope) != len(baseline_specs) or len(scope) != len(selected_specs):
        raise ValueError("scope and mapping lists must have equal length")
    if loss not in {"mae", "mse"}:
        raise ValueError("loss must be 'mae' or 'mse'")
    info = state_certificate(dynamics)
    T = int(info["max_time"])
    _validate_scope(scope, T, int(info["member_count"]))
    c_by_j = [0.0 for _ in range(T + 1)]
    term_records: List[Dict[str, Any]] = []
    for term, b_spec, s_spec in zip(scope, baseline_specs, selected_specs):
        o, h, member, weight = int(term["origin"]), int(term["horizon"]), int(term["target_member"]), float(term["weight"])
        b = _mapping_stats(b_spec, o, info)
        s = _mapping_stats(s_spec, o, info)
        target_t = o + h
        target_range = info["state_range"][target_t][member]
        target_gain = [0.0 for _ in range(T + 1)]
        for j in range(1, target_t + 1):
            target_gain[j] = _mat_row_sum(info["transfer_abs"][target_t][j], member)
        error_b = target_range + b["range"]
        error_s = target_range + s["range"]
        for j in range(1, T + 1):
            d_j = _innovation_block_value(dynamics, "innovation_diameter", j)
            if loss == "mae":
                u = d_j * ((2.0 - r) * target_gain[j] + (1.0 - r) * b["influence"][j] + s["influence"][j])
            else:
                u = 2.0 * d_j * ((1.0 - r) * error_b * (target_gain[j] + b["influence"][j]) + error_s * (target_gain[j] + s["influence"][j]))
            c_by_j[j] += weight * u
        term_records.append({"origin": o, "horizon": h, "target_member": member, "weight": weight, "target_range": target_range, "baseline": b, "selected": s, "error_range_baseline": error_b, "error_range_selected": error_s})
    c = c_by_j[1:]
    c_sq = sum(v * v for v in c)
    V_es = 0.5 * c_sq
    return {
        "loss": loss,
        "r": r,
        "alpha": alpha,
        "scope_weight_total": sum(float(t["weight"]) for t in scope),
        "state_range": info["state_range"],
        "c_by_innovation_time": c,
        "c_squared_sum": c_sq,
        "V_es": V_es,
        "mcdiarmid_threshold": math.sqrt(0.5 * math.log(1.0 / alpha) * c_sq) if c_sq > 0 else 0.0,
        "cantelli_threshold": math.sqrt(V_es * (1.0 - alpha) / alpha) if V_es > 0 else 0.0,
        "term_records": term_records,
    }


def quadratic_mse_certificate(
    dynamics: Mapping[str, Any],
    scope: Sequence[Mapping[str, Any]],
    baseline_specs: Sequence[Mapping[str, Any]],
    selected_specs: Sequence[Mapping[str, Any]],
    r: float,
    alpha: float,
    innovation_moments: Mapping[Tuple[int, int], Mapping[str, Number]],
) -> Dict[str, Any]:
    """Exact conditional MSE quadratic variance for independent scalar innovations.

    The P-class is conditional independence across every (time, member)
    coordinate, zero conditional means, and finite moments s2/m3/m4.  No
    symmetry or Gaussian assumption is made; the diagonal third-moment term is
    retained.  If innovations are vector-dependent within a time block, this
    scalar-coordinate identity is not applicable and the caller must stay with
    the block-level bounded/Efron--Stein certificate.
    """
    if not (0.0 < alpha < 1.0 and 0.0 <= r < 1.0):
        raise ValueError("alpha must be in (0,1), r in [0,1)")
    if len(scope) != len(baseline_specs) or len(scope) != len(selected_specs):
        raise ValueError("scope and mapping lists must have equal length")
    info = state_certificate(dynamics)
    m, T = int(info["member_count"]), int(info["max_time"])
    _validate_scope(scope, T, m)
    indices = [(t, q) for t in range(1, T + 1) for q in range(m)]
    pos = {index: i for i, index in enumerate(indices)}
    n = len(indices)
    A = [[0.0 for _ in range(n)] for _ in range(n)]
    g = [0.0 for _ in range(n)]
    k_const = 0.0
    if m != 1:
        raise ValueError("quadratic_mse_certificate currently requires member_count=1")
    signed_transfer = _signed_transfer_table_scalar(dynamics, T)

    def state_coeff(t: int, member: int) -> List[float]:
        out = [0.0 for _ in range(n)]
        if t <= 0:
            return out
        for j in range(1, t + 1):
            out[pos[(j, 0)]] = signed_transfer[t][j]
        return out

    def base_state(t: int, member: int) -> float:
        return float(info["base_path"][t][member]) if t >= 0 else _initial_value(dynamics, t, member)

    for term, b_spec, s_spec in zip(scope, baseline_specs, selected_specs):
        if b_spec.get("kind", "affine") != "affine" or s_spec.get("kind", "affine") != "affine":
            raise ValueError("quadratic certificate requires exact affine frozen mappings")
        o, h, member, weight = int(term["origin"]), int(term["horizon"]), int(term["target_member"]), float(term["weight"])
        target = state_coeff(o + h, member)
        b_vec = _mapping_coeff_vector(b_spec, o, info, pos, n, signed_transfer)
        s_vec = _mapping_coeff_vector(s_spec, o, info, pos, n, signed_transfer)
        v_b = [target[i] - b_vec[i] for i in range(n)]
        v_s = [target[i] - s_vec[i] for i in range(n)]
        b_base = _mapping_base(b_spec, o, info)
        s_base = _mapping_base(s_spec, o, info)
        c_b = base_state(o + h, member) - b_base
        c_s = base_state(o + h, member) - s_base
        for i in range(n):
            g[i] += weight * ((1.0 - r) * c_b * v_b[i] - c_s * v_s[i])
            for j in range(n):
                A[i][j] += weight * ((1.0 - r) * v_b[i] * v_b[j] - v_s[i] * v_s[j])
        k_const += weight * ((1.0 - r) * c_b * c_b - c_s * c_s)

    mean = k_const
    for i, index in enumerate(indices):
        moments = innovation_moments[index]
        if float(moments.get("mean", 0.0)) != 0.0:
            raise ValueError("quadratic identity requires zero conditional means")
        mean += A[i][i] * float(moments["s2"])
    variance = 0.0
    for i, index in enumerate(indices):
        moments = innovation_moments[index]
        s2 = float(moments["s2"])
        m3 = float(moments["m3"])
        m4 = float(moments["m4"])
        variance += A[i][i] * A[i][i] * (m4 - s2 * s2)
        variance += 4.0 * g[i] * g[i] * s2
        variance += 4.0 * A[i][i] * g[i] * m3
        if m4 < s2 * s2 - 1e-12:
            raise ValueError("invalid moments: m4 must dominate s2^2")
    for i in range(n):
        for j in range(i + 1, n):
            s2_i = float(innovation_moments[indices[i]]["s2"])
            s2_j = float(innovation_moments[indices[j]]["s2"])
            variance += 4.0 * A[i][j] * A[i][j] * s2_i * s2_j
    if variance < -1e-9:
        raise ValueError("computed conditional variance is negative")
    variance = max(0.0, variance)
    return {
        "r": r,
        "alpha": alpha,
        "A": A,
        "g": g,
        "k": k_const,
        "conditional_mean": mean,
        "conditional_variance": variance,
        "cantelli_threshold": math.sqrt(variance * (1.0 - alpha) / alpha) if variance > 0 else 0.0,
        "strict_rule": "reject iff W_r > threshold; when variance=0 reject iff W_r>0",
    }


def _signed_transfer_table_scalar(dynamics: Mapping[str, Any], T: int) -> Dict[int, Dict[int, float]]:
    """Finite dynamic program for exact signed scalar innovation transfer."""
    transfer: Dict[int, Dict[int, float]] = {}
    for t in range(1, T + 1):
        transfer[t] = {}
        lag_map = _key(dynamics["coefficients"], t)
        for j in range(1, t + 1):
            value = 1.0 if j == t else 0.0
            if j < t:
                for lag, matrix_raw in lag_map.items():
                    source = t - int(lag)
                    if source >= j:
                        value += float(_as_matrix(matrix_raw, 1)[0][0]) * transfer[source][j]
            transfer[t][j] = value
    return transfer


def _mapping_coeff_vector(
    spec: Mapping[str, Any],
    origin: int,
    info: Mapping[str, Any],
    pos: Mapping[Tuple[int, int], int],
    n: int,
    signed_transfer: Mapping[int, Mapping[int, float]],
) -> List[float]:
    out = [0.0 for _ in range(n)]
    for c in spec.get("coefficients", []):
        member, lag, beta = int(c["member"]), int(c["lag"]), float(c["value"])
        t = origin - lag
        if t <= 0:
            continue
        for j in range(1, t + 1):
            if int(info["member_count"]) != 1:
                raise ValueError("quadratic_mse_certificate currently requires member_count=1")
            out[pos[(j, 0)]] += beta * float(signed_transfer[t][j])
    return out


def _mapping_base(spec: Mapping[str, Any], origin: int, info: Mapping[str, Any]) -> float:
    value = float(spec.get("intercept", 0.0))
    for c in spec.get("coefficients", []):
        member, lag, beta = int(c["member"]), int(c["lag"]), float(c["value"])
        t = origin - lag
        if t < 0:
            value += beta * _initial_value({"member_count": int(info["member_count"]), "initial_values": info["history_base"]}, t, member)
        else:
            value += beta * float(info["base_path"][t][member])
    return value
