# Stage 36 master protocol

Protocol version: `UBOA_STAGE36_MASTER_V1`

## Objective and frozen claim boundary

This is one coordinated pre-OOS program. It strengthens the evidence for UBOA as a selected-realization claim-certification system without changing the historical scientific record. The program has six workstreams A--F and exactly one downstream cohort-level OOS Human Gate. No new-cohort OOS numerical value may be decoded, inspected, hashed as content, predicted, tested, or authorized in Stage 36.

The final local method is frozen as `C2_SN_MEAN_BROWNIAN_FUNCTIONAL_V2`, method identity `6019950f9c3bc3d241133b13a5e1574ba64acc1265df885c5965caf3fc8cf124`, production source SHA-256 `c7ea82b0a1543639674e0b9d86e5fefcfd5ff6e4b7f425bcdc5e54f6b8b22824`, Brownian reference SHA-256 `bbb43c2d578f85aef64b30f873812143409a9f3c341ceaf3ce4f42d97ff5f5cf`, and upper-tail 0.95 critical value `5.298829753159216`. There is no C1 fallback and no tuning of the statistic, normalizer, reference, critical value, or tail convention.

The ordered relative-loss claim ladder is frozen as `r=(0,0.02,0.05)` with one-sided local alpha 0.05. Structural identity means exact predictor-specification identity with the comparator and authorizes no superiority test. A valid first-node nonrejection means no positive-improvement support. A later valid nonrejection retains the last promoted tier and is not an upper bound. Invalid C2 evidence is unresolved and cannot promote.

## Historical state

Traffic and Electricity remain closed structural terminals. Weather and ETTm2 remain positive-improvement-only terminals: 2% was not supported, 5% was not reached, and the descriptive OOS reductions remain 0.874% and 0.862%. Their OOS streams must not be reopened. The post-validation-selection, pre-OOS amendment from prewhitened HAC to C2 remains disclosed. Stages 22--35 and the handoff manuscript are read-only inputs.

## Workstream A: formalization and adjacent methods

A must distinguish the random selection procedure, realized selected object, comparator, loss, fixed scope/weights, ordered thresholds, pre-later-outcome information sigma-field, and terminal evidence state. It must distinguish realized-rule claims, repeated-procedure claims, and new claim objects created by changing comparator/loss/scope. It will give a method-agnostic first-true-null result, a correctly scoped UBOA composition proposition, three formal counterexamples, and a primary-source comparison covering Reality Check, SPA, fixed sequence/sequential rejection, selective inference, learn-then-test/risk control where aligned, forecast comparison, and self-normalized inference. It must state confidence-bound equivalence when it holds and place novelty in claim identity, terminal semantics, applicability, and evidence lifecycle.

## Workstream B: final-configuration end-to-end study

The transparent forecasting DGP is retained: `x_t` is a standardized dependent driver; `y_t=beta*x_{t-1}+epsilon_t`; predictions are `g*x_{t-1}`; comparator `g=0`; squared loss; validation selects the minimum validation MSE with lexicographic numeric-g tie break. Candidate pool is `g in {0,0.05,0.10,0.20,0.30,0.40}`. Exact selected-realization truth is computed as `(2*beta*g-g^2)/(1+beta^2)`.

The 144 frozen cells are the Cartesian product of six processes, two OOS lengths, six signals, and two innovation laws:

- processes: `AR_MILD(phi=.2)`, `AR_STRONG(phi=.8)`, `SEASONAL_AR(lag=12,coef=.65)`, `MULTISCALE_AR(phi=.35,seasonal_lag=12,seasonal_coef=.40)`, `BLOCK_VARIANCE(block=32,sigma_ratio=4)`, `MARKOV_VARIANCE(p00=.97,p11=.92,sigma0=1,sigma1=4)`;
- OOS `n in {128,512}`; validation length equals OOS length;
- `beta in {0,.05,.10,.18,.26,.40}`;
- innovations `GAUSSIAN` and standardized `T5`.

All cells use the frozen C2 chain. `beta in {0,.10}` cells receive 5,000 replications; all others receive 2,000. Seeds are fixed by the seed policy. Dedicated deterministic invalid fixtures are added for constant and nonfinite evidence but are not counted among the 144 stochastic cells. Raw records cannot be dropped. Required metrics are false promotion, exact depth recovery, at-least-positive recovery, underclaim, mean depth error, structural resolution, unresolved/C2-invalid rates, and recovery by truth distance to the nearest 0/2/5 boundary.

## Workstream C: baselines and ablations

C consumes the same B records. Frozen policies are: direct descriptive tier mapping; three separate nominal .05 C2 tests without ordered stopping; UBOA fixed sequence+C2; one-sided C2 inversion/confidence-bound analogue using the same statistic and reference; always-abstain conservative utility baseline; comparator-equal generic-test routing; and native-question pool-level Reality Check/SPA only where its estimand is meaningful. It also ablates structural routing, invalid-evidence routing, ordered stopping, fixed claim identity, and outcome isolation. Pool-level methods must not be forced into UBOA terminal depths. Statistical false promotions and semantic-state errors are separate outcomes.

## Workstream D: blind external stress and power

A separate challenge designer must seal the exact implementation before any new D result is inspected. The frozen families are: ARMA(2,1) `(phi1=.55,phi2=-.20,theta=.35)`; SAR(1)xSAR(1) at lag 12 `(phi=.35,Phi=.55)`; GARCH(1,1) `(omega=.05,alpha=.08,beta=.87)`; two-state Markov variance `(p00=.97,p11=.92,sigma=(1,4))`; threshold AR `(phi_negative=.35,phi_positive=.75)`; AR(1) `.6` with standardized t7; ARFIMA-like fractional noise `d=.35` (out of scope); and local-to-unity/nonstationary `rho=.995` plus deterministic drift `.002*t/sqrt(n)` (out of scope). Lengths are 256, 512, 1024. Relative effects are `0,.005,.01,.02,.03,.05,.07,.10`. Null cells use 2,000 replications and positive-effect cells 1,000. The same C2 method is evaluated without retuning. In-scope and deliberate out-of-scope results are reported separately.

## Workstream E: prospective real cohort

Exactly six outcome-blind, CC-BY-4.0 UCI applications are frozen because their exact names had no hit in the pre-Stage-36 repository history and their official pages supplied identity, license, temporal structure, and instance counts before numerical outcomes were opened:

| ID | Stratum | Official instances | Target | Comparator | Loss | frequency / seasonal lag |
|---|---|---:|---|---|---|---|
| UCI374_APPLIANCES | multivariate building energy | 19,735 | Appliances | seasonal naive | MAE | 10-minute / 144 |
| UCI501_BEIJING_PM25 | multisite panel sensor | 420,768 (12 x 35,064) | PM2.5 aggregated across stations per origin | last value | MAE | hourly / none |
| UCI275_BIKE_HOURLY | univariate seasonal demand | 17,379 primary hourly rows | cnt | seasonal naive | MAE | hourly / 24 |
| UCI235_HOUSEHOLD_POWER | multivariate household power | 2,075,259 minute rows, hourly aggregation | Global_active_power | seasonal naive | MSE | minute to hourly / 24 |
| UCI360_AIR_QUALITY_CO | multivariate environmental sensor | 9,358 | CO(GT) | last value | MSE | hourly / none |
| UCI492_METRO_TRAFFIC | univariate traffic demand | 48,204 | traffic_volume | seasonal naive | MSE | hourly / 24 |

Canonical order is the table order. Each source uses the official UCI static-public archive for the recorded dataset ID. Downloading an opaque archive is not a numerical OOS read; numerical decoding is permitted only for the chronological prefix through the fixed validation boundary. Each primary series (or each Beijing station) is split by row identity: first 60% train, next 20% validation, final 20% sealed OOS. The split counts are computed solely from the official instance count (or 35,064 per Beijing station) by floor. Any format/count mismatch is a hold, not a changed boundary. No OOS suffix is extracted or semantically decoded. All terminal evaluations, if later authorized, use the first 1,024 complete origins after the fixed OOS boundary, with origin stride 1 and a gap equal to maximum forecast horizon.

Horizons are `(1,6,24)` after frequency normalization; Appliances uses `(1,6,18)` at 10-minute frequency. Loss is averaged over fixed horizons and, for Beijing, over the 12 station members at each time origin. Multiple series are never flattened into independent origins. Missing values are converted from documented sentinels, then causal forward fill within the decoded prefix only; a target with more than 20% missing validation origins is held.

Every pool contains the comparator, `MEAN_LAST3_V1`, `RIDGE_AR_V1`, and a genuinely learned `DLINEAR_CLASS_V1`. A `PATCHTST_CLASS_TINY_V1` candidate is additionally included for UCI374, UCI275, UCI360, and UCI492; it is excluded from UCI501 because the panel/missingness interface is not supported and from UCI235 because minute-source aggregation plus CPU-only budget exceeds the sealed training budget. Lookback is 48 normalized steps (Appliances 144); ridge alpha is 1.0; DLinear trains at most 4,096 deterministic evenly spaced train windows for 20 epochs, Adam lr .001, batch 128; tiny PatchTST uses patch 8/stride 4, d_model 16, one 2-head encoder layer, at most 4,096 train windows, 12 epochs, Adam lr .001, batch 128. Checkpoint is the last epoch; there is no manual early stopping. Validation selects minimum aggregate primary loss; ties within `1e-12` use candidate ID ordering. Candidate/model seeds are fixed before data access.

For every nonstructural selection, the validation-side descriptor-to-generator mapping is frozen: AR coefficient is clipped lag-1 ACF; seasonal coefficient is clipped fixed-season ACF; block-variance ratio is clipped to `[1,9]` with block length 32; multiscale combines half-strength clipped AR and seasonal coefficients. Each of four generator families is crossed with Gaussian/t5 innovations and all three thresholds: 24 null cells at n=1024, 2,000 replications each. The common pass rule is zero invalid C2 results, all 24 rejection rates <=.075, at least 23/24 <=.065, and a six-cell short-n check at n=512 with maximum <=.075. Positive-effect diagnostics use `.005,.02,.05,.075`, all four families, 1,000 replications. They cannot rescue a null-calibration failure. A statistical entry is OOS-ready only if it passes; structural selections terminate structurally; format, license, insufficient-origin, missingness, or local-validity failures are held without replacement.

## Workstream F: design sensitivity

Frozen same-claim evidence variations are sample length `{128,512}`, dependence `{.2,.8}`, variance geometry `{constant,block}`, and training/selection seed `{0,1}` conditional on identical selected realization. Frozen claim-changing variations are comparator `g=0` versus `.05`, MSE versus MAE, full versus first-half horizon/member scope, threshold ladder `(0,.02,.05)` versus `(0,.01,.03)`, and candidate pool full versus `{0,.10,.30}`. Thirty-two base worlds use beta `{.10,.18,.26,.40}` and 1,000 replications. Reports must separately mark claim identity change, truth-depth change, evidence-only terminal change, false promotion, and underclaim.

## Integration and decisions

Every frozen cell and application remains in the result registry. No benchmark, process, comparator, loss, threshold, pass rule, or model may be replaced because of results. The manuscript baseline is not overwritten; pre-OOS prose/figure candidates live only under `90_integration/manuscript_candidates/`. Integration answers the eight reviewer questions listed in the takeover prompt and produces exactly one cohort OOS packet.

The only legal final pre-OOS statuses are the eight statuses in the takeover prompt. `PASS_PARALLEL_STRONG_ACCEPT_PREOOS_PROGRAM_READY_FOR_COHORT_OOS_HUMAN_GATE` requires all six applications either structurally complete or statistically ready. `PASS_PARALLEL_STRONG_ACCEPT_PREOOS_PROGRAM_PARTIAL_COHORT_READY_FOR_OOS_REVIEW` is used when at least one clean entry is ready and all other frozen entries are transparently held. Integrity or inherited-state conflicts dominate all pass statuses.

