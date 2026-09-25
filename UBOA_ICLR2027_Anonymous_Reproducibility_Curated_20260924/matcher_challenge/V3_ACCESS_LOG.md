# V3 Authoring Access Log

**Date:** 2026-09-17  
**Agent:** Claude Code (claude-opus-5) — agent-authored controlled evaluation  
**Challenge version:** V3_20260917

## Files read in author phase (before freeze)

| File | Purpose |
|------|---------|
| 05_AUTHOR_ONLY/CHALLENGE_RULE_CONTRACT.md | M1–M8 rule contract |
| 05_AUTHOR_ONLY/CURRENT_CLAIM_DEFINITION.tex | Scientific target definitions |
| 05_AUTHOR_ONLY/CURRENT_FORMAL_APPENDIX_AB.tex | Formal matcher rules M1–M8 and proof |
| 05_AUTHOR_ONLY/PUBLIC_RECORD_FORMAT.md | Native input schema |
| 05_AUTHOR_ONLY/PUBLIC_SCORING_RULES.md | Scoring rules |
| 09_NEXT_OUTPUTS/final_matcher/NATIVE_INPUT_CONTRACT.md | **Critical:** declared_coarsenings encoding; provenance requirements; theorem premises requirements |
| 09_NEXT_OUTPUTS/final_matcher/FINAL_MATCHER_FREEZE.json | Authorized changes only (metadata); matcher.py NOT read |

## Files NOT read before freeze

- matcher.py (any version: original, revised, final)
- FINAL_MATCHER_PATCH.diff
- test_final_matcher.py
- REGRESSION_REPORT.md
- Any V1 or V2 challenge cases
- Any V1 or V2 checker predictions or outputs
- Any evaluator package contents beyond FINAL_MATCHER_FREEZE.json metadata

## Key contract points internalized before authoring

1. declared_coarsenings must contain the **bare request conditioning identifier** (e.g. "full_history"), not a path string like "sub_sigma to full_history"
2. M2 provenance: must be a non-empty, non-whitespace string; absence or empty string → OBSERVED_COPY_PROVENANCE_MISSING
3. M4 premises: must be non-empty list; empty list → THEOREM_PREMISES_EMPTY
4. All other encoding rules from PUBLIC_RECORD_FORMAT.md and CHALLENGE_RULE_CONTRACT.md

## Post-freeze access

EvaluatorOnly package / final matcher: NOT opened until after freeze hashes are recorded.
