# Frozen protocol

## 1. Scientific question

本 study 不问“哪些 synthetic settings 容易得到 2%/5% support”。它问：

> 在两个预先声明、primitive constants 全部由 generator/design 给出的 nonempty P-classes 中，Route-1 local certificate 的代码实现是否保持原 `mu_r^0 = E[W_r|H]`、完整 overlap 与固定序列语义，并且 fresh conditional continuations 是否出现与 nominal 5% control 不相容的 implementation red flag？

`H` 是完整 pre-evaluation history：generator/design parameters、burn-in/validation path、candidate pool、deterministic tie-break、selected rule、comparator、loss、horizons、weights、ladder 与 certificate parameters。

## 2. Evidence firewall

以下均为 historical/development evidence，**不得**进入 confirmatory numerators/denominators：
- Route A 432,000-replication study；
- external process challenge；
- six UCI application cohort 与 earlier Weather/ETTm2 records；
- Route-1 之前的 deterministic nonvacuity examples `R1C-PRE-001/002`；
- theory-development calculations used to choose this protocol.

Fresh confirmatory evidence 仅由本 protocol 锁定后、master seed `7fae9301e8e38493e1917601eef359468a74b79fab00cd4a31777da6074dc110` 派生的新随机流产生。

## 3. Common evaluation semantics

- thresholds: `r in {0, 0.02, 0.05}`;
- local alpha: `0.05` at every potential node;
- contrast: `W_r = sum_i w_i[(1-r)B_i - S_i]`;
- null: `mu_r^0=E[W_r|H] <= 0`, equivalently `theta^0(H)<=r` when comparator risk is positive;
- strict rejection only;
- fixed sequence stops at first nonrejection;
- any reached invalid certificate makes the public request unresolved;
- no continuous inversion or cohort-wide claim.

Validation selection is completed before any evaluation innovation is generated. Comparator is fixed by cell, not tuned to the realized validation path.

## 4. Primary block B1-MAE

Generator:
`Y_t = 0.5 Y_(t-1) + eps_t`, `eps_t` iid Rademacher `{-1,+1}` after `H`. Initial burn-in starts at zero.

Forecast mapping:
`f_delta(o,h)=0.5^h Y_o + delta`.

Selected pool:
`delta in {-1/10,+1/10}`; validation selects smaller mean raw MAE over 64 stride-one origins and horizons `{1,3,6}`; exact tie => `-1/10`.

Evaluation:
512 stride-one origins, same horizons, equal weights over all origin-horizon terms.

Comparator shifts and exact truth are frozen in `CELL_TABLE_B1_MAE.tsv`. Exact comparator constants are rational. Because future innovation sums are symmetric and the selected shifts have equal magnitude, selected sign may adapt to validation but the conditional expected risk is identical for the two labels. Exact boundary cells have `theta=0.02` and `theta=0.05` without floating reclassification.

Certificate:
Theorem A bounded-innovation whole-functional McDiarmid. Use state support implied by `|Y_t|<=2`; innovation replacement diameter is 2. No empirical maximum may replace these structural quantities.

## 5. Primary block QB-MSE

Generator:
`Y_t = 0.5 Y_(t-1) + eps_t`, `eps_t` iid `N(0,1)` scalar coordinates after `H`.

Forecast mapping:
`f_gamma(o,h)=(0.5^h+gamma)Y_o`.

Selected pool:
`gamma in {-0.1,+0.1}`; validation selects smaller mean raw MSE over 64 stride-one origins and horizons `{1,3,6}`; exact tie => `-0.1`.

Evaluation:
256 stride-one origins, same horizons, equal weights.

Comparator gamma values are frozen in `CELL_TABLE_QB_MSE.tsv`. The labels `NOM02/NOM05/...` are only design labels obtained from the stationary second-moment reference. **They never define truth.** For every frozen `H`, compute exact `L_b^0(H), L_s^0(H), theta^0(H)` and the first true null from that history.

With evaluation-start state `y0`, for origin offset `k`:
`E[Y_k^2|H] = 0.5^(2k)y0^2 + (1-0.5^(2k))/(1-0.25)`.
For horizon `h`, future innovation variance is `(1-0.5^(2h))/(1-0.25)`.
Thus the conditional expected MSE for gamma is the exact average of
`q_h + gamma^2 E[Y_k^2|H]`.

Certificate:
Theorem B exact quadratic variance plus Cantelli using `s_j^2=1`, `m_3j=0`, `m_4j=3`. Compute the full quadratic form with all shared innovations; do not diagonalize away overlap.


### Exact time-index convention

Use state `Y_0=0`. Generate innovations through state 256 for burn-in. Validation origins are exactly `256,...,319`; with max horizon 6, the last validation target is `Y_325`. The full `H` includes the entire realized path through `Y_325`, the validation scores and selected label. The first evaluation origin is exactly 325, so `Y_325` is context already in `H`; every evaluation target depends only on innovations from time 326 onward. B1 evaluation origins are `325,...,836`; QB evaluation origins are `325,...,580`.

All 80 outer histories are generated and frozen before any inner continuation is produced; no history is filtered after seeing its label or truth depth.

## 6. Randomness and replication

Each of the 10 cells has exactly 8 outer histories. For each frozen history, generate exactly 4096 independent evaluation continuations. No history is dropped based on selection label, truth depth, certificate margin, rejection rate, numerical attractiveness or power.

Per-stream seed:
`SHA256(master_seed | cell_id | stream_type | index)`, first 128 bits interpreted as unsigned big-endian integer and passed to `PCG64DXSM`.

Outer history index is 0..7. Each history has one inner stream that generates the 4096 continuations in a fixed batch order.

## 7. Negative controls

The five deterministic invalid fixtures in `05_AUDIT/INVALID_FIXTURES.md` must be evaluated before stochastic execution. Any positive promotion from them is a hard implementation FAIL.

## 8. No success-based redesign

Low or zero power does not permit redesign. An audit red flag does not permit a new seed or silently repaired rerun. The original result is retained and status becomes `IMPLEMENTATION_HOLD`; any repair is a new development study.
