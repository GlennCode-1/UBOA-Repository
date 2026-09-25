#!/usr/bin/env python3
"""Verify the selective public export without changing any scientific file."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "frozen_study"
F1_PATH = FROZEN / "01_FREEZE" / "SCIENTIFIC_FREEZE_MANIFEST.json"
F2_PATH = FROZEN / "10_IMPLEMENTATION" / "IMPLEMENTATION_FREEZE.json"
F1_SHA = "315479da6ef361311219e9ba92b8b9d7cdfc7e1068bf44bb281b987e3f638a15"
F2_SHA = "0f9d5bb9e6b19a1cffa3e1fbe38d34054a0c2328a03f12ea56efe6bf35ca285c"
H_SHA = "5229432f2384a80b2cde4097c68cf08e383cdacbf67642f8de12537895c0e8c9"
EXPECTED_OMISSIONS = {
    "06_PROMPTS/CLAUDE_POSTRUN_AUDIT.md",
    "06_PROMPTS/CLAUDE_PREEXEC_AUDIT.md",
    "06_PROMPTS/CODEX_EXECUTE_AFTER_PASS.md",
    "06_PROMPTS/CODEX_IMPLEMENT_DRYRUN.md",
    "07_REFERENCE/latest_routeA.pdf",
}
OMISSION_METADATA = {
    "frozen_study/06_PROMPTS/CLAUDE_POSTRUN_AUDIT.md": (704, "479088e7dfe0ef4002cf435b78c720e71657a440d32f0eab2610fad2c3c0cf93"),
    "frozen_study/06_PROMPTS/CLAUDE_PREEXEC_AUDIT.md": (1379, "57c1038355336b6572876e3f20dc52206cd6ee6be316b063e2906e7c41aaa576"),
    "frozen_study/06_PROMPTS/CODEX_EXECUTE_AFTER_PASS.md": (773, "b2f8fdf892685aa75bf5ff86207f539504d808d23f1247b7760659801f44e5d7"),
    "frozen_study/06_PROMPTS/CODEX_IMPLEMENT_DRYRUN.md": (1052, "b7e40addc15795dcd8838fa3c35afabe06aed0981b79030bb9cb6471f3b948e5"),
    "frozen_study/07_REFERENCE/latest_routeA.pdf": (392511, "d3c3c39745c6dd59018082473b881b3bda319c65febec69c6dceab59c99c7c10"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fail(issues, message):
    issues.append(message)


def main() -> int:
    issues = []
    omissions_path = ROOT / "PUBLIC_EXPORT_OMISSIONS.json"
    manifest_path = ROOT / "REPRO_PACKAGE_MANIFEST.json"
    if not omissions_path.is_file():
        fail(issues, "missing PUBLIC_EXPORT_OMISSIONS.json")
        omissions = {}
    else:
        omissions = load(omissions_path)
    records = omissions.get("omissions", [])
    omission_paths = {r.get("path") for r in records}
    if omission_paths != {"frozen_study/" + p for p in EXPECTED_OMISSIONS} or len(records) != 5:
        fail(issues, "omission allowlist is not exactly the five fixed paths")
    if omissions.get("source_archive_sha256") != "c858869ce135b04f8b575abd81869d4e4db1dd86a142a46d6e28d6dd56b7398a":
        fail(issues, "source archive SHA mismatch in omission record")
    for record in records:
        source = ROOT / record["path"]
        if source.exists():
            fail(issues, f"omitted file present: {record['path']}")
        rel = record.get("path", "").removeprefix("frozen_study/")
        if record.get("size_bytes") != OMISSION_METADATA.get(record.get("path"), OMISSION_METADATA.get("frozen_study/" + rel, (None, None)))[0] or record.get("sha256") != OMISSION_METADATA.get(record.get("path"), OMISSION_METADATA.get("frozen_study/" + rel, (None, None)))[1]:
            fail(issues, f"omission metadata mismatch: {record['path']}")

    if not F1_PATH.is_file() or sha(F1_PATH) != F1_SHA:
        fail(issues, "F1 scientific manifest hash mismatch")
    if not F2_PATH.is_file() or sha(F2_PATH) != F2_SHA:
        fail(issues, "F2 implementation freeze hash mismatch")
    f1 = load(F1_PATH) if F1_PATH.is_file() else {}
    f2 = load(F2_PATH) if F2_PATH.is_file() else {}
    if f2.get("scientific_protocol_manifest_sha256") != F1_SHA:
        fail(issues, "F2 binding does not retain the F1 manifest hash")
    f1_files = f1.get("files_sha256", {})
    retained = 0
    for rel, expected in f1_files.items():
        path = FROZEN / rel
        if rel in EXPECTED_OMISSIONS:
            if path.exists():
                fail(issues, f"omission unexpectedly restored: {rel}")
            continue
        if not path.is_file():
            fail(issues, f"retained F1 file missing: {rel}")
        elif sha(path) != expected:
            fail(issues, f"retained F1 hash mismatch: {rel}")
        else:
            retained += 1
    if len(f1_files) != 36 or retained != 31:
        fail(issues, f"F1 retained count mismatch: total={len(f1_files)} retained={retained}")

    for field in ("executable_source_sha256", "schema_sha256", "dry_run_artifact_sha256"):
        for rel, expected in f2.get(field, {}).items():
            path = FROZEN / "10_IMPLEMENTATION" / rel
            if not path.is_file() or sha(path) != expected:
                fail(issues, f"F2 {field} mismatch: {rel}")

    h_path = FROZEN / "09_OUTPUTS" / "confirmatory_run" / "H_FREEZE_MANIFEST.json"
    if not h_path.is_file() or sha(h_path) != H_SHA:
        fail(issues, "H_FREEZE_MANIFEST hash mismatch")
    for rel in ("HISTORY_RESULTS.json", "ANALYSIS_SUMMARY.json", "EXECUTION_LOG.jsonl"):
        if not (h_path.parent / rel).is_file():
            fail(issues, f"saved result file missing: {rel}")

    if not manifest_path.is_file():
        fail(issues, "missing distribution manifest")
        manifest = {}
    else:
        manifest = load(manifest_path)
    members = manifest.get("members", [])
    paths = [m.get("path") for m in members]
    if len(paths) != len(set(paths)):
        fail(issues, "distribution manifest contains duplicate paths")
    if "REPRO_PACKAGE_MANIFEST.json" in paths:
        fail(issues, "distribution manifest must exclude itself")
    full_omissions = {"frozen_study/" + p for p in EXPECTED_OMISSIONS}
    if any(p in full_omissions for p in paths):
        fail(issues, "distribution manifest lists an omitted path")
    for p in paths:
        path = ROOT / p
        if not p or Path(p).is_absolute() or ".." in Path(p).parts:
            fail(issues, f"unsafe manifest path: {p}")
        elif not path.is_file() or path.is_symlink():
            fail(issues, f"manifest member missing or symlink: {p}")
        else:
            entry = next(m for m in members if m.get("path") == p)
            if entry.get("size_bytes") != path.stat().st_size or entry.get("sha256") != sha(path):
                fail(issues, f"manifest member hash/size mismatch: {p}")

    result = {
        "status": "PASS" if not issues else "FAIL",
        "retained_F1_files_verified": retained,
        "intentionally_not_distributed": len(EXPECTED_OMISSIONS),
        "full_original_tree_verified": False,
        "f1_manifest_sha256": F1_SHA,
        "f2_freeze_sha256": F2_SHA,
        "h_freeze_sha256": H_SHA,
        "manifest_members": len(members),
        "issues": issues,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
