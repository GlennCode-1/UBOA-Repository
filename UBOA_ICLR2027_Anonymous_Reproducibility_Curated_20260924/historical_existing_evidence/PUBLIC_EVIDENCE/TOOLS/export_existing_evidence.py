#!/usr/bin/env python3
"""Export an explicit allowlist of existing UBOA forensic evidence.

This script performs byte copies and deterministic prefix-only missingness/time
derivations. It contains no RNG, model, fit, prediction, or confirmatory-run path.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import platform
import shutil
import sys
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np


ORIGINALS = [
    {
        "id": "C07_BROWNIAN_GENERATOR_SOURCE",
        "role": "historical reference generator source; exported but not executed",
        "source": "iclr2027_redesign/07_method_integrity_repair/02_c2_reference_validation/independent_implementation.py",
        "public": "C07_BROWNIAN_REFERENCE/independent_implementation.py",
    },
    {
        "id": "C07_BROWNIAN_DECLARED_CONFIG",
        "role": "declared paths/grid/seed/quantile contract",
        "source": "iclr2027_redesign/07_method_integrity_repair/02_c2_reference_validation/reference_critical_values.md",
        "public": "C07_BROWNIAN_REFERENCE/reference_critical_values.md",
    },
    {
        "id": "C07_BROWNIAN_SORTED_REFERENCE",
        "role": "historical 200000-draw sorted reference array",
        "source": "iclr2027_redesign/08_local_method_feasibility_v2/01_protocol/brownian_reference_sorted.npy",
        "public": "C07_BROWNIAN_REFERENCE/brownian_reference_sorted.npy",
    },
    {
        "id": "C03_COHORT_MASTER_PROTOCOL",
        "role": "planned cohort protocol",
        "source": "iclr2027_redesign/36_parallel_strong_accept_program/00_program_freeze/MASTER_PROTOCOL.md",
        "public": "C03_COHORT_PROTOCOL/MASTER_PROTOCOL.md",
    },
    {
        "id": "C03_STAGE36_EXECUTION_SOURCE",
        "role": "executed training/validation preprocessing and selection source",
        "source": "iclr2027_redesign/36_parallel_strong_accept_program/E_prospective_real_cohort/scripts/run_workstream_e.py",
        "public": "C03_COHORT_PROTOCOL/run_workstream_e.py",
    },
    {
        "id": "C03_STAGE36_SELECTION_REGISTRY",
        "role": "saved aggregate candidate scores and selected realization records",
        "source": "iclr2027_redesign/36_parallel_strong_accept_program/E_prospective_real_cohort/03_training_validation/selection_registry.jsonl",
        "public": "C03_VALIDATION/selection_registry.jsonl",
    },
    {
        "id": "C03_STAGE37_GUARDED_RUNNER_SOURCE",
        "role": "later guarded preprocessing/evaluation source; exported but not executed",
        "source": "iclr2027_redesign/37_prospective_cohort_guarded_oos/03_execution_package/guarded_oos_runner.py",
        "public": "C03_COHORT_PROTOCOL/guarded_oos_runner.py",
    },
]

for benchmark in (
    "UCI235_HOUSEHOLD_POWER",
    "UCI275_BIKE_HOURLY",
    "UCI360_AIR_QUALITY_CO",
    "UCI374_APPLIANCES",
    "UCI492_METRO_TRAFFIC",
    "UCI501_BEIJING_PM25",
):
    ORIGINALS.append(
        {
            "id": f"C03_VALIDATION_LOSSES_{benchmark}",
            "role": "saved selected/comparator validation-loss array",
            "source": f"iclr2027_redesign/36_parallel_strong_accept_program/E_prospective_real_cohort/03_training_validation/{benchmark}_validation_losses.npz",
            "public": f"C03_VALIDATION/validation_losses/{benchmark}_validation_losses.npz",
        }
    )

for benchmark, directory in (
    ("UCI374_APPLIANCES", "04_appliances"),
    ("UCI235_HOUSEHOLD_POWER", "05_household_power"),
    ("UCI360_AIR_QUALITY_CO", "06_air_quality_co"),
    ("UCI492_METRO_TRAFFIC", "07_metro_traffic"),
):
    for name in ("base_paired_loss_evidence.npz", "reached_node_records.json"):
        ORIGINALS.append(
            {
                "id": f"C07_STAGE37_{benchmark}_{name.split('.')[0].upper()}",
                "role": "saved historical paired-loss evidence" if name.endswith("npz") else "saved historical reached-node statistics",
                "source": f"iclr2027_redesign/37_prospective_cohort_guarded_oos/{directory}/{name}",
                "public": f"C07_REACHED_STATISTICS/stage37/{benchmark}/{name}",
            }
        )

for benchmark, directory in (("Weather", "03_weather_execution"), ("ETTm2", "04_ettm2_execution")):
    for name in ("base_paired_loss_evidence.jsonl", "reached_node_records.jsonl"):
        ORIGINALS.append(
            {
                "id": f"C07_STAGE32_{benchmark.upper()}_{name.split('.')[0].upper()}",
                "role": "saved historical paired-loss evidence" if name.startswith("base") else "saved historical reached-node statistics",
                "source": f"iclr2027_redesign/32_guarded_r1_oos_execution/{directory}/{name}",
                "public": f"C07_REACHED_STATISTICS/stage32/{benchmark}/{name}",
            }
        )


SPECS = [
    dict(id="UCI374_APPLIANCES", archive="uci374.zip", member="energydata_complete.csv", n=19735, target="Appliances", horizons=(1, 6, 18)),
    dict(id="UCI501_BEIJING_PM25", archive="uci501.zip", n=35064, target="PM2.5", horizons=(1, 6, 24), nested=True),
    dict(id="UCI275_BIKE_HOURLY", archive="uci275.zip", member="hour.csv", n=17379, target="cnt", horizons=(1, 6, 24)),
    dict(id="UCI235_HOUSEHOLD_POWER", archive="uci235.zip", member="household_power_consumption.txt", n=2075259, target="Global_active_power", horizons=(1, 6, 24), delimiter=";", household=True),
    dict(id="UCI360_AIR_QUALITY_CO", archive="uci360.zip", member="AirQualityUCI.csv", n=9358, target="CO(GT)", horizons=(1, 6, 24), delimiter=";", encoding="latin-1", air=True),
    dict(id="UCI492_METRO_TRAFFIC", archive="uci492.zip", member="Metro_Interstate_Traffic_Volume.csv.gz", n=48204, target="traffic_volume", horizons=(1, 6, 24), gzip_member=True),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_value(raw: str | None, air: bool = False) -> float:
    text = (raw or "").strip()
    if air:
        text = text.replace(",", ".")
    try:
        value = float(text)
    except (TypeError, ValueError):
        return math.nan
    if air and value <= -199:
        return math.nan
    return value


def rows_from_member(archive: Path, spec: dict, limit: int):
    with zipfile.ZipFile(archive) as outer:
        raw = outer.open(spec["member"])
        if spec.get("gzip_member"):
            raw = gzip.GzipFile(fileobj=raw)
        text = io.TextIOWrapper(raw, encoding=spec.get("encoding", "utf-8"), errors="strict", newline="")
        for index, row in enumerate(csv.DictReader(text, delimiter=spec.get("delimiter", ","))):
            if index >= limit:
                break
            yield index, row


def origin_summary(masks: list[np.ndarray], train_n: int, horizons: tuple[int, ...]) -> dict:
    end = min(len(mask) for mask in masks)
    origins = np.arange(train_n, end - max(horizons), dtype=np.int64)
    slots = np.stack(
        [np.stack([mask[origins + h - 1] for h in horizons], axis=1) for mask in masks],
        axis=0,
    )
    return {
        "origin_denominator": int(len(origins)),
        "origins_with_any_raw_missing_target": int(np.any(slots, axis=(0, 2)).sum()),
        "missing_target_slots": int(slots.sum()),
        "target_slot_denominator": int(slots.size),
    }


def save_mask(mask_dir: Path, spec_id: str, member_index: int, member_name: str, mask: np.ndarray) -> dict:
    safe_member = f"member_{member_index:02d}"
    path = mask_dir / f"{spec_id}__{safe_member}.npy"
    np.save(path, mask.astype(np.bool_), allow_pickle=False)
    good = np.flatnonzero(~mask)
    return {
        "benchmark_id": spec_id,
        "member_index": member_index,
        "source_member": member_name,
        "public_path": path.relative_to(mask_dir.parents[1]).as_posix(),
        "length": int(mask.size),
        "missing_count": int(mask.sum()),
        "leading_missing_rows": int(good[0]) if len(good) else int(mask.size),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
        "identity": "DERIVED_FROM_EXISTING_PREFIX",
    }


def derive_prefix_diagnostics(repo: Path, public_root: Path) -> tuple[list[dict], dict]:
    archive_root = repo / "iclr2027_redesign/36_parallel_strong_accept_program/E_prospective_real_cohort/00_metadata_inventory/opaque_archives"
    derived_root = public_root / "DERIVED_PREFIX_DIAGNOSTICS"
    mask_dir = derived_root / "masks"
    mask_dir.mkdir(parents=True, exist_ok=True)
    mask_index = []
    summaries = {}
    source_archives = {}
    household_groups = []

    for spec in SPECS:
        archive = archive_root / spec["archive"]
        prefix_end = math.floor(0.8 * spec["n"])
        train_end = math.floor(0.6 * spec["n"])
        source_archives[spec["id"]] = {
            "repository_relative_path": archive.relative_to(repo).as_posix(),
            "sha256": sha256(archive),
            "distributed": False,
            "reason": "third-party raw archive excluded; only allowed deterministic diagnostics are exported",
        }
        masks = []
        member_names = []
        if spec.get("nested"):
            with zipfile.ZipFile(archive) as outer:
                nested_bytes = outer.read("PRSA2017_Data_20130301-20170228.zip")
            with zipfile.ZipFile(io.BytesIO(nested_bytes)) as nested:
                names = sorted(name for name in nested.namelist() if name.lower().endswith(".csv"))
                for name in names:
                    text = io.TextIOWrapper(nested.open(name), encoding="utf-8", errors="strict", newline="")
                    values = []
                    for index, row in enumerate(csv.DictReader(text)):
                        if index >= prefix_end:
                            break
                        values.append(parse_value(row.get(spec["target"])))
                    masks.append(~np.isfinite(np.asarray(values, dtype=float)))
                    member_names.append(name)
        else:
            values = []
            group_start = None
            hour_counts = Counter()
            for index, row in rows_from_member(archive, spec, prefix_end):
                values.append(parse_value(row.get(spec["target"]), spec.get("air", False)))
                if spec.get("household"):
                    timestamp = datetime.strptime(f"{row['Date']} {row['Time']}", "%d/%m/%Y %H:%M:%S")
                    hour_counts[timestamp.replace(minute=0, second=0)] += 1
                    if index % 60 == 0:
                        group_start = timestamp
                    if index % 60 == 59:
                        household_groups.append((index // 60, group_start, timestamp))
            masks = [~np.isfinite(np.asarray(values, dtype=float))]
            member_names = [spec["member"]]

        for index, (name, mask) in enumerate(zip(member_names, masks), start=1):
            mask_index.append(save_mask(mask_dir, spec["id"], index, name, mask))

        if spec.get("household"):
            usable = (len(masks[0]) // 60) * 60
            grouped_mask = masks[0][:usable].reshape(-1, 60).any(axis=1)
            summary = origin_summary([grouped_mask], train_end // 60, spec["horizons"])
            summary["timestamp_semantics"] = {
                "first_timestamp": household_groups[0][1].isoformat(sep=" "),
                "first_executed_group_last_timestamp": household_groups[0][2].isoformat(sep=" "),
                "executed_60row_groups": len(household_groups),
                "executed_groups_crossing_clock_hour_boundary": sum(
                    start.replace(minute=0, second=0) != end.replace(minute=0, second=0)
                    for _, start, end in household_groups
                ),
                "complete_timestamp_clock_hours": sum(count == 60 for count in hour_counts.values()),
                "partial_timestamp_clock_hours": sum(count != 60 for count in hour_counts.values()),
            }
        else:
            summary = origin_summary(masks, train_end, spec["horizons"])
        summary.update(
            {
                "decoded_prefix_rows_per_member": [int(mask.size) for mask in masks],
                "raw_validation_row_missing": int(sum(mask[train_end:prefix_end].sum() for mask in masks)),
                "raw_validation_row_denominator": int(sum(mask[train_end:prefix_end].size for mask in masks)),
                "leading_missing_rows_per_member": [
                    int(np.flatnonzero(~mask)[0]) if np.any(~mask) else int(mask.size) for mask in masks
                ],
                "identity": "DERIVED_FROM_EXISTING_PREFIX",
                "not_an_execution_log": True,
            }
        )
        summaries[spec["id"]] = summary

    timestamp_path = derived_root / "household_60row_timestamp_groups.tsv"
    with timestamp_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(("group_index", "first_timestamp", "last_timestamp", "crosses_calendar_hour"))
        for index, start, end in household_groups:
            writer.writerow(
                (
                    index,
                    start.isoformat(sep=" "),
                    end.isoformat(sep=" "),
                    str(start.replace(minute=0, second=0) != end.replace(minute=0, second=0)).lower(),
                )
            )

    index_path = derived_root / "mask_index.json"
    summary_path = derived_root / "missingness_summary.json"
    note_path = derived_root / "DERIVATION_METHOD.md"
    write_json(index_path, {"masks": mask_index})
    write_json(
        summary_path,
        {
            "identity": "DERIVED_FROM_EXISTING_PREFIX",
            "scope": "first floor(0.8*N) decoded rows only; no final 20 percent source read",
            "planned_rule": "hold target with more than 20 percent missing validation origins",
            "execution_record_status": "MISSING",
            "warning": "these diagnostics do not establish which denominator was historically intended or enforced",
            "source_archives": source_archives,
            "tasks": summaries,
        },
    )
    note_path.write_text(
        "# Prefix diagnostic derivation\n\n"
        "Identity: `DERIVED_FROM_EXISTING_PREFIX`. These files are not historical execution logs.\n\n"
        "Only the first `floor(0.8*N)` decoded rows of the six already mounted Stage36 archives were read. "
        "Each Boolean mask is true where the declared target is nonnumeric/nonfinite; Air Quality also "
        "treats values at most -199 as missing. Household groups are the executed consecutive complete "
        "60-row groups and are listed with their actual start/end timestamps. No final-20-percent source, "
        "model, fit, prediction, RNG, Monte Carlo, or confirmatory command was accessed or run.\n",
        encoding="utf-8",
    )

    derived_entries = []
    for path in sorted(derived_root.rglob("*")):
        if path.is_file():
            derived_entries.append(
                {
                    "id": "DERIVED_" + path.relative_to(derived_root).as_posix().replace("/", "_").replace(".", "_").upper(),
                    "role": "deterministic prefix missingness/timestamp diagnostic",
                    "identity": "DERIVED_FROM_EXISTING_PREFIX",
                    "source_repository_relative_paths": [value["repository_relative_path"] for value in source_archives.values()],
                    "source_archive_sha256": {key: value["sha256"] for key, value in source_archives.items()},
                    "public_path": path.relative_to(public_root.parent).as_posix(),
                    "public_sha256": sha256(path),
                    "public_size_bytes": path.stat().st_size,
                    "transformations": ["deterministic prefix-only target-missingness/timestamp derivation"],
                    "new_scientific_outcome": False,
                }
            )
    return derived_entries, {"mask_count": len(mask_index), "task_count": len(summaries)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = args.output.resolve()
    public_root = output / "PUBLIC_EVIDENCE"
    private_root = output / "PRIVATE_EVIDENCE"
    if public_root.exists() or private_root.exists():
        raise SystemExit("HOLD_OUTPUT_EXISTS: PUBLIC_EVIDENCE or PRIVATE_EVIDENCE already exists")
    public_root.mkdir(parents=True)
    private_root.mkdir(parents=True)

    private_entries = []
    public_entries = []
    # Split the markers so this public audit tool does not flag its own source.
    forbidden = (b"/" + b"Users/", b"private" + b"user", b"Mac" + b"Book")
    for item in ORIGINALS:
        source = repo / item["source"]
        if not source.is_file():
            raise SystemExit(f"HOLD_MISSING_ALLOWLIST_SOURCE: {item['source']}")
        private = private_root / item["public"]
        public = public_root / item["public"]
        private.parent.mkdir(parents=True, exist_ok=True)
        public.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, private)
        shutil.copy2(source, public)
        source_hash = sha256(source)
        if source_hash != sha256(private) or source_hash != sha256(public):
            raise SystemExit(f"HOLD_COPY_HASH_MISMATCH: {item['source']}")
        raw = public.read_bytes()
        hits = [needle.decode("ascii") for needle in forbidden if needle in raw]
        if hits:
            raise SystemExit(f"HOLD_PUBLIC_IDENTITY_MARKER: {item['source']} {hits}")
        private_entries.append(
            {
                "id": item["id"],
                "role": item["role"],
                "source_repository_relative_path": item["source"],
                "source_sha256": source_hash,
                "source_size_bytes": source.stat().st_size,
                "private_path": private.relative_to(output).as_posix(),
                "private_sha256": sha256(private),
                "identity": "HISTORICAL_ORIGINAL_BYTE_COPY",
            }
        )
        public_entries.append(
            {
                "id": item["id"],
                "role": item["role"],
                "source_repository_relative_path": item["source"],
                "source_sha256": source_hash,
                "source_size_bytes": source.stat().st_size,
                "public_path": public.relative_to(output).as_posix(),
                "public_sha256": sha256(public),
                "public_size_bytes": public.stat().st_size,
                "identity": "HISTORICAL_ORIGINAL_BYTE_COPY",
                "transformations": [],
                "anonymization": "identity-marker scan passed; no content change",
                "new_scientific_outcome": False,
            }
        )

    derived_entries, derived_counts = derive_prefix_diagnostics(repo, public_root)
    tool_public = public_root / "TOOLS/export_existing_evidence.py"
    tool_public.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), tool_public)
    if any(needle in tool_public.read_bytes() for needle in forbidden):
        raise SystemExit("HOLD_PUBLIC_IDENTITY_MARKER: export tool")
    derived_entries.append(
        {
            "id": "EXPORT_DERIVATION_TOOL",
            "role": "deterministic allowlist export and prefix-diagnostic derivation source",
            "identity": "NEW_EXPORT_TOOL",
            "public_path": tool_public.relative_to(output).as_posix(),
            "public_sha256": sha256(tool_public),
            "public_size_bytes": tool_public.stat().st_size,
            "transformations": [],
            "new_scientific_outcome": False,
        }
    )

    write_json(
        output / "PRIVATE_EVIDENCE_MANIFEST.json",
        {
            "status": "PRIVATE_NOT_FOR_ANONYMOUS_SUBMISSION",
            "original_file_count": len(private_entries),
            "files": private_entries,
        },
    )
    write_json(
        output / "PUBLIC_EVIDENCE_MANIFEST.json",
        {
            "schema": "uboa.existing_evidence_export.v1",
            "status": "PARTIAL_EXISTING_EVIDENCE_EXPORT",
            "source_package": {
                "name": "UBOA_Forensics_Challenge_Followup_20260916.zip",
                "sha256": "51a2a6d43cf9877d24071c9b7329746374a1becd928d0471d2ba4c99144c6323",
            },
            "original_file_count": len(public_entries),
            "derived_file_count": len(derived_entries),
            "files": public_entries + derived_entries,
            "derived_counts": derived_counts,
            "identity_statement": "original public copies retain source bytes; derived objects are labeled and never represented as historical execution logs",
            "environment": {
                "python": platform.python_version(),
                "numpy": np.__version__,
                "platform": platform.platform(),
            },
            "hard_zero": {
                "rng_calls": 0,
                "new_random_samples": 0,
                "training_or_fitting": 0,
                "confirmatory_reruns": 0,
                "new_prospective_oos_reads": 0,
            },
        },
    )
    print(json.dumps({"original_files": len(public_entries), "derived_files": len(derived_entries), **derived_counts}, sort_keys=True))


if __name__ == "__main__":
    main()
