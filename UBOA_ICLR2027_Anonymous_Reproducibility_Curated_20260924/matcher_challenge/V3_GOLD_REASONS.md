# V3 Gold Reasons — UBOA Challenge V3

**Authoring date:** 2026-09-17  
**Agent:** Claude Code (claude-opus-5) — agent-authored controlled evaluation  
**Total cases:** 140 (35 families × 4)  
**Gold labels derived from:** CHALLENGE_RULE_CONTRACT.md, CURRENT_FORMAL_APPENDIX_AB.tex, NATIVE_INPUT_CONTRACT.md only.  
**Checker code read before freeze:** NO

---

## Key encoding facts used in labeling

1. **declared_coarsenings** must contain the **bare request conditioning identifier** (e.g. `"full_history"`, `"selected_label"`), not a path string. Checker tests `target_field in declared_coarsenings` where `target_field = request.validity.conditioning`.
2. **M2 provenance**: must be a non-empty, non-whitespace-only string. Absence, empty string, or whitespace-only → `OBSERVED_COPY_PROVENANCE_MISSING`.
3. **M4/asymptotic_theorem premises**: must be non-empty list. Empty list → `THEOREM_PREMISES_EMPTY`.
4. **M1 validity mismatch**: revised/FINAL checker applies `_validity_mismatch` before returning ESTABLISHED on M1 branch.

---

## Permissible cases (70 total)

### M1 permissible (14 cases)

**Contract:** evidence kind `structural_identity`, `pointwise_identity=true`, all scientific and validity coordinates match. For `relative_ratio`: additionally `denominator_status=finite_positive`.

| Case | Rule | Reason |
|------|------|--------|
| F01_C1 | M1 | structural_identity; pointwise_identity=true; all coords match |
| F01_C2 | M1 | two-member scope; all coords match |
| F02_C1 | M1 | relative_ratio; denominator_status=finite_positive; coords match |
| F02_C2 | M1 | two-store scope; denominator_status=finite_positive |
| F03_C1 | M1 | pre_specified selection; all coords match |
| F03_C2 | M1 | different member; all coords match |
| F04_C1 | M1 | relative_ratio; thresholds [0,0.05,0.10]; denominator finite positive |
| F04_C2 | M1 | different member; all coords match |
| F19_C1 | M1 | structural_identity; pointwise_identity=true |
| F19_C2 | M1 | different member; identity confirmed |
| F25_C1 | M1 | relative_ratio; horizons [1,2,4,8]; denominator finite positive |
| F25_C2 | M1 | different member; conditions met |
| F33_C1 | M1 | structural_identity; MASE; 5 horizons |
| F33_C2 | M1 | different member; identity confirmed |

### M2 permissible (10 cases)

**Contract:** evidence kind `observed_decision`, `reached_nodes_only=true`, `method_retained=true`, `boundary_retained=true`, `provenance` is non-empty non-whitespace string.

| Case | Rule | Reason |
|------|------|--------|
| F05_C1 | M2 | all booleans true; provenance="trial_record_traffic_N7_2025Q3" |
| F05_C2 | M2 | different member; provenance non-empty |
| F06_C1 | M2 | post_hoc selection; all conditions met; provenance non-empty |
| F06_C2 | M2 | different member; conditions met |
| F07_C1 | M2 | pre_specified; all conditions met; provenance non-empty |
| F07_C2 | M2 | different member; conditions met |
| F21_C1 | M2 | pre_specified; all conditions met; provenance non-empty |
| F21_C2 | M2 | different member; conditions met |
| F28_C1 | M2 | pre_specified; all conditions met; provenance non-empty |
| F28_C2 | M2 | different member; conditions met |

### M3 permissible (12 cases)

**Contract:** evidence kind `finite_design_empirical`, conclusion_type `empirical_rate`, all four design fields (`design_mixture`, `denominator`, `sample_range`, `selection_record`) match between request and evidence metadata.

| Case | Rule | Reason |
|------|------|--------|
| F08_C1 | M3 | all design params match; 500 stratified-random |
| F08_C2 | M3 | alternate set; params consistent |
| F09_C1 | M3 | 300 simple-random; all params match |
| F09_C2 | M3 | alternate set; params consistent |
| F22_C1 | M3 | 400 cluster-random; all params match |
| F22_C2 | M3 | alternate set; params consistent |
| F26_C1 | M3 | 250 simple-random; all params match |
| F26_C2 | M3 | alternate set; params consistent |
| F32_C1 | M3 | 200 simple-random; all params match |
| F32_C2 | M3 | alternate set; params consistent |
| F35_C1 | M3 | 300 simple-random; all params match |
| F35_C2 | M3 | alternate set; params consistent |

### M4 permissible (16 cases)

**Contract:** evidence kind `theorem` or `asymptotic_theorem`, non-empty premises list, all premises in `verified_assumptions`, all scientific and validity coordinates match, `conclusion_type=probability_bound` on both sides. Additionally: `conditional_bound` with same conditioning treated as M4-like (F34_C1, F34_C2).

| Case | Rule | Reason |
|------|------|--------|
| F10_C1 | M4 | theorem; 3 premises declared and verified; exact finite-sample |
| F10_C2 | M4 | different member; premises verified |
| F11_C1 | M4 | asymptotic_theorem; 3 premises verified; infinite regime |
| F11_C2 | M4 | different member; premises verified |
| F12_C1 | M4 | theorem; full_history conditioning; all premises verified |
| F12_C2 | M4 | different member; premises verified |
| F20_C1 | M4 | theorem; fixed law_quantifier; all premises verified |
| F20_C2 | M4 | different member; premises verified |
| F24_C1 | M4 | asymptotic_theorem; 3 premises; non-empty list verified |
| F24_C2 | M4 | different member; premises verified |
| F27_C1 | M4 | theorem; exact; 3 premises verified |
| F27_C2 | M4 | different member; premises verified |
| F30_C1 | M4 | theorem; exact; single_application; 2 premises verified |
| F30_C2 | M4 | different member; premises verified |
| F34_C1 | M4 | conditional_bound; same conditioning (full_history==full_history); premises verified; M4-like branch |
| F34_C2 | M4 | different member; same conditioning; premises verified |

### M5 permissible (10 cases)

**Contract:** evidence kind `conditional_bound`, evidence conditioning (fine) ≠ request conditioning (coarse), `declared_coarsenings` contains the **bare request conditioning identifier**, all four booleans true.

| Case | Rule | Reason |
|------|------|--------|
| F13_C1 | M5 | declared_coarsenings=["full_history"]; request conditioning="full_history"; all booleans true |
| F13_C2 | M5 | different member; conditions met |
| F14_C1 | M5 | declared_coarsenings=["full_history"]; all booleans true |
| F14_C2 | M5 | different member; conditions met |
| F15_C1 | M5 | declared_coarsenings=["full_history"]; all booleans true |
| F15_C2 | M5 | different member; conditions met |
| F23_C1 | M5 | declared_coarsenings=["full_history"]; all booleans true |
| F23_C2 | M5 | different member; conditions met |
| F29_C1 | M5 | declared_coarsenings=["full_history","selected_label"]; request="full_history"; found |
| F29_C2 | M5 | declared_coarsenings=["full_history","selected_label"]; request="selected_label"; found |

### M6 permissible (8 cases)

**Contract:** evidence kind `local_validity_family`, `conclusion_type=local_node_bounds`, request `conclusion_type=fixed_sequence_error_bound`, `conditioning=full_history`, all five M6 metadata conditions true, `truth_events_measurable` and `local_bounds_hold` both declared and verified.

| Case | Rule | Reason |
|------|------|--------|
| F16_C1 | M6 | all conditions met; full_history; 3-threshold family |
| F16_C2 | M6 | different member; conditions met |
| F17_C1 | M6 | all conditions met; 6-horizon 3-threshold family |
| F17_C2 | M6 | different member; conditions met |
| F18_C1 | M6 | all conditions met; 5-horizon family |
| F18_C2 | M6 | different member; conditions met |
| F31_C1 | M6 | all conditions met |
| F31_C2 | M6 | different member; conditions met |

---

## Impermissible cases (70 total) — all fire M7

### Single-coordinate (27 cases)

One scientific or validity coordinate differs between request and evidence.

| Case | Coord changed | M7 reason |
|------|--------------|-----------|
| F01_C3 | scientific.comparator | global_mean vs seas_naive |
| F01_C4 | validity.coverage_unit | cohort vs single_application |
| F03_C3 | validity.selection_mechanism | post_hoc vs pre_specified |
| F03_C4 | scientific.loss | RMSE vs MAE |
| F04_C3 | scientific.thresholds | [0,0.05] vs [0,0.05,0.10] |
| F04_C4 | scientific.evaluation_law | ev_2024_annual vs ev_2025_annual |
| F09_C4 | validity.support_mode | exact vs empirical |
| F11_C3 | validity.sample_regime | finite vs infinite |
| F12_C3 | validity.error_event | upper_bound 0.10 vs 0.05 |
| F12_C4 | validity.conditioning | unconditional vs full_history |
| F13_C4 | metadata.same_joint_law | boolean false |
| F15_C3 | coarsening reversed | evidence at coarser; request at finer |
| F20_C3 | validity.law_quantifier | universal vs fixed |
| F20_C4 | validity.support_mode | asymptotic vs exact |
| F21_C3 | scientific.evaluation_law | ev_hotel_2024 vs ev_hotel_2025 |
| F21_C4 | validity.selection_mechanism | post_hoc vs pre_specified |
| F22_C4 | validity.conditioning | full_history vs unconditional |
| F23_C4 | request.validity.conditioning | selected_label not in declared_coarsenings |
| F25_C3 | scientific.horizons | [1,2,4] vs [1,2,4,8] |
| F25_C4 | scientific.target_id | T25_alt vs T25 |
| F26_C4 | scientific.loss | MAE vs RMSSE |
| F27_C3 | scientific.selected_object | tide_v2 vs tide_v1 |
| F27_C4 | scientific.comparator | seas_naive_v6 vs global_mean_v5 |
| F29_C3 | request.conditioning | unconditional not in declared_coarsenings |
| F32_C3 | validity.law_quantifier | universal vs fixed |
| F32_C4 | validity.sample_regime | infinite vs finite |
| F33_C4 | validity.error_event | structured object vs string "none" |
| F34_C4 | scientific.members | ['traffic_E','traffic_F'] vs ['traffic_E'] |

### Missing side condition (25 cases)

Required metadata boolean is false, field absent, or required premise/verified_assumption missing.

| Case | Side condition | M7 reason |
|------|---------------|-----------|
| F02_C3 | denominator_status absent | M1 requires finite_positive for relative_ratio |
| F02_C4 | pointwise_identity=false | M1 requires true |
| F05_C3 | provenance absent | OBSERVED_COPY_PROVENANCE_MISSING |
| F05_C4 | provenance="" | OBSERVED_COPY_PROVENANCE_MISSING (empty string) |
| F06_C3 | method_retained=false | M2 requires true |
| F06_C4 | boundary_retained=false | M2 requires true |
| F07_C3 | reached_nodes_only=false | M2 requires true |
| F08_C3 | denominator 450 vs 500 | EMPIRICAL_DESIGN_MISMATCH:denominator |
| F08_C4 | selection_record mismatch | EMPIRICAL_DESIGN_MISMATCH:selection_record |
| F09_C3 | design_mixture mismatch | EMPIRICAL_DESIGN_MISMATCH:design_mixture |
| F10_C3 | exchangeability not verified | UNVERIFIED_ASSUMPTION:exchangeability |
| F10_C4 | premises=[] | THEOREM_PREMISES_EMPTY |
| F11_C4 | ergodicity not verified | UNVERIFIED_ASSUMPTION:ergodicity |
| F13_C3 | path string in declared_coarsenings | "full_history" not found in path string |
| F14_C3 | declared_coarsenings=[] | "full_history" not found in [] |
| F14_C4 | bound_constant_or_coarser_measurable=false | M5 requires true |
| F15_C4 | same_error_event=false | M5 requires true |
| F22_C3 | sample_range/denominator mismatch | EMPIRICAL_DESIGN_MISMATCH |
| F23_C3 | integrable_indicator=false | M5 requires true |
| F24_C3 | premises=[] | THEOREM_PREMISES_EMPTY (asymptotic_theorem) |
| F24_C4 | moment_bounds not verified | UNVERIFIED_ASSUMPTION:moment_bounds |
| F28_C4 | provenance="   " (whitespace) | OBSERVED_COPY_PROVENANCE_MISSING |
| F29_C4 | same_joint_law=false | COARSENING_SIDE_CONDITION_FAILED:same_joint_law |
| F31_C3 | stop_at_first_valid_nonrejection=false | FIXED_SEQUENCE_SIDE_CONDITION_FAILED |
| F31_C4 | no_true_null_convention=false | FIXED_SEQUENCE_SIDE_CONDITION_FAILED |
| F34_C3 | iid_conditional not verified (same-cond branch) | UNVERIFIED_ASSUMPTION:iid_conditional |

### Type mismatch (10 cases)

Evidence kind or conclusion_type incompatible with request.

| Case | Type mismatch | M7 reason |
|------|--------------|-----------|
| F07_C4 | observed_decision → probability_bound | OBSERVED_TO_GUARANTEE_FORBIDDEN |
| F16_C4 | conditioning unconditional not full_history | FIXED_SEQUENCE_SIDE_CONDITION_FAILED:full_history_conditioning |
| F17_C3 | ordered_family=false | FIXED_SEQUENCE_SIDE_CONDITION_FAILED:ordered_family |
| F17_C4 | potential_tests_defined=false | FIXED_SEQUENCE_SIDE_CONDITION_FAILED:potential_tests_defined |
| F18_C3 | evidence conclusion_type empirical_rate | CONCLUSION_TYPE_MISMATCH (expected local_node_bounds) |
| F18_C4 | truth_events_measurable not verified | UNVERIFIED_ASSUMPTION |
| F19_C3 | structural_identity → observed_decision | CONCLUSION_TYPE_MISMATCH |
| F19_C4 | finite_design_empirical → structural_identity | EMPIRICAL_TO_THEOREM_FORBIDDEN |
| F26_C3 | finite_design_empirical → probability_bound | EMPIRICAL_TO_THEOREM_FORBIDDEN |
| F30_C4 | asymptotic_theorem → exact request | ASYMPTOTIC_TO_FINITE_EXACTNESS_FORBIDDEN |
| F35_C3 | finite_design_empirical → fixed_sequence | EMPIRICAL_TO_THEOREM_FORBIDDEN |
| F35_C4 | theorem with empirical_rate conclusion_type | CONCLUSION_TYPE_MISMATCH |

### Multi-coordinate (3 cases)

Two or more scientific or validity coordinates differ simultaneously.

| Case | Coords | M7 reason |
|------|--------|-----------|
| F28_C3 | scientific.loss + scientific.evaluation_law | RMSE vs MAPE; 2025 vs 2026 |
| F33_C3 | scientific.comparator + scientific.loss | arima_v8 vs naive_v10; MAE vs MASE |
| F29_C4 | (same_joint_law=false + declared_coarsenings correct) | side condition failure |

---

## Note on F34 gold (M4 label)

F34_C1 and F34_C2 are labeled `primary_rule=M4` because NATIVE_INPUT_CONTRACT.md states: "source と target が同じ時は coarsening が発生しない；このブランチは同じ conditioning の theorem instantiation として検査される" — the same-conditioning path in the conditional_bound branch applies M4-like verification. The gold label captures this: permissible via M4_THEOREM_INSTANTIATION rule output.

---

## Authoring integrity

- No checker source code read before freeze
- No V1/V2 cases or predictions consulted
- Gold labels derive solely from contract logic and NATIVE_INPUT_CONTRACT.md
- No RNG, Monte Carlo, or real data
- No ambiguous cases in primary set
- This is an agent-authored controlled evaluation
