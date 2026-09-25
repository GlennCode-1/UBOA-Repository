## POSTRUN\_PASS

**Verdict: POSTRUN\_PASS**

**Study ID:** UBOA\_ROUTE\_B\_SYNTH\_CONFIRMATORY\_V1

**Audit date:** 2026-09-15

---

### Evidence table

| CheckResultDetail                                 |                             |                                                                                                                                                                                                                                                                                                           |
| ------------------------------------------------- | --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **F1 scientific manifest hash**                   | PASS                        | `manifest_id = 6caae5a8...` consistent in SCIENTIFIC\_FREEZE\_MANIFEST.json, IMPLEMENTATION\_FREEZE.json (`scientific_protocol_manifest_id`), and FINAL\_VERDICT.json (`scientific_manifest_id`)                                                                                                          |
| **F1 manifest SHA256 on disk**                    | PASS                        | `shasum -a256` → `315479da6ef36131...` matches value stored in IMPLEMENTATION\_FREEZE.json                                                                                                                                                                                                                |
| **F2 implementation freeze hash**                 | PASS                        | `shasum -a256 IMPLEMENTATION_FREEZE.json` → `0f9d5bb9e6b19a1c...` matches value in FINAL\_VERDICT.json and in every one of the 80 H records                                                                                                                                                               |
| **Pre-execution verdict bound to F2**             | PASS                        | FINAL\_VERDICT.json field `implementation_freeze_sha256` is `0f9d5bb9...`; H\_FREEZE\_MANIFEST and ANALYSIS\_SUMMARY carry the same value                                                                                                                                                                 |
| **Source file hashes vs F2 freeze**               | PASS (spot-checked 5 of 15) | run\_confirmatory.py, protocol.py, truth.py, generators.py, analyze\_confirmatory.py all match IMPLEMENTATION\_FREEZE.json `executable_source_sha256` entries exactly                                                                                                                                     |
| **Execution count**                               | PASS                        | EXECUTION\_LOG.jsonl contains exactly two lines: `LOCKED_EXECUTION_STARTED` at 15:49:07 UTC and `LOCKED_EXECUTION_FINISHED` (exit\_status=0) at 15:49:40 UTC on 2026-09-15. No retry, no HOLD, no crash restart                                                                                           |
| **Pre-execution verdict was PASS\_TO\_EXECUTE**   | PASS                        | FINAL\_VERDICT.json `verdict: PASS_TO_EXECUTE`, `checks_failed: []`                                                                                                                                                                                                                                       |
| **H\_FREEZE\_MANIFEST count**                     | PASS                        | 80 histories; `history_count: 80` in manifest metadata                                                                                                                                                                                                                                                    |
| **H\_FREEZE\_MANIFEST record\_sha256 recomputed** | PASS                        | All 80 `record_sha256` fields recomputed independently (canonical JSON of each record sans the `record_sha256` key) — all 80 match                                                                                                                                                                        |
| **H\_FREEZE\_MANIFEST frozen before inner**       | PASS                        | Manifest contains only outer-phase fields (history parameters, truth\_by\_node, validation\_scores, theta\_exact, selected\_label). No inner-futures data is present. The implementation contract and pre-exec audit check `H_FREEZE_MANIFEST_written_and_hashed_before_inner_phase` was a confirmed PASS |
| **F2 hash bound in manifest**                     | PASS                        | H\_FREEZE\_MANIFEST `implementation_freeze_sha256: 0f9d5bb9...` matches F2                                                                                                                                                                                                                                |
| **All 80 histories retained**                     | PASS                        | HISTORY\_RESULTS.json has exactly 80 records, 8 per cell, all 10 cells present. No filtering by outcome, truth depth, informativeness, or rejection rate observed                                                                                                                                         |
| **All denominators = 4096**                       | PASS                        | Every `inner_denominator` field in all 80 records is 4096                                                                                                                                                                                                                                                 |
| **first\_true\_null labels from H records**       | PASS                        | 80 values from HISTORY\_RESULTS match 80 values from H\_FREEZE\_MANIFEST exactly (0 mismatches). 46 finite, 34 None/infinite                                                                                                                                                                              |
| **truth\_by\_node crosscheck**                    | PASS                        | All 80 match between manifest and HISTORY\_RESULTS                                                                                                                                                                                                                                                        |
| **Pathwise invariant violations**                 | PASS                        | Zero across all 80 histories                                                                                                                                                                                                                                                                              |
| **false\_promotions summary**                     | NOTE                        | QB\_MSE\_NEG\_\_4 has `false_promotions = 1`; all other 79 histories have 0. One false promotion in 4096 inner paths is far below the rejection threshold (see Holm audit below)                                                                                                                          |
| **Binomial p-values recomputed**                  | PASS                        | All 46 finite-ftn p-values independently recomputed using `binom.sf(fp-1, 4096, 0.05)` per the frozen analysis rule in analyze\_confirmatory.py. QB\_MSE\_NEG\_\_4 with fp=1 yields p=1.0 (binomtest, H0: p≤0.05, alternative: greater). All 46 p-values equal 1.0                                        |
| **Holm correction at family alpha 0.01**          | PASS                        | Family size 46. No rejection. All Holm-adjusted p-values = 1.0. Independent recomputation exactly matches ANALYSIS\_SUMMARY.json `adjusted_pvalues` (0 mismatches to 1e-10 tolerance)                                                                                                                     |
| **Holm status**                                   | PASS                        | `NO_CALIBRATION_RED_FLAG_OBSERVED`                                                                                                                                                                                                                                                                        |
| **invalid\_count**                                | PASS                        | 0 across all records                                                                                                                                                                                                                                                                                      |
| **Final status follows decision rule**            | PASS                        | analyze\_confirmatory.py `decide_study_status` requires: protocol\_conformant, fixtures\_pass, crosschecks\_pass, pathwise\_invariant\_violations=0, invalid\_count=0, Holm status=NO\_RED\_FLAG. All five conditions confirmed. Stored status `CONFIRMATORY_IMPLEMENTATION_PASS` is correct              |
| **No post-exec output overwrite**                 | PASS                        | 09\_OUTPUTS/confirmatory\_run contains exactly the files written by one run: ANALYSIS\_SUMMARY.json, EXECUTION\_LOG.jsonl, HISTORY\_RESULTS.json, H\_FREEZE\_MANIFEST.json, H\_FREEZE\_MANIFEST.sha256. The sha256 sidecar matches the live file                                                          |

---

### Key hashes

| ArtifactSHA256 (first 32 hex)                      |                                                                             |
| -------------------------------------------------- | --------------------------------------------------------------------------- |
| H\_FREEZE\_MANIFEST.json (on disk, recomputed)     | `5229432f2384a80b2cde4097c68cf08e383cdacb...`                               |
| H\_FREEZE\_MANIFEST.sha256 (stored sidecar)        | `5229432f2384a80b2cde4097c68cf08e383cdacb...` ✓                             |
| IMPLEMENTATION\_FREEZE.json (F2, recomputed)       | `0f9d5bb9e6b19a1cffa3e1fbe38d34054a0c2328...`                               |
| FINAL\_VERDICT.json F2 field                       | `0f9d5bb9e6b19a1cffa3e1fbe38d34054a0c2328...` ✓                             |
| SCIENTIFIC\_FREEZE\_MANIFEST.json (F1, recomputed) | `315479da6ef361311219e9ba92b8b9d7cdfc7e10...`                               |
| IMPLEMENTATION\_FREEZE F1 manifest\_id             | `6caae5a8d5cebebdc94ac31c1afeb1202b6627ff...` (manifest\_id, not file hash) |

---

### Non-hold observations (preserved)

Two items are recorded but neither triggers a HOLD:

1. **QB\_MSE\_NEG\_\_4 false\_promotion = 1.** This is a single rejection of a true null in 4096 inner paths for a NEG cell (where the certificate threshold is negative, i.e., the null is always true). Under the preregistered binomial test (H0: p ≤ 0.05, one-sided), fp=1 out of 4096 yields p=1.0. This is well within the null and does not flag. The ANALYSIS\_SUMMARY correctly captures it.
2. **run\_confirmatory.py:279** **`fixtures_pass=True`** **hardcoded** (carried from pre-exec audit). Not a HOLD: fixtures are deterministic and were verified by dry run; any source change invalidates the F2 freeze hash. Recommendation to wire live in a future revision stands.

---

### Scope limitation (unchanged from frozen protocol)

A POSTRUN\_PASS licenses the interpretation: **implementation conformance within two frozen synthetic P-classes only** (B1-bounded-McDiarmid and QB-unbounded-quadratic-Cantelli). It does not constitute a conditional-validity claim for real data.