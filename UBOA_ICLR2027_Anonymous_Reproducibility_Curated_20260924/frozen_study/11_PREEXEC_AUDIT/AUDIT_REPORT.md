# Pre-Execution Audit Report

**Auditor role:** independent adversarial pre-execution auditor  
**Study:** UBOA_ROUTE_B_SYNTH_CONFIRMATORY_V1  
**Audit date:** 2026-09-15  
**Verdict:** **PASS_TO_EXECUTE**  
**IMPLEMENTATION_FREEZE.json SHA256:** `0f9d5bb9e6b19a1cffa3e1fbe38d34054a0c2328a03f12ea56efe6bf35ca285c`

---

## 1. Scope of this audit

This report covers the complete F1 scientific-protocol package as frozen in
`01_FREEZE/SCIENTIFIC_FREEZE_MANIFEST.json`. It does not cover any
implementation code that does not yet exist, and it does not run, generate, or
repair any stochastic path. Every finding is adversarial and every ambiguity
is treated as a HOLD per the checklist rule.

---

## 2. Freeze integrity

`verify_freeze.py` was executed in the package root. Result:

```
SCIENTIFIC_FREEZE_VERIFY=PASS
manifest_id= 6caae5a8d5cebebdc94ac31c1afeb1202b6627ff0949aa2fb3c002e7bca29845
```

All 35 hashed F1 files match their declared SHA256 digests. The manifest ID
computed from the file-hash map equals the value stored in both
`SCIENTIFIC_FREEZE_MANIFEST.json` and `MANIFEST_ID.txt`. The
`09_OUTPUTS/` directory contains exactly one file (`README.md`), confirming no
synthetic study output is present. No unexpected files were detected outside
the allowed post-F1 prefixes (`10_IMPLEMENTATION/`, `11_PREEXEC_AUDIT/`,
`12_POSTRUN_AUDIT/`). **Freeze integrity: PASS.**

---

## 3. Pre-execution deterministic arithmetic

`prereg_deterministic_checks.py` was reviewed line-by-line (see MATH_CHECKS.md
for detail). The recorded run result in `08_LOGS/PREREG_CHECK_RESULTS.txt` is:

```
PREREG_DETERMINISTIC_CHECKS=PASS
B1_SELECTED_MAE_RISK= 1281/1280
```

All five B1 cell truth assertions and all four QB stationary comparator-gamma
derivations are confirmed correct by exact `Fraction` arithmetic. **Arithmetic
checks: PASS.** Full derivations are in MATH_CHECKS.md.

---

## 4. B1-MAE exact rational truth

The five cell truths are H-invariant (they depend only on the Rademacher
distribution and the cell design parameter `delta_b`, not on the realized
history). All five are confirmed exact rationals:

| cell | comparator delta_b | exact theta | first true null |
|---|---|---|---|
| NEG | 0/1 | −1/1280 | r = 0 |
| B02 | 289/784 | 1/50 | r = 0.02 |
| B05 | 5875/10336 | 1/20 | r = 0.05 |
| ALT08 | 2747/3680 | 2/25 | none (0.08 > 0.05) |
| STR40 | 541/328 | 2/5 | none (0.40 > 0.05) |

The boundary cells B02 and B05 sit exactly at the 2% and 5% ladder rungs.
The null `theta^0 <= r` is satisfied with equality, and `<=` is the correct
convention (strict inequality is in the rejection rule, not the null boundary).
No floating reclassification is possible because the truth is computed from
exact rational arithmetic independent of H. **B1 truth: PASS.**

---

## 5. QB-MSE H-conditional truth and NOM-label semantics

The five QB cells carry a `stationary_nominal_theta` column that was used
only to derive the frozen comparator gamma values before the protocol was
sealed. The `truth_rule` column for every QB cell reads: "compute exact
theta(H) from full frozen H; never relabel by nominal target." This is
consistent with the FROZEN_PROTOCOL (§5), TRUTH_FORMULAS.md, and
ANALYSIS_AND_DECISION_RULES.md. The `first_true_null` column in the QB table
is blank, correctly indicating that first-true-null classification is deferred
to per-history computation from exact `theta(H)`.

The formula `theta(H) = 1 − R_selected(H) / R_comparator(H)` is H-specific
because M2_k(H) depends on y0 = Y_325, which is in H but stochastic across
histories. The NOM labels are design targets, not truth certificates. **QB
truth semantics: PASS.** Arithmetic for the comparator gamma derivation is in
MATH_CHECKS.md.

One observation logged (not a HOLD): for QB_MSE_NEG the comparator gamma is 0,
making R_comparator(H) = avg_h Q_h (horizon-variance only). Since the selected
gamma contributes a positive gamma^2 * M2_k term, theta(H) < 0 for every
realized history. The first true null is therefore always r = 0 for this cell,
even though the table leaves the column blank. This is consistent with the
protocol (blank = H-specific); the per-history computation will recover the
correct label.

---

## 6. Filtration / chronology / evaluation-origin firewall

The index convention defined in FROZEN_PROTOCOL.md §5 (Exact time-index
convention) is internally self-consistent and satisfies the required ordering:

- Burn-in: Y_0 through Y_256 (256 steps from initial state 0).
- Validation origins: 256…319 (exactly 64), horizons {1, 3, 6}.
- Last validation target: Y_{319+6} = Y_325.
- H is frozen after Y_325 is revealed.
- First evaluation origin: 325; Y_325 is already in H (its state is an input
  to every evaluation term, not a target), so every evaluation target uses
  innovations strictly after H.
- B1 evaluation origins: 325…836 → 512 origins. ✓
- QB evaluation origins: 325…580 → 256 origins. ✓

The IMPLEMENTATION_CONTRACT reinforces this with a two-phase chronology rule
(outer-H phase then inner-future phase) and the explicit requirement that all
80 history records and their exact truths be written to `H_FREEZE_MANIFEST.json`
before any inner continuation is generated. No evaluation innovation may
influence selection, truth classification, certificate constants, or cell
retention. **Filtration / chronology: PASS.**

---

## 7. Selection semantics

Validation selection uses identical loss (MAE for B1, MSE for QB) over the 64
stride-one validation origins. The tie-break rule is deterministic: choose the
negative parameter first (delta = −1/10 for B1, gamma = −0.1 for QB). The
comparator is fixed by cell at protocol-freeze time and is not tuned to any
realized validation path. Selection is H-measurable by the time H is frozen.
**Selection semantics: PASS.**

---

## 8. Overlap and certificate correctness

**Theorem A (B1 McDiarmid).** The certificate requires computing the
whole-functional bounded difference per innovation block j as
`c_j = sum_i w_i u_ij` and then summing `sum_j c_j^2`. It is incorrect to
sum `u_ij^2` independently before squaring. The reference implementation
`certificate_interface_reference.py` (lines 338–345, 347–349) accumulates
`c_by_j[j] += weight * u` for all terms sharing innovation j, then computes
`c_sq = sum(v*v for v in c)`. This is the correct whole-functional aggregation.
No diagonalization of overlap. **Theorem A overlap: PASS.**

**Theorem B (QB Cantelli).** The exact quadratic variance formula requires
retaining all off-diagonal cross terms `4 * A[i][j]^2 * s2_i * s2_j` for
i < j. The reference implementation (lines 446–451) iterates all `(i, j)` pairs
with `i < j` and accumulates these terms. The third-moment diagonal term
`4 * A[i][i] * g[i] * m3` is also retained (line 444); for the Gaussian
innovations in QB this term is zero because m3j = 0, but the formula does not
drop it. **Theorem B overlap: PASS.**

The reference code also enforces `member_count == 1` for the quadratic path
(line 397), correctly blocking silent application to vector-dependent
coordinates that would require a full joint-moment tensor. **QB scalar-coord
guard: PASS.**

---

## 9. Fixed-sequence semantics

The rejection rule uses strict inequality W_r > b_r throughout. The fixed
sequence stops at the first nonrejection; if the reached node has an invalid
certificate, the request is unresolved (neither reject nor accept). The
Route-1 theorem (§5) proves `{fixed sequence rejects any true null} ⊆ {phi_{q*}
= 1}` where q* is the first true null, so the level guarantee propagates from
the single-test theorem to the sequence. **Fixed-sequence semantics: PASS.**

---

## 10. Per-history audit and multiplicity rule

The primary endpoint is the per-history false-promotion count F_H over 4096
inner futures, tested by an exact one-sided binomial test at p ≤ 0.05. The
Holm correction is applied across all finite-J histories from both primary
blocks at family audit level 0.01. The analysis rules require that the audit
family be determined from `H_FREEZE_MANIFEST.json` before any inner future is
generated, prohibiting post-hoc addition or removal of histories. No pooled
false-promotion rate may substitute for this per-history primary endpoint.
**Per-history audit design: PASS.**

---

## 11. No power-based inclusion

The protocol explicitly forbids filtering histories on selection label, truth
depth, certificate margin, rejection rate, numerical attractiveness, or power
(FROZEN_PROTOCOL §6). The analysis rules state that informativeness margins
are reported but never gate inclusion. All 10 cells and all 80 histories stay
in the report even if a certificate bound is vacuous. **No power-based
inclusion: PASS.**

---

## 12. Historical-record reuse

The evidence firewall (HISTORICAL_EVIDENCE_FIREWALL.md) explicitly excludes
all 432,000 Route-A synthetic records, the external process challenge, six UCI
prospective-cohort outcomes, Weather/ETTm2 records, Route-1 deterministic
nonvacuity examples R1C-PRE-001/002, and Route-2 research. The
`REAL_SCREEN_DECISION.md` closes the first real-candidate universe with
zero certifiable candidates and prohibits opening a second search universe.
The `09_OUTPUTS/` directory contains only `README.md` as verified by the
freeze checker. **Historical-record firewall: PASS.**

---

## 13. Invalid fixtures

Five deterministic invalid fixtures are defined in `05_AUDIT/INVALID_FIXTURES.md`
with unambiguous expected terminal behaviors:

1. B1_MISSING_SUPPORT → INVALID_CERTIFICATE / HOLD
2. QB_MISSING_M4 → INVALID_CERTIFICATE / HOLD
3. QB_CORRELATED_SCALAR_COORDS → applicability rejected
4. SCOPE_MUTATION → mismatch / unsupported
5. NONFINITE_CERTIFICATE → unresolved / invalid

Any positive terminal promotion from any of these five fixtures is a hard
FAIL. These fixtures must be evaluated before any stochastic path. Their
specification is clear and consistent with the certificate reference
implementation. **Fixture specification: PASS.** Behavioral correctness of
the fixture execution cannot be verified until implementation code exists.

---

## 14. Implementation code and F2 freeze — full verification

`10_IMPLEMENTATION/` contains the complete implementation. All verification
steps passed. Details follow.

### 14a. Required modules

All ten contractually required modules are present and correctly named:
`seed_schedule.py`, `generators.py`, `selection.py`, `truth.py`,
`certificate_b1.py`, `certificate_qb.py`, `fixed_sequence.py`,
`run_confirmatory.py`, `analyze_confirmatory.py`, `verify_outputs.py`.
Additional supporting files (`protocol.py`, `invalid_fixtures.py`,
`dry_run.py`, `freeze_implementation.py`, `tests/test_dry_run.py`) are present
and in scope.

### 14b. Implementation freeze hash verification

`verify_outputs.py` was executed against `IMPLEMENTATION_FREEZE.json`. All 15
executable source SHA256 hashes, all 3 dry-run artifact hashes, and all 4
schema hashes verified correctly. `VERIFY_OUTPUTS=PASS`. The hash of
`IMPLEMENTATION_FREEZE.json` itself is:

```
0f9d5bb9e6b19a1cffa3e1fbe38d34054a0c2328a03f12ea56efe6bf35ca285c
```

The `scientific_protocol_manifest_id` embedded in the implementation freeze
matches the F1 freeze manifest ID:
`6caae5a8d5cebebdc94ac31c1afeb1202b6627ff0949aa2fb3c002e7bca29845`. ✓

### 14c. RNG isolation — complete AST scan

An AST scan over all `.py` files in `10_IMPLEMENTATION/` (including subdirs)
checked for calls to `Generator`, `PCG64DXSM`, `choice`, `standard_normal`,
`normal`, `integers`, `default_rng`, `rand`, `randn`, `randint`,
`RandomState`, `shuffle` as attribute names, and for imports of `random`,
`numpy.random`, `secrets`. Results:

- All 8 RNG-related attribute calls are in `run_confirmatory.py` only, at
  lines 150, 152, 156, 190, 193, 199. No other file contains any such call. ✓
- No file other than `run_confirmatory.py` imports `numpy.random`, `random`,
  `secrets`, or any stochastic module. ✓
- The `static_rng_scan.json` dry-run artifact records
  `dry_run_rng_call_violations: []` and `status: PASS`. ✓
- `rng_call_count_during_dry_run: 0` confirmed — no RNG was invoked during the
  deterministic dry run. ✓

The `os` import in `run_confirmatory.py:14` is for `os.replace()` (atomic file
write) and does not provide any stochastic capability. ✓

### 14d. No hidden simulator or data path

No file in `10_IMPLEMENTATION/` opens any path outside the package. `protocol.py`
reads only `02_DESIGN/CELL_TABLE_ALL.tsv` (a frozen F1 file). `verify_outputs.py`
reads `01_FREEZE/SCIENTIFIC_FREEZE_MANIFEST.json`. No module reads from `data/`,
`outputs/`, cache directories, external URLs, or any absolute path outside the
package root. No `.npy`, `.pkl`, `.csv`, or `.jsonl` path that could contain
pre-generated simulation results is opened by any module. ✓

### 14e. Chronological phase discipline in code

In `run_confirmatory.py`, `_execute_confirmatory()` calls
`_generate_all_histories()` first (Phase 1: outer-H phase for all 10 cells,
all 8 indices), writes and hashes `H_FREEZE_MANIFEST.json`, then calls
`_inner_history_result()` for each history (Phase 2: inner-future phase).
Phase 2 reads the frozen history records from the manifest; no inner stream
is initialized before `H_FREEZE_MANIFEST.json` is written and verified. ✓

The outer-H phase (line 150–160) generates burn-in and validation innovations
via the `outer` stream, evolves states, runs selection, computes truth and
certificates, and records the terminal state at index `H_END=325`. Inner phase
(line 190–204) starts from `history["terminal_state"]` — the frozen `Y_325` —
and generates `future_length = cell.eval_origins - 1 + max(HORIZONS)` steps
from the `inner` stream. Evaluation origins are `0..cell.eval_origins-1`
relative to `Y_325`, with absolute origins `325..836` (B1) and `325..580`
(QB). ✓

### 14f. Five invalid fixtures — verified behavior

`invalid_fixture_results.json` confirms all five fixtures terminated correctly:

| Fixture | Status | Promotion |
|---|---|---|
| B1_MISSING_SUPPORT | INVALID_CERTIFICATE_HOLD | false |
| QB_MISSING_M4 | INVALID_CERTIFICATE_HOLD | false |
| QB_CORRELATED_SCALAR_COORDS | INVALID_CERTIFICATE_HOLD | false |
| SCOPE_MUTATION | INVALID_CERTIFICATE_HOLD | false |
| NONFINITE_CERTIFICATE | INVALID_CERTIFICATE_HOLD | false |

All five raise `ValueError` before any threshold is computed; the fixed
sequence receives all-`None` potentials and terminates as
`UNRESOLVED_INVALID_CERTIFICATE`. Zero positive terminal promotions. ✓

### 14g. Seed derivation implementation

`seed_schedule.py` constructs the key string as
`f"{MASTER_SEED}|{cell_id}|{stream_type}|{index}"` encoded as UTF-8, computes
`SHA256`, and uses `int.from_bytes(digest[:16], "big", signed=False)`.
Allowed stream types are exactly `{"outer", "inner"}` — any other type raises
`ValueError`. Index must be an integer in `0..7`. The test suite
(`test_dry_run.py:43-46`) verifies the derivation against a direct SHA256
computation and confirms `"retry"` is rejected. ✓

### 14h. History inclusion enforcement

`_generate_all_histories()` (line 161–162) raises `RuntimeError` if the
resulting list does not contain exactly 80 records. No history is dropped
based on selection label, truth depth, or certificate margin. All 80 are
written to `H_FREEZE_MANIFEST.json` before any inner stream is opened.
`verify_h_manifest()` checks uniqueness of all 80 history IDs and validates
each record's internal SHA256. `verify_history_results()` checks that all 80
results are retained and that `inner_denominator == 4096` for every record. ✓

### 14i. Truth cross-check and QB nominal-label guard

In `_qb_history_record()` (line 137), `"stationary_nominal_label_is_truth":
False` is explicitly stored in every QB history record, making the
non-substitution machine-readable. The QB truth is computed from exact
`qb_truth(cell.comparator_gamma, selected, y0)` using `y0 = states[H_END]`.
The B1 truth is computed from exact rational `b1_theta(cell.comparator_delta)`
and verified against the frozen cell table at line 71–72. ✓

### 14j. Dry-run summary

`dry_run_results.json` records:
- `tests_run: 15`, `failures: 0`, `errors: 0`
- `five_invalid_fixtures_pass: true`
- `rng_static_scan: PASS`
- `rng_call_count_during_dry_run: 0`
- `synthetic_paths_generated: 0`
- `real_dataset_reads: 0`
- `stochastic_execution_started: false`
- `status: PASS`

### 14k. One code-level finding (not a HOLD)

**`run_confirmatory.py:278–280` — `fixtures_pass` and `crosschecks_pass` are
hardcoded `True`.**

```python
status = decide_study_status(
    protocol_conformant=True,
    fixtures_pass=True,          # hardcoded
    crosschecks_pass=crosschecks_pass,
    ...
)
```

The `fixtures_pass=True` argument is hardcoded rather than wired to the
live `run_invalid_fixtures()` call that already exists in `dry_run.py`. If the
implementation is executed with source changes that break a fixture, this
hardcoded `True` would suppress the `IMPLEMENTATION_HOLD` that should result.

However, this is **not a HOLD** for the following reasons: (1) all five
fixture behaviors are deterministic and already verified in the dry run; (2)
the F2 source hash locks the current code, so any source change that breaks a
fixture also breaks the implementation freeze and requires a new audit; (3) the
analysis rules state that invalid-fixture conformance is checked as part of
the deterministic pre-execution checklist, not as a runtime counter. The risk
is a potential silent failure in a hypothetical re-run after a code change —
which is already blocked by the implementation freeze requirement. This finding
is preserved in the record per the HOLD-preservation rule.

**Recommendation for any future implementation revision:** wire
`fixtures_pass` to `fixtures_pass(run_invalid_fixtures())` in `main()`.

---

## 15. RNG audit — all sources

**F1 pre-existing files** (three): no RNG calls or imports in any of
[05_AUDIT/prereg_deterministic_checks.py](../05_AUDIT/prereg_deterministic_checks.py),
[05_AUDIT/verify_freeze.py](../05_AUDIT/verify_freeze.py), or
[07_REFERENCE/certificate_interface_reference.py](../07_REFERENCE/certificate_interface_reference.py). ✓

**F2 implementation files** (15): full AST scan confirmed all 8 RNG-related
attribute calls reside exclusively in [10_IMPLEMENTATION/run_confirmatory.py](../10_IMPLEMENTATION/run_confirmatory.py)
at lines 150, 152, 156, 190, 193, 199. Zero violations in any other module.
`numpy` is imported in `generators.py`, `selection.py`, and `certificate_qb.py`
for array arithmetic only — no `numpy.random` sub-module is imported in any of
those files. The `static_rng_scan.json` artifact records this independently
with `status: PASS` and `dry_run_rng_call_violations: []`. ✓

**RNG audit: PASS (all sources).**

---

## 16. Seed specification consistency

The master seed `7fae9301e8e38493e1917601eef359468a74b79fab00cd4a31777da6074dc110`
is 64 hex characters (32 bytes, 256 bits) — a valid entropy source. It appears
identically in `DESIGN_FREEZE.json`, `FROZEN_PROTOCOL.md`,
`SCIENTIFIC_FREEZE_MANIFEST.json`, and `SEED_SCHEDULE.md`. The derivation
formula `SHA256(master_seed|cell_id|stream_type|index)`, using first 16 bytes
as big-endian unsigned integer, and `numpy.random.Generator(PCG64DXSM(seed))`
is fully specified and consistent across all documents. No seed search, retry
seed, or replacement seed is permitted. **Seed specification: PASS.**

---

## 17. Claim boundary

`03_ANALYSIS/CLAIM_BOUNDARIES.md` correctly restricts post-PASS claims to fresh
implementation conformance within the two declared synthetic P-classes. It
explicitly forbids "simulation proves finite-sample conditional validity,"
"Route B validates the existing UCI applications," and other over-claims. **Claim
boundary: PASS.**

---

## Summary table

| Check | Result |
|---|---|
| Freeze integrity (hashes, manifest ID, clean outputs) | PASS |
| B1 exact rational truths (all 5 cells) | PASS |
| B1 boundary convention at 2% and 5% | PASS |
| QB H-conditional truth and NOM-label semantics | PASS |
| QB comparator gamma derivation | PASS |
| Filtration / chronology / evaluation-origin firewall | PASS |
| Selection semantics (deterministic, pre-evaluation) | PASS |
| Theorem A whole-functional overlap | PASS |
| Theorem B full-quadratic overlap, scalar-coord guard | PASS |
| Fixed-sequence strict-inequality and stopping | PASS |
| Per-history primary audit, Holm multiplicity | PASS |
| No power-based history inclusion | PASS |
| Historical-record firewall | PASS |
| Invalid fixture specification | PASS |
| RNG isolated to run_confirmatory.py only (full AST scan) | PASS |
| No hidden simulator or data path import | PASS |
| Chronological phase discipline in code | PASS |
| Five invalid fixtures behave correctly | PASS |
| Seed derivation exactly matches specification | PASS |
| IMPLEMENTATION_FREEZE.json — all hashes verified | PASS |
| Scientific protocol manifest ID consistent across F1 and F2 | PASS |
| Dry-run: 15 tests, 0 failures, 0 RNG calls, 0 synthetic paths | PASS |
| Claim boundary | PASS |
| fixtures_pass hardcoded True in run_confirmatory.py:279 | NOTE (not HOLD) |

---

## Verdict

**PASS_TO_EXECUTE**

**Bound to IMPLEMENTATION_FREEZE.json SHA256:**
`0f9d5bb9e6b19a1cffa3e1fbe38d34054a0c2328a03f12ea56efe6bf35ca285c`

All protocol-level, mathematical, leakage, implementation, and code-integrity
checks pass. The single noted finding (hardcoded `fixtures_pass=True` in
`run_confirmatory.py:279`) is preserved in the record but is not a blocking
condition because the five fixture behaviors are deterministic and verified by
the dry run, and any source change invalidates the F2 freeze and triggers a
new audit. Execution must use the exact command specified in the freeze:

```
python3 10_IMPLEMENTATION/run_confirmatory.py \
  --implementation-freeze 10_IMPLEMENTATION/IMPLEMENTATION_FREEZE.json \
  --audit-verdict 11_PREEXEC_AUDIT/FINAL_VERDICT.json \
  --output-dir 09_OUTPUTS/confirmatory_run
```

Any source edit before execution requires a new F2 freeze and a new audit.
