# Pre-execution audit checklist

The independent auditor must verify, before any stochastic execution:

- scientific protocol files match the frozen manifest;
- no file in `09_OUTPUTS` contains synthetic results;
- no RNG call occurred in the implementation/dry-run log;
- B1 exact rational cell truths are correct, especially equality at 2% and 5%;
- QB exact H-conditional truth and the fact that NOM labels are not truth;
- selection uses validation only and H ends after all validation targets;
- evaluation origins begin only after H is frozen;
- full overlap is retained in both certificate implementations;
- strict endpoints are used;
- first-true-null is H-measurable and computed before inner futures;
- primary audit is per-history, not pooled;
- no power threshold controls cell/history inclusion;
- all five invalid fixtures terminate correctly;
- code hashes are frozen before PASS_TO_EXECUTE.

Any ambiguity => HOLD, not inferred PASS.
