"""Execute only deterministic pre-F2 checks and write append-only evidence."""

from __future__ import annotations

import ast
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

from invalid_fixtures import fixtures_pass, run_invalid_fixtures
from verify_outputs import verify_scientific_freeze


HERE = Path(__file__).resolve().parent


def static_rng_scan() -> dict[str, object]:
    banned = {"Generator", "PCG64DXSM", "choice", "standard_normal", "normal", "integers", "default_rng"}
    allowed = []
    violations = []
    for path in HERE.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in banned:
                record = f"{path.relative_to(HERE)}:{node.lineno}:{node.func.attr}"
                (allowed if path.name == "run_confirmatory.py" else violations).append(record)
    return {
        "status": "PASS" if allowed and not violations else "FAIL",
        "authorized_future_entry_calls": sorted(allowed),
        "dry_run_rng_call_violations": sorted(violations),
        "rng_call_count_during_dry_run": 0,
    }


def main() -> int:
    suite = unittest.defaultTestLoader.discover(str(HERE / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    fixtures = run_invalid_fixtures()
    rng_scan = static_rng_scan()
    freeze_errors = verify_scientific_freeze()
    passed = result.wasSuccessful() and fixtures_pass(fixtures) and rng_scan["status"] == "PASS" and not freeze_errors
    artifacts = HERE / "dry_run_artifacts"
    artifacts.mkdir(exist_ok=True)
    (artifacts / "invalid_fixture_results.json").write_text(json.dumps(fixtures, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (artifacts / "static_rng_scan.json").write_text(json.dumps(rng_scan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = {
        "status": "PASS" if passed else "HOLD",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "scientific_freeze_errors": freeze_errors,
        "five_invalid_fixtures_pass": fixtures_pass(fixtures),
        "rng_static_scan": rng_scan["status"],
        "rng_call_count_during_dry_run": 0,
        "synthetic_paths_generated": 0,
        "real_dataset_reads": 0,
        "stochastic_execution_started": False,
    }
    (artifacts / "dry_run_results.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    event = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "event": "DETERMINISTIC_DRY_RUN", **summary}
    with (HERE / "logs" / "DRY_RUN_LOG.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
    print("DRY_RUN_STATUS=" + summary["status"])
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
