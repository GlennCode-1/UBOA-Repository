# Frozen reference critical values

Critical values are obtained from the limiting Brownian functional, never from the
old or any future finite-sample feasibility outcome.

Approximation contract:

- independent implementation: `independent_implementation.py`;
- paths: 200,000;
- grid: 2,048 equal subintervals with left-endpoint cumulative Brownian sums;
- seed: `2027090801`;
- chunk size: 2,000 paths;
- quantile: linear empirical quantile at `1-alpha`;
- approximation error report: Monte Carlo standard error for a quantile is recorded
  by an independent batch rerun in `validation_results.md`; no calibration data enter.

The frozen critical value used by the repaired method is the signed upper-tail 95%
quantile produced by this contract. It must be regenerated only under a new method
identity if the approximation contract changes.

Observed under the frozen contract:

| alpha | upper critical value |
|---:|---:|
| 0.10 | 3.84112387 |
| 0.05 | 5.29882975 |
| 0.025 | 6.75023698 |
| 0.01 | 8.58619281 |
