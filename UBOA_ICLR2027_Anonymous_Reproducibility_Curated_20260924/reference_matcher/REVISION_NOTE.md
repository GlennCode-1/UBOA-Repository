# Matcher repair, separate from original record

This version was edited on 2026-09-16 after reading the source. It fixes empirically missing-field matches, unverified conditional-coarsening premises, conclusion-type omissions, truthy non-Boolean flags, and selected malformed-input cases. It also requires the explicitly declared local-family premise labels.

Original GOLD_FIXTURES.json is byte-identical. All original tests pass, as do 16 new invalid regressions and 2 valid controls. Original code is retained in ../reference_matcher_original. Development examples were constructed with knowledge of the code and are not blinded or expert-adjudicated evidence.

The checker still operates on supplied theorem assertions and annotations. It does not verify actual probability values, derive law-class assumptions, authenticate source provenance, or claim exhaustive schema/security assurance. No stochastic results were recomputed using this repair.
