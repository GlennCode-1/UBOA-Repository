"""Potential local tests and operational fixed-sequence stopping."""

from __future__ import annotations

import math
from collections.abc import Sequence

from protocol import LADDER, first_true_null


def potential_local_tests(
    w_values: Sequence[float], thresholds: Sequence[float | None]
) -> tuple[bool | None, ...]:
    if len(w_values) != len(LADDER) or len(thresholds) != len(LADDER):
        raise ValueError("node vectors must match the frozen ladder")
    decisions: list[bool | None] = []
    for w_value, threshold in zip(w_values, thresholds):
        if threshold is None or not math.isfinite(float(threshold)) or not math.isfinite(float(w_value)):
            decisions.append(None)
        else:
            decisions.append(float(w_value) > float(threshold))
    return tuple(decisions)


def run_fixed_sequence(
    potential: Sequence[bool | None], truth_by_node: Sequence[bool]
) -> dict[str, object]:
    if len(potential) != len(LADDER) or len(truth_by_node) != len(LADDER):
        raise ValueError("node vectors must match the frozen ladder")
    reached = [False] * len(LADDER)
    rejected = [False] * len(LADDER)
    invalid = False
    terminal = "ABOVE_0.05"
    for index, decision in enumerate(potential):
        reached[index] = True
        if decision is None:
            invalid = True
            terminal = "UNRESOLVED_INVALID_CERTIFICATE"
            break
        if not decision:
            terminal = "NONE" if index == 0 else str(LADDER[index - 1])
            break
        rejected[index] = True
    first_true = first_true_null(truth_by_node)
    false_promotion = any(rejected[i] and bool(truth_by_node[i]) for i in range(len(LADDER)))
    inclusion_ok = first_true is None or not false_promotion or potential[first_true] is True
    return {
        "reached": tuple(reached),
        "rejected": tuple(rejected),
        "terminal_report": terminal,
        "invalid": invalid,
        "false_promotion": false_promotion,
        "first_true_null": first_true,
        "first_true_null_inclusion_ok": inclusion_ok,
    }
