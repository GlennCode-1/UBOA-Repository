# Analysis and decision rules

## Primary endpoint: per-history family false-promotion audit

For every frozen history `H` with finite first true null `J(H)`, run the complete fixed sequence on each of the 4096 inner continuations. Define

`F_H = #{inner futures on which fixed sequence rejects any true null}`.

The theorem asserts the conditional probability is at most 0.05. The simulation does not prove this theorem; it is an implementation audit.

For each such history, compute an exact one-sided binomial test of `p<=0.05` versus `p>0.05` using `F_H` and `M=4096`. Apply Holm correction across **all finite-J histories from both primary blocks** at family audit level `0.01`. This realized audit family is determined from `H_FREEZE_MANIFEST.json` before any inner future is generated; no history is added or removed afterward.

- any Holm-adjusted rejection => `CALIBRATION_RED_FLAG`;
- no adjusted rejection => `NO_CALIBRATION_RED_FLAG_OBSERVED`.

Do not replace this with pooled false-promotion as the primary metric.

## Mandatory pathwise invariant

For every inner path with finite `J(H)`:

`{fixed sequence rejects any true null} subseteq {phi_J(H)=1}`.

Any violation is deterministic `IMPLEMENTATION_FAIL`, regardless of Monte Carlo counts.

## Secondary local diagnostics

For each history/node:
- local rejection rate for each true and false null;
- reached-node rate under fixed sequence;
- terminal ladder report;
- invalid/unresolved count.

These are descriptive. No post hoc multiplicity claim is made.

## Truth and certificate cross-checks

B1-MAE:
1. exact risk/truth from rational enumeration of the Rademacher horizon errors;
2. independent floating implementation must agree within `1e-12` absolute error;
3. the exact first-true-null labels in the frozen cell table are authoritative.

QB-MSE:
1. direct conditional-risk formula from `E[Y_k^2|H]`;
2. independent quadratic-form expectation `k + trace(A)` under Gaussian innovations;
3. agreement tolerance `1e-10*(1+|value|)`.
Disagreement => hard FAIL before use of rejection results.

Certificate checks:
- B1: general certificate code and an independent scalar-AR reference calculation must agree within `1e-10` relative/absolute combined tolerance.
- QB: variance formula and an independent Gaussian quadratic identity `2 tr(A^2)+4||g||^2` must agree within `1e-10`.

## Informativeness

Report, but never gate inclusion on:
- exact `mu_r^0 - threshold_r` for each H/node;
- whether a false null is structurally informative (`mu_r^0 > threshold_r`);
- rejection probability for false nulls;
- terminal recovery.

All 10 cells and all 80 outer histories stay in the report even if a bound is vacuous.

## Pooled summaries

Pooled rates may be shown only as clearly secondary design-mixture summaries with the exact denominator. They are never called conditional validity.

## Study-level status

`CONFIRMATORY_IMPLEMENTATION_PASS` requires:
1. protocol/hash/seed conformance;
2. all deterministic invalid fixtures behave correctly;
3. no truth/certificate cross-check failure;
4. no pathwise first-true-null inclusion violation;
5. no Holm family audit red flag.

Otherwise: `IMPLEMENTATION_HOLD`, with all negative results retained.

A PASS does **not** license a real-data conditional-validity claim. Allowed interpretation is limited to fresh implementation conformance within the two declared synthetic P-classes.
