#!/usr/bin/env python3
"""Deterministic reference matcher for hand-authored request/evidence metadata.

This module does not read research data or execute statistical tests. It checks whether an
annotated evidence record licenses an unchanged requested conclusion under a small rule set.
"""

from __future__ import annotations

import copy
import json
import sys
from typing import Any


SCIENTIFIC_FIELDS = (
    "target_id",
    "selected_object",
    "comparator",
    "loss",
    "members",
    "horizons",
    "weights",
    "evaluation_law",
    "thresholds",
)
VALIDITY_FIELDS = (
    "error_event",
    "conditioning",
    "law_quantifier",
    "coverage_unit",
    "support_mode",
    "sample_regime",
    "selection_mechanism",
)
EMPIRICAL_FIELDS = ("design_mixture", "denominator", "sample_range", "selection_record")
FIXED_SEQUENCE_FLAGS = (
    "potential_tests_defined",
    "ordered_family",
    "stop_at_first_valid_nonrejection",
    "no_true_null_convention",
)


def _unsupported(request: dict[str, Any], evidence: dict[str, Any], *reasons: str) -> dict[str, Any]:
    return {
        "status": "UNSUPPORTED_REQUEST",
        "rule": "M7_MISMATCH",
        "reasons": list(reasons),
        "request": copy.deepcopy(request),
        "weaker_evidence": copy.deepcopy(evidence),
    }


def _established(request: dict[str, Any], evidence: dict[str, Any], rule: str) -> dict[str, Any]:
    return {
        "status": "ESTABLISHED",
        "rule": rule,
        "reasons": [],
        "request": copy.deepcopy(request),
        "supporting_evidence_id": evidence["evidence_id"],
    }


def _required(record: dict[str, Any], keys: tuple[str, ...], prefix: str) -> list[str]:
    return [f"MISSING_FIELD:{prefix}.{key}" for key in keys if key not in record]


def _schema_reasons(request: dict[str, Any], evidence: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if not isinstance(request, dict) or not isinstance(evidence, dict):
        return ["INVALID_RECORD_TYPE"]
    reasons += _required(request, ("request_id", "conclusion_type", "scientific", "validity"), "request")
    reasons += _required(
        evidence,
        (
            "evidence_id",
            "kind",
            "conclusion_type",
            "scientific",
            "validity",
            "premises",
            "verified_assumptions",
            "metadata",
        ),
        "evidence",
    )
    if reasons:
        return reasons
    for label, record in (("request", request), ("evidence", evidence)):
        for field in ("scientific", "validity"):
            if not isinstance(record[field], dict):
                reasons.append(f"INVALID_FIELD_TYPE:{label}.{field}")
        if "metadata" in record and not isinstance(record["metadata"], dict):
            reasons.append(f"INVALID_FIELD_TYPE:{label}.metadata")
    for field in ("premises", "verified_assumptions"):
        value = evidence[field]
        if not isinstance(value, list) or any(not isinstance(x, str) for x in value):
            reasons.append(f"INVALID_FIELD_TYPE:evidence.{field}")
    if reasons:
        return reasons
    reasons += _required(request["scientific"], SCIENTIFIC_FIELDS, "request.scientific")
    reasons += _required(evidence["scientific"], SCIENTIFIC_FIELDS, "evidence.scientific")
    reasons += _required(request["validity"], VALIDITY_FIELDS, "request.validity")
    reasons += _required(evidence["validity"], VALIDITY_FIELDS, "evidence.validity")
    return reasons


def _scientific_mismatch(request: dict[str, Any], evidence: dict[str, Any]) -> str | None:
    rs, es = request["scientific"], evidence["scientific"]
    for field in SCIENTIFIC_FIELDS:
        if rs[field] != es[field]:
            if field == "evaluation_law":
                return "EVALUATION_LAW_MISMATCH"
            return f"SCIENTIFIC_TARGET_MISMATCH:{field}"
    return None


def _validity_mismatch(
    request: dict[str, Any], evidence: dict[str, Any], *, ignore: tuple[str, ...] = ()
) -> str | None:
    rv, ev = request["validity"], evidence["validity"]
    for field in VALIDITY_FIELDS:
        if field in ignore or rv[field] == ev[field]:
            continue
        if field == "error_event":
            return "ERROR_EVENT_MISMATCH"
        if field == "coverage_unit" and ev[field] == "one_request" and rv[field] != "one_request":
            return "SINGLE_TO_SIMULTANEOUS_UPGRADE_FORBIDDEN"
        if field == "selection_mechanism" and ev[field] == "fixed_rule" and rv[field] == "selected_procedure":
            return "FIXED_TO_SELECTED_UPGRADE_FORBIDDEN"
        if field == "conditioning":
            return "CONDITIONING_STRENGTHENING_FORBIDDEN"
        return f"VALIDITY_SCOPE_MISMATCH:{field}"
    return None


def _unverified(evidence: dict[str, Any]) -> str | None:
    verified = set(evidence["verified_assumptions"])
    for premise in evidence["premises"]:
        if premise not in verified:
            return f"UNVERIFIED_ASSUMPTION:{premise}"
    return None


def match(request: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    """Apply one admissibility rule and preserve the original request in every result."""

    malformed = _schema_reasons(request, evidence)
    if malformed:
        return _unsupported(request, evidence, *malformed)

    kind = evidence["kind"]
    requested = request["conclusion_type"]

    # Type-level prohibitions are reported before generic support-mode mismatch reasons.
    if kind == "observed_decision" and requested != "observed_decision":
        return _unsupported(request, evidence, "OBSERVED_TO_GUARANTEE_FORBIDDEN")
    if kind == "finite_design_empirical" and requested != "empirical_rate":
        return _unsupported(request, evidence, "EMPIRICAL_TO_THEOREM_FORBIDDEN")
    if (
        kind == "asymptotic_theorem"
        and evidence["validity"]["support_mode"] == "asymptotic"
        and request["validity"]["support_mode"] == "finite_sample_exact"
    ):
        return _unsupported(request, evidence, "ASYMPTOTIC_TO_FINITE_EXACTNESS_FORBIDDEN")

    mismatch = _scientific_mismatch(request, evidence)
    if mismatch:
        return _unsupported(request, evidence, mismatch)

    if kind == "structural_identity":
        if evidence["conclusion_type"] != "structural_identity":
            return _unsupported(request, evidence, "CONCLUSION_TYPE_MISMATCH")
        mismatch = _validity_mismatch(request, evidence)
        if mismatch:
            return _unsupported(request, evidence, mismatch)
        if evidence["metadata"].get("pointwise_identity") is not True:
            return _unsupported(request, evidence, "POINTWISE_IDENTITY_NOT_CERTIFIED")
        if requested == "relative_ratio":
            if evidence["metadata"].get("denominator_status") != "finite_positive":
                return _unsupported(request, evidence, "DENOMINATOR_NONPOSITIVE")
        elif requested != "structural_identity":
            return _unsupported(request, evidence, "CONCLUSION_TYPE_MISMATCH")
        return _established(request, evidence, "M1_POINTWISE_IDENTITY")

    if kind == "observed_decision":
        if evidence["conclusion_type"] != "observed_decision":
            return _unsupported(request, evidence, "CONCLUSION_TYPE_MISMATCH")
        mismatch = _validity_mismatch(request, evidence)
        if mismatch:
            return _unsupported(request, evidence, mismatch)
        required = ("reached_nodes_only", "method_retained", "boundary_retained")
        failed = next((x for x in required if evidence["metadata"].get(x) is not True), None)
        if failed:
            return _unsupported(request, evidence, f"OBSERVED_COPY_SIDE_CONDITION_FAILED:{failed}")
        provenance = evidence["metadata"].get("provenance")
        if not isinstance(provenance, str) or not provenance.strip():
            return _unsupported(request, evidence, "OBSERVED_COPY_PROVENANCE_MISSING")
        return _established(request, evidence, "M2_OBSERVED_COPY")

    if kind == "finite_design_empirical":
        if evidence["conclusion_type"] != "empirical_rate":
            return _unsupported(request, evidence, "CONCLUSION_TYPE_MISMATCH")
        mismatch = _validity_mismatch(request, evidence)
        if mismatch:
            return _unsupported(request, evidence, mismatch)
        requested_meta = request.get("metadata", {})
        for field in EMPIRICAL_FIELDS:
            for label, meta in (("request", requested_meta), ("evidence", evidence["metadata"])):
                if field not in meta or meta[field] is None or meta[field] == "":
                    return _unsupported(request, evidence, f"MISSING_FIELD:{label}.metadata.{field}")
                if field == "denominator" and (type(meta[field]) is not int or meta[field] <= 0):
                    return _unsupported(request, evidence, f"INVALID_DENOMINATOR:{label}")
            if requested_meta.get(field) != evidence["metadata"].get(field):
                return _unsupported(request, evidence, f"EMPIRICAL_DESIGN_MISMATCH:{field}")
        return _established(request, evidence, "M3_FINITE_EMPIRICAL")

    if kind in {"theorem", "asymptotic_theorem"}:
        mismatch = _validity_mismatch(request, evidence)
        if mismatch:
            return _unsupported(request, evidence, mismatch)
        if not evidence["premises"]:
            return _unsupported(request, evidence, "THEOREM_PREMISES_EMPTY")
        premise = _unverified(evidence)
        if premise:
            return _unsupported(request, evidence, premise)
        if requested != "probability_bound" or evidence["conclusion_type"] != "probability_bound":
            return _unsupported(request, evidence, "CONCLUSION_TYPE_MISMATCH")
        return _established(request, evidence, "M4_THEOREM_INSTANTIATION")

    if kind == "conditional_bound":
        if requested != "probability_bound" or evidence["conclusion_type"] != "probability_bound":
            return _unsupported(request, evidence, "CONCLUSION_TYPE_MISMATCH")
        premise = _unverified(evidence)
        if premise:
            return _unsupported(request, evidence, premise)
        mismatch = _validity_mismatch(request, evidence, ignore=("conditioning",))
        if mismatch:
            return _unsupported(request, evidence, mismatch)
        source_field = evidence["validity"]["conditioning"]
        target_field = request["validity"]["conditioning"]
        meta = evidence["metadata"]
        if source_field == target_field:
            premise = _unverified(evidence)
            if premise:
                return _unsupported(request, evidence, premise)
            return _established(request, evidence, "M4_THEOREM_INSTANTIATION")
        coarsenings = meta.get("declared_coarsenings", [])
        if not isinstance(coarsenings, list) or any(not isinstance(x, str) for x in coarsenings):
            return _unsupported(request, evidence, "INVALID_FIELD_TYPE:declared_coarsenings")
        if target_field not in coarsenings:
            return _unsupported(request, evidence, "CONDITIONING_STRENGTHENING_FORBIDDEN")
        for field in (
            "same_joint_law",
            "same_error_event",
            "integrable_indicator",
            "bound_constant_or_coarser_measurable",
        ):
            if meta.get(field) is not True:
                return _unsupported(request, evidence, f"COARSENING_SIDE_CONDITION_FAILED:{field}")
        return _established(request, evidence, "M5_CONDITIONING_COARSEN")

    if kind == "local_validity_family":
        mismatch = _validity_mismatch(request, evidence)
        if mismatch:
            return _unsupported(request, evidence, mismatch)
        if requested != "fixed_sequence_error_bound" or evidence["conclusion_type"] != "local_node_bounds":
            return _unsupported(request, evidence, "CONCLUSION_TYPE_MISMATCH")
        if request["validity"]["conditioning"] != "full_history":
            return _unsupported(
                request, evidence, "FIXED_SEQUENCE_SIDE_CONDITION_FAILED:full_history_conditioning"
            )
        premise = _unverified(evidence)
        if premise:
            return _unsupported(request, evidence, premise)
        for required_premise in ("truth_events_measurable", "local_bounds_hold"):
            if required_premise not in evidence["premises"] or required_premise not in evidence["verified_assumptions"]:
                return _unsupported(request, evidence, f"UNVERIFIED_ASSUMPTION:{required_premise}")
        meta = evidence["metadata"]
        for field in FIXED_SEQUENCE_FLAGS:
            if meta.get(field) is not True:
                return _unsupported(request, evidence, f"FIXED_SEQUENCE_SIDE_CONDITION_FAILED:{field}")
        if meta.get("invalid_policy") != "whole_request_unresolved":
            return _unsupported(request, evidence, "FIXED_SEQUENCE_SIDE_CONDITION_FAILED:invalid_policy")
        return _established(request, evidence, "M6_FIXED_SEQUENCE")

    return _unsupported(request, evidence, f"UNKNOWN_EVIDENCE_KIND:{kind}")


def terminalize_trace(node_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply the frozen whole-request terminal policy to an already supplied node trace.

    This function does not compute node results. It only validates a hand-authored/static trace and
    maps it to the public terminal semantics recovered from the historical policy.
    """

    if not node_results:
        raise ValueError("EMPTY_TRACE")
    expected_ordinal = 1
    promoted: list[int] = []
    for index, node in enumerate(node_results):
        if node.get("ordinal") != expected_ordinal:
            raise ValueError("NONPREFIX_TRACE")
        expected_ordinal += 1
        status = node.get("status")
        if status == "INVALID":
            if index != len(node_results) - 1:
                raise ValueError("CONTINUED_AFTER_INVALID")
            return {
                "public_terminal": "UNRESOLVED",
                "public_positive_promotion": None,
                "internal_trace": copy.deepcopy(node_results),
                "stop_reason": "INVALID_EVIDENCE",
            }
        if status != "VALID" or not isinstance(node.get("reject"), bool):
            raise ValueError("MALFORMED_NODE")
        if node["reject"]:
            promoted.append(node["ordinal"])
            continue
        if index != len(node_results) - 1:
            raise ValueError("CONTINUED_AFTER_NONREJECTION")
        return {
            "public_terminal": "VALID_NONREJECTION",
            "public_positive_promotion": promoted[-1] if promoted else None,
            "internal_trace": copy.deepcopy(node_results),
            "stop_reason": "VALID_NONREJECTION",
        }
    return {
        "public_terminal": "SEQUENCE_EXHAUSTED",
        "public_positive_promotion": promoted[-1] if promoted else None,
        "internal_trace": copy.deepcopy(node_results),
        "stop_reason": "ALL_NODES_REJECTED",
    }


def main() -> None:
    payload = json.load(sys.stdin)
    json.dump(match(payload["request"], payload["evidence"]), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
