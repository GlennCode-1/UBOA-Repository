"""Create the F2 implementation freeze after deterministic dry-run PASS."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy
import scipy

from protocol import ROOT, STUDY_ID
from verify_outputs import sha256_file, verify_scientific_freeze


HERE = Path(__file__).resolve().parent
SCIENTIFIC_ID = "6caae5a8d5cebebdc94ac31c1afeb1202b6627ff0949aa2fb3c002e7bca29845"
FUTURE_COMMAND = "python3 10_IMPLEMENTATION/run_confirmatory.py --implementation-freeze 10_IMPLEMENTATION/IMPLEMENTATION_FREEZE.json --audit-verdict 11_PREEXEC_AUDIT/FINAL_VERDICT.json --output-dir 09_OUTPUTS/confirmatory_run"


def hashes(paths: list[Path]) -> dict[str, str]:
    return {str(path.relative_to(HERE)): sha256_file(path) for path in sorted(paths)}


def main() -> int:
    if verify_scientific_freeze():
        raise RuntimeError("scientific freeze verification failed")
    dry_path = HERE / "dry_run_artifacts" / "dry_run_results.json"
    dry = json.loads(dry_path.read_text(encoding="utf-8"))
    if dry.get("status") != "PASS" or dry.get("rng_call_count_during_dry_run") != 0 or dry.get("synthetic_paths_generated") != 0:
        raise RuntimeError("deterministic dry-run is not a zero-randomness PASS")
    source_files = list(HERE.glob("*.py")) + list((HERE / "tests").glob("*.py"))
    schema_files = list((HERE / "schemas").glob("*.json"))
    artifact_files = list((HERE / "dry_run_artifacts").glob("*.json"))
    scientific_manifest = ROOT / "01_FREEZE" / "SCIENTIFIC_FREEZE_MANIFEST.json"
    document = {
        "study_id": STUDY_ID,
        "status": "READY_FOR_INDEPENDENT_AUDIT",
        "freeze_created_utc": datetime.now(timezone.utc).isoformat(),
        "scientific_protocol_manifest_id": SCIENTIFIC_ID,
        "scientific_protocol_manifest_sha256": sha256_file(scientific_manifest),
        "executable_source_sha256": hashes(source_files),
        "schema_sha256": hashes(schema_files),
        "dry_run_artifact_sha256": hashes(artifact_files),
        "environment": {
            "python": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "numpy": numpy.__version__,
            "scipy": scipy.__version__,
            "os": platform.platform(),
            "architecture": platform.machine(),
        },
        "future_execution_command": FUTURE_COMMAND,
        "stochastic_execution_count": 0,
        "rng_call_count_during_dry_run": 0,
        "synthetic_paths_generated_during_dry_run": 0,
        "real_dataset_reads": 0,
        "manuscript_edits": 0,
    }
    target = HERE / "IMPLEMENTATION_FREEZE.json"
    target.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    event = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "event": "F2_IMPLEMENTATION_FREEZE_CREATED",
        "status": document["status"],
        "implementation_freeze_sha256": sha256_file(target),
        "source_file_count": len(source_files),
        "stochastic_execution_count": 0,
    }
    with (HERE / "logs" / "IMPLEMENTATION_LOG.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
    print(document["status"])
    print("implementation_freeze_sha256=", event["implementation_freeze_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
