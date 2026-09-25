"""Single locked stochastic entry point for the future F2 execution.

Do not invoke before an independent audit binds PASS_TO_EXECUTE to the exact
IMPLEMENTATION_FREEZE.json hash. Dry-run tests compile and inspect this file but
never import or execute ``main``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import numpy as np

from analyze_confirmatory import analyze_history_records, decide_study_status
from certificate_b1 import b1_certificate, b1_scalar_reference
from certificate_qb import gaussian_variance_identity, quadratic_certificate
from fixed_sequence import potential_local_tests, run_fixed_sequence
from generators import evolve_b1, evolve_qb
from protocol import (
    H_END, HORIZONS, INNER_FUTURES, LADDER, OUTER_HISTORIES, ROOT, load_cells,
)
from seed_schedule import derive_seed, stream_key
from selection import select_b1_delta, select_qb_gamma
from truth import b1_mae_risk, b1_theta, b1_truth_vector, qb_truth, serialize_fraction
from verify_outputs import (
    sha256_file, verify_h_manifest, verify_history_results,
    verify_cross_manifest, verify_implementation_freeze, verify_scientific_freeze,
)


def _canonical_hash(document: object) -> str:
    payload = json.dumps(document, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(payload).hexdigest()


def _atomic_json(path: Path, document: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(document, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _append_event(path: Path, event: dict[str, object]) -> None:
    record = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), **event}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True, allow_nan=False) + "\n")


def _require_audit(audit_path: Path, implementation_freeze: Path) -> None:
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    verdict = audit.get("verdict", audit.get("status"))
    if verdict != "PASS_TO_EXECUTE":
        raise RuntimeError("independent pre-execution verdict is not PASS_TO_EXECUTE")
    expected = sha256_file(implementation_freeze)
    if audit.get("implementation_freeze_sha256") != expected:
        raise RuntimeError("audit verdict is not bound to this implementation freeze")


def _b1_history_record(cell: object, outer_index: int, states: np.ndarray) -> dict[str, object]:
    selected, scores = select_b1_delta(states)
    theta = b1_theta(cell.comparator_delta)
    truths = b1_truth_vector(cell.comparator_delta)
    first = next((i for i, value in enumerate(truths) if value), None)
    expected_label = None if cell.frozen_first_true_null == "none" else {"r=0": 0, "r=0.02": 1, "r=0.05": 2}[cell.frozen_first_true_null]
    if first != expected_label or theta != cell.exact_theta:
        raise RuntimeError(f"B1 exact truth mismatch:{cell.cell_id}")
    selected_risk = b1_mae_risk(Fraction(1, 10))
    baseline_risk = b1_mae_risk(cell.comparator_delta)
    certificates = []
    means = []
    for r in LADDER:
        cert = b1_certificate(r)
        ref = b1_scalar_reference(r)
        if not math.isclose(float(cert["threshold"]), float(ref["threshold"]), rel_tol=1e-10, abs_tol=1e-10):
            raise RuntimeError(f"B1 certificate cross-check:{cell.cell_id}:{r}")
        certificates.append(float(cert["threshold"]))
        means.append(float((1 - r) * baseline_risk - selected_risk))
    return {
        "history_id": f"{cell.cell_id}__{outer_index}",
        "cell_id": cell.cell_id,
        "outer_index": outer_index,
        "branch": "B1",
        "outer_rng_key": stream_key(cell.cell_id, "outer", outer_index),
        "state_path_through_325": states.tolist(),
        "selected_label": f"delta={selected:+.1f}",
        "selected_parameter": selected,
        "validation_scores": scores,
        "terminal_state": float(states[H_END]),
        "baseline_parameter": serialize_fraction(cell.comparator_delta),
        "theta_exact": serialize_fraction(theta),
        "mu_by_node": means,
        "truth_by_node": list(truths),
        "first_true_null": first,
        "certificate_thresholds": certificates,
    }


def _qb_history_record(cell: object, outer_index: int, states: np.ndarray) -> dict[str, object]:
    selected, scores = select_qb_gamma(states)
    y0 = float(states[H_END])
    direct = qb_truth(cell.comparator_gamma, selected, y0)
    certificates = []
    means = []
    variance_checks = []
    for index, r in enumerate(LADDER):
        cert = quadratic_certificate(cell.comparator_gamma, selected, y0, r)
        direct_mean = float(direct["mu_by_node"][index])
        quadratic_mean = float(cert["conditional_mean"])
        if not math.isclose(direct_mean, quadratic_mean, rel_tol=1e-10, abs_tol=1e-10 * (1.0 + abs(direct_mean))):
            raise RuntimeError(f"QB truth/quadratic expectation mismatch:{cell.cell_id}:{outer_index}:{r}")
        gaussian_v = gaussian_variance_identity(cert["A"], cert["g"])
        if not math.isclose(float(cert["conditional_variance"]), gaussian_v, rel_tol=1e-10, abs_tol=1e-10):
            raise RuntimeError(f"QB variance identity mismatch:{cell.cell_id}:{outer_index}:{r}")
        means.append(quadratic_mean)
        certificates.append(float(cert["threshold"]))
        variance_checks.append(gaussian_v)
    return {
        "history_id": f"{cell.cell_id}__{outer_index}",
        "cell_id": cell.cell_id,
        "outer_index": outer_index,
        "branch": "QB",
        "outer_rng_key": stream_key(cell.cell_id, "outer", outer_index),
        "state_path_through_325": states.tolist(),
        "selected_label": f"gamma={selected:+.1f}",
        "selected_parameter": selected,
        "validation_scores": scores,
        "terminal_state": y0,
        "baseline_parameter": cell.comparator_gamma,
        "theta_exact_H_conditional": float(direct["theta"]),
        "stationary_nominal_label_is_truth": False,
        "mu_by_node": means,
        "truth_by_node": list(direct["truth_by_node"]),
        "first_true_null": direct["first_true_null"],
        "certificate_thresholds": certificates,
        "gaussian_variance_crosschecks": variance_checks,
    }


def _generate_all_histories() -> list[dict[str, object]]:
    histories = []
    for cell in load_cells():
        for outer_index in range(OUTER_HISTORIES):
            seed = derive_seed(cell.cell_id, "outer", outer_index)
            rng = np.random.Generator(np.random.PCG64DXSM(seed))
            if cell.branch.startswith("B1_"):
                innovations = rng.choice(np.asarray([-1, 1], dtype=np.int8), size=H_END, replace=True)
                states = evolve_b1(0.0, innovations)
                record = _b1_history_record(cell, outer_index, states)
            else:
                innovations = rng.standard_normal(H_END, dtype=np.float64)
                states = evolve_qb(0.0, innovations)
                record = _qb_history_record(cell, outer_index, states)
            record["record_sha256"] = _canonical_hash(record)
            histories.append(record)
    if len(histories) != 80:
        raise RuntimeError("all 80 outer histories were not retained")
    return histories


def _loss_averages(states: np.ndarray, branch: str, baseline: float, selected: float, eval_origins: int) -> tuple[np.ndarray, np.ndarray]:
    baseline_total = np.zeros(states.shape[0], dtype=np.float64)
    selected_total = np.zeros(states.shape[0], dtype=np.float64)
    for origin in range(eval_origins):
        origin_state = states[:, origin]
        for horizon in HORIZONS:
            target = states[:, origin + horizon]
            if branch == "B1":
                baseline_error = target - ((0.5**horizon) * origin_state + baseline)
                selected_error = target - ((0.5**horizon) * origin_state + selected)
                baseline_total += np.abs(baseline_error)
                selected_total += np.abs(selected_error)
            else:
                baseline_error = target - ((0.5**horizon + baseline) * origin_state)
                selected_error = target - ((0.5**horizon + selected) * origin_state)
                baseline_total += baseline_error * baseline_error
                selected_total += selected_error * selected_error
    denominator = eval_origins * len(HORIZONS)
    return baseline_total / denominator, selected_total / denominator


def _inner_history_result(history: dict[str, object], cell: object, freeze_hash: str) -> dict[str, object]:
    index = int(history["outer_index"])
    seed = derive_seed(cell.cell_id, "inner", index)
    rng = np.random.Generator(np.random.PCG64DXSM(seed))
    future_length = cell.eval_origins - 1 + max(HORIZONS)
    if history["branch"] == "B1":
        innovations = rng.choice(
            np.asarray([-1, 1], dtype=np.int8), size=(INNER_FUTURES, future_length), replace=True
        )
        states = evolve_b1(float(history["terminal_state"]), innovations)
        baseline = float(Fraction(str(history["baseline_parameter"])))
    else:
        innovations = rng.standard_normal((INNER_FUTURES, future_length), dtype=np.float64)
        states = evolve_qb(float(history["terminal_state"]), innovations)
        baseline = float(history["baseline_parameter"])
    selected = float(history["selected_parameter"])
    baseline_loss, selected_loss = _loss_averages(
        states, str(history["branch"]), baseline, selected, cell.eval_origins
    )
    w_values = np.column_stack(
        [(1.0 - float(r)) * baseline_loss - selected_loss for r in LADDER]
    )
    thresholds = tuple(float(value) for value in history["certificate_thresholds"])
    local_counts = np.zeros(3, dtype=np.int64)
    reached_counts = np.zeros(3, dtype=np.int64)
    false_promotions = 0
    invalid_count = 0
    invariant_violations = 0
    terminal_counts: dict[str, int] = {}
    for row in w_values:
        potential = potential_local_tests(row.tolist(), thresholds)
        local_counts += np.asarray([decision is True for decision in potential], dtype=np.int64)
        operational = run_fixed_sequence(potential, history["truth_by_node"])
        reached_counts += np.asarray(operational["reached"], dtype=np.int64)
        false_promotions += int(operational["false_promotion"])
        invalid_count += int(operational["invalid"])
        invariant_violations += int(not operational["first_true_null_inclusion_ok"])
        terminal = str(operational["terminal_report"])
        terminal_counts[terminal] = terminal_counts.get(terminal, 0) + 1
    checksum_header = f"{innovations.dtype.str}|{innovations.shape}".encode()
    checksum = hashlib.sha256(checksum_header + innovations.tobytes(order="C")).hexdigest()
    return {
        "history_id": history["history_id"],
        "cell_id": cell.cell_id,
        "outer_index": index,
        "history_record_sha256": history["record_sha256"],
        "implementation_freeze_sha256": freeze_hash,
        "inner_rng_key": stream_key(cell.cell_id, "inner", index),
        "inner_batch_sha256": checksum,
        "inner_denominator": INNER_FUTURES,
        "truth_by_node": history["truth_by_node"],
        "first_true_null": history["first_true_null"],
        "local_reject_counts": local_counts.tolist(),
        "reached_counts": reached_counts.tolist(),
        "terminal_report_counts": terminal_counts,
        "false_promotions": false_promotions,
        "invalid_count": invalid_count,
        "pathwise_invariant_violations": invariant_violations,
        "informativeness_margin_mu_minus_threshold": [
            float(mu) - threshold for mu, threshold in zip(history["mu_by_node"], thresholds)
        ],
    }


def _execute_confirmatory(output: Path, implementation_freeze_hash: str) -> int:
    # Phase 1 is complete for all cells before Phase 2 initializes any inner stream.
    histories = _generate_all_histories()
    h_manifest = {
        "study_id": "UBOA_ROUTE_B_SYNTH_CONFIRMATORY_V1",
        "implementation_freeze_sha256": implementation_freeze_hash,
        "history_count": len(histories),
        "histories": histories,
    }
    h_errors = verify_h_manifest(h_manifest)
    if h_errors:
        raise RuntimeError("H manifest invalid: " + "; ".join(h_errors))
    h_path = output / "H_FREEZE_MANIFEST.json"
    _atomic_json(h_path, h_manifest)
    h_hash = sha256_file(h_path)
    (output / "H_FREEZE_MANIFEST.sha256").write_text(f"{h_hash}  H_FREEZE_MANIFEST.json\n", encoding="ascii")

    cells = {cell.cell_id: cell for cell in load_cells()}
    results = [_inner_history_result(history, cells[str(history["cell_id"])], implementation_freeze_hash) for history in histories]
    result_errors = verify_history_results(results)
    result_errors += verify_cross_manifest(h_manifest, results)
    if result_errors:
        raise RuntimeError("history results invalid: " + "; ".join(result_errors))
    _atomic_json(output / "HISTORY_RESULTS.json", results)
    analysis = analyze_history_records(results)
    crosschecks_pass = True
    status = decide_study_status(
        protocol_conformant=True,
        fixtures_pass=True,
        crosschecks_pass=crosschecks_pass,
        analysis=analysis,
    )
    final = {
        "study_id": "UBOA_ROUTE_B_SYNTH_CONFIRMATORY_V1",
        "status": status,
        "h_freeze_manifest_sha256": h_hash,
        "implementation_freeze_sha256": implementation_freeze_hash,
        "analysis": analysis,
        "claim_boundary": "implementation conformance within two frozen synthetic P-classes only",
    }
    _atomic_json(output / "ANALYSIS_SUMMARY.json", final)
    return 0 if status == "CONFIRMATORY_IMPLEMENTATION_PASS" else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--implementation-freeze", required=True, type=Path)
    parser.add_argument("--audit-verdict", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    allowed_parent = (ROOT / "09_OUTPUTS").resolve()
    if output.parent != allowed_parent or output.name != "confirmatory_run":
        raise RuntimeError("output directory must be exactly 09_OUTPUTS/confirmatory_run")
    if output.exists() and any(output.iterdir()):
        raise RuntimeError("refusing to overwrite an existing confirmatory output")
    errors = verify_scientific_freeze() + verify_implementation_freeze(args.implementation_freeze)
    if errors:
        raise RuntimeError("freeze verification failed: " + "; ".join(errors))
    _require_audit(args.audit_verdict, args.implementation_freeze)
    implementation_freeze_hash = sha256_file(args.implementation_freeze)
    output.mkdir(parents=True, exist_ok=True)
    execution_log = output / "EXECUTION_LOG.jsonl"
    _append_event(execution_log, {"event": "LOCKED_EXECUTION_STARTED", "implementation_freeze_sha256": implementation_freeze_hash})
    try:
        status = _execute_confirmatory(output, implementation_freeze_hash)
    except Exception as exc:
        _append_event(
            output / "CRASH_LOG.jsonl",
            {
                "event": "LOCKED_EXECUTION_CRASH",
                "status": "INCOMPLETE_SAME_F2",
                "implementation_freeze_sha256": implementation_freeze_hash,
                "exception_type": type(exc).__name__,
                "message": str(exc),
            },
        )
        raise
    _append_event(execution_log, {"event": "LOCKED_EXECUTION_FINISHED", "exit_status": status})
    return status


if __name__ == "__main__":
    raise SystemExit(main())
