"""Manifest, schema-shape, hash, and denominator verification."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from protocol import EXPECTED_CELLS, INNER_FUTURES, OUTER_HISTORIES, ROOT


IMPLEMENTATION_DIR = Path(__file__).resolve().parent


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_scientific_freeze() -> list[str]:
    manifest = json.loads((ROOT / "01_FREEZE" / "SCIENTIFIC_FREEZE_MANIFEST.json").read_text())
    errors = []
    for relative, expected in manifest["files_sha256"].items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing scientific file:{relative}")
        elif sha256_file(path) != expected:
            errors.append(f"scientific hash mismatch:{relative}")
    canonical = hashlib.sha256(
        json.dumps(manifest["files_sha256"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if canonical != manifest["manifest_id"]:
        errors.append("scientific manifest internal id mismatch")
    return errors


def verify_implementation_freeze(path: Path | None = None) -> list[str]:
    path = path or IMPLEMENTATION_DIR / "IMPLEMENTATION_FREEZE.json"
    if not path.is_file():
        return ["implementation freeze missing"]
    freeze = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    expected_sources = freeze.get("executable_source_sha256", {})
    actual_sources = {
        str(source.relative_to(IMPLEMENTATION_DIR))
        for source in IMPLEMENTATION_DIR.rglob("*.py")
    }
    if actual_sources != set(expected_sources):
        errors.append(
            "implementation source set mismatch:"
            + repr({"unlisted": sorted(actual_sources - set(expected_sources)), "missing": sorted(set(expected_sources) - actual_sources)})
        )
    for relative, expected in expected_sources.items():
        source = IMPLEMENTATION_DIR / relative
        if not source.is_file():
            errors.append(f"missing implementation source:{relative}")
        elif sha256_file(source) != expected:
            errors.append(f"implementation hash mismatch:{relative}")
    for field in ("schema_sha256", "dry_run_artifact_sha256"):
        for relative, expected in freeze.get(field, {}).items():
            artifact = IMPLEMENTATION_DIR / relative
            if not artifact.is_file():
                errors.append(f"missing frozen artifact:{relative}")
            elif sha256_file(artifact) != expected:
                errors.append(f"frozen artifact hash mismatch:{relative}")
    return errors


def verify_h_manifest(document: dict[str, object]) -> list[str]:
    errors = []
    histories = document.get("histories")
    if not isinstance(histories, list) or len(histories) != EXPECTED_CELLS * OUTER_HISTORIES:
        return ["H manifest must contain all 80 histories"]
    ids = set()
    for row in histories:
        required = {"history_id", "cell_id", "outer_index", "state_path_through_325", "selected_label", "validation_scores", "terminal_state", "truth_by_node", "first_true_null", "certificate_thresholds"}
        if not required.issubset(row):
            errors.append(f"H record missing fields:{row.get('history_id','UNKNOWN')}")
            continue
        ids.add(row["history_id"])
        if len(row["state_path_through_325"]) != 326:
            errors.append(f"H path length:{row['history_id']}")
        if len(row["truth_by_node"]) != 3 or len(row["certificate_thresholds"]) != 3:
            errors.append(f"H node vector length:{row['history_id']}")
        if any(not isinstance(value, (int, float)) for value in row["state_path_through_325"]):
            errors.append(f"H nonnumeric state path:{row['history_id']}")
        expected_record_hash = hashlib.sha256(
            json.dumps(
                {key: value for key, value in row.items() if key != "record_sha256"},
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode()
        ).hexdigest()
        if row.get("record_sha256") != expected_record_hash:
            errors.append(f"H record hash:{row['history_id']}")
    if len(ids) != EXPECTED_CELLS * OUTER_HISTORIES:
        errors.append("H history ids are not unique")
    return errors


def verify_history_results(records: list[dict[str, object]]) -> list[str]:
    errors = []
    if len(records) != EXPECTED_CELLS * OUTER_HISTORIES:
        errors.append("history results must retain all 80 histories")
    ids = set()
    for row in records:
        ids.add(row.get("history_id"))
        if int(row.get("inner_denominator", -1)) != INNER_FUTURES:
            errors.append(f"inner denominator:{row.get('history_id','UNKNOWN')}")
        for key in ("false_promotions", "invalid_count", "pathwise_invariant_violations"):
            value = int(row.get(key, -1))
            if not 0 <= value <= INNER_FUTURES:
                errors.append(f"invalid count {key}:{row.get('history_id','UNKNOWN')}")
        for key in ("local_reject_counts", "reached_counts"):
            values = row.get(key)
            if not isinstance(values, list) or len(values) != 3 or any(not 0 <= int(v) <= INNER_FUTURES for v in values):
                errors.append(f"invalid node counts {key}:{row.get('history_id','UNKNOWN')}")
        if sum(int(v) for v in row.get("terminal_report_counts", {}).values()) != INNER_FUTURES:
            errors.append(f"terminal denominator:{row.get('history_id','UNKNOWN')}")
        reached = row.get("reached_counts", [])
        if len(reached) == 3 and (int(reached[0]) != INNER_FUTURES or int(reached[0]) < int(reached[1]) or int(reached[1]) < int(reached[2])):
            errors.append(f"fixed-sequence reached monotonicity:{row.get('history_id','UNKNOWN')}")
    if len(ids) != EXPECTED_CELLS * OUTER_HISTORIES:
        errors.append("history result ids are not unique")
    return errors


def verify_cross_manifest(h_document: dict[str, object], records: list[dict[str, object]]) -> list[str]:
    histories = {row["history_id"]: row for row in h_document.get("histories", [])}
    results = {row["history_id"]: row for row in records}
    if set(histories) != set(results):
        return ["H/result history-id sets differ"]
    errors = []
    for history_id, history in histories.items():
        result = results[history_id]
        for key in ("cell_id", "outer_index", "truth_by_node", "first_true_null"):
            if result.get(key) != history.get(key):
                errors.append(f"H/result mismatch {key}:{history_id}")
        if result.get("history_record_sha256") != history.get("record_sha256"):
            errors.append(f"H/result record hash mismatch:{history_id}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--implementation-freeze", type=Path, default=IMPLEMENTATION_DIR / "IMPLEMENTATION_FREEZE.json")
    parser.add_argument("--h-manifest", type=Path)
    parser.add_argument("--history-results", type=Path)
    args = parser.parse_args()
    errors = verify_scientific_freeze() + verify_implementation_freeze(args.implementation_freeze)
    h_document = json.loads(args.h_manifest.read_text(encoding="utf-8")) if args.h_manifest else None
    records = json.loads(args.history_results.read_text(encoding="utf-8")) if args.history_results else None
    if h_document:
        errors += verify_h_manifest(h_document)
    if records:
        errors += verify_history_results(records)
    if h_document and records:
        errors += verify_cross_manifest(h_document, records)
    if errors:
        print("VERIFY_OUTPUTS=FAIL")
        for error in errors:
            print(error)
        return 1
    print("VERIFY_OUTPUTS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
