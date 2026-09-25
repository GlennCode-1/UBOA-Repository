#!/usr/bin/env python3
"""Single-use, noninteractive Stage-37 guarded OOS execution."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import math
import os
import sys
import zipfile
from pathlib import Path

import numpy as np

from stage37_common import (
    ARCHIVES,
    AUTH_ID,
    E36,
    ENTRIES,
    METHOD,
    SPLIT_ID,
    STAGE,
    THRESHOLDS,
    canonical_json_bytes,
    load_c2,
    read_json,
    sha256,
    sha256_bytes,
    terminal_from_results,
    threshold_contrast,
    write_json_atomic,
    write_text_atomic,
)


OOS_COUNT = 1024
SESSION_LEDGER = STAGE / "10_integrity/oos_session_ledger.jsonl"
GLOBAL_STATUS = STAGE / "12_gate/FINAL_STAGE37_STATUS.txt"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def ffill(values: np.ndarray) -> np.ndarray:
    result = np.asarray(values, dtype=np.float64).copy()
    last = math.nan
    for index, value in enumerate(result):
        if math.isfinite(float(value)):
            last = float(value)
        elif math.isfinite(last):
            result[index] = last
    return result


def append_session(record: dict) -> None:
    with SESSION_LEDGER.open("a") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def verify_package_and_authorization() -> None:
    preflight = read_json(STAGE / "01_preflight/cohort_preflight.json")
    if preflight["status"] != "PASS" or not all(preflight["checks"].values()):
        raise RuntimeError("PREFLIGHT_NOT_PASS")
    seal = STAGE / "03_execution_package/COHORT_EXECUTION_PACKAGE_SEAL.txt"
    for line in seal.read_text().splitlines():
        if not line or line.startswith("#") or line.startswith("aggregate_sha256="):
            continue
        digest, relative = line.split("  ", 1)
        path = STAGE / relative
        if not path.is_file() or sha256(path) != digest:
            raise RuntimeError(f"EXECUTION_PACKAGE_MISMATCH:{relative}")
    auth = STAGE / f"02_authorization/{AUTH_ID}.json"
    auth_hash = (STAGE / "02_authorization/authorization_hash.txt").read_text().strip().split()[0]
    if sha256(auth) != auth_hash:
        raise RuntimeError("AUTHORIZATION_HASH_MISMATCH")
    auth_data = read_json(auth)
    if auth_data["authorized_benchmark_ids"] != [x["benchmark_id"] for x in ENTRIES]:
        raise RuntimeError("AUTHORIZED_ORDER_MISMATCH")
    consumption = read_json(STAGE / "02_authorization/authorization_consumption_record.json")
    if consumption["authorization_use_count_after"] != 1:
        raise RuntimeError("AUTHORIZATION_NOT_CONSUMED_EXACTLY_ONCE")
    if consumption["cohort_execution_package_seal_sha256"] != sha256(seal):
        raise RuntimeError("CONSUMED_PACKAGE_SEAL_MISMATCH")
    if GLOBAL_STATUS.exists():
        raise RuntimeError("STAGE37_TERMINAL_STATUS_ALREADY_EXISTS_NO_RETRY")
    if SESSION_LEDGER.exists() and SESSION_LEDGER.stat().st_size:
        raise RuntimeError("OOS_SESSION_LEDGER_NOT_EMPTY_NO_RETRY")
    load_c2()


def stream_source_values(entry: dict, row_limit: int) -> np.ndarray:
    """Open exactly one archive/member session and decode at most row_limit rows."""
    archive_path = ARCHIVES / entry["archive"]
    values = []
    with zipfile.ZipFile(archive_path) as archive:
        raw = archive.open(entry["member"])
        if entry.get("gzip_member"):
            raw = gzip.GzipFile(fileobj=raw)
        encoding = "latin-1" if entry["benchmark_id"] == "UCI360_AIR_QUALITY_CO" else "utf-8"
        delimiter = ";" if entry["benchmark_id"] in {"UCI235_HOUSEHOLD_POWER", "UCI360_AIR_QUALITY_CO"} else ","
        with io.TextIOWrapper(raw, encoding=encoding, errors="replace", newline="") as text:
            for index, row in enumerate(csv.DictReader(text, delimiter=delimiter)):
                if index >= row_limit:
                    break
                token = (row.get(entry["target"]) or "").strip()
                if entry["benchmark_id"] == "UCI360_AIR_QUALITY_CO":
                    token = token.replace(",", ".")
                try:
                    value = float(token)
                except ValueError:
                    value = math.nan
                if entry["benchmark_id"] == "UCI360_AIR_QUALITY_CO" and value <= -199:
                    value = math.nan
                values.append(value)
    if len(values) != row_limit:
        raise RuntimeError(f"SOURCE_ROW_COUNT_MISMATCH:{len(values)}:{row_limit}")
    return np.asarray(values, dtype=np.float64)


def load_one_authorized_suffix(entry: dict) -> tuple[np.ndarray, int, dict]:
    source_boundary = math.floor(0.8 * entry["source_rows"])
    horizon = max(entry["horizons"])
    needed_normalized_oos = entry["gap"] + OOS_COUNT + horizon - 1
    if entry.get("aggregate_hourly"):
        row_limit = source_boundary + needed_normalized_oos * 60
        if row_limit > entry["source_rows"]:
            raise RuntimeError("INSUFFICIENT_AUTHORIZED_OOS_ROWS")
        raw = ffill(stream_source_values(entry, row_limit))
        if not np.all(np.isfinite(raw)):
            raise RuntimeError("UNSUPPORTED_INITIAL_MISSINGNESS")
        prefix_usable = (source_boundary // 60) * 60
        prefix = raw[:prefix_usable].reshape(-1, 60).mean(axis=1)
        suffix = raw[source_boundary:row_limit].reshape(-1, 60).mean(axis=1)
        series = np.concatenate([prefix, suffix])
        normalized_boundary = len(prefix)
        content = suffix
        meta = {
            "source_boundary_row": source_boundary,
            "raw_rows_decoded_this_session": row_limit,
            "oos_raw_rows_numerically_exposed": needed_normalized_oos * 60,
            "normalized_boundary": normalized_boundary,
            "oos_normalized_values_used": len(suffix),
            "causal_hourly_aggregation": "60 consecutive suffix rows per OOS hour; prefix partial hour excluded",
        }
    else:
        row_limit = source_boundary + needed_normalized_oos
        if row_limit > entry["source_rows"]:
            raise RuntimeError("INSUFFICIENT_AUTHORIZED_OOS_ROWS")
        series = ffill(stream_source_values(entry, row_limit))
        if not np.all(np.isfinite(series)):
            raise RuntimeError("UNSUPPORTED_INITIAL_MISSINGNESS")
        normalized_boundary = source_boundary
        content = series[source_boundary:row_limit]
        meta = {
            "source_boundary_row": source_boundary,
            "rows_decoded_this_session": row_limit,
            "oos_values_numerically_exposed": len(content),
            "normalized_boundary": normalized_boundary,
        }
    content_bytes = np.ascontiguousarray(content, dtype="<f8").tobytes()
    meta["post_authorization_oos_content_sha256"] = sha256_bytes(content_bytes)
    meta["content_hash_domain"] = "CAUSALLY_FILLED_NORMALIZED_OOS_VALUES_USED_BY_FROZEN_EXECUTION"
    return series, normalized_boundary, meta


def atomic_npz(path: Path, **arrays) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("wb") as handle:
        np.savez_compressed(handle, **arrays)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def compute_losses(entry: dict, series: np.ndarray, boundary: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    origin_start = boundary + entry["gap"]
    origins = np.arange(origin_start, origin_start + OOS_COUNT, dtype=np.int64)
    last_target = int(origins[-1] + max(entry["horizons"]) - 1)
    if last_target >= len(series):
        raise RuntimeError("OOS_SCOPE_EXCEEDS_SINGLE_SESSION_CONTENT")
    lookback = entry["lookback"]
    x = np.stack([series[t - lookback:t] for t in origins])
    y = np.stack([[series[t + horizon - 1] for horizon in entry["horizons"]] for t in origins])
    checkpoint = E36 / "03_training_validation/checkpoints" / entry["checkpoint"]
    coef = np.load(checkpoint)["coef"]
    if coef.shape != (lookback + 1, len(entry["horizons"])):
        raise RuntimeError("RIDGE_CHECKPOINT_SHAPE_MISMATCH")
    selected_prediction = np.c_[np.ones(len(x)), x] @ coef
    if entry["comparator"].startswith("SEASONAL_NAIVE_LAG"):
        lag = int(entry["comparator"].split("LAG")[-1])
        comparator_prediction = np.repeat(series[origins - lag, None], len(entry["horizons"]), axis=1)
    elif entry["comparator"] == "LAST_VALUE":
        comparator_prediction = np.repeat(series[origins - 1, None], len(entry["horizons"]), axis=1)
    else:
        raise RuntimeError("COMPARATOR_IDENTITY_MISMATCH")
    if entry["primary_loss"] == "MAE":
        comparator_loss = np.abs(comparator_prediction - y).mean(axis=1)
        selected_loss = np.abs(selected_prediction - y).mean(axis=1)
    elif entry["primary_loss"] == "MSE":
        comparator_loss = ((comparator_prediction - y) ** 2).mean(axis=1)
        selected_loss = ((selected_prediction - y) ** 2).mean(axis=1)
    else:
        raise RuntimeError("LOSS_IDENTITY_MISMATCH")
    return origins, comparator_loss.astype(np.float64), selected_loss.astype(np.float64)


def run_nodes(comparator_loss: np.ndarray, selected_loss: np.ndarray) -> list[dict]:
    evaluate, reference = load_c2()
    results = []
    for threshold in THRESHOLDS:
        contrast = threshold_contrast(comparator_loss, selected_loss, threshold)
        result = evaluate(contrast, reference, METHOD["critical_value"], mu0=0.0)
        node = {
            "threshold": threshold,
            "status": result["status"],
            "rejection": result.get("rejection"),
            "p_value": result.get("p_value"),
            "test_statistic": result.get("test_statistic"),
            "normalizer": result.get("normalizer"),
            "sample_mean_contrast": result.get("sample_mean"),
            "reason": result.get("reason"),
            "method_id": METHOD["method_id"],
            "critical_value": METHOD["critical_value"],
            "confirmatory": True,
        }
        results.append(node)
        if node["status"] != "VALID" or not node["rejection"]:
            break
    return results


def replay_saved_evidence(entry: dict, evidence_path: Path, original_nodes: list[dict], outdir: Path) -> None:
    saved = np.load(evidence_path)
    replay_nodes = run_nodes(saved["comparator_loss"], saved["selected_loss"])
    exact = canonical_json_bytes(replay_nodes) == canonical_json_bytes(original_nodes)
    record = {
        "benchmark_id": entry["benchmark_id"],
        "source": "SAVED_EVIDENCE_ONLY",
        "oos_source_reopened": False,
        "prediction_rerun": False,
        "reached_nodes_only": [x["threshold"] for x in original_nodes],
        "exact": exact,
        "original_nodes_sha256": sha256_bytes(canonical_json_bytes(original_nodes)),
        "replay_nodes_sha256": sha256_bytes(canonical_json_bytes(replay_nodes)),
    }
    write_json_atomic(outdir / "saved_evidence_C2_reconciliation.json", record)
    if not exact:
        raise RuntimeError("SAVED_EVIDENCE_C2_RECONCILIATION_FAILURE")


def diagnostics_from_saved(entry: dict, evidence_path: Path, outdir: Path) -> None:
    saved = np.load(evidence_path)
    comparator = saved["comparator_loss"]
    selected = saved["selected_loss"]
    z = comparator - selected
    centered = z - z.mean()
    rho1 = 0.0
    if np.std(centered[:-1]) > 0 and np.std(centered[1:]) > 0:
        rho1 = float(np.corrcoef(centered[:-1], centered[1:])[0, 1])
    block = 128
    variances = [float(np.var(z[i:i + block])) for i in range(0, len(z), block)]
    diagnostic = {
        "label": "NONCONFIRMATORY_DIAGNOSTIC",
        "confirmatory_promotion_allowed": False,
        "benchmark_id": entry["benchmark_id"],
        "source": "SAVED_BASE_EVIDENCE_ONLY",
        "mean_loss_difference": float(z.mean()),
        "median_loss_difference": float(np.median(z)),
        "lag1_autocorrelation": rho1,
        "block_variance_ratio": max(variances) / max(min(variances), 1e-15),
        "terminal_change_allowed": False,
        "next_benchmark_adaptation_allowed": False,
    }
    write_json_atomic(STAGE / "09_post_terminal_diagnostics" / f"{entry['benchmark_id']}_diagnostic.json", diagnostic)
    write_json_atomic(outdir / "diagnostic_pointer.json", {
        "benchmark_id": entry["benchmark_id"],
        "diagnostic_path": str((STAGE / "09_post_terminal_diagnostics" / f"{entry['benchmark_id']}_diagnostic.json").relative_to(STAGE)),
        "confirmatory_promotion_allowed": False,
    })


def run_entry(entry: dict) -> dict:
    outdir = STAGE / entry["output_dir"]
    session_id = f"STAGE37_{entry['benchmark_id']}_SINGLE_OOS_SESSION"
    lineage = {
        "authorization_id": AUTH_ID,
        "authorization_consumption_record_sha256": sha256(STAGE / "02_authorization/authorization_consumption_record.json"),
        "benchmark_id": entry["benchmark_id"],
        "selection_lock_sha256": entry["selection_lock_sha256"],
        "execution_order": entry["execution_order"],
        "single_session_id": session_id,
    }
    write_json_atomic(outdir / "authorization_lineage.json", lineage)
    append_session({"event": "SESSION_STARTED", "session_id": session_id, "benchmark_id": entry["benchmark_id"], "utc": utc_now()})
    exposed = False
    try:
        exposed = True
        series, boundary, source_meta = load_one_authorized_suffix(entry)
        origins, comparator_loss, selected_loss = compute_losses(entry, series, boundary)
        evidence = outdir / "base_paired_loss_evidence.npz"
        atomic_npz(evidence, origin=origins, comparator_loss=comparator_loss, selected_loss=selected_loss)
        evidence_hash = sha256(evidence)
        write_text_atomic(outdir / "base_evidence_hash.txt", f"{evidence_hash}  base_paired_loss_evidence.npz\n")
        os.chmod(evidence, 0o444)
        write_json_atomic(outdir / "post_authorization_content_hash.json", {
            "benchmark_id": entry["benchmark_id"],
            **source_meta,
            "hash_created_after_authorization_consumption": True,
            "oos_session_count": 1,
        })
        finite = bool(np.all(np.isfinite(comparator_loss)) and np.all(np.isfinite(selected_loss)))
        if finite:
            nodes = run_nodes(comparator_loss, selected_loss)
        else:
            nodes = [{
                "threshold": 0.0,
                "status": "INVALID",
                "rejection": None,
                "reason": "NONFINITE_LOSSES",
                "method_id": METHOD["method_id"],
                "critical_value": METHOD["critical_value"],
                "confirmatory": True,
            }]
        terminal = terminal_from_results(nodes)
        write_json_atomic(outdir / "reached_node_records.json", nodes)
        write_json_atomic(outdir / "fixed_sequence_trace.json", {
            "benchmark_id": entry["benchmark_id"],
            "fixed_order": list(THRESHOLDS),
            "reached_nodes": [x["threshold"] for x in nodes],
            "unreached_nodes_not_computed": [x for x in THRESHOLDS if x not in [n["threshold"] for n in nodes]],
            "stop_rule_followed": True,
            "c1_fallback": False,
            "terminal": terminal,
        })
        descriptive_reduction = 1.0 - float(selected_loss.mean()) / float(comparator_loss.mean())
        terminal_record = {
            "benchmark_id": entry["benchmark_id"],
            "pre_oos_disposition": "STATISTICAL_READY",
            "selected_realization": entry["selected_realization"],
            "comparator": entry["comparator"],
            "primary_loss": entry["primary_loss"],
            "scope": {"horizons": entry["horizons"], "origins": OOS_COUNT, "aggregation": "MEAN_ACROSS_FIXED_HORIZONS_PER_ORIGIN"},
            "oos_authorized": True,
            "oos_executed": True,
            "oos_session_count": 1,
            "base_evidence_stream_count": 1,
            "terminal_outcome": terminal,
            "reached_nodes": [x["threshold"] for x in nodes],
            "descriptive_relative_loss_reduction": descriptive_reduction,
            "positive_promotion_allowed": terminal != "UNRESOLVED_INVALID_EVIDENCE",
            "diagnostic_only_flags": ["POST_TERMINAL_DIAGNOSTICS_NONCONFIRMATORY"],
            "base_evidence_sha256": evidence_hash,
            "post_authorization_oos_content_sha256": source_meta["post_authorization_oos_content_sha256"],
        }
        write_json_atomic(outdir / "terminal_record.json", terminal_record)
        write_json_atomic(outdir / "descriptive_summary.json", {
            "benchmark_id": entry["benchmark_id"],
            "mean_comparator_loss": float(comparator_loss.mean()),
            "mean_selected_loss": float(selected_loss.mean()),
            "descriptive_relative_loss_reduction": descriptive_reduction,
            "confirmatory_promotion_allowed": False,
            "label": "DESCRIPTIVE_ONLY_EXCEPT_FROZEN_C2_TRACE",
        })
        # Source is closed and terminal is sealed before any diagnostics or replay.
        diagnostics_from_saved(entry, evidence, outdir)
        replay_saved_evidence(entry, evidence, nodes, outdir)
        write_json_atomic(outdir / "execution_integrity_report.json", {
            "benchmark_id": entry["benchmark_id"],
            "status": "PASS",
            "oos_execution_sessions": 1,
            "base_paired_loss_evidence_streams": 1,
            "post_authorization_content_hashes": 1,
            "scientific_retries": 0,
            "node_specific_oos_reloads": 0,
            "prediction_reruns": 0,
            "candidate_reselection": 0,
            "comparator_loss_scope_threshold_method_mutations": 0,
            "source_closed_before_saved_evidence_replay": True,
        })
        append_session({"event": "SESSION_CLOSED", "session_id": session_id, "benchmark_id": entry["benchmark_id"], "terminal": terminal, "utc": utc_now()})
        return terminal_record
    except Exception as exc:
        append_session({"event": "SESSION_FAILED", "session_id": session_id, "benchmark_id": entry["benchmark_id"], "after_possible_numerical_exposure": exposed, "error": repr(exc), "utc": utc_now()})
        write_text_atomic(GLOBAL_STATUS, "FINAL_STAGE37_STATUS=HOLD_PARTIAL_COHORT_OOS_EXPOSURE_RECOVERY_REQUIRED\n")
        write_json_atomic(STAGE / "10_integrity/execution_failure.json", {
            "benchmark_id": entry["benchmark_id"],
            "error": repr(exc),
            "after_possible_oos_exposure": exposed,
            "not_yet_opened_benchmarks_forbidden": True,
            "retry_forbidden": True,
        })
        raise


def self_test() -> int:
    comparator = np.array([2.0, 2.0, 2.0])
    selected = np.array([1.0, 1.0, 1.0])
    assert np.allclose(threshold_contrast(comparator, selected, 0.02), 0.96)
    assert terminal_from_results([{"status": "VALID", "rejection": False}]) == "NO_POSITIVE_CLAIM"
    assert terminal_from_results([{"status": "VALID", "rejection": True}, {"status": "VALID", "rejection": False}]) == "POSITIVE_IMPROVEMENT"
    assert terminal_from_results([{"status": "INVALID", "rejection": None}]) == "UNRESOLVED_INVALID_EVIDENCE"
    load_c2()
    print("SELF_TEST_PASS_NO_OOS_ACCESS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    verify_package_and_authorization()
    write_json_atomic(STAGE / "10_integrity/execution_start.json", {
        "utc": utc_now(),
        "execution_order": [x["benchmark_id"] for x in ENTRIES],
        "authorization_consumption_count": 1,
        "prior_oos_sessions": 0,
    })
    terminals = []
    for entry in ENTRIES:
        terminals.append(run_entry(entry))
    write_json_atomic(STAGE / "08_terminal_registry/statistical_terminal_records.json", terminals)
    write_json_atomic(STAGE / "10_integrity/execution_complete.json", {
        "utc": utc_now(),
        "statistical_oos_benchmark_sessions": 4,
        "base_paired_loss_evidence_streams": 4,
        "post_authorization_oos_content_hashes": 4,
        "confirmatory_c2_calls": sum(len(x["reached_nodes"]) for x in terminals),
        "saved_evidence_replay_c2_calls": sum(len(x["reached_nodes"]) for x in terminals),
        "scientific_retries": 0,
        "node_specific_oos_reloads": 0,
        "prediction_reruns": 0,
        "beijing_oos_sessions": 0,
        "bike_oos_sessions": 0,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
