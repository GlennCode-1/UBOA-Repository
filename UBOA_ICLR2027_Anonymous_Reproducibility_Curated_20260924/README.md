# UBOA anonymous reproducibility package (curated public export)

This is a filtered public distribution derived byte-for-byte from the audited anonymous ZIP. It preserves the scientific payload, frozen protocol, saved histories and counts, certificate inputs, matcher/challenge materials, historical evidence export, negative results, and explicit missing-artifact boundaries. Five internal workflow/reference files are intentionally omitted; the original ZIP and the omission record remain outside this archive.

All checks below are deterministic. They must not call an RNG, generate future paths, train or fit a model, read a new prospective OOS, or execute the original confirmatory entry point. Aggregate reconstruction is not independent replay of individual future paths.

## Deterministic checks

Run from this package root, in order:

```bash
python scripts/verify_public_export.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/reconstruct_public_export.py
python scripts/brownian_reference_quadrature.py
(cd matcher_final && python -m unittest -v test_final_matcher_portable.py)
python matcher_challenge/verify_matcher_challenge.py
python scripts/check_reached_cutoff_sensitivity.py
```

`verify_public_export.py` checks the release manifest, the exact five-file omission allowlist, the original F1/F2 hashes, all retained F1 files, protected F2 sources/schemas/dry-run artifacts, and the retained H/results records. It reports `retained_F1_files_verified=31`, `intentionally_not_distributed=5`, and `full_original_tree_verified=false`; the original complete 36-file tree remains verifiable only from the original ZIP. `reconstruct_public_export.py` is a deterministic public-export adapter of the saved-record reconstruction. It compares the reconstructed table values and certificate arrays with retained outputs using the parent script's numeric tolerance (`rtol=1e-10`, `atol=1e-10*(1+max(abs(reference)))`); nonnumeric table fields and record ordering must match. It writes only derived reconstruction files and a scope report; it does not alter the scientific algorithm or generate paths.

The original `scripts/reconstruct_saved_audit.py` is retained unchanged as an archival scientific script. Because this is a selective public export, it cannot be represented as a complete-tree PASS when run directly: use the public verifier and adapter above.

Do **not** run `frozen_study/10_IMPLEMENTATION/run_confirmatory.py`. It is retained only as the original frozen executable and is not a verification command.

## Main contents

- `frozen_study/`: original conditional-certificate preregistration, implementation freeze, saved histories/counts, and pre/post-run audits. The original stochastic run is not altered or rerun.
- `certificates/` and `derived/`: 123 reconstructed coefficient files, 80-history and 240-node tables, count-based audit reconstruction, later upper bounds/power diagnostics, and deterministic Brownian reference calculations.
- `reference_matcher_original/`: original metadata matcher and historical fixtures.
- `reference_matcher/`: intermediate revised matcher and development regressions retained for provenance.
- `matcher_final/`: finalized matcher candidate, native input contract, freeze record, patch, deterministic tests, and a curated public execution log. The frozen original test file is retained unchanged; `test_final_matcher_portable.py` is the reviewer entry point.
- `matcher_challenge/`: 140-case code-blind agent-authored contract challenge, frozen gold rationales, predictions, evaluation report, and deterministic verifier.
- `historical_existing_evidence/`: anonymous export of recovered historical evidence for the real cohort and Brownian reference, including public manifest and explicit missing-artifact list.
- `scripts/`: original deterministic numerical scripts plus the public-export verifier and reconstruction adapter.
- `PUBLIC_EXPORT_OMISSIONS.json`, `RELEASE_SCOPE.md`: release boundary and exact omission records.
- `audit_notes/`: provenance boundaries and unresolved gaps.

## What can be reconstructed

- Every saved history-specific certificate quantity and all 240 history-threshold records.
- The 46 count-based binomial/Holm audit calculations from retained aggregate counts.
- The finalized matcher behavior on the frozen 140-case challenge: 0/70 false accepts and 0/70 false rejects; original matcher 9/70 false accepts; coordinate equality 29/70 false accepts and 10/70 false rejects; schema presence 70/70 false accepts.
- Historical candidate aggregate scores and selected/comparator validation arrays for six applications.
- Historical Brownian reference source/configuration, the sorted 200,000-value reference array, and 16 reached-node statistics.

## Remaining limits

- Original individual future paths and per-path terminal/invariant decisions were not retained; aggregate `0 pathwise violations` cannot be independently replayed.
- The historical 20% missing-target denominator/enforcement record is not recovered.
- Household Power used consecutive complete 60-row groups rather than calendar-hour aggregation; a corrected counterfactual would require new preprocessing/refitting and is not created here.
- Raw Brownian increments and the original generator execution transcript were not retained, even though generator source/configuration and the final sorted reference array are available.
- The 140-case challenge is agent-authored controlled contract-conformance evidence. It is not expert adjudication, a human-utility study, or a population-generalization claim.
- The matcher checks supplied metadata and verification annotations; it does not authenticate provenance or verify that a stochastic assumption is true in raw data.

## Release boundary

The distribution manifest lists only actual archive files and excludes itself to avoid recursive hashing. Its external SHA-256 file and the final ZIP SHA-256 are outside the archive. The original release manifest and original five omitted files remain in the author-side input archive; they were not deleted or rewritten.
