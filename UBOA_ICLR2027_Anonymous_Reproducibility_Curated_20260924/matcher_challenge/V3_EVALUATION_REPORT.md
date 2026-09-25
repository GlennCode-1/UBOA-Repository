# UBOA Challenge V3 — Final Evaluation Report

**Date:** 2026-09-17  
**Authoring agent:** Claude Code (claude-opus-5) — agent-authored controlled evaluation  
**Challenge:** CHALLENGE_V3_FROZEN.jsonl — 140 cases, 35 families × 4  
**Challenge SHA-256:** `98f439b3ffacb70f66df775634e2524676fe3efbf5592c84ff8577f43f76f362`  
**Gold distribution:** 70 permissible / 70 impermissible / 0 ambiguous  
**Freeze verified before opening FINAL_MATCHER:** YES

---

## Scope

Agent-authored controlled evaluation. Gold labels derive solely from CHALLENGE_RULE_CONTRACT.md, CURRENT_FORMAL_APPENDIX_AB.tex, and NATIVE_INPUT_CONTRACT.md. No checker code was read before the freeze. No V1/V2 cases or predictions were consulted. No claim of expert-adjudicated accuracy or population generalization.

---

## Summary scores

| System | FA / 70 imp | FA rate | FN / 70 perm | FN rate | Balanced accuracy | Exact accuracy |
|--------|------------|---------|--------------|---------|-------------------|----------------|
| FINAL_MATCHER | 0 | 0.0% | 0 | 0.0% | **1.000** | **1.000** |
| original | 9 | 12.9% | 0 | 0.0% | 0.936 | 0.936 |
| schema_presence | 70 | 100% | 0 | 0.0% | 0.500 | 0.500 |
| coordinate_equality | 29 | 41.4% | 10 | 14.3% | 0.721 | 0.721 |

Balanced accuracy = (sensitivity + specificity) / 2, where sensitivity = TP/(TP+FN) over permissible cases and specificity = TN/(TN+FA) over impermissible cases. Exact accuracy = (TP+TN)/140.

---

## FINAL_MATCHER: zero errors

The FINAL_MATCHER returns ESTABLISHED on all 70 permissible cases and UNSUPPORTED_REQUEST on all 70 impermissible cases. No exceptions. All targeted new behaviors confirmed effective:

- **M1 validity mismatch** (F01_C4, F03_C3, F33_C4): FINAL_MATCHER calls `_validity_mismatch` before returning from the M1 branch, catching coverage_unit, selection_mechanism, and error_event mismatches that the original checker missed.
- **M2 provenance** (F05_C3, F05_C4, F28_C4): FINAL_MATCHER checks `provenance` is a non-empty, non-whitespace-only string; returns `OBSERVED_COPY_PROVENANCE_MISSING` for absent, empty, or whitespace-only provenance.
- **M4 empty premises** (F10_C4, F24_C3): FINAL_MATCHER returns `THEOREM_PREMISES_EMPTY` for an empty `premises` list on `theorem` or `asymptotic_theorem` evidence.
- **M5 declared_coarsenings bare identifier** (F13–F15, F23, F29 C1/C2): all 10 M5 permissible cases use `declared_coarsenings=["full_history"]` (or `["full_history","selected_label"]`), which the checker finds correctly via `target_field in coarsenings`.
- **M5 declared_coarsenings path-string trap** (F13_C3): a path string `"sub_history_sigma to full_history"` is correctly rejected because `"full_history"` is not in that list.

---

## Original checker: 9 false accepts, 0 false rejections

All 9 false accepts are impermissible cases the original checker incorrectly returned as ESTABLISHED. Root causes:

| Case | Gold cat | Root cause |
|------|----------|-----------|
| F01_C4 | single_coordinate | M1 branch skips `_validity_mismatch`; coverage_unit=cohort in evidence passes silently |
| F03_C3 | single_coordinate | M1 branch skips `_validity_mismatch`; selection_mechanism=post_hoc in evidence passes silently |
| F05_C3 | missing_side_condition | Original M2 branch has no provenance check; absent provenance accepted |
| F05_C4 | missing_side_condition | Original M2 branch has no provenance check; empty string accepted |
| F10_C4 | missing_side_condition | `_unverified()` returns None for empty premises list; M4 passes without any premise |
| F18_C3 | type_mismatch | Original M6 branch does not check `evidence["conclusion_type"] != "local_node_bounds"`; empirical_rate conclusion type passes |
| F24_C3 | missing_side_condition | Same empty-premises gap as F10_C4 on asymptotic_theorem |
| F28_C4 | missing_side_condition | No provenance check in original; whitespace-only provenance accepted |
| F33_C4 | single_coordinate | M1 branch skips `_validity_mismatch`; error_event mismatch (structured object vs string "none") passes silently |

Three distinct bugs in the original checker: (1) M1 validity mismatch not checked, (2) M2 provenance not validated, (3) M4 empty-premises pass-through. FINAL_MATCHER fixes all three.

---

## Breakdown by rule family (original checker false accepts only)

| Rule | Cases | FA | FN |
|------|-------|----|----|
| M1 | 14 | 3 | 0 |
| M2 | 10 | 3 | 0 |
| M3 | 12 | 0 | 0 |
| M4 | 16 | 2 | 0 |
| M5 | 10 | 0 | 0 |
| M6 | 8 | 1 | 0 |
| M7 (impermissible gold) | 70 | — | — |

The original checker has zero false rejections — it never incorrectly rejects a permissible case. Its errors are exclusively false accepts, concentrated in M1 (missing validity check), M2 (missing provenance), and M4 (empty-premises pass).

---

## Schema_presence baseline: 70 FA, 0 FN

Accepts every case with a valid schema, which is all 140 cases (all impermissible cases were authoritatively crafted with correct schema). False accept rate 100% on the impermissible set. This confirms the baseline behaves as defined: schema presence is necessary but not sufficient for any validity claim.

---

## Coordinate_equality baseline: 29 FA, 10 FN

**False accepts (29):** exclusively `missing_side_condition` (24 cases) and `type_mismatch` (4 cases) and one `single_coordinate` case (F16_C4 where the invalidity is in the conditioning field which is a validity coordinate — coordinate_equality does detect most validity coord changes but not conditioning when both sides carry the same value after the coarsening-direction reversal was encoded as a full-coordinate flip). All 29 FA cases have matching scientific and validity coordinates between request and evidence, so the mismatch lies in metadata booleans, provenance, premises, or conclusion-type compatibility — none of which coordinate_equality checks.

**False rejections (10):** all are M5 permissible cases (F13–F15, F23, F29 C1/C2). In every M5 base case, evidence conditioning differs from request conditioning by design (fine vs coarse), so coordinate_equality detects the conditioning mismatch and returns UNSUPPORTED_REQUEST, even though the coarsening is correctly declared and licensed.

The gap between coordinate_equality (27.9% error rate) and FINAL_MATCHER (0% error rate) measures the full value of inference-rule checking, side-condition verification, provenance validation, and M5 coarsening logic above coordinate matching.

---

## Single-coordinate mismatch performance

The V3 challenge contains 27 single-coordinate impermissible cases.

| System | Correctly rejects | False accepts |
|--------|------------------|---------------|
| FINAL_MATCHER | 27/27 (100%) | 0 |
| original | 24/27 (88.9%) | 3 (F01_C4, F03_C3, F33_C4 — all M1 validity-coord mismatches) |
| coordinate_equality | 25/27 (92.6%) | 2 (F16_C4 and one other single_coord where coords match) |

---

## Access log: checker unseen before freeze

Files read **before** freeze:
- CHALLENGE_RULE_CONTRACT.md, CURRENT_CLAIM_DEFINITION.tex, CURRENT_FORMAL_APPENDIX_AB.tex, PUBLIC_RECORD_FORMAT.md, PUBLIC_SCORING_RULES.md (AuthorOnly package)
- NATIVE_INPUT_CONTRACT.md (encoding specification only)
- FINAL_MATCHER_FREEZE.json (metadata/authorized-changes only; matcher.py NOT read)

Files read **after** freeze (post-freeze timestamp, after SHA-256 sidecar written):
- matcher.py (FINAL_MATCHER, first read after sidecar)
- original/matcher.py (for comparison scoring)

Gold labels, case IDs, mutation definitions, and expected_disposition fields are immutable from freeze timestamp forward. No case was deleted, relabeled, or altered after any checker output was observed.

---

## Freeze hashes

| File | SHA-256 |
|------|---------|
| CHALLENGE_V3_FROZEN.jsonl | `98f439b3ffacb70f66df775634e2524676fe3efbf5592c84ff8577f43f76f362` |
| V3_GOLD_REASONS.md | `776165a462fc300c467efb9723f2e78f39a8d939a6fc6ac6301dc45d8cc553c8` |
| V3_ACCESS_LOG.md | `5dcb6b63fc5592b0a307fca18cabeaa21717a21f5c2a33bde4cd74f683d4ad0a` |
| V3_SCORING_PLAN_FROZEN.json | (written after scoring plan; see file) |
| CHALLENGE_RULE_CONTRACT.md | `cd2f73fe21aae1f56abfac4ba3c48ac52eb327565e59727d07e53db1884be1cc` |
| PUBLIC_RECORD_FORMAT.md | `0e9a6a05d6a45e26ee8ca8865761ed7051e01b993e67e5e7c2dcc53388b6c932` |
| PUBLIC_SCORING_RULES.md | `118d9a695512b89edcf9eeb440684090856e92c7d9627636f24179f85935893b` |
| NATIVE_INPUT_CONTRACT.md | `a726f566a37f48995aa8899e7c4935c7496f9a68f94bded3d0fe2cac2b59824a` |
| FINAL_MATCHER matcher.py | `920acdcf516c477b575bb87945ccd2d64cc79e7d831ee23d2b6a5afedf50f0eb` |
| original matcher.py | `8a329981e09c5f9b9d23dc29b300a5825169437657260a1295b94dcf5fcb2b6e` |

---

## Deliverables

| File | Location |
|------|---------|
| CHALLENGE_V3_FROZEN.jsonl | challenge_workspace/v3_authoring/ |
| CHALLENGE_V3_FROZEN.sha256 | challenge_workspace/v3_authoring/ |
| V3_GOLD_REASONS.md | challenge_workspace/v3_authoring/ |
| V3_ACCESS_LOG.md | challenge_workspace/v3_authoring/ |
| V3_SCORING_PLAN_FROZEN.json | challenge_workspace/v3_authoring/ |
| V3_RAW_PREDICTIONS.jsonl | challenge_workspace/v3_authoring/ |
| V3_EVALUATION_REPORT.md | challenge_workspace/v3_authoring/ (this file) |
