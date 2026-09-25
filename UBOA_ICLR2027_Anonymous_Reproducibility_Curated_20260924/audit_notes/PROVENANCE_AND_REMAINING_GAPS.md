# Provenance levels and remaining gaps

## Conditional-certificate study

Original scientific manifest identifier: `6caae5a8d5cebebdc94ac31c1afeb1202b6627ff0949aa2fb3c002e7bca29845`.
Original implementation-freeze file SHA256: `0f9d5bb9e6b19a1cffa3e1fbe38d34054a0c2328a03f12ea56efe6bf35ca285c`.
Original H file SHA256: `5229432f2384a80b2cde4097c68cf08e383cdacbf67642f8de12537895c0e8c9`.

The original execution log records one started/completed stochastic run. The package does not infer absence of every possible unlogged execution. Individual future paths and individual pathwise decisions were not retained, so later reconstruction verifies certificates and aggregate counts rather than independently replaying every continuation.

## Matcher development and controlled challenge

The original matcher is retained byte-for-byte. Deterministic audits exposed fail-open cases; subsequent revisions are separately versioned. The finalized matcher source SHA256 is `920acdcf516c477b575bb87945ccd2d64cc79e7d831ee23d2b6a5afedf50f0eb`.

Strengthening the observed-record contract to require explicit nonblank provenance intentionally reclassifies one legacy observed-copy fixture that omitted provenance. Its original bytes and expected result remain preserved; the other 22 legacy cases retain their outcomes, and a provenance-complete positive control is accepted.

The final 140-case challenge was authored from the public rule contract and native encoding specification, then frozen before checker-source access. The challenge is controlled contract-conformance evidence only. It does not establish expert reviewer accuracy, adoption value, or performance under a population distribution of benchmark reports.

## Historical real-data evidence

Saved aggregate candidate scores show the smallest top-two gap across the six recorded selections is `0.018147357786163942`, so changing only exact-tie versus `1e-12` tie handling does not alter those six stored winners. Checked target prefixes contain no leading missing run, so the future-assisted initial-fill branch was not triggered for those target prefixes.

The original 20% missing-target denominator and execution-side enforcement record remain missing. Retrospectively derived masks do not substitute for that record. Household Power used consecutive complete 60-row groups; the exported timestamp table shows this differs from calendar-hour grouping, and no refit under corrected grouping is claimed.

## Historical Brownian reference

The anonymous evidence export includes the historical generator source, its declared configuration, and a sorted 200,000-value reference array. The array's linear 0.95 empirical quantile is `5.298829753159216`. Sixteen reached-node statistics recompute from exported paired-loss records, and none lies between that cutoff and the ideal continuous-reference quantile `5.322679900530264`.

Raw Brownian increments, unreached-node statistics, and the original generator execution transcript remain unavailable. Source/array hashes fix bytes but do not by themselves prove a unique historical execution chain.
