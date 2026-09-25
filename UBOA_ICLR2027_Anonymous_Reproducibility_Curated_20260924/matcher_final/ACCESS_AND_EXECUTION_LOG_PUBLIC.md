# Access and execution log (curated public derivative)

Date: 2026-09-17 (parent record); curated release: 2026-09-24.

This file is a curated public derivative of the parent public log. Parent SHA-256: `2dac3679f7c56c6f3afb2034dd89f6bb47a5330f440746552029d5a28aa29554`. The parent log remains in the audited input archive. Internal workspace and handoff names are replaced here by neutral source IDs; the original private path mapping is not distributed.

## Read-only inputs opened in the parent record

- `SOURCE-CHALLENGE-REVISED`: revised matcher and its frozen challenge fixtures.
- `SOURCE-CHALLENGE-REPORT`: challenge report, V2 post-exposure regression summary, and public record format.
- `SOURCE-GOLD-REASONS`: frozen gold rationales and authoring preflight.
- `SOURCE-THEORY-CONTRACT`: theory matcher fixtures and formal matcher specification.
- `SOURCE-LEGACY-REPRO`: legacy matcher, README, revision note, tests, and deterministic fixtures from the prior reproducibility archive.
- `SOURCE-MEMORY-PRECEDENT`: one system-provided workflow/provenance precedent; no scientific result or matcher decision was sourced from it.

These are historical source records; the corresponding original paths are not distributed in this public release.

No raw data, training data, validation outcomes, OOS outcomes, prediction caches, manuscript source, frozen synthetic outputs, or historical scientific records were opened by the matcher repair work.

## Parent writes and deterministic outcomes

The parent record states that durable writes were confined to its author-side matcher output directory and that no source input was overwritten. It records the following attempts and outcomes without rewriting them:

- The first candidate-test invocation failed before matcher assertions because a workspace-relative helper resolved one directory too high; the helper was corrected in the parent workstream and the event was retained.
- A temporary harness command failed before execution because its requested directory did not yet exist; no scientific subcommand ran.
- The frozen legacy matcher test had exactly one expected failing subcase (`observed_decision_copy`, absent provenance); other legacy/regression checks passed.
- Full V2 execution was only a post-exposure development regression, not held-out evaluation.
- A combined path-check command failed on relative paths while the unit-test portion passed; final file/hash checks were rerun from the parent workspace root.
- Only an unfrozen generated `__pycache__` directory was removed before the parent artifact freeze.

## Curated public release action

The public export removes exactly five files listed in `PUBLIC_EXPORT_OMISSIONS.json`. No scientific protocol, proof, assumption document, matcher source, modification history, negative result, saved history/node/coefficient, challenge case, reference rationale, F1/F2 file, reference array, or reached-node record was removed or rewritten.

## Hard-zero counters in the parent record

| Action | Count |
|---|---:|
| RNG calls | 0 |
| stochastic simulation | 0 |
| model training/fitting | 0 |
| new OOS access | 0 |
| manuscript edits | 0 |
| frozen scientific-result edits | 0 |
