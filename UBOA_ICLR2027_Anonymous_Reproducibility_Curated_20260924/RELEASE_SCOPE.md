# Curated Public Release Scope

This package is a selective, lossless public distribution of the audited anonymous reproducibility ZIP with exactly five internal workflow/reference files omitted. The omitted original files and their SHA-256/size are listed in `PUBLIC_EXPORT_OMISSIONS.json`; they remain in the author-side source archive and were not deleted.

Preserved scientific material includes the F1 protocol and all retained F1 files, F2 implementation sources/schemas/dry-run artifacts, H/results/aggregate records, original and revised matcher sources, development regressions, the 140-case challenge and rationales, all histories/nodes/coefficients, historical reference generator/configuration/array, reached-node evidence, negative results, and unresolved-artifact records.

`REPRO_PACKAGE_MANIFEST.json` is a distribution manifest, not a scientific freeze. It lists actual archive files exactly once and excludes itself to avoid recursive self-hashing. The external `.sha256` files bind the manifest and final ZIP. F1/F2 IDs and hashes are preserved and checked by `scripts/verify_public_export.py`.

The public adapter `scripts/reconstruct_public_export.py` is a deterministic publication-view check. It does not change any numerical formula, generate random paths, import frozen certificate code, or claim complete-tree F1 verification. The full original tree remains a separate author-side input.
