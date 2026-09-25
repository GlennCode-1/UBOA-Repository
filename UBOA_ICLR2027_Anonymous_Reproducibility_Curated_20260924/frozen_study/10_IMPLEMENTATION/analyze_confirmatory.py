"""Frozen per-history binomial/Holm analysis for completed confirmatory outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from scipy.stats import binom

from protocol import INNER_FUTURES


FAMILY_AUDIT_ALPHA = 0.01
NULL_RATE = 0.05


def one_sided_binomial_pvalue(false_promotions: int, denominator: int = INNER_FUTURES) -> float:
    if denominator != INNER_FUTURES or not 0 <= false_promotions <= denominator:
        raise ValueError("invalid per-history binomial count/denominator")
    return float(binom.sf(false_promotions - 1, denominator, NULL_RATE))


def holm_step_down(pvalues: dict[str, float], alpha: float = FAMILY_AUDIT_ALPHA) -> dict[str, object]:
    if alpha != FAMILY_AUDIT_ALPHA:
        raise ValueError("Holm family level changed")
    ordered = sorted(pvalues.items(), key=lambda item: (item[1], item[0]))
    m = len(ordered)
    rejected: set[str] = set()
    still_rejecting = True
    running_adjusted = 0.0
    adjusted: dict[str, float] = {}
    for rank, (key, pvalue) in enumerate(ordered):
        if not 0.0 <= pvalue <= 1.0:
            raise ValueError("p-value outside [0,1]")
        multiplier = m - rank
        running_adjusted = max(running_adjusted, min(1.0, multiplier * pvalue))
        adjusted[key] = running_adjusted
        if still_rejecting and pvalue <= alpha / multiplier:
            rejected.add(key)
        else:
            still_rejecting = False
    return {
        "family_size": m,
        "family_alpha": alpha,
        "adjusted_pvalues": adjusted,
        "rejected_history_ids": sorted(rejected),
        "status": "CALIBRATION_RED_FLAG" if rejected else "NO_CALIBRATION_RED_FLAG_OBSERVED",
    }


def analyze_history_records(records: Iterable[dict[str, object]]) -> dict[str, object]:
    records = list(records)
    finite = [row for row in records if row.get("first_true_null") is not None]
    pvalues = {
        str(row["history_id"]): one_sided_binomial_pvalue(
            int(row["false_promotions"]), int(row["inner_denominator"])
        )
        for row in finite
    }
    holm = holm_step_down(pvalues)
    invariant_violations = sum(int(row.get("pathwise_invariant_violations", 0)) for row in records)
    invalid_count = sum(int(row.get("invalid_count", 0)) for row in records)
    return {
        "all_history_count": len(records),
        "finite_first_true_null_history_count": len(finite),
        "primary_holm_audit": holm,
        "pathwise_invariant_violations": invariant_violations,
        "invalid_count": invalid_count,
    }


def decide_study_status(
    *, protocol_conformant: bool, fixtures_pass: bool, crosschecks_pass: bool,
    analysis: dict[str, object]
) -> str:
    holm = analysis["primary_holm_audit"]
    passed = (
        protocol_conformant
        and fixtures_pass
        and crosschecks_pass
        and int(analysis["pathwise_invariant_violations"]) == 0
        and int(analysis["invalid_count"]) == 0
        and holm["status"] == "NO_CALIBRATION_RED_FLAG_OBSERVED"
    )
    return "CONFIRMATORY_IMPLEMENTATION_PASS" if passed else "IMPLEMENTATION_HOLD"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("history_results", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    records = json.loads(args.history_results.read_text(encoding="utf-8"))
    summary = analyze_history_records(records)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
