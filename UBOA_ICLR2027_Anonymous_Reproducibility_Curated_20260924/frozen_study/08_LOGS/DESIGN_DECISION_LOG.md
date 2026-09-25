# Design decision log

Preserved decisions and discarded alternatives:

- Real prospective cohort was not forced after the first frozen applicability universe returned zero certifiable real candidates.
- Route 2 predictable-risk inference is not used as the primary scientific target because it changes the estimand.
- Old 432k synthetic records are not reused as confirmatory evidence.
- No adaptive comparator chosen from a realized history is used; comparator parameters are frozen by cell.
- B1 primary empirical block uses raw MAE because it gives a transparent bounded-loss whole-functional test with exact rational truth boundaries.
- QB primary block uses raw MSE with Gaussian innovations because the exact quadratic variance certificate directly handles unbounded loss and all overlap.
- B1 raw MSE remains theorem-supported but is not promoted to a separate primary stochastic block; earlier theory already showed valid certificates can be highly uninformative.
- Power/informativeness is reported but never used as an eligibility gate.
- Ten cells, eight outer histories per cell and 4096 inner futures per history are frozen before any DGP run.
