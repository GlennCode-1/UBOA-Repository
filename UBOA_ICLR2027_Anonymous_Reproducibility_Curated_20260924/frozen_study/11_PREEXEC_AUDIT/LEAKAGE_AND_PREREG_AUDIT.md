# Leakage and Preregistration Integrity Audit

**Auditor role:** independent adversarial pre-execution auditor  
**Study:** UBOA_ROUTE_B_SYNTH_CONFIRMATORY_V1  
**Audit date:** 2026-09-15

This document adversarially examines every potential leakage channel, every
preregistration-integrity risk, and every scenario in which the confirmatory
claim could be inflated by design or execution choices that occurred after
the first view of outcome-relevant information.

---

## 1. Evidence firewall — exhaustive channel check

### 1.1 Route-A 432,000-replication study

The historical study produced 432,000 synthetic evaluation paths under a
different master seed and a different execution context. The frozen protocol
prohibits reuse of any record, numerator, denominator, or derived quantity
from that study. The `09_OUTPUTS/` directory is confirmed empty (only `README.md`).
No import of a Route-A results file appears in any existing source. The
`IMPLEMENTATION_CONTRACT.md` explicitly states: "Do not reuse a hidden old
simulator unless its complete source is copied into this package and
independently checked against the frozen protocol." **Route-A reuse: no
evidence of violation at F1.**

### 1.2 External process challenge

The historical evidence firewall lists the external process challenge as
excluded. No reference to it appears in any protocol or design file. No file
containing external challenge results is present in the package. **External
challenge: no evidence of inclusion.**

### 1.3 UCI / OOS / Weather / ETTm2 records

The real applicability screen (`REAL_SCREEN_DECISION.md`) determined
`A_CERTIFIABLE_REAL = 0` and explicitly closes the first real-candidate
universe. No second real-candidate search universe will be opened for Route B.
No existing UCI or OOS record can become Route-B confirmatory evidence. The
`09_OUTPUTS/` directory contains no such records. The evidence firewall
explicitly names these datasets. **Real-data leakage: no evidence of inclusion.**

### 1.4 R1C-PRE-001 / R1C-PRE-002 deterministic nonvacuity examples

These are listed as historical development evidence in the firewall. The
`ROUTE1_NONVACUITY.md` document exists as a reference artifact — it is the
analytical specification of the nonvacuity examples, not empirical simulation
output. The document contains deterministic calculations only and correctly
labels itself as "not simulation results." It is classified as mathematical
specification rather than fresh empirical evidence, consistent with
`HISTORICAL_EVIDENCE_FIREWALL.md`: "The study may cite theorem formulas and
deterministic parameter calculations from development, because they are
mathematical specification rather than fresh empirical evidence."

The auditor confirms these two examples do not supply confirmatory
numerators or denominators. They are analytic power bounds used to justify
the choice of n=4096 and to motivate the study design. Including them in a
reference directory does not constitute leakage. **R1C-PRE examples: correctly
classified as specification, not confirmatory evidence.**

### 1.5 Theory-development calculations

Protocol design choices (cell grid, lambda ladder, alpha, horizon set, n=4096)
were made using deterministic calculations before the study was frozen. This
is appropriate preregistration practice: the design is chosen before any
stochastic execution, and the choices are locked in `DESIGN_FREEZE.json`.
None of these calculations constitute fresh empirical evidence because they
involve no random draws from the frozen master seed. **Design-choice
calculations: no leakage, consistent with preregistration principles.**

---

## 2. Seed and RNG integrity

### 2.1 Master seed provenance

The master seed `7fae9301...dc110` was generated "before any DGP execution"
according to `ACCESS_AND_EXECUTION_LOG.md`. The log confirms no synthetic
history or evaluation path was generated before the seed was frozen. A 256-bit
seed of this complexity is consistent with fresh generation (no apparent
structure suggesting a chosen or recycled value). **Seed provenance: no
evidence of manipulation.**

### 2.2 No seed search

The protocol explicitly prohibits seed search, retry seeds, "nice seeds," and
replacement seeds. No mechanism for seed selection based on outcomes is present
in the design. Since no stochastic paths have been generated at F1, no
outcome-dependent seed choice is possible. **Seed selection manipulation:
not applicable at F1; prohibited for F2.**

### 2.3 RNG calls in existing source files

All three Python files present at F1 were examined for RNG calls:

- [05_AUDIT/prereg_deterministic_checks.py](../05_AUDIT/prereg_deterministic_checks.py): imports `fractions.Fraction`, `itertools.product`, `math`. No `numpy`, `random`, `os.urandom`, `secrets`, or any RNG import or call. ✓
- [05_AUDIT/verify_freeze.py](../05_AUDIT/verify_freeze.py): imports `pathlib`, `hashlib`, `json`, `sys`. No RNG. ✓
- [07_REFERENCE/certificate_interface_reference.py](../07_REFERENCE/certificate_interface_reference.py): imports `math`, `typing`. No RNG. Docstring: "no file, network, data, fitting, or random-generation entry point." ✓

**No RNG call exists outside `run_confirmatory.py` — because `run_confirmatory.py`
does not yet exist.** Once implementation is supplied, the F2 audit must verify
that `run_confirmatory.py` is the *only* module that instantiates any
`numpy.random.Generator` or calls any stochastic function, and that no other
module imports `numpy.random`, `random`, `os.urandom`, or `secrets` for
probabilistic purposes. This remains an open verification item for F2.

---

## 3. Cell grid and study design — frozen before outcomes

The cell grid (10 cells, 5 B1 + 5 QB), all exact truth values, all
comparator constants, all horizon sets, all replication counts, the alpha
level, the ladder, the weight convention, and the seed derivation formula are
all documented in `DESIGN_FREEZE.json` and in the hashed F1 files. The
`SCIENTIFIC_FREEZE_MANIFEST.json` records SHA256 hashes of all these files.
Any post-freeze edit to a hashed file would be detectable by `verify_freeze.py`.

The freeze was executed with `status: SCIENTIFIC_PROTOCOL_FROZEN_NOT_EXECUTED`
— meaning no stochastic execution has occurred that could have informed any
redesign. **Cell grid frozen before outcomes: CONFIRMED.**

---

## 4. Selection contamination

### 4.1 Validation-evaluation boundary

The FROZEN_PROTOCOL (§5) specifies an exact time-index convention:
- Validation origins 256…319 with horizons {1,3,6}, last validation target Y_325.
- Evaluation origins begin at 325; every evaluation target depends on
  innovations from time 326 onward.

There is no ambiguity or off-by-one error: Y_325 is simultaneously (a) the
last validation target (as horizon-6 outcome from origin 319) and (b) the
input context for the first evaluation origin. Its value is in H. The first
evaluation *target* is Y_326, generated by an innovation that is strictly
post-H. This is a clean boundary.

### 4.2 Selection based on validation only

The selected rule (delta or gamma) is chosen by comparing mean validation-phase
loss over 64 stride-one origins. The comparator is fixed by cell design, not
adapted to the validation outcome. The deterministic tie-break rule (negative
parameter first) eliminates any ambiguity. Selection is H-measurable. **Selection
contamination: no mechanism for leakage.**

### 4.3 Comparator frozen at design time

The comparator constants are preregistered rational values in the cell tables,
not chosen to maximize or minimize power against any realized outcome. For B1,
all five comparator deltas are rational fractions derived from the exact risk
function. For QB, comparator gammas are derived from the stationary second-moment
reference. Neither depends on any stochastic simulation. **Comparator
manipulation: not possible at F1.**

---

## 5. Per-history truth and first-true-null computation

### 5.1 B1-MAE: H-invariant truth

B1 exact truth does not depend on the realized history (the future Rademacher
sums are H-independent). The first_true_null column is preregistered in the
cell table for every B1 cell. This eliminates any possibility of post-hoc
truth relabeling. **B1 truth computation: no leakage risk.**

### 5.2 QB-MSE: H-specific truth computed before inner futures

QB exact theta(H) depends on the evaluation-start state y0 = Y_325, which is
in H. The protocol requires computing exact theta(H) for every frozen history
and recording it in `H_FREEZE_MANIFEST.json` before any inner continuation is
generated. The first_true_null label is therefore H-measurable and fixed before
the inner-future phase. No inner-future outcome can influence truth labeling.
**QB truth computation discipline: correct.**

The NOM labels in the QB cell table are design targets that correlate with the
typical truth depth across histories but are not authoritative. The audit
family (set of finite-J histories) is determined from `H_FREEZE_MANIFEST.json`
before any inner future. Adding or removing histories from the Holm correction
family after seeing rejection rates would be a serious integrity violation; the
protocol prohibits it. **NOM-label non-substitution: correctly specified.**

---

## 6. Multiplicity and Holm-correction integrity

### 6.1 Family defined pre-execution

The audit family for Holm correction is all finite-J histories from both primary
blocks, determined from `H_FREEZE_MANIFEST.json` before any inner future is
generated. This is a preregistered rule. **Family definition: correct.**

### 6.2 Holm correction across both blocks

The correction is applied across all finite-J histories from both B1 and QB
blocks jointly at family level 0.01. This is more conservative than
block-separate Holm. The primary endpoint is per-history, not pooled.
Pooled false-promotion rates are secondary and descriptive only. **Multiplicity
rule: conservative, correctly specified.**

### 6.3 No power-based cell/history filtering

The protocol explicitly prohibits filtering on rejection rate, certificate
margin, power, or "numerical attractiveness." All 10 cells and all 80 outer
histories are included regardless of whether any certificate is vacuous or any
history is uninformative. The analysis rules state: "All 10 cells and all 80
outer histories stay in the report even if a bound is vacuous." This is a strong
integrity constraint. **Power-based filtering: prohibited and correctly specified.**

---

## 7. Mandatory pathwise invariant

The analysis rules require that for every inner path:

`{fixed sequence rejects any true null} ⊆ {phi_{J(H)} = 1}`

Any violation of this inclusion is a deterministic IMPLEMENTATION_FAIL regardless
of Monte Carlo counts. This invariant is verifiable per-path and serves as a
logical consistency check on the implementation independent of calibration.
**Pathwise invariant: correctly specified.**

---

## 8. No outcome-dependent redesign

The protocol (§8) states: "Low or zero power does not permit redesign. An audit
red flag does not permit a new seed or silently repaired rerun." Any repair
required after a failure must be labeled `REPAIR_RUN` and the original failed
run must be preserved. This is stated in both `FROZEN_PROTOCOL.md` and
`IMPLEMENTATION_CONTRACT.md` (crash policy section). **No success-based
redesign: correctly prohibited.**

---

## 9. Claim boundary integrity

`CLAIM_BOUNDARIES.md` prohibits the following post-PASS over-claims:
- "simulation proves finite-sample conditional validity"
- "Route B validates the existing UCI applications"
- "the method is distribution-free"
- "the theorem applies to general nonstationary/long-memory forecasting"
- "no red flag = powerful"
- replacing the fresh nested study with the old 432k study
- calling pooled error rates history-conditional control

The only permitted claim after a PASS is that fresh nested conditional
simulation found no preregistered implementation-calibration red flag within
the two declared synthetic P-classes, and that the finite-sample guarantee
itself follows from the stated theorem and its law-class assumptions, not from
simulation. **Claim boundary: correctly restricted.**

---

## 10. Historical evidence access log integrity

`08_LOGS/ACCESS_AND_EXECUTION_LOG.md` records that during F1 freeze:
- Only project manuscript/theory/applicability artifacts already in the project
  were read.
- Deterministic algebra was performed to freeze generator parameters and exact
  truth constants.
- One 256-bit master RNG seed was generated before any DGP execution.
- No synthetic history, evaluation path, Monte Carlo loop, training,
  validation selection, benchmark replay, or real-data access occurred.
- The manuscript was not modified.

This log is hashed in the scientific freeze manifest (hash:
`dab0cc7ee907ea69303f7ef400b344e81cb788c8d51f1022a64d6d31edede5ff`). Any
post-freeze modification to the log would be detectable. **Access log: consistent
with clean preregistration practice.**

---

## 11. Implementation not yet supplied — open leakage risks for F2

The following leakage risks cannot be evaluated until implementation code
exists. They must be checked in the F2 audit:

1. **Hidden old simulator import.** Any `import` of a module outside the
   declared package that wraps an existing simulator must be detected. The
   implementation contract requires: "Do not reuse a hidden old simulator unless
   its complete source is copied into this package and independently checked
   against the frozen protocol."

2. **Hidden data path.** Any `open()`, `pathlib.Path.read_*()`, `numpy.load()`,
   `pandas.read_*()`, or similar call to a file outside the package (especially
   under paths like `data/`, `outputs/`, `cache/`, or any absolute path) must be
   flagged unless it reads only implementation-internal configuration.

3. **Cached path reuse.** Any `.npy`, `.pkl`, `.csv`, `.jsonl`, or similar file
   that could contain pre-generated paths must be absent from the package or
   demonstrably unread by the implementation.

4. **RNG calls outside `run_confirmatory.py`.** Every Python file in
   `10_IMPLEMENTATION/` must be scanned for `numpy.random`, `random`, `os.urandom`,
   `secrets`, and any third-party RNG. Any such call outside `run_confirmatory.py`
   is a violation.

5. **Seed override.** Any mechanism that overrides the SHA256-derived seed
   (environment variable, config file, command-line argument to the seed
   function) must be flagged.

6. **Evaluation before H freeze.** Any code path that generates evaluation
   innovations before writing `H_FREEZE_MANIFEST.json` and hashing it violates
   the chronological discipline.

7. **History filtering after inner futures.** Any logic that removes a history
   or marks it `DROPPED` based on its inner-future rejection rate, certificate
   margin, or label before writing final outputs violates the inclusion rules.

---

## Summary

| Leakage / Integrity Check | Result |
|---|---|
| Route-A 432k records excluded | PASS |
| External challenge excluded | PASS |
| UCI/OOS/real-data excluded | PASS |
| R1C-PRE examples classified as specification (not confirmatory evidence) | PASS |
| Design-choice calculations predate stochastic execution | PASS |
| Master seed generated before any DGP execution | PASS |
| No seed search mechanism | PASS |
| No RNG in any existing source file | PASS |
| Cell grid frozen before outcomes | PASS |
| Validation-evaluation boundary clean (Y_325 in H, Y_326 first target) | PASS |
| Selection uses validation only, comparator fixed at design time | PASS |
| B1 truth H-invariant, preregistered | PASS |
| QB truth H-specific but computed before inner futures | PASS |
| Holm family preregistered and determined before inner futures | PASS |
| No power-based history filtering | PASS |
| Pathwise invariant specified correctly | PASS |
| No outcome-dependent redesign permitted | PASS |
| Claim boundary correctly restricted | PASS |
| Access log consistent with clean freeze | PASS |
| Hidden simulator / data path / RNG scan | **PENDING F2** |
| Cached path absence | **PENDING F2** |
| Chronological phase enforcement in code | **PENDING F2** |
| History-inclusion enforcement in code | **PENDING F2** |

All currently verifiable leakage and preregistration integrity checks pass.
The pending items are structurally unavoidable — they require implementation
code that does not yet exist — and are the primary subject of the F2 audit.
