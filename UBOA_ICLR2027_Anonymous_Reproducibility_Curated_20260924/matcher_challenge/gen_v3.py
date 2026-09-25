#!/usr/bin/env python3
"""
UBOA Challenge V3 — deterministic generator. 140 cases, 35 families x 4.
Key fix: declared_coarsenings contains bare request conditioning identifier.
No checker code read before freeze.
"""
import json, copy

OUT = "CHALLENGE_V3_FROZEN.jsonl"

def m(obj, path, val):
    o = copy.deepcopy(obj)
    keys = path.split(".")
    d = o
    for k in keys[:-1]: d = d[k]
    d[keys[-1]] = val
    return o

def sc(tid,sel,comp,loss,members,horizons,weights,law,thresh):
    return {"target_id":tid,"selected_object":sel,"comparator":comp,"loss":loss,
            "members":members,"horizons":horizons,"weights":weights,
            "evaluation_law":law,"thresholds":thresh}

def vc(event,cond,lq,cu,sm,sr,sel):
    return {"error_event":event,"conditioning":cond,"law_quantifier":lq,
            "coverage_unit":cu,"support_mode":sm,"sample_regime":sr,
            "selection_mechanism":sel}

def ev(eid,kind,ctype,sci,val,prem,ver,meta):
    return {"evidence_id":eid,"kind":kind,"conclusion_type":ctype,
            "scientific":sci,"validity":val,"premises":prem,
            "verified_assumptions":ver,"metadata":meta}

def rq(rid,ctype,sci,val,meta=None):
    r={"request_id":rid,"conclusion_type":ctype,"scientific":sci,"validity":val}
    if meta: r["metadata"]=meta
    return r

def case(cid,fid,desc,req,evid,disp,rule,gold,mut):
    return {"case_id":cid,"family_id":fid,"scenario_description":desc,
            "request":req,"evidence":evid,"expected_disposition":disp,
            "primary_rule":rule,"gold_reason":gold,"mutation":mut}

def mut(base,cat,paths,reason):
    return {"base_case_id":base,"category":cat,"changed_paths":paths,"reason":reason}

cases = []

# ===========================================================================
# F01 — M1 structural_identity, MAE, validity-coord check
# ===========================================================================
S01=sc("T01","ridge_ar","seas_naive","MAE",["grid_A"],[1],[1.0],"ev_2025Q4",[])
V01=vc("none","unconditional","fixed","single_application","exact","finite","none")
cases.append(case("F01_C1","F01",
  "Hypothetical: ridge_ar and seas_naive produce byte-for-byte identical 1-step demand predictions on grid_A, 2025-Q4 holdout. Author claims structural identity under MAE.",
  rq("R01_C1","structural_identity",S01,V01),
  ev("E01_C1","structural_identity","structural_identity",S01,V01,
     ["predictors evaluated on identical inputs"],["predictors evaluated on identical inputs"],
     {"pointwise_identity":True}),
  "permissible","M1",
  "M1: pointwise_identity=true; all scientific and validity coordinates match; structural identity licensed.",
  mut(None,"base",[],"")))

S01b=sc("T01","ridge_ar","seas_naive","MAE",["grid_A","grid_B"],[1],[0.5,0.5],"ev_2025Q4",[])
cases.append(case("F01_C2","F01",
  "Hypothetical: Same systems on two-region scope; identity holds for both. Equal weights.",
  rq("R01_C2","structural_identity",S01b,V01),
  ev("E01_C2","structural_identity","structural_identity",S01b,V01,
     ["predictors evaluated on identical inputs"],["predictors evaluated on identical inputs"],
     {"pointwise_identity":True}),
  "permissible","M1",
  "M1: two-member scope; request and evidence match; pointwise_identity=true.",
  mut("F01_C1","variant",["scientific.members","scientific.weights"],"")))

cases.append(case("F01_C3","F01",
  "Hypothetical: Evidence comparator is global_mean but request comparator is seas_naive; single scientific coordinate mismatch.",
  rq("R01_C3","structural_identity",S01,V01),
  ev("E01_C3","structural_identity","structural_identity",m(S01,"comparator","global_mean"),V01,
     ["predictors evaluated on identical inputs"],["predictors evaluated on identical inputs"],
     {"pointwise_identity":True}),
  "impermissible","M7",
  "M7: comparator mismatch (global_mean vs seas_naive); single scientific coordinate changed.",
  mut("F01_C1","single_coordinate",["evidence.scientific.comparator"],"comparator changed")))

V01_coh=vc("none","unconditional","fixed","cohort","exact","finite","none")
cases.append(case("F01_C4","F01",
  "Hypothetical: Evidence coverage_unit is cohort but request is single_application; M1 must pass validity mismatch check.",
  rq("R01_C4","structural_identity",S01,V01),
  ev("E01_C4","structural_identity","structural_identity",S01,V01_coh,
     ["predictors evaluated on identical inputs"],["predictors evaluated on identical inputs"],
     {"pointwise_identity":True}),
  "impermissible","M7",
  "M7: validity.coverage_unit mismatch (cohort vs single_application); single validity coordinate changed.",
  mut("F01_C1","single_coordinate",["evidence.validity.coverage_unit"],"coverage_unit changed to cohort")))

# ===========================================================================
# F02 — M1 relative_ratio, denominator check
# ===========================================================================
S02=sc("T02","lstm_v1","naive_v1","RMSE",["store_1"],[1,2,3],[1/3,1/3,1/3],"ev_2025H1",[0.0,0.05])
V02=vc("none","unconditional","fixed","single_application","exact","finite","none")
M02_ok={"pointwise_identity":True,"denominator_status":"finite_positive"}
cases.append(case("F02_C1","F02",
  "Hypothetical: LSTM v1 vs naive v1 on store_1, RMSE, horizons 1-3; identical outputs; comparator RMSE is finite positive. Author claims >0% and >5% relative improvement.",
  rq("R02_C1","relative_ratio",S02,V02),
  ev("E02_C1","structural_identity","structural_identity",S02,V02,
     ["predictions identical","comparator RMSE finite positive"],
     ["predictions identical","comparator RMSE finite positive"],M02_ok),
  "permissible","M1",
  "M1: pointwise_identity=true, denominator_status=finite_positive; all coordinates match; relative ratio licensed.",
  mut(None,"base",[],"")))

S02b=sc("T02","lstm_v1","naive_v1","RMSE",["store_1","store_2"],[1,2,3],[1/6,1/6,1/6,1/6,1/6,1/6],"ev_2025H1",[0.0,0.05])
cases.append(case("F02_C2","F02",
  "Hypothetical: Same systems, two-store scope, equal weights; identity confirmed, comparator finite positive.",
  rq("R02_C2","relative_ratio",S02b,V02),
  ev("E02_C2","structural_identity","structural_identity",S02b,V02,
     ["predictions identical","comparator RMSE finite positive"],
     ["predictions identical","comparator RMSE finite positive"],M02_ok),
  "permissible","M1",
  "M1: two-member scope; all coordinates match; relative ratio licensed.",
  mut("F02_C1","variant",["scientific.members","scientific.weights"],"")))

cases.append(case("F02_C3","F02",
  "Hypothetical: denominator_status absent from evidence metadata; ratio cannot be confirmed valid.",
  rq("R02_C3","relative_ratio",S02,V02),
  ev("E02_C3","structural_identity","structural_identity",S02,V02,
     ["predictions identical"],["predictions identical"],
     {"pointwise_identity":True}),
  "impermissible","M7",
  "M7/missing_side_condition: denominator_status absent; M1 requires finite_positive denominator for relative_ratio.",
  mut("F02_C1","missing_side_condition",["evidence.metadata.denominator_status"],"denominator_status removed")))

cases.append(case("F02_C4","F02",
  "Hypothetical: pointwise_identity=false; predictions differ on one timestep; structural identity not licensed.",
  rq("R02_C4","relative_ratio",S02,V02),
  ev("E02_C4","structural_identity","structural_identity",S02,V02,
     ["predictions identical"],["predictions identical"],
     {"pointwise_identity":False,"denominator_status":"finite_positive"}),
  "impermissible","M7",
  "M7/missing_side_condition: pointwise_identity=false; M1 cannot license structural identity or relative ratio.",
  mut("F02_C1","missing_side_condition",["evidence.metadata.pointwise_identity"],"pointwise_identity false")))

# ===========================================================================
# F03 — M1 structural_identity, selection_mechanism validity mismatch
# ===========================================================================
S03=sc("T03","xgb_v1","arima_v1","MAE",["sku_A"],[1,2],[0.5,0.5],"ev_2026Q1",[])
V03_pre=vc("none","unconditional","fixed","single_application","exact","finite","pre_specified")
V03_post=vc("none","unconditional","fixed","single_application","exact","finite","post_hoc")

cases.append(case("F03_C1","F03",
  "Hypothetical: XGBoost v1 and ARIMA v1 produce identical 2-step SKU predictions on a pre-specified 2026-Q1 holdout. Author claims structural identity under MAE.",
  rq("R03_C1","structural_identity",S03,V03_pre),
  ev("E03_C1","structural_identity","structural_identity",S03,V03_pre,
     ["predictions identical"],["predictions identical"],{"pointwise_identity":True}),
  "permissible","M1",
  "M1: all scientific and validity coordinates match including selection_mechanism=pre_specified; pointwise_identity=true.",
  mut(None,"base",[],"")))

cases.append(case("F03_C2","F03",
  "Hypothetical: Same systems on sku_B; pre_specified selection; identity confirmed.",
  rq("R03_C2","structural_identity",m(S03,"members",["sku_B"]),V03_pre),
  ev("E03_C2","structural_identity","structural_identity",m(S03,"members",["sku_B"]),V03_pre,
     ["predictions identical"],["predictions identical"],{"pointwise_identity":True}),
  "permissible","M1","M1: different member; all coordinates match.",
  mut("F03_C1","variant",["scientific.members"],"")))

cases.append(case("F03_C3","F03",
  "Hypothetical: Request selection_mechanism is pre_specified but evidence is post_hoc; single validity coordinate mismatch.",
  rq("R03_C3","structural_identity",S03,V03_pre),
  ev("E03_C3","structural_identity","structural_identity",S03,V03_post,
     ["predictions identical"],["predictions identical"],{"pointwise_identity":True}),
  "impermissible","M7",
  "M7: validity.selection_mechanism mismatch (post_hoc vs pre_specified); single validity coordinate changed.",
  mut("F03_C1","single_coordinate",["evidence.validity.selection_mechanism"],"selection_mechanism changed")))

cases.append(case("F03_C4","F03",
  "Hypothetical: Evidence loss is RMSE but request loss is MAE; single scientific coordinate mismatch.",
  rq("R03_C4","structural_identity",S03,V03_pre),
  ev("E03_C4","structural_identity","structural_identity",m(S03,"loss","RMSE"),V03_pre,
     ["predictions identical"],["predictions identical"],{"pointwise_identity":True}),
  "impermissible","M7",
  "M7: scientific.loss mismatch (RMSE vs MAE); single scientific coordinate changed.",
  mut("F03_C1","single_coordinate",["evidence.scientific.loss"],"loss changed to RMSE")))

# ===========================================================================
# F04 — M1 relative_ratio, thresholds and evaluation_law mismatches
# ===========================================================================
S04=sc("T04","nhits_v1","ses_v1","MAPE",["region_X"],[1,4,8,12],[0.25,0.25,0.25,0.25],"ev_2025_annual",[0.0,0.05,0.10])
V04=vc("none","unconditional","fixed","single_application","exact","finite","none")
M04={"pointwise_identity":True,"denominator_status":"finite_positive"}

cases.append(case("F04_C1","F04",
  "Hypothetical: N-HiTS v1 and SES v1 produce identical annual forecasts for region_X on a fixed 2025 holdout. Comparator MAPE is finite positive. Author claims >0%, >5%, >10% relative improvement.",
  rq("R04_C1","relative_ratio",S04,V04),
  ev("E04_C1","structural_identity","structural_identity",S04,V04,
     ["predictions identical","comparator MAPE finite positive"],
     ["predictions identical","comparator MAPE finite positive"],M04),
  "permissible","M1","M1: all coordinates match; denominator finite positive; relative ratio licensed.",
  mut(None,"base",[],"")))

cases.append(case("F04_C2","F04",
  "Hypothetical: Same systems region_Y; same evaluation law and thresholds; identity confirmed.",
  rq("R04_C2","relative_ratio",m(S04,"members",["region_Y"]),V04),
  ev("E04_C2","structural_identity","structural_identity",m(S04,"members",["region_Y"]),V04,
     ["predictions identical","comparator MAPE finite positive"],
     ["predictions identical","comparator MAPE finite positive"],M04),
  "permissible","M1","M1: different member; coordinates match; licensed.",
  mut("F04_C1","variant",["scientific.members"],"")))

cases.append(case("F04_C3","F04",
  "Hypothetical: Evidence thresholds are [0.0,0.05] but request thresholds are [0.0,0.05,0.10]; single scientific coordinate mismatch.",
  rq("R04_C3","relative_ratio",S04,V04),
  ev("E04_C3","structural_identity","structural_identity",m(S04,"thresholds",[0.0,0.05]),V04,
     ["predictions identical","comparator MAPE finite positive"],
     ["predictions identical","comparator MAPE finite positive"],M04),
  "impermissible","M7",
  "M7: scientific.thresholds mismatch ([0.0,0.05] vs [0.0,0.05,0.10]); single scientific coordinate changed.",
  mut("F04_C1","single_coordinate",["evidence.scientific.thresholds"],"top threshold removed")))

cases.append(case("F04_C4","F04",
  "Hypothetical: Evidence evaluation_law is ev_2024_annual but request is ev_2025_annual; single scientific coordinate mismatch.",
  rq("R04_C4","relative_ratio",S04,V04),
  ev("E04_C4","structural_identity","structural_identity",m(S04,"evaluation_law","ev_2024_annual"),V04,
     ["predictions identical","comparator MAPE finite positive"],
     ["predictions identical","comparator MAPE finite positive"],M04),
  "impermissible","M7",
  "M7: evaluation_law mismatch (ev_2024_annual vs ev_2025_annual); single scientific coordinate changed.",
  mut("F04_C1","single_coordinate",["evidence.scientific.evaluation_law"],"evaluation_law changed")))

# ===========================================================================
# F05 — M2 observed_decision, provenance required (FINAL_MATCHER fix)
# ===========================================================================
S05=sc("T05","prophet_v1","naive_v1","MAE",["traffic_N7"],[1,7],[0.5,0.5],"ev_2025Q3",[])
V05=vc("none","unconditional","fixed","single_application","exact","finite","pre_specified")
M05_ok={"reached_nodes_only":True,"method_retained":True,"boundary_retained":True,
        "provenance":"trial_record_traffic_N7_2025Q3"}

cases.append(case("F05_C1","F05",
  "Hypothetical: Prophet v1 vs naive v1 on traffic node N7, MAE, horizons 1 and 7. Pre-specified trial executed; decision record retains method, boundary, provenance.",
  rq("R05_C1","observed_decision",S05,V05),
  ev("E05_C1","observed_decision","observed_decision",S05,V05,
     [],["reached_nodes_only","method_retained","boundary_retained","provenance_recorded"],M05_ok),
  "permissible","M2",
  "M2: reached_nodes_only=true, method_retained=true, boundary_retained=true, provenance is non-empty string; literal decision licensed.",
  mut(None,"base",[],"")))

cases.append(case("F05_C2","F05",
  "Hypothetical: Same protocol on traffic node N8; all metadata present and correct.",
  rq("R05_C2","observed_decision",m(S05,"members",["traffic_N8"]),V05),
  ev("E05_C2","observed_decision","observed_decision",m(S05,"members",["traffic_N8"]),V05,
     [],["reached_nodes_only","method_retained","boundary_retained","provenance_recorded"],
     {"reached_nodes_only":True,"method_retained":True,"boundary_retained":True,
      "provenance":"trial_record_traffic_N8_2025Q3"}),
  "permissible","M2","M2: different member; all side conditions met; literal decision licensed.",
  mut("F05_C1","variant",["scientific.members"],"")))

cases.append(case("F05_C3","F05",
  "Hypothetical: provenance field is absent from evidence metadata. FINAL_MATCHER requires non-empty provenance string.",
  rq("R05_C3","observed_decision",S05,V05),
  ev("E05_C3","observed_decision","observed_decision",S05,V05,
     [],[],{"reached_nodes_only":True,"method_retained":True,"boundary_retained":True}),
  "impermissible","M7",
  "M7/missing_side_condition: provenance absent; FINAL_MATCHER requires non-empty provenance string for M2; OBSERVED_COPY_PROVENANCE_MISSING.",
  mut("F05_C1","missing_side_condition",["evidence.metadata.provenance"],"provenance removed")))

cases.append(case("F05_C4","F05",
  "Hypothetical: provenance is an empty string; FINAL_MATCHER rejects empty or whitespace-only provenance.",
  rq("R05_C4","observed_decision",S05,V05),
  ev("E05_C4","observed_decision","observed_decision",S05,V05,
     [],[],{"reached_nodes_only":True,"method_retained":True,"boundary_retained":True,
             "provenance":""}),
  "impermissible","M7",
  "M7/missing_side_condition: provenance is empty string; FINAL_MATCHER returns OBSERVED_COPY_PROVENANCE_MISSING for empty or whitespace-only provenance.",
  mut("F05_C1","missing_side_condition",["evidence.metadata.provenance"],"provenance emptied")))

# ===========================================================================
# F06 — M2 observed_decision, side-condition booleans
# ===========================================================================
S06=sc("T06","lgbm_v1","arima_v2","sMAPE",["hospital_H1"],[1,2,4,7],[0.25,0.25,0.25,0.25],"ev_2026H1",[])
V06=vc("none","unconditional","fixed","single_application","exact","finite","post_hoc")
M06={"reached_nodes_only":True,"method_retained":True,"boundary_retained":True,
     "provenance":"hosp_H1_trial_2026H1_audit_id"}

cases.append(case("F06_C1","F06",
  "Hypothetical: LightGBM v1 vs ARIMA v2 on hospital H1, sMAPE, 4 horizons. Post-hoc selection declared; all M2 side conditions satisfied.",
  rq("R06_C1","observed_decision",S06,V06),
  ev("E06_C1","observed_decision","observed_decision",S06,V06,[],[],M06),
  "permissible","M2","M2: all side conditions true; provenance non-empty; literal decision licensed.",
  mut(None,"base",[],"")))

cases.append(case("F06_C2","F06",
  "Hypothetical: Same protocol, hospital H2; all metadata present.",
  rq("R06_C2","observed_decision",m(S06,"members",["hospital_H2"]),V06),
  ev("E06_C2","observed_decision","observed_decision",m(S06,"members",["hospital_H2"]),V06,
     [],[],{"reached_nodes_only":True,"method_retained":True,"boundary_retained":True,
             "provenance":"hosp_H2_trial_2026H1_audit_id"}),
  "permissible","M2","M2: different member; all conditions met.",
  mut("F06_C1","variant",["scientific.members"],"")))

cases.append(case("F06_C3","F06",
  "Hypothetical: method_retained=false; procedure changed after decision was reached.",
  rq("R06_C3","observed_decision",S06,V06),
  ev("E06_C3","observed_decision","observed_decision",S06,V06,
     [],[],{"reached_nodes_only":True,"method_retained":False,"boundary_retained":True,
             "provenance":"hosp_H1_trial_2026H1_audit_id"}),
  "impermissible","M7",
  "M7/missing_side_condition: method_retained=false; M2 requires method retained unchanged.",
  mut("F06_C1","missing_side_condition",["evidence.metadata.method_retained"],"method_retained false")))

cases.append(case("F06_C4","F06",
  "Hypothetical: boundary_retained=false; decision boundary revised after evaluation.",
  rq("R06_C4","observed_decision",S06,V06),
  ev("E06_C4","observed_decision","observed_decision",S06,V06,
     [],[],{"reached_nodes_only":True,"method_retained":True,"boundary_retained":False,
             "provenance":"hosp_H1_trial_2026H1_audit_id"}),
  "impermissible","M7",
  "M7/missing_side_condition: boundary_retained=false; M2 requires boundary retained.",
  mut("F06_C1","missing_side_condition",["evidence.metadata.boundary_retained"],"boundary_retained false")))

# ===========================================================================
# F07 — M2 observed_decision, reached_nodes_only and type-mismatch
# ===========================================================================
S07=sc("T07","deepar_v1","global_mean_v1","MAE",["elec_zone_3"],[1,2,4,8],[0.25,0.25,0.25,0.25],"ev_2025Q4",[])
V07=vc("none","unconditional","fixed","single_application","exact","finite","pre_specified")
M07={"reached_nodes_only":True,"method_retained":True,"boundary_retained":True,"provenance":"elec_z3_trial_2025Q4_v1"}

cases.append(case("F07_C1","F07",
  "Hypothetical: DeepAR v1 vs global mean on electricity zone 3, MAE, 4 horizons. Pre-specified trial; all M2 side conditions satisfied including non-empty provenance.",
  rq("R07_C1","observed_decision",S07,V07),
  ev("E07_C1","observed_decision","observed_decision",S07,V07,[],[],M07),
  "permissible","M2","M2: all side conditions true; provenance non-empty string; literal decision licensed.",
  mut(None,"base",[],"")))

cases.append(case("F07_C2","F07",
  "Hypothetical: Same protocol, zone 4; provenance updated; all conditions satisfied.",
  rq("R07_C2","observed_decision",m(S07,"members",["elec_zone_4"]),V07),
  ev("E07_C2","observed_decision","observed_decision",m(S07,"members",["elec_zone_4"]),V07,[],[],
     {"reached_nodes_only":True,"method_retained":True,"boundary_retained":True,"provenance":"elec_z4_trial_2025Q4_v1"}),
  "permissible","M2","M2: different member; all conditions met.",
  mut("F07_C1","variant",["scientific.members"],"")))

cases.append(case("F07_C3","F07",
  "Hypothetical: reached_nodes_only=false; unreached nodes were appended retroactively.",
  rq("R07_C3","observed_decision",S07,V07),
  ev("E07_C3","observed_decision","observed_decision",S07,V07,[],[],
     {"reached_nodes_only":False,"method_retained":True,"boundary_retained":True,"provenance":"elec_z3_trial_2025Q4_v1"}),
  "impermissible","M7",
  "M7/missing_side_condition: reached_nodes_only=false; M2 requires only reached nodes in copy.",
  mut("F07_C1","missing_side_condition",["evidence.metadata.reached_nodes_only"],"reached_nodes_only false")))

cases.append(case("F07_C4","F07",
  "Hypothetical: Request asks for probability_bound; evidence kind is observed_decision. Type-level guard fires before M2.",
  rq("R07_C4","probability_bound",S07,vc({"indicator_id":"phi07","event_definition":"coverage_fail","upper_bound":0.05},"unconditional","fixed","single_application","exact","finite","pre_specified")),
  ev("E07_C4","observed_decision","observed_decision",S07,V07,[],[],M07),
  "impermissible","M7",
  "M7/type_mismatch: observed_decision evidence cannot license probability_bound; OBSERVED_TO_GUARANTEE_FORBIDDEN fires.",
  mut("F07_C1","type_mismatch",["request.conclusion_type"],"request elevated to probability_bound")))

# ===========================================================================
# F08 — M3 finite_design_empirical, all design fields
# ===========================================================================
S08=sc("T08","ets_v1","naive_v2","MAE",["m4_monthly_A"],[1,2,3],[1/3,1/3,1/3],"m4_2023",[])
V08=vc("none","unconditional","fixed","design_unit","empirical","finite","pre_specified")
RM08={"design_mixture":"stratified_random","denominator":500,"sample_range":"m4_monthly_2023_1_500","selection_record":"prereg_m4_A_2023"}
EM08={"design_mixture":"stratified_random","denominator":500,"sample_range":"m4_monthly_2023_1_500","selection_record":"prereg_m4_A_2023"}

cases.append(case("F08_C1","F08",
  "Hypothetical: ETS v1 vs naive v2 on M4 monthly set A, MAE, 3 horizons, 500 pre-registered series, stratified random design.",
  rq("R08_C1","empirical_rate",S08,V08,RM08),
  ev("E08_C1","finite_design_empirical","empirical_rate",S08,V08,[],["design matches pre-registration"],EM08),
  "permissible","M3","M3: all design parameters match; empirical rate licensed.",
  mut(None,"base",[],"")))

cases.append(case("F08_C2","F08",
  "Hypothetical: Same setup set B, idx 501-1000; all params updated consistently.",
  rq("R08_C2","empirical_rate",m(S08,"members",["m4_monthly_B"]),V08,
     {"design_mixture":"stratified_random","denominator":500,"sample_range":"m4_monthly_2023_501_1000","selection_record":"prereg_m4_B_2023"}),
  ev("E08_C2","finite_design_empirical","empirical_rate",m(S08,"members",["m4_monthly_B"]),V08,
     [],["design matches pre-registration"],
     {"design_mixture":"stratified_random","denominator":500,"sample_range":"m4_monthly_2023_501_1000","selection_record":"prereg_m4_B_2023"}),
  "permissible","M3","M3: alternate set, all params consistent; licensed.",
  mut("F08_C1","variant",["scientific.members"],"")))

cases.append(case("F08_C3","F08",
  "Hypothetical: denominator in evidence is 450, request metadata denominator is 500; mismatch.",
  rq("R08_C3","empirical_rate",S08,V08,RM08),
  ev("E08_C3","finite_design_empirical","empirical_rate",S08,V08,[],[],
     {"design_mixture":"stratified_random","denominator":450,"sample_range":"m4_monthly_2023_1_500","selection_record":"prereg_m4_A_2023"}),
  "impermissible","M7",
  "M7/missing_side_condition: EMPIRICAL_DESIGN_MISMATCH:denominator (450 vs 500); M3 requires matching denominator.",
  mut("F08_C1","missing_side_condition",["evidence.metadata.denominator"],"denominator reduced to 450")))

cases.append(case("F08_C4","F08",
  "Hypothetical: selection_record in evidence is post_hoc_audit, request specifies prereg_m4_A_2023; mismatch.",
  rq("R08_C4","empirical_rate",S08,V08,RM08),
  ev("E08_C4","finite_design_empirical","empirical_rate",S08,V08,[],[],
     {"design_mixture":"stratified_random","denominator":500,"sample_range":"m4_monthly_2023_1_500","selection_record":"post_hoc_audit"}),
  "impermissible","M7",
  "M7/missing_side_condition: EMPIRICAL_DESIGN_MISMATCH:selection_record; M3 requires matching selection_record.",
  mut("F08_C1","missing_side_condition",["evidence.metadata.selection_record"],"selection_record changed")))

# ===========================================================================
# F09 — M3 empirical_rate, design_mixture and support_mode mismatches
# ===========================================================================
S09=sc("T09","croston_v1","naive_v3","RMSSE",["intermittent_A"],[1,2,4,8],[0.25,0.25,0.25,0.25],"ev_2024",[])
V09=vc("none","unconditional","fixed","design_unit","empirical","finite","pre_specified")
RM09={"design_mixture":"simple_random","denominator":300,"sample_range":"interm_2024_1_300","selection_record":"prereg_interm_2024"}
EM09={"design_mixture":"simple_random","denominator":300,"sample_range":"interm_2024_1_300","selection_record":"prereg_interm_2024"}

cases.append(case("F09_C1","F09",
  "Hypothetical: Croston v1 vs naive on intermittent set A, RMSSE, 4 horizons, 300 pre-registered simple-random series.",
  rq("R09_C1","empirical_rate",S09,V09,RM09),
  ev("E09_C1","finite_design_empirical","empirical_rate",S09,V09,[],["design matches pre-registration"],EM09),
  "permissible","M3","M3: all design parameters match; empirical rate licensed.",
  mut(None,"base",[],"")))

cases.append(case("F09_C2","F09",
  "Hypothetical: Same setup set B, idx 301-600, all params updated.",
  rq("R09_C2","empirical_rate",m(S09,"members",["intermittent_B"]),V09,
     {"design_mixture":"simple_random","denominator":300,"sample_range":"interm_2024_301_600","selection_record":"prereg_interm_2024_B"}),
  ev("E09_C2","finite_design_empirical","empirical_rate",m(S09,"members",["intermittent_B"]),V09,
     [],["design matches pre-registration"],
     {"design_mixture":"simple_random","denominator":300,"sample_range":"interm_2024_301_600","selection_record":"prereg_interm_2024_B"}),
  "permissible","M3","M3: alternate set, params consistent; licensed.",
  mut("F09_C1","variant",["scientific.members"],"")))

cases.append(case("F09_C3","F09",
  "Hypothetical: design_mixture in evidence is cluster_random but request specifies simple_random.",
  rq("R09_C3","empirical_rate",S09,V09,RM09),
  ev("E09_C3","finite_design_empirical","empirical_rate",S09,V09,[],[],
     {"design_mixture":"cluster_random","denominator":300,"sample_range":"interm_2024_1_300","selection_record":"prereg_interm_2024"}),
  "impermissible","M7",
  "M7/missing_side_condition: EMPIRICAL_DESIGN_MISMATCH:design_mixture (cluster_random vs simple_random).",
  mut("F09_C1","missing_side_condition",["evidence.metadata.design_mixture"],"design_mixture changed")))

cases.append(case("F09_C4","F09",
  "Hypothetical: Request validity support_mode is exact but evidence support_mode is empirical; single validity coordinate mismatch.",
  rq("R09_C4","empirical_rate",S09,vc("none","unconditional","fixed","design_unit","exact","finite","pre_specified"),RM09),
  ev("E09_C4","finite_design_empirical","empirical_rate",S09,V09,[],[],EM09),
  "impermissible","M7",
  "M7: validity.support_mode mismatch (exact in request vs empirical in evidence); single validity coordinate changed.",
  mut("F09_C1","single_coordinate",["request.validity.support_mode"],"support_mode changed to exact")))

# ===========================================================================
# F10 — M4 theorem, all premises verified, exact finite-sample
# ===========================================================================
EV10={"indicator_id":"phi10","event_definition":"coverage_failure","upper_bound":0.05}
S10=sc("T10","conformal_v1","seas_naive_v1","MAPE",["weather_A"],[1],[1.0],"ev_weather_2025",[0.0])
V10=vc(EV10,"full_history","fixed","single_application","exact","finite","pre_specified")

cases.append(case("F10_C1","F10",
  "Hypothetical: Conformal theorem provides exact finite-sample coverage for conformal_v1 vs seasonal naive on weather_A, MAPE, horizon 1, alpha=0.05. All premises verified.",
  rq("R10_C1","probability_bound",S10,V10),
  ev("E10_C1","theorem","probability_bound",S10,V10,
     ["exchangeability","nonconformity_MAPE","prespecified_threshold"],
     ["exchangeability","nonconformity_MAPE","prespecified_threshold"],
     {"theorem_id":"conformal_exact_v1"}),
  "permissible","M4","M4: all scientific and validity coordinates match; all three premises declared and verified; exact bound licensed.",
  mut(None,"base",[],"")))

cases.append(case("F10_C2","F10",
  "Hypothetical: Same theorem on weather_B; all coordinates and premises consistent.",
  rq("R10_C2","probability_bound",m(S10,"members",["weather_B"]),V10),
  ev("E10_C2","theorem","probability_bound",m(S10,"members",["weather_B"]),V10,
     ["exchangeability","nonconformity_MAPE","prespecified_threshold"],
     ["exchangeability","nonconformity_MAPE","prespecified_threshold"],
     {"theorem_id":"conformal_exact_v1"}),
  "permissible","M4","M4: different member; premises verified; licensed.",
  mut("F10_C1","variant",["scientific.members"],"")))

cases.append(case("F10_C3","F10",
  "Hypothetical: exchangeability declared in premises but absent from verified_assumptions; M4 requires all premises verified.",
  rq("R10_C3","probability_bound",S10,V10),
  ev("E10_C3","theorem","probability_bound",S10,V10,
     ["exchangeability","nonconformity_MAPE","prespecified_threshold"],
     ["nonconformity_MAPE","prespecified_threshold"],
     {"theorem_id":"conformal_exact_v1"}),
  "impermissible","M7",
  "M7/missing_side_condition: UNVERIFIED_ASSUMPTION:exchangeability; M4 requires every declared premise in verified_assumptions.",
  mut("F10_C1","missing_side_condition",["evidence.verified_assumptions"],"exchangeability not verified")))

cases.append(case("F10_C4","F10",
  "Hypothetical: premises list is empty; FINAL_MATCHER returns THEOREM_PREMISES_EMPTY.",
  rq("R10_C4","probability_bound",S10,V10),
  ev("E10_C4","theorem","probability_bound",S10,V10,
     [],[],{"theorem_id":"conformal_exact_v1"}),
  "impermissible","M7",
  "M7/missing_side_condition: THEOREM_PREMISES_EMPTY; FINAL_MATCHER requires at least one premise for theorem/asymptotic_theorem evidence.",
  mut("F10_C1","missing_side_condition",["evidence.premises"],"premises emptied")))

# ===========================================================================
# F11 — M4 asymptotic_theorem, regime and coverage_unit
# ===========================================================================
EV11={"indicator_id":"phi11","event_definition":"improvement_exceeds_0","upper_bound":0.10}
S11=sc("T11","var_v1","seas_naive_v2","MSE",["macro_A"],[1,2,4,8,12],[0.2,0.2,0.2,0.2,0.2],"ev_macro_2025",[0.0])
V11=vc(EV11,"unconditional","fixed","single_application","asymptotic","infinite","pre_specified")

cases.append(case("F11_C1","F11",
  "Hypothetical: Asymptotic theorem for VAR v1 vs seasonal naive on macro_A, MSE, 5 horizons, alpha=0.10. All premises verified.",
  rq("R11_C1","probability_bound",S11,V11),
  ev("E11_C1","asymptotic_theorem","probability_bound",S11,V11,
     ["stationarity","ergodicity","finite_fourth_moments"],
     ["stationarity","ergodicity","finite_fourth_moments"],
     {"theorem_id":"asymp_var_v1"}),
  "permissible","M4","M4: asymptotic_theorem; all coordinates match; premises declared and verified; asymptotic bound licensed.",
  mut(None,"base",[],"")))

cases.append(case("F11_C2","F11",
  "Hypothetical: Same theorem macro_B; all consistent.",
  rq("R11_C2","probability_bound",m(S11,"members",["macro_B"]),V11),
  ev("E11_C2","asymptotic_theorem","probability_bound",m(S11,"members",["macro_B"]),V11,
     ["stationarity","ergodicity","finite_fourth_moments"],
     ["stationarity","ergodicity","finite_fourth_moments"],
     {"theorem_id":"asymp_var_v1"}),
  "permissible","M4","M4: different member; premises verified; licensed.",
  mut("F11_C1","variant",["scientific.members"],"")))

cases.append(case("F11_C3","F11",
  "Hypothetical: Request validity sample_regime is finite but evidence is infinite; asymptotic theorem not applicable at finite-sample scope.",
  rq("R11_C3","probability_bound",S11,vc(EV11,"unconditional","fixed","single_application","asymptotic","finite","pre_specified")),
  ev("E11_C3","asymptotic_theorem","probability_bound",S11,V11,
     ["stationarity","ergodicity","finite_fourth_moments"],
     ["stationarity","ergodicity","finite_fourth_moments"],
     {"theorem_id":"asymp_var_v1"}),
  "impermissible","M7",
  "M7: validity.sample_regime mismatch (finite in request vs infinite in evidence); single validity coordinate changed.",
  mut("F11_C1","single_coordinate",["request.validity.sample_regime"],"sample_regime changed to finite")))

cases.append(case("F11_C4","F11",
  "Hypothetical: ergodicity is in premises but not in verified_assumptions.",
  rq("R11_C4","probability_bound",S11,V11),
  ev("E11_C4","asymptotic_theorem","probability_bound",S11,V11,
     ["stationarity","ergodicity","finite_fourth_moments"],
     ["stationarity","finite_fourth_moments"],
     {"theorem_id":"asymp_var_v1"}),
  "impermissible","M7",
  "M7/missing_side_condition: UNVERIFIED_ASSUMPTION:ergodicity; M4 requires all declared premises verified.",
  mut("F11_C1","missing_side_condition",["evidence.verified_assumptions"],"ergodicity not verified")))

# ===========================================================================
# F12 — M4 theorem, error_event and conditioning mismatches
# ===========================================================================
EV12a={"indicator_id":"phi12","event_definition":"coverage_failure","upper_bound":0.05}
EV12b={"indicator_id":"phi12b","event_definition":"coverage_failure","upper_bound":0.10}
S12=sc("T12","mlp_v1","naive_v4","MAE",["retail_A"],[1,2,4,7],[0.25,0.25,0.25,0.25],"ev_retail_2025",[0.0,0.02])
V12=vc(EV12a,"full_history","fixed","single_application","exact","finite","pre_specified")

cases.append(case("F12_C1","F12",
  "Hypothetical: Exact theorem for MLP v1 vs naive on retail_A, MAE, 4 horizons, full_history conditioning, alpha=0.05. All premises verified.",
  rq("R12_C1","probability_bound",S12,V12),
  ev("E12_C1","theorem","probability_bound",S12,V12,
     ["iid_residuals","score_bounded","prespecified_threshold"],
     ["iid_residuals","score_bounded","prespecified_threshold"],
     {"theorem_id":"exact_mlp_v1"}),
  "permissible","M4","M4: all coordinates match; premises declared and verified; exact full_history-conditional bound licensed.",
  mut(None,"base",[],"")))

cases.append(case("F12_C2","F12",
  "Hypothetical: Same theorem retail_B; all consistent.",
  rq("R12_C2","probability_bound",m(S12,"members",["retail_B"]),V12),
  ev("E12_C2","theorem","probability_bound",m(S12,"members",["retail_B"]),V12,
     ["iid_residuals","score_bounded","prespecified_threshold"],
     ["iid_residuals","score_bounded","prespecified_threshold"],
     {"theorem_id":"exact_mlp_v1"}),
  "permissible","M4","M4: different member; premises verified; licensed.",
  mut("F12_C1","variant",["scientific.members"],"")))

cases.append(case("F12_C3","F12",
  "Hypothetical: Evidence error_event upper_bound is 0.10 but request error_event upper_bound is 0.05; error_event mismatch.",
  rq("R12_C3","probability_bound",S12,V12),
  ev("E12_C3","theorem","probability_bound",S12,
     vc(EV12b,"full_history","fixed","single_application","exact","finite","pre_specified"),
     ["iid_residuals","score_bounded","prespecified_threshold"],
     ["iid_residuals","score_bounded","prespecified_threshold"],
     {"theorem_id":"exact_mlp_v1_alpha10"}),
  "impermissible","M7",
  "M7: ERROR_EVENT_MISMATCH; upper_bound 0.10 vs 0.05; single validity sub-field changed.",
  mut("F12_C1","single_coordinate",["evidence.validity.error_event.upper_bound"],"alpha changed to 0.10")))

cases.append(case("F12_C4","F12",
  "Hypothetical: Evidence conditioning is unconditional but request requires full_history; single validity coordinate mismatch.",
  rq("R12_C4","probability_bound",S12,V12),
  ev("E12_C4","theorem","probability_bound",S12,
     vc(EV12a,"unconditional","fixed","single_application","exact","finite","pre_specified"),
     ["iid_residuals","score_bounded","prespecified_threshold"],
     ["iid_residuals","score_bounded","prespecified_threshold"],
     {"theorem_id":"exact_mlp_v1_uncond"}),
  "impermissible","M7",
  "M7: CONDITIONING_STRENGTHENING_FORBIDDEN; evidence conditioning unconditional vs request full_history; single validity coordinate changed.",
  mut("F12_C1","single_coordinate",["evidence.validity.conditioning"],"conditioning changed to unconditional")))

# ===========================================================================
# F13 — M5 conditioning coarsening: declared_coarsenings = bare identifier
# KEY FIX: declared_coarsenings = ["full_history"] not a path string
# ===========================================================================
EV13={"indicator_id":"phi13","event_definition":"coverage_failure","upper_bound":0.05}
S13=sc("T13","deepar_v2","seas_naive_v3","RMSE",["energy_A"],[1,4,8,12,24],[0.2,0.2,0.2,0.2,0.2],"ev_energy_2025",[0.0])
V13_fine=vc(EV13,"sub_history_sigma","fixed","single_application","exact","finite","pre_specified")
V13_coarse=vc(EV13,"full_history","fixed","single_application","exact","finite","pre_specified")
M13_ok={"declared_coarsenings":["full_history"],"same_joint_law":True,"same_error_event":True,"integrable_indicator":True,"bound_constant_or_coarser_measurable":True}

cases.append(case("F13_C1","F13",
  "Hypothetical: Conditional bound at sub_history_sigma for DeepAR v2 vs seasonal naive, RMSE, energy_A. Request coarsens to full_history. declared_coarsenings=['full_history'] (bare identifier). All booleans true.",
  rq("R13_C1","probability_bound",S13,V13_coarse),
  ev("E13_C1","conditional_bound","probability_bound",S13,V13_fine,
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],M13_ok),
  "permissible","M5",
  "M5: declared_coarsenings contains bare request conditioning identifier 'full_history'; all four booleans true; tower property licenses coarser bound.",
  mut(None,"base",[],"")))

cases.append(case("F13_C2","F13",
  "Hypothetical: Same structure energy_B; all coarsening conditions consistent.",
  rq("R13_C2","probability_bound",m(S13,"members",["energy_B"]),V13_coarse),
  ev("E13_C2","conditional_bound","probability_bound",m(S13,"members",["energy_B"]),V13_fine,
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],M13_ok),
  "permissible","M5","M5: different member; coarsening conditions met.",
  mut("F13_C1","variant",["scientific.members"],"")))

cases.append(case("F13_C3","F13",
  "Hypothetical: declared_coarsenings contains path string 'sub_history_sigma to full_history' instead of bare identifier 'full_history'; checker cannot find bare target identifier.",
  rq("R13_C3","probability_bound",S13,V13_coarse),
  ev("E13_C3","conditional_bound","probability_bound",S13,V13_fine,
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],
     {"declared_coarsenings":["sub_history_sigma to full_history"],"same_joint_law":True,"same_error_event":True,"integrable_indicator":True,"bound_constant_or_coarser_measurable":True}),
  "impermissible","M7",
  "M7: CONDITIONING_STRENGTHENING_FORBIDDEN; declared_coarsenings contains path string not bare identifier; checker tests target_field in declared_coarsenings and 'full_history' is not found in ['sub_history_sigma to full_history'].",
  mut("F13_C1","missing_side_condition",["evidence.metadata.declared_coarsenings"],"path string instead of bare identifier")))

cases.append(case("F13_C4","F13",
  "Hypothetical: same_joint_law=false; M5 requires same joint law for tower property.",
  rq("R13_C4","probability_bound",S13,V13_coarse),
  ev("E13_C4","conditional_bound","probability_bound",S13,V13_fine,
     ["G_subset_H","same_error_event","integrable_indicator"],
     ["G_subset_H","same_error_event","integrable_indicator"],
     {"declared_coarsenings":["full_history"],"same_joint_law":False,"same_error_event":True,"integrable_indicator":True,"bound_constant_or_coarser_measurable":True}),
  "impermissible","M7",
  "M7/missing_side_condition: COARSENING_SIDE_CONDITION_FAILED:same_joint_law; M5 requires same_joint_law=true.",
  mut("F13_C1","missing_side_condition",["evidence.metadata.same_joint_law"],"same_joint_law false")))

# ===========================================================================
# F14 — M5 coarsening: other boolean checks + coarsenings=[]
# ===========================================================================
EV14={"indicator_id":"phi14","event_definition":"coverage_failure","upper_bound":0.05}
S14=sc("T14","tft_v1","arima_v3","MAE",["retail_C"],[1,2,4,8],[0.25,0.25,0.25,0.25],"ev_retail_2026",[0.0])
V14_fine=vc(EV14,"sub_sigma_season","fixed","single_application","exact","finite","pre_specified")
V14_coarse=vc(EV14,"full_history","fixed","single_application","exact","finite","pre_specified")
M14_ok={"declared_coarsenings":["full_history"],"same_joint_law":True,"same_error_event":True,"integrable_indicator":True,"bound_constant_or_coarser_measurable":True}

cases.append(case("F14_C1","F14",
  "Hypothetical: Conditional bound at sub_sigma_season for TFT v1 vs ARIMA, MAE, retail_C. Coarsened to full_history using bare identifier. All booleans true.",
  rq("R14_C1","probability_bound",S14,V14_coarse),
  ev("E14_C1","conditional_bound","probability_bound",S14,V14_fine,
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],M14_ok),
  "permissible","M5","M5: bare identifier in declared_coarsenings; all booleans true; licensed.",
  mut(None,"base",[],"")))

cases.append(case("F14_C2","F14",
  "Hypothetical: Same structure retail_D; conditions met.",
  rq("R14_C2","probability_bound",m(S14,"members",["retail_D"]),V14_coarse),
  ev("E14_C2","conditional_bound","probability_bound",m(S14,"members",["retail_D"]),V14_fine,
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],M14_ok),
  "permissible","M5","M5: different member; conditions met.",
  mut("F14_C1","variant",["scientific.members"],"")))

cases.append(case("F14_C3","F14",
  "Hypothetical: declared_coarsenings is empty list; no coarsening path declared.",
  rq("R14_C3","probability_bound",S14,V14_coarse),
  ev("E14_C3","conditional_bound","probability_bound",S14,V14_fine,
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],
     {"declared_coarsenings":[],"same_joint_law":True,"same_error_event":True,"integrable_indicator":True,"bound_constant_or_coarser_measurable":True}),
  "impermissible","M7",
  "M7: CONDITIONING_STRENGTHENING_FORBIDDEN; declared_coarsenings is empty; 'full_history' not found in []; coarsening not licensed.",
  mut("F14_C1","missing_side_condition",["evidence.metadata.declared_coarsenings"],"declared_coarsenings emptied")))

cases.append(case("F14_C4","F14",
  "Hypothetical: bound_constant_or_coarser_measurable=false; M5 requires this boolean true.",
  rq("R14_C4","probability_bound",S14,V14_coarse),
  ev("E14_C4","conditional_bound","probability_bound",S14,V14_fine,
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],
     {"declared_coarsenings":["full_history"],"same_joint_law":True,"same_error_event":True,"integrable_indicator":True,"bound_constant_or_coarser_measurable":False}),
  "impermissible","M7",
  "M7/missing_side_condition: COARSENING_SIDE_CONDITION_FAILED:bound_constant_or_coarser_measurable; boolean is false.",
  mut("F14_C1","missing_side_condition",["evidence.metadata.bound_constant_or_coarser_measurable"],"bool false")))

# ===========================================================================
# F15 — M5 coarsening: reversed direction (fine→coarse vs coarse→fine)
# and same_error_event=false
# ===========================================================================
EV15={"indicator_id":"phi15","event_definition":"coverage_failure","upper_bound":0.05}
EV15b={"indicator_id":"phi15b","event_definition":"improvement_exceeds_0.05","upper_bound":0.05}
S15=sc("T15","nhits_v2","global_mean_v2","RMSE",["macro_C"],[1,4,8,12],[0.25,0.25,0.25,0.25],"ev_macro_2026",[0.0])
V15_fine=vc(EV15,"sub_sigma_vol","fixed","single_application","exact","finite","pre_specified")
V15_coarse=vc(EV15,"full_history","fixed","single_application","exact","finite","pre_specified")
M15_ok={"declared_coarsenings":["full_history"],"same_joint_law":True,"same_error_event":True,"integrable_indicator":True,"bound_constant_or_coarser_measurable":True}

cases.append(case("F15_C1","F15",
  "Hypothetical: Conditional bound at sub_sigma_vol coarsened to full_history for N-HiTS v2. declared_coarsenings=['full_history']. All booleans true.",
  rq("R15_C1","probability_bound",S15,V15_coarse),
  ev("E15_C1","conditional_bound","probability_bound",S15,V15_fine,
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],M15_ok),
  "permissible","M5","M5: bare identifier; all booleans true; coarsening licensed.",
  mut(None,"base",[],"")))

cases.append(case("F15_C2","F15",
  "Hypothetical: Same structure macro_D; conditions met.",
  rq("R15_C2","probability_bound",m(S15,"members",["macro_D"]),V15_coarse),
  ev("E15_C2","conditional_bound","probability_bound",m(S15,"members",["macro_D"]),V15_fine,
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],M15_ok),
  "permissible","M5","M5: different member; conditions met.",
  mut("F15_C1","variant",["scientific.members"],"")))

cases.append(case("F15_C3","F15",
  "Hypothetical: Coarsening reversed: evidence is at full_history (coarser), request asks for sub_sigma_vol (finer); M5 cannot reverse direction.",
  rq("R15_C3","probability_bound",S15,V15_fine),
  ev("E15_C3","conditional_bound","probability_bound",S15,V15_coarse,
     ["same_joint_law","same_error_event","integrable_indicator"],
     ["same_joint_law","same_error_event","integrable_indicator"],
     {"declared_coarsenings":[],"same_joint_law":True,"same_error_event":True,"integrable_indicator":True,"bound_constant_or_coarser_measurable":True}),
  "impermissible","M7",
  "M7: CONDITIONING_STRENGTHENING_FORBIDDEN; coarsening direction reversed; M5 cannot go from coarser evidence to finer request.",
  mut("F15_C1","single_coordinate",["request.validity.conditioning","evidence.validity.conditioning"],"direction reversed")))

cases.append(case("F15_C4","F15",
  "Hypothetical: same_error_event=false; evidence event is improvement_exceeds_0.05 but request event is coverage_failure; M5 requires same error event.",
  rq("R15_C4","probability_bound",S15,V15_coarse),
  ev("E15_C4","conditional_bound","probability_bound",S15,
     vc(EV15b,"sub_sigma_vol","fixed","single_application","exact","finite","pre_specified"),
     ["G_subset_H","same_joint_law","integrable_indicator"],
     ["G_subset_H","same_joint_law","integrable_indicator"],
     {"declared_coarsenings":["full_history"],"same_joint_law":True,"same_error_event":False,"integrable_indicator":True,"bound_constant_or_coarser_measurable":True}),
  "impermissible","M7",
  "M7/missing_side_condition: COARSENING_SIDE_CONDITION_FAILED:same_error_event; boolean is false; error events differ.",
  mut("F15_C1","missing_side_condition",["evidence.metadata.same_error_event","evidence.validity.error_event"],"error event changed")))

# ===========================================================================
# F16 — M6 fixed_sequence, all conditions satisfied
# ===========================================================================
EV16={"indicator_id":"phi16","event_definition":"sequential_type1_error","upper_bound":0.05}
S16=sc("T16","seq_model_v1","seas_naive_v4","MAE",["macro_E"],[1,2,4,8],[0.25,0.25,0.25,0.25],"ev_macro_2025",[0.0,0.02,0.05])
V16=vc(EV16,"full_history","fixed","single_application","exact","finite","pre_specified")
M16={"potential_tests_defined":True,"ordered_family":True,"stop_at_first_valid_nonrejection":True,"no_true_null_convention":True,"invalid_policy":"whole_request_unresolved"}

cases.append(case("F16_C1","F16",
  "Hypothetical: Sequential testing family for seq_model_v1 vs seasonal naive, MAE, macro_E, thresholds [0,0.02,0.05]. All M6 conditions satisfied.",
  rq("R16_C1","fixed_sequence_error_bound",S16,V16),
  ev("E16_C1","local_validity_family","local_node_bounds",S16,V16,
     ["truth_events_measurable","local_bounds_hold"],
     ["truth_events_measurable","local_bounds_hold"],M16),
  "permissible","M6","M6: all five metadata booleans/policy met; premises declared and verified; full_history conditioning; licensed.",
  mut(None,"base",[],"")))

cases.append(case("F16_C2","F16",
  "Hypothetical: Same family on macro_F; all conditions consistent.",
  rq("R16_C2","fixed_sequence_error_bound",m(S16,"members",["macro_F"]),V16),
  ev("E16_C2","local_validity_family","local_node_bounds",m(S16,"members",["macro_F"]),V16,
     ["truth_events_measurable","local_bounds_hold"],
     ["truth_events_measurable","local_bounds_hold"],M16),
  "permissible","M6","M6: different member; all conditions met.",
  mut("F16_C1","variant",["scientific.members"],"")))

cases.append(case("F16_C3","F16",
  "Hypothetical: invalid_policy='continue_on_invalid' instead of 'whole_request_unresolved'; M6 requires whole_request_unresolved.",
  rq("R16_C3","fixed_sequence_error_bound",S16,V16),
  ev("E16_C3","local_validity_family","local_node_bounds",S16,V16,
     ["truth_events_measurable","local_bounds_hold"],
     ["truth_events_measurable","local_bounds_hold"],
     {"potential_tests_defined":True,"ordered_family":True,"stop_at_first_valid_nonrejection":True,"no_true_null_convention":True,"invalid_policy":"continue_on_invalid"}),
  "impermissible","M7",
  "M7/missing_side_condition: FIXED_SEQUENCE_SIDE_CONDITION_FAILED:invalid_policy; must be 'whole_request_unresolved'.",
  mut("F16_C1","missing_side_condition",["evidence.metadata.invalid_policy"],"invalid_policy changed")))

cases.append(case("F16_C4","F16",
  "Hypothetical: conditioning is unconditional not full_history; M6 requires full_history conditioning.",
  rq("R16_C4","fixed_sequence_error_bound",S16,vc(EV16,"unconditional","fixed","single_application","exact","finite","pre_specified")),
  ev("E16_C4","local_validity_family","local_node_bounds",S16,vc(EV16,"unconditional","fixed","single_application","exact","finite","pre_specified"),
     ["truth_events_measurable","local_bounds_hold"],["truth_events_measurable","local_bounds_hold"],M16),
  "impermissible","M7",
  "M7/missing_side_condition: FIXED_SEQUENCE_SIDE_CONDITION_FAILED:full_history_conditioning; conditioning is unconditional.",
  mut("F16_C1","single_coordinate",["request.validity.conditioning","evidence.validity.conditioning"],"conditioning changed")))

# ===========================================================================
# F17 — M6 fixed_sequence, ordered_family and potential_tests checks
# ===========================================================================
EV17={"indicator_id":"phi17","event_definition":"sequential_type1_error","upper_bound":0.10}
S17=sc("T17","nbeats_v1","global_mean_v3","RMSE",["energy_B"],[1,2,4,8,12,24],[1/6,1/6,1/6,1/6,1/6,1/6],"ev_energy_2026",[0.0,0.05,0.10])
V17=vc(EV17,"full_history","fixed","single_application","exact","finite","pre_specified")
M17={"potential_tests_defined":True,"ordered_family":True,"stop_at_first_valid_nonrejection":True,"no_true_null_convention":True,"invalid_policy":"whole_request_unresolved"}

cases.append(case("F17_C1","F17",
  "Hypothetical: N-BEATS v1 vs global mean on energy_B, RMSE, 6 horizons, sequential family 3 thresholds, alpha=0.10. All M6 conditions satisfied.",
  rq("R17_C1","fixed_sequence_error_bound",S17,V17),
  ev("E17_C1","local_validity_family","local_node_bounds",S17,V17,
     ["truth_events_measurable","local_bounds_hold"],["truth_events_measurable","local_bounds_hold"],M17),
  "permissible","M6","M6: all conditions satisfied; licensed.",
  mut(None,"base",[],"")))

cases.append(case("F17_C2","F17",
  "Hypothetical: Same family, energy_C; all conditions consistent.",
  rq("R17_C2","fixed_sequence_error_bound",m(S17,"members",["energy_C"]),V17),
  ev("E17_C2","local_validity_family","local_node_bounds",m(S17,"members",["energy_C"]),V17,
     ["truth_events_measurable","local_bounds_hold"],["truth_events_measurable","local_bounds_hold"],M17),
  "permissible","M6","M6: different member; all conditions met.",
  mut("F17_C1","variant",["scientific.members"],"")))

cases.append(case("F17_C3","F17",
  "Hypothetical: ordered_family=false; tests not ordered; M6 requires ordered stopping.",
  rq("R17_C3","fixed_sequence_error_bound",S17,V17),
  ev("E17_C3","local_validity_family","local_node_bounds",S17,V17,
     ["truth_events_measurable","local_bounds_hold"],["truth_events_measurable","local_bounds_hold"],
     {"potential_tests_defined":True,"ordered_family":False,"stop_at_first_valid_nonrejection":True,"no_true_null_convention":True,"invalid_policy":"whole_request_unresolved"}),
  "impermissible","M7",
  "M7/missing_side_condition: FIXED_SEQUENCE_SIDE_CONDITION_FAILED:ordered_family; ordered_family=false.",
  mut("F17_C1","missing_side_condition",["evidence.metadata.ordered_family"],"ordered_family false")))

cases.append(case("F17_C4","F17",
  "Hypothetical: potential_tests_defined=false; tests not defined on joint sample space; M6 cannot apply.",
  rq("R17_C4","fixed_sequence_error_bound",S17,V17),
  ev("E17_C4","local_validity_family","local_node_bounds",S17,V17,
     ["truth_events_measurable","local_bounds_hold"],["truth_events_measurable","local_bounds_hold"],
     {"potential_tests_defined":False,"ordered_family":True,"stop_at_first_valid_nonrejection":True,"no_true_null_convention":True,"invalid_policy":"whole_request_unresolved"}),
  "impermissible","M7",
  "M7/missing_side_condition: FIXED_SEQUENCE_SIDE_CONDITION_FAILED:potential_tests_defined; boolean false.",
  mut("F17_C1","missing_side_condition",["evidence.metadata.potential_tests_defined"],"potential_tests_defined false")))

# ===========================================================================
# F18 — M6 fixed_sequence, conclusion_type and premises checks
# ===========================================================================
EV18={"indicator_id":"phi18","event_definition":"sequential_type1_error","upper_bound":0.05}
S18=sc("T18","scinet_v1","arima_v4","MAPE",["transport_A"],[1,3,6,12,24],[0.2,0.2,0.2,0.2,0.2],"ev_transport_2025",[0.0,0.02,0.05])
V18=vc(EV18,"full_history","fixed","single_application","exact","finite","pre_specified")
M18={"potential_tests_defined":True,"ordered_family":True,"stop_at_first_valid_nonrejection":True,"no_true_null_convention":True,"invalid_policy":"whole_request_unresolved"}

cases.append(case("F18_C1","F18",
  "Hypothetical: SCINet v1 vs ARIMA on transport_A, MAPE, 5 horizons, sequential 3-threshold family. All M6 conditions met; premises declared and verified.",
  rq("R18_C1","fixed_sequence_error_bound",S18,V18),
  ev("E18_C1","local_validity_family","local_node_bounds",S18,V18,
     ["truth_events_measurable","local_bounds_hold"],["truth_events_measurable","local_bounds_hold"],M18),
  "permissible","M6","M6: all conditions met; licensed.",
  mut(None,"base",[],"")))

cases.append(case("F18_C2","F18",
  "Hypothetical: Same family transport_B; conditions consistent.",
  rq("R18_C2","fixed_sequence_error_bound",m(S18,"members",["transport_B"]),V18),
  ev("E18_C2","local_validity_family","local_node_bounds",m(S18,"members",["transport_B"]),V18,
     ["truth_events_measurable","local_bounds_hold"],["truth_events_measurable","local_bounds_hold"],M18),
  "permissible","M6","M6: different member; conditions met.",
  mut("F18_C1","variant",["scientific.members"],"")))

cases.append(case("F18_C3","F18",
  "Hypothetical: evidence conclusion_type is empirical_rate instead of local_node_bounds; type mismatch for M6.",
  rq("R18_C3","fixed_sequence_error_bound",S18,V18),
  ev("E18_C3","local_validity_family","empirical_rate",S18,V18,
     ["truth_events_measurable","local_bounds_hold"],["truth_events_measurable","local_bounds_hold"],M18),
  "impermissible","M7",
  "M7/type_mismatch: CONCLUSION_TYPE_MISMATCH; evidence conclusion_type empirical_rate vs required local_node_bounds.",
  mut("F18_C1","type_mismatch",["evidence.conclusion_type"],"conclusion_type changed to empirical_rate")))

cases.append(case("F18_C4","F18",
  "Hypothetical: truth_events_measurable in premises but NOT in verified_assumptions; M6 requires both declared and verified.",
  rq("R18_C4","fixed_sequence_error_bound",S18,V18),
  ev("E18_C4","local_validity_family","local_node_bounds",S18,V18,
     ["truth_events_measurable","local_bounds_hold"],["local_bounds_hold"],M18),
  "impermissible","M7",
  "M7/missing_side_condition: UNVERIFIED_ASSUMPTION:truth_events_measurable; declared in premises but missing from verified_assumptions.",
  mut("F18_C1","missing_side_condition",["evidence.verified_assumptions"],"truth_events_measurable not verified")))

# ===========================================================================
# F19 — M1 type-mismatch: conclusion_type incompatible with evidence kind
# ===========================================================================
S19=sc("T19","autoformer_v1","naive_v5","RMSE",["solar_A"],[1,2,4,8,12,24],[1/6,1/6,1/6,1/6,1/6,1/6],"ev_solar_2025",[])
V19=vc("none","unconditional","fixed","single_application","exact","finite","none")

cases.append(case("F19_C1","F19",
  "Hypothetical: Autoformer v1 and naive v5 produce identical solar forecasts. Author claims structural identity under RMSE.",
  rq("R19_C1","structural_identity",S19,V19),
  ev("E19_C1","structural_identity","structural_identity",S19,V19,
     ["predictions identical"],["predictions identical"],{"pointwise_identity":True}),
  "permissible","M1","M1: pointwise_identity=true; all coordinates match; structural identity licensed.",
  mut(None,"base",[],"")))

cases.append(case("F19_C2","F19",
  "Hypothetical: Same systems solar_B; identity confirmed.",
  rq("R19_C2","structural_identity",m(S19,"members",["solar_B"]),V19),
  ev("E19_C2","structural_identity","structural_identity",m(S19,"members",["solar_B"]),V19,
     ["predictions identical"],["predictions identical"],{"pointwise_identity":True}),
  "permissible","M1","M1: different member; identity confirmed.",
  mut("F19_C1","variant",["scientific.members"],"")))

cases.append(case("F19_C3","F19",
  "Hypothetical: Request conclusion_type is observed_decision; evidence kind is structural_identity; type incompatibility.",
  rq("R19_C3","observed_decision",S19,V19),
  ev("E19_C3","structural_identity","structural_identity",S19,V19,
     ["predictions identical"],["predictions identical"],{"pointwise_identity":True}),
  "impermissible","M7",
  "M7/type_mismatch: CONCLUSION_TYPE_MISMATCH; structural_identity evidence cannot license observed_decision request.",
  mut("F19_C1","type_mismatch",["request.conclusion_type"],"request changed to observed_decision")))

cases.append(case("F19_C4","F19",
  "Hypothetical: evidence kind is finite_design_empirical but request conclusion_type is structural_identity; EMPIRICAL_TO_THEOREM_FORBIDDEN fires.",
  rq("R19_C4","structural_identity",S19,V19),
  ev("E19_C4","finite_design_empirical","empirical_rate",S19,V19,
     [],["design matches"],{"design_mixture":"simple_random","denominator":100,"sample_range":"solar_2025_1_100","selection_record":"prereg_solar"}),
  "impermissible","M7",
  "M7/type_mismatch: EMPIRICAL_TO_THEOREM_FORBIDDEN; finite_design_empirical evidence cannot license structural_identity request.",
  mut("F19_C1","type_mismatch",["evidence.kind","evidence.conclusion_type"],"evidence kind changed to finite_design_empirical")))

# ===========================================================================
# F20 — M4 theorem, law_quantifier and support_mode mismatches
# ===========================================================================
EV20={"indicator_id":"phi20","event_definition":"coverage_failure","upper_bound":0.05}
S20=sc("T20","quantile_v1","seas_naive_v5","PINBALL",["wind_A"],[1,2,4,8,12,24],[1/6]*6,"ev_wind_2025",[0.0,0.05])
V20_fixed=vc(EV20,"unconditional","fixed","single_application","exact","finite","pre_specified")
V20_univ=vc(EV20,"unconditional","universal","single_application","exact","finite","pre_specified")

cases.append(case("F20_C1","F20",
  "Hypothetical: Exact theorem for quantile_v1 vs seasonal naive on wind_A, PINBALL, 6 horizons, fixed law, alpha=0.05. All premises verified.",
  rq("R20_C1","probability_bound",S20,V20_fixed),
  ev("E20_C1","theorem","probability_bound",S20,V20_fixed,
     ["exchangeability","quantile_consistency","prespecified_threshold"],
     ["exchangeability","quantile_consistency","prespecified_threshold"],
     {"theorem_id":"quantile_exact_v1"}),
  "permissible","M4","M4: all coordinates match; all premises verified; fixed law; exact bound licensed.",
  mut(None,"base",[],"")))

cases.append(case("F20_C2","F20",
  "Hypothetical: Same theorem wind_B; all consistent.",
  rq("R20_C2","probability_bound",m(S20,"members",["wind_B"]),V20_fixed),
  ev("E20_C2","theorem","probability_bound",m(S20,"members",["wind_B"]),V20_fixed,
     ["exchangeability","quantile_consistency","prespecified_threshold"],
     ["exchangeability","quantile_consistency","prespecified_threshold"],
     {"theorem_id":"quantile_exact_v1"}),
  "permissible","M4","M4: different member; all premises verified; licensed.",
  mut("F20_C1","variant",["scientific.members"],"")))

cases.append(case("F20_C3","F20",
  "Hypothetical: Evidence law_quantifier is universal but request specifies fixed; distinct validity scope.",
  rq("R20_C3","probability_bound",S20,V20_fixed),
  ev("E20_C3","theorem","probability_bound",S20,V20_univ,
     ["exchangeability","quantile_consistency","prespecified_threshold"],
     ["exchangeability","quantile_consistency","prespecified_threshold"],
     {"theorem_id":"quantile_exact_v1_univ"}),
  "impermissible","M7",
  "M7: VALIDITY_SCOPE_MISMATCH:law_quantifier (universal vs fixed); single validity coordinate changed.",
  mut("F20_C1","single_coordinate",["evidence.validity.law_quantifier"],"law_quantifier changed to universal")))

cases.append(case("F20_C4","F20",
  "Hypothetical: Request support_mode is asymptotic but evidence is exact; cannot upgrade exact to asymptotic scope.",
  rq("R20_C4","probability_bound",S20,vc(EV20,"unconditional","fixed","single_application","asymptotic","finite","pre_specified")),
  ev("E20_C4","theorem","probability_bound",S20,V20_fixed,
     ["exchangeability","quantile_consistency","prespecified_threshold"],
     ["exchangeability","quantile_consistency","prespecified_threshold"],
     {"theorem_id":"quantile_exact_v1"}),
  "impermissible","M7",
  "M7: VALIDITY_SCOPE_MISMATCH:support_mode (exact vs asymptotic); single validity coordinate changed.",
  mut("F20_C1","single_coordinate",["request.validity.support_mode"],"support_mode changed to asymptotic")))

# ===========================================================================
# F21 — M2 observed_decision, evaluation_law and selection_mechanism mismatches
# ===========================================================================
S21=sc("T21","tsmixer_v1","ses_v2","MASE",["hotel_A"],[1,2,3,4],[0.25,0.25,0.25,0.25],"ev_hotel_2025",[])
V21=vc("none","unconditional","fixed","single_application","exact","finite","pre_specified")
M21={"reached_nodes_only":True,"method_retained":True,"boundary_retained":True,"provenance":"hotel_A_trial_2025_ref_7829"}

cases.append(case("F21_C1","F21",
  "Hypothetical: TSMixer v1 vs SES v2 on hotel_A, MASE, 4 horizons. Pre-specified trial; all M2 conditions met; provenance is non-empty.",
  rq("R21_C1","observed_decision",S21,V21),
  ev("E21_C1","observed_decision","observed_decision",S21,V21,[],[],M21),
  "permissible","M2","M2: all side conditions true; provenance non-empty; literal decision licensed.",
  mut(None,"base",[],"")))

cases.append(case("F21_C2","F21",
  "Hypothetical: Same protocol hotel_B; conditions met.",
  rq("R21_C2","observed_decision",m(S21,"members",["hotel_B"]),V21),
  ev("E21_C2","observed_decision","observed_decision",m(S21,"members",["hotel_B"]),V21,[],[],
     {"reached_nodes_only":True,"method_retained":True,"boundary_retained":True,"provenance":"hotel_B_trial_2025_ref_7830"}),
  "permissible","M2","M2: different member; conditions met.",
  mut("F21_C1","variant",["scientific.members"],"")))

cases.append(case("F21_C3","F21",
  "Hypothetical: Evidence evaluation_law is ev_hotel_2024 but request is ev_hotel_2025; single scientific coordinate mismatch.",
  rq("R21_C3","observed_decision",S21,V21),
  ev("E21_C3","observed_decision","observed_decision",m(S21,"evaluation_law","ev_hotel_2024"),V21,[],[],M21),
  "impermissible","M7",
  "M7: EVALUATION_LAW_MISMATCH; evidence law ev_hotel_2024 vs request ev_hotel_2025; single scientific coordinate changed.",
  mut("F21_C1","single_coordinate",["evidence.scientific.evaluation_law"],"evaluation_law changed")))

cases.append(case("F21_C4","F21",
  "Hypothetical: Request validity selection_mechanism is post_hoc but evidence is pre_specified; single validity coordinate mismatch.",
  rq("R21_C4","observed_decision",S21,vc("none","unconditional","fixed","single_application","exact","finite","post_hoc")),
  ev("E21_C4","observed_decision","observed_decision",S21,V21,[],[],M21),
  "impermissible","M7",
  "M7: VALIDITY_SCOPE_MISMATCH:selection_mechanism (pre_specified in evidence vs post_hoc in request); single validity coordinate changed.",
  mut("F21_C1","single_coordinate",["request.validity.selection_mechanism"],"selection_mechanism changed to post_hoc")))

# ===========================================================================
# F22 — M3 empirical_rate: sample_range and validity conditioning
# ===========================================================================
S22=sc("T22","patchtst_v1","ses_v3","MAE",["tourism_A"],[1,2,3,4,5,6],[1/6]*6,"ev_tourism_2024",[])
V22=vc("none","unconditional","fixed","design_unit","empirical","finite","pre_specified")
RM22={"design_mixture":"cluster_random","denominator":400,"sample_range":"tourism_2024_1_400","selection_record":"prereg_tourism_2024_A"}
EM22={"design_mixture":"cluster_random","denominator":400,"sample_range":"tourism_2024_1_400","selection_record":"prereg_tourism_2024_A"}

cases.append(case("F22_C1","F22",
  "Hypothetical: PatchTST v1 vs SES on monthly tourism set A, MAE, 6 horizons, 400 cluster-random series.",
  rq("R22_C1","empirical_rate",S22,V22,RM22),
  ev("E22_C1","finite_design_empirical","empirical_rate",S22,V22,[],["design matches"],EM22),
  "permissible","M3","M3: all design parameters match; empirical rate licensed.",
  mut(None,"base",[],"")))

cases.append(case("F22_C2","F22",
  "Hypothetical: Same setup set B, idx 401-800; all params updated.",
  rq("R22_C2","empirical_rate",m(S22,"members",["tourism_B"]),V22,
     {"design_mixture":"cluster_random","denominator":400,"sample_range":"tourism_2024_401_800","selection_record":"prereg_tourism_2024_B"}),
  ev("E22_C2","finite_design_empirical","empirical_rate",m(S22,"members",["tourism_B"]),V22,[],["design matches"],
     {"design_mixture":"cluster_random","denominator":400,"sample_range":"tourism_2024_401_800","selection_record":"prereg_tourism_2024_B"}),
  "permissible","M3","M3: alternate set; params consistent; licensed.",
  mut("F22_C1","variant",["scientific.members"],"")))

cases.append(case("F22_C3","F22",
  "Hypothetical: sample_range in evidence is tourism_2024_1_350 but request is tourism_2024_1_400; mismatch.",
  rq("R22_C3","empirical_rate",S22,V22,RM22),
  ev("E22_C3","finite_design_empirical","empirical_rate",S22,V22,[],[],
     {"design_mixture":"cluster_random","denominator":350,"sample_range":"tourism_2024_1_350","selection_record":"prereg_tourism_2024_A"}),
  "impermissible","M7",
  "M7/missing_side_condition: EMPIRICAL_DESIGN_MISMATCH:denominator and sample_range; M3 requires exact match.",
  mut("F22_C1","missing_side_condition",["evidence.metadata.sample_range","evidence.metadata.denominator"],"sample_range and denominator changed")))

cases.append(case("F22_C4","F22",
  "Hypothetical: Evidence validity conditioning is full_history but request is unconditional; single validity coordinate mismatch.",
  rq("R22_C4","empirical_rate",S22,V22,RM22),
  ev("E22_C4","finite_design_empirical","empirical_rate",S22,
     vc("none","full_history","fixed","design_unit","empirical","finite","pre_specified"),
     [],[],EM22),
  "impermissible","M7",
  "M7: CONDITIONING_STRENGTHENING_FORBIDDEN; evidence conditioning full_history vs request unconditional; single validity coordinate changed.",
  mut("F22_C1","single_coordinate",["evidence.validity.conditioning"],"conditioning changed to full_history")))

# ===========================================================================
# F23 — M5 coarsening: integrable_indicator + different coarsenings targets
# ===========================================================================
EV23={"indicator_id":"phi23","event_definition":"coverage_failure","upper_bound":0.05}
S23=sc("T23","timesnet_v1","arima_v5","MAE",["hospital_C"],[1,2,4,7],[0.25,0.25,0.25,0.25],"ev_hosp_2026",[0.0])
V23_fine=vc(EV23,"sub_sigma_admit","fixed","single_application","exact","finite","pre_specified")
V23_coarse=vc(EV23,"full_history","fixed","single_application","exact","finite","pre_specified")
V23_selected=vc(EV23,"selected_label","fixed","single_application","exact","finite","pre_specified")
M23_ok={"declared_coarsenings":["full_history"],"same_joint_law":True,"same_error_event":True,"integrable_indicator":True,"bound_constant_or_coarser_measurable":True}

cases.append(case("F23_C1","F23",
  "Hypothetical: Conditional bound at sub_sigma_admit coarsened to full_history for TimesNet v1. declared_coarsenings=['full_history']. All booleans true.",
  rq("R23_C1","probability_bound",S23,V23_coarse),
  ev("E23_C1","conditional_bound","probability_bound",S23,V23_fine,
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],M23_ok),
  "permissible","M5","M5: bare identifier 'full_history' in declared_coarsenings; all booleans true; licensed.",
  mut(None,"base",[],"")))

cases.append(case("F23_C2","F23",
  "Hypothetical: Same structure hospital_D; conditions met.",
  rq("R23_C2","probability_bound",m(S23,"members",["hospital_D"]),V23_coarse),
  ev("E23_C2","conditional_bound","probability_bound",m(S23,"members",["hospital_D"]),V23_fine,
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],M23_ok),
  "permissible","M5","M5: different member; conditions met.",
  mut("F23_C1","variant",["scientific.members"],"")))

cases.append(case("F23_C3","F23",
  "Hypothetical: integrable_indicator=false; M5 requires integrable indicator for tower property.",
  rq("R23_C3","probability_bound",S23,V23_coarse),
  ev("E23_C3","conditional_bound","probability_bound",S23,V23_fine,
     ["G_subset_H","same_joint_law","same_error_event"],
     ["G_subset_H","same_joint_law","same_error_event"],
     {"declared_coarsenings":["full_history"],"same_joint_law":True,"same_error_event":True,"integrable_indicator":False,"bound_constant_or_coarser_measurable":True}),
  "impermissible","M7",
  "M7/missing_side_condition: COARSENING_SIDE_CONDITION_FAILED:integrable_indicator; boolean is false.",
  mut("F23_C1","missing_side_condition",["evidence.metadata.integrable_indicator"],"integrable_indicator false")))

cases.append(case("F23_C4","F23",
  "Hypothetical: Request conditioning is selected_label; declared_coarsenings=['full_history'] does not contain 'selected_label'; coarsening not declared for this target.",
  rq("R23_C4","probability_bound",S23,V23_selected),
  ev("E23_C4","conditional_bound","probability_bound",S23,V23_fine,
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],
     {"declared_coarsenings":["full_history"],"same_joint_law":True,"same_error_event":True,"integrable_indicator":True,"bound_constant_or_coarser_measurable":True}),
  "impermissible","M7",
  "M7: CONDITIONING_STRENGTHENING_FORBIDDEN; 'selected_label' not in declared_coarsenings ['full_history']; wrong target identifier.",
  mut("F23_C1","single_coordinate",["request.validity.conditioning"],"request conditioning changed to selected_label")))

# ===========================================================================
# F24 — M4 asymptotic_theorem premises empty (FINAL_MATCHER fix)
# ===========================================================================
EV24={"indicator_id":"phi24","event_definition":"coverage_failure","upper_bound":0.10}
S24=sc("T24","itransformer_v1","naive_v6","MSE",["macro_G"],[1,4,8,12,16,20,24],[1/7]*7,"ev_macro_2026",[0.0,0.05])
V24=vc(EV24,"unconditional","fixed","single_application","asymptotic","infinite","pre_specified")

cases.append(case("F24_C1","F24",
  "Hypothetical: Asymptotic theorem for iTransformer v1 vs naive on macro_G, MSE, 7 horizons, alpha=0.10. Non-empty premises, all verified.",
  rq("R24_C1","probability_bound",S24,V24),
  ev("E24_C1","asymptotic_theorem","probability_bound",S24,V24,
     ["stationarity","mixing_conditions","moment_bounds"],
     ["stationarity","mixing_conditions","moment_bounds"],{"theorem_id":"asymp_itransformer_v1"}),
  "permissible","M4","M4: three premises declared and all verified; asymptotic bound licensed.",
  mut(None,"base",[],"")))

cases.append(case("F24_C2","F24",
  "Hypothetical: Same theorem macro_H; all consistent.",
  rq("R24_C2","probability_bound",m(S24,"members",["macro_H"]),V24),
  ev("E24_C2","asymptotic_theorem","probability_bound",m(S24,"members",["macro_H"]),V24,
     ["stationarity","mixing_conditions","moment_bounds"],
     ["stationarity","mixing_conditions","moment_bounds"],{"theorem_id":"asymp_itransformer_v1"}),
  "permissible","M4","M4: different member; premises verified; licensed.",
  mut("F24_C1","variant",["scientific.members"],"")))

cases.append(case("F24_C3","F24",
  "Hypothetical: premises list is empty; FINAL_MATCHER returns THEOREM_PREMISES_EMPTY for asymptotic_theorem.",
  rq("R24_C3","probability_bound",S24,V24),
  ev("E24_C3","asymptotic_theorem","probability_bound",S24,V24,
     [],[],{"theorem_id":"asymp_itransformer_v1"}),
  "impermissible","M7",
  "M7/missing_side_condition: THEOREM_PREMISES_EMPTY; FINAL_MATCHER requires at least one premise for asymptotic_theorem.",
  mut("F24_C1","missing_side_condition",["evidence.premises"],"premises list emptied")))

cases.append(case("F24_C4","F24",
  "Hypothetical: moment_bounds declared in premises but not in verified_assumptions.",
  rq("R24_C4","probability_bound",S24,V24),
  ev("E24_C4","asymptotic_theorem","probability_bound",S24,V24,
     ["stationarity","mixing_conditions","moment_bounds"],
     ["stationarity","mixing_conditions"],{"theorem_id":"asymp_itransformer_v1"}),
  "impermissible","M7",
  "M7/missing_side_condition: UNVERIFIED_ASSUMPTION:moment_bounds; declared in premises but absent from verified_assumptions.",
  mut("F24_C1","missing_side_condition",["evidence.verified_assumptions"],"moment_bounds not verified")))

# ===========================================================================
# F25 — M1 relative_ratio: members, horizons, weights mismatches
# ===========================================================================
S25=sc("T25","fedformer_v1","global_mean_v4","MAE",["retail_E"],[1,2,4,8],[0.25,0.25,0.25,0.25],"ev_retail_2026",[0.0,0.05])
V25=vc("none","unconditional","fixed","single_application","exact","finite","none")
M25={"pointwise_identity":True,"denominator_status":"finite_positive"}

cases.append(case("F25_C1","F25",
  "Hypothetical: FEDformer v1 vs global mean on retail_E, MAE, horizons 1/2/4/8; identical predictions; comparator MAE finite positive.",
  rq("R25_C1","relative_ratio",S25,V25),
  ev("E25_C1","structural_identity","structural_identity",S25,V25,
     ["predictions identical","comparator MAE finite positive"],
     ["predictions identical","comparator MAE finite positive"],M25),
  "permissible","M1","M1: all conditions met; relative ratio licensed.",
  mut(None,"base",[],"")))

cases.append(case("F25_C2","F25",
  "Hypothetical: Same systems retail_F; same horizons, weights, law; licensed.",
  rq("R25_C2","relative_ratio",m(S25,"members",["retail_F"]),V25),
  ev("E25_C2","structural_identity","structural_identity",m(S25,"members",["retail_F"]),V25,
     ["predictions identical","comparator MAE finite positive"],
     ["predictions identical","comparator MAE finite positive"],M25),
  "permissible","M1","M1: different member; conditions met; licensed.",
  mut("F25_C1","variant",["scientific.members"],"")))

cases.append(case("F25_C3","F25",
  "Hypothetical: Evidence horizons are [1,2,4] (3 entries) but request has [1,2,4,8] (4 entries); single scientific coordinate mismatch.",
  rq("R25_C3","relative_ratio",S25,V25),
  ev("E25_C3","structural_identity","structural_identity",
     sc("T25","fedformer_v1","global_mean_v4","MAE",["retail_E"],[1,2,4],[1/3,1/3,1/3],"ev_retail_2026",[0.0,0.05]),
     V25,["predictions identical","comparator MAE finite positive"],
     ["predictions identical","comparator MAE finite positive"],M25),
  "impermissible","M7",
  "M7: SCIENTIFIC_TARGET_MISMATCH:horizons ([1,2,4] vs [1,2,4,8]); single scientific coordinate changed.",
  mut("F25_C1","single_coordinate",["evidence.scientific.horizons","evidence.scientific.weights"],"horizons shortened")))

cases.append(case("F25_C4","F25",
  "Hypothetical: Evidence target_id is T25_alt but request is T25; single scientific sub-field mismatch.",
  rq("R25_C4","relative_ratio",S25,V25),
  ev("E25_C4","structural_identity","structural_identity",m(S25,"target_id","T25_alt"),V25,
     ["predictions identical","comparator MAE finite positive"],
     ["predictions identical","comparator MAE finite positive"],M25),
  "impermissible","M7",
  "M7: SCIENTIFIC_TARGET_MISMATCH:target_id (T25_alt vs T25); single scientific sub-field changed.",
  mut("F25_C1","single_coordinate",["evidence.scientific.target_id"],"target_id changed")))

# ===========================================================================
# F26 — M3 empirical_rate: conclusion_type mismatch (empirical_to_theorem)
# ===========================================================================
S26=sc("T26","croston_v2","naive_v7","RMSSE",["intermittent_C"],[1,2,4,8],[0.25,0.25,0.25,0.25],"ev_interm_2025",[])
V26=vc("none","unconditional","fixed","design_unit","empirical","finite","pre_specified")
RM26={"design_mixture":"simple_random","denominator":250,"sample_range":"interm_2025_1_250","selection_record":"prereg_interm_2025_C"}
EM26={"design_mixture":"simple_random","denominator":250,"sample_range":"interm_2025_1_250","selection_record":"prereg_interm_2025_C"}

cases.append(case("F26_C1","F26",
  "Hypothetical: Croston v2 vs naive v7 on intermittent set C, RMSSE, 4 horizons, 250 simple-random series.",
  rq("R26_C1","empirical_rate",S26,V26,RM26),
  ev("E26_C1","finite_design_empirical","empirical_rate",S26,V26,[],["design matches"],EM26),
  "permissible","M3","M3: all design parameters match; empirical rate licensed.",
  mut(None,"base",[],"")))

cases.append(case("F26_C2","F26",
  "Hypothetical: Same setup set D, idx 251-500; params updated consistently.",
  rq("R26_C2","empirical_rate",m(S26,"members",["intermittent_D"]),V26,
     {"design_mixture":"simple_random","denominator":250,"sample_range":"interm_2025_251_500","selection_record":"prereg_interm_2025_D"}),
  ev("E26_C2","finite_design_empirical","empirical_rate",m(S26,"members",["intermittent_D"]),V26,
     [],["design matches"],
     {"design_mixture":"simple_random","denominator":250,"sample_range":"interm_2025_251_500","selection_record":"prereg_interm_2025_D"}),
  "permissible","M3","M3: alternate set; params consistent; licensed.",
  mut("F26_C1","variant",["scientific.members"],"")))

cases.append(case("F26_C3","F26",
  "Hypothetical: Request conclusion_type is probability_bound; evidence is finite_design_empirical; EMPIRICAL_TO_THEOREM_FORBIDDEN fires.",
  rq("R26_C3","probability_bound",S26,vc({"indicator_id":"phi26","event_definition":"coverage_failure","upper_bound":0.05},"unconditional","fixed","single_application","exact","finite","pre_specified"),RM26),
  ev("E26_C3","finite_design_empirical","empirical_rate",S26,V26,[],[],EM26),
  "impermissible","M7",
  "M7/type_mismatch: EMPIRICAL_TO_THEOREM_FORBIDDEN; finite_design_empirical cannot license probability_bound.",
  mut("F26_C1","type_mismatch",["request.conclusion_type"],"request elevated to probability_bound")))

cases.append(case("F26_C4","F26",
  "Hypothetical: Evidence scientific loss is MAE but request is RMSSE; single scientific coordinate mismatch.",
  rq("R26_C4","empirical_rate",S26,V26,RM26),
  ev("E26_C4","finite_design_empirical","empirical_rate",m(S26,"loss","MAE"),V26,[],[],EM26),
  "impermissible","M7",
  "M7: SCIENTIFIC_TARGET_MISMATCH:loss (MAE vs RMSSE); single scientific coordinate changed.",
  mut("F26_C1","single_coordinate",["evidence.scientific.loss"],"loss changed to MAE")))

# ===========================================================================
# F27 — M4 theorem, selected_object and comparator mismatches
# ===========================================================================
EV27={"indicator_id":"phi27","event_definition":"coverage_failure","upper_bound":0.05}
S27=sc("T27","tide_v1","global_mean_v5","RMSE",["solar_C"],[1,2,4,8,12,24],[1/6]*6,"ev_solar_2026",[0.0,0.02])
V27=vc(EV27,"unconditional","fixed","single_application","exact","finite","pre_specified")

cases.append(case("F27_C1","F27",
  "Hypothetical: Exact theorem for TiDE v1 vs global mean on solar_C, RMSE, 6 horizons, alpha=0.05. All premises verified.",
  rq("R27_C1","probability_bound",S27,V27),
  ev("E27_C1","theorem","probability_bound",S27,V27,
     ["iid_residuals","score_bounded","prespecified_threshold"],
     ["iid_residuals","score_bounded","prespecified_threshold"],{"theorem_id":"exact_tide_v1"}),
  "permissible","M4","M4: all coordinates match; premises declared and verified; exact bound licensed.",
  mut(None,"base",[],"")))

cases.append(case("F27_C2","F27",
  "Hypothetical: Same theorem solar_D; all consistent.",
  rq("R27_C2","probability_bound",m(S27,"members",["solar_D"]),V27),
  ev("E27_C2","theorem","probability_bound",m(S27,"members",["solar_D"]),V27,
     ["iid_residuals","score_bounded","prespecified_threshold"],
     ["iid_residuals","score_bounded","prespecified_threshold"],{"theorem_id":"exact_tide_v1"}),
  "permissible","M4","M4: different member; premises verified; licensed.",
  mut("F27_C1","variant",["scientific.members"],"")))

cases.append(case("F27_C3","F27",
  "Hypothetical: Evidence selected_object is tide_v2 but request is tide_v1; single scientific coordinate mismatch.",
  rq("R27_C3","probability_bound",S27,V27),
  ev("E27_C3","theorem","probability_bound",m(S27,"selected_object","tide_v2"),V27,
     ["iid_residuals","score_bounded","prespecified_threshold"],
     ["iid_residuals","score_bounded","prespecified_threshold"],{"theorem_id":"exact_tide_v2"}),
  "impermissible","M7",
  "M7: SCIENTIFIC_TARGET_MISMATCH:selected_object (tide_v2 vs tide_v1); single scientific coordinate changed.",
  mut("F27_C1","single_coordinate",["evidence.scientific.selected_object"],"selected_object changed")))

cases.append(case("F27_C4","F27",
  "Hypothetical: Evidence comparator is seas_naive_v6 but request is global_mean_v5; single scientific coordinate mismatch.",
  rq("R27_C4","probability_bound",S27,V27),
  ev("E27_C4","theorem","probability_bound",m(S27,"comparator","seas_naive_v6"),V27,
     ["iid_residuals","score_bounded","prespecified_threshold"],
     ["iid_residuals","score_bounded","prespecified_threshold"],{"theorem_id":"exact_tide_v1_seas"}),
  "impermissible","M7",
  "M7: SCIENTIFIC_TARGET_MISMATCH:comparator (seas_naive_v6 vs global_mean_v5); single scientific coordinate changed.",
  mut("F27_C1","single_coordinate",["evidence.scientific.comparator"],"comparator changed")))

# ===========================================================================
# F28 — M2 observed_decision: multi-coordinate and type invalids
# ===========================================================================
S28=sc("T28","wavenet_v1","arima_v6","MAPE",["transport_C"],[1,2,4,8,12,24],[1/6]*6,"ev_transport_2026",[])
V28=vc("none","unconditional","fixed","single_application","exact","finite","pre_specified")
M28={"reached_nodes_only":True,"method_retained":True,"boundary_retained":True,"provenance":"transport_C_trial_2026_id_4421"}

cases.append(case("F28_C1","F28",
  "Hypothetical: WaveNet v1 vs ARIMA on transport_C, MAPE, 6 horizons. Pre-specified trial; all M2 conditions satisfied.",
  rq("R28_C1","observed_decision",S28,V28),
  ev("E28_C1","observed_decision","observed_decision",S28,V28,[],[],M28),
  "permissible","M2","M2: all side conditions true; provenance non-empty; literal decision licensed.",
  mut(None,"base",[],"")))

cases.append(case("F28_C2","F28",
  "Hypothetical: Same protocol transport_D; conditions met.",
  rq("R28_C2","observed_decision",m(S28,"members",["transport_D"]),V28),
  ev("E28_C2","observed_decision","observed_decision",m(S28,"members",["transport_D"]),V28,[],[],
     {"reached_nodes_only":True,"method_retained":True,"boundary_retained":True,"provenance":"transport_D_trial_2026_id_4422"}),
  "permissible","M2","M2: different member; conditions met.",
  mut("F28_C1","variant",["scientific.members"],"")))

cases.append(case("F28_C3","F28",
  "Hypothetical: Evidence loss is RMSE AND evaluation_law is ev_transport_2025; two scientific coordinates changed — multi_coordinate.",
  rq("R28_C3","observed_decision",S28,V28),
  ev("E28_C3","observed_decision","observed_decision",
     sc("T28","wavenet_v1","arima_v6","RMSE",["transport_C"],[1,2,4,8,12,24],[1/6]*6,"ev_transport_2025",[]),
     V28,[],[],M28),
  "impermissible","M7",
  "M7: multiple scientific coordinates differ (loss: RMSE vs MAPE; evaluation_law: 2025 vs 2026); multi_coordinate invalid.",
  mut("F28_C1","multi_coordinate",["evidence.scientific.loss","evidence.scientific.evaluation_law"],"loss and law changed")))

cases.append(case("F28_C4","F28",
  "Hypothetical: provenance is a whitespace-only string; FINAL_MATCHER rejects whitespace-only provenance.",
  rq("R28_C4","observed_decision",S28,V28),
  ev("E28_C4","observed_decision","observed_decision",S28,V28,[],[],
     {"reached_nodes_only":True,"method_retained":True,"boundary_retained":True,"provenance":"   "}),
  "impermissible","M7",
  "M7/missing_side_condition: OBSERVED_COPY_PROVENANCE_MISSING; provenance is whitespace-only after strip; FINAL_MATCHER rejects.",
  mut("F28_C1","missing_side_condition",["evidence.metadata.provenance"],"provenance whitespace-only")))

# ===========================================================================
# F29 — M5 coarsening: multiple valid coarsening targets in declared_coarsenings
# ===========================================================================
EV29={"indicator_id":"phi29","event_definition":"coverage_failure","upper_bound":0.05}
S29=sc("T29","crossformer_v1","naive_v8","MAE",["macro_I"],[1,4,8,12],[0.25,0.25,0.25,0.25],"ev_macro_2027",[0.0])
V29_fine=vc(EV29,"sub_sigma_trend","fixed","single_application","exact","finite","pre_specified")
V29_fh=vc(EV29,"full_history","fixed","single_application","exact","finite","pre_specified")
V29_sl=vc(EV29,"selected_label","fixed","single_application","exact","finite","pre_specified")
# Multiple targets declared: both full_history and selected_label are valid coarsening targets
M29_multi={"declared_coarsenings":["full_history","selected_label"],"same_joint_law":True,"same_error_event":True,"integrable_indicator":True,"bound_constant_or_coarser_measurable":True}

cases.append(case("F29_C1","F29",
  "Hypothetical: Conditional bound at sub_sigma_trend. declared_coarsenings=['full_history','selected_label']. Request targets full_history; bare identifier present. All booleans true.",
  rq("R29_C1","probability_bound",S29,V29_fh),
  ev("E29_C1","conditional_bound","probability_bound",S29,V29_fine,
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],M29_multi),
  "permissible","M5","M5: 'full_history' found in declared_coarsenings; all booleans true; licensed.",
  mut(None,"base",[],"")))

cases.append(case("F29_C2","F29",
  "Hypothetical: Same setup; request targets selected_label; 'selected_label' also present in declared_coarsenings.",
  rq("R29_C2","probability_bound",S29,V29_sl),
  ev("E29_C2","conditional_bound","probability_bound",S29,V29_fine,
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],M29_multi),
  "permissible","M5","M5: 'selected_label' found in declared_coarsenings; all booleans true; licensed.",
  mut("F29_C1","variant",["request.validity.conditioning"],"")))

cases.append(case("F29_C3","F29",
  "Hypothetical: Request targets unconditional; declared_coarsenings=['full_history','selected_label'] does not contain 'unconditional'.",
  rq("R29_C3","probability_bound",S29,vc(EV29,"unconditional","fixed","single_application","exact","finite","pre_specified")),
  ev("E29_C3","conditional_bound","probability_bound",S29,V29_fine,
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],
     ["G_subset_H","same_joint_law","same_error_event","integrable_indicator"],M29_multi),
  "impermissible","M7",
  "M7: CONDITIONING_STRENGTHENING_FORBIDDEN; 'unconditional' not found in declared_coarsenings; coarsening not licensed.",
  mut("F29_C1","single_coordinate",["request.validity.conditioning"],"request conditioning changed to unconditional")))

cases.append(case("F29_C4","F29",
  "Hypothetical: same_joint_law=false; M5 requires same_joint_law=true regardless of declared_coarsenings.",
  rq("R29_C4","probability_bound",S29,V29_fh),
  ev("E29_C4","conditional_bound","probability_bound",S29,V29_fine,
     ["G_subset_H","same_error_event","integrable_indicator"],
     ["G_subset_H","same_error_event","integrable_indicator"],
     {"declared_coarsenings":["full_history","selected_label"],"same_joint_law":False,"same_error_event":True,"integrable_indicator":True,"bound_constant_or_coarser_measurable":True}),
  "impermissible","M7",
  "M7/missing_side_condition: COARSENING_SIDE_CONDITION_FAILED:same_joint_law; boolean false despite correct declared_coarsenings.",
  mut("F29_C1","missing_side_condition",["evidence.metadata.same_joint_law"],"same_joint_law false")))

# ===========================================================================
# F30 — M4 theorem: coverage_unit and support_mode mismatches
# ===========================================================================
EV30={"indicator_id":"phi30","event_definition":"coverage_failure","upper_bound":0.05}
S30=sc("T30","dlinear_v1","naive_v9","RMSE",["retail_G"],[1,2,4],[1/3,1/3,1/3],"ev_retail_2027",[0.0,0.02])
V30_single=vc(EV30,"unconditional","fixed","single_application","exact","finite","pre_specified")
V30_cohort=vc(EV30,"unconditional","fixed","cohort","exact","finite","pre_specified")
V30_asymp=vc(EV30,"unconditional","fixed","single_application","asymptotic","infinite","pre_specified")

cases.append(case("F30_C1","F30",
  "Hypothetical: Exact theorem for DLinear v1 vs naive on retail_G, RMSE, 3 horizons, single_application coverage. All premises verified.",
  rq("R30_C1","probability_bound",S30,V30_single),
  ev("E30_C1","theorem","probability_bound",S30,V30_single,
     ["exchangeability","score_function_bounded"],
     ["exchangeability","score_function_bounded"],{"theorem_id":"exact_dlinear_v1"}),
  "permissible","M4","M4: all coordinates match; premises verified; exact single_application bound licensed.",
  mut(None,"base",[],"")))

cases.append(case("F30_C2","F30",
  "Hypothetical: Same theorem retail_H; all consistent.",
  rq("R30_C2","probability_bound",m(S30,"members",["retail_H"]),V30_single),
  ev("E30_C2","theorem","probability_bound",m(S30,"members",["retail_H"]),V30_single,
     ["exchangeability","score_function_bounded"],
     ["exchangeability","score_function_bounded"],{"theorem_id":"exact_dlinear_v1"}),
  "permissible","M4","M4: different member; premises verified; licensed.",
  mut("F30_C1","variant",["scientific.members"],"")))

cases.append(case("F30_C3","F30",
  "Hypothetical: Evidence coverage_unit is cohort but request is single_application; distinct validity scopes.",
  rq("R30_C3","probability_bound",S30,V30_single),
  ev("E30_C3","theorem","probability_bound",S30,V30_cohort,
     ["exchangeability","score_function_bounded"],
     ["exchangeability","score_function_bounded"],{"theorem_id":"exact_dlinear_v1_cohort"}),
  "impermissible","M7",
  "M7: VALIDITY_SCOPE_MISMATCH:coverage_unit (cohort vs single_application); single validity coordinate changed.",
  mut("F30_C1","single_coordinate",["evidence.validity.coverage_unit"],"coverage_unit changed to cohort")))

cases.append(case("F30_C4","F30",
  "Hypothetical: Evidence is asymptotic_theorem with asymptotic/infinite support_mode; request asks for exact/finite; ASYMPTOTIC_TO_FINITE_EXACTNESS_FORBIDDEN.",
  rq("R30_C4","probability_bound",S30,V30_single),
  ev("E30_C4","asymptotic_theorem","probability_bound",S30,V30_asymp,
     ["stationarity","consistency"],["stationarity","consistency"],{"theorem_id":"asymp_dlinear_v1"}),
  "impermissible","M7",
  "M7: ASYMPTOTIC_TO_FINITE_EXACTNESS_FORBIDDEN; asymptotic_theorem with asymptotic support_mode cannot license exact finite-sample request.",
  mut("F30_C1","type_mismatch",["evidence.kind","evidence.validity.support_mode","evidence.validity.sample_regime"],"kind changed to asymptotic_theorem")))

# ===========================================================================
# F31 — M6 fixed_sequence: stop_at_first_valid_nonrejection and no_true_null
# ===========================================================================
EV31={"indicator_id":"phi31","event_definition":"sequential_type1_error","upper_bound":0.05}
S31=sc("T31","autoformer_v2","seas_naive_v6","MAE",["macro_J"],[1,4,8,12],[0.25,0.25,0.25,0.25],"ev_macro_2025",[0.0,0.02,0.05])
V31=vc(EV31,"full_history","fixed","single_application","exact","finite","pre_specified")
M31={"potential_tests_defined":True,"ordered_family":True,"stop_at_first_valid_nonrejection":True,"no_true_null_convention":True,"invalid_policy":"whole_request_unresolved"}

cases.append(case("F31_C1","F31",
  "Hypothetical: Autoformer v2 vs seasonal naive on macro_J, MAE, sequential 3-threshold family. All M6 conditions satisfied.",
  rq("R31_C1","fixed_sequence_error_bound",S31,V31),
  ev("E31_C1","local_validity_family","local_node_bounds",S31,V31,
     ["truth_events_measurable","local_bounds_hold"],["truth_events_measurable","local_bounds_hold"],M31),
  "permissible","M6","M6: all conditions met; licensed.",
  mut(None,"base",[],"")))

cases.append(case("F31_C2","F31",
  "Hypothetical: Same family macro_K; all conditions consistent.",
  rq("R31_C2","fixed_sequence_error_bound",m(S31,"members",["macro_K"]),V31),
  ev("E31_C2","local_validity_family","local_node_bounds",m(S31,"members",["macro_K"]),V31,
     ["truth_events_measurable","local_bounds_hold"],["truth_events_measurable","local_bounds_hold"],M31),
  "permissible","M6","M6: different member; conditions met.",
  mut("F31_C1","variant",["scientific.members"],"")))

cases.append(case("F31_C3","F31",
  "Hypothetical: stop_at_first_valid_nonrejection=false; procedure continues after first valid non-rejection.",
  rq("R31_C3","fixed_sequence_error_bound",S31,V31),
  ev("E31_C3","local_validity_family","local_node_bounds",S31,V31,
     ["truth_events_measurable","local_bounds_hold"],["truth_events_measurable","local_bounds_hold"],
     {"potential_tests_defined":True,"ordered_family":True,"stop_at_first_valid_nonrejection":False,"no_true_null_convention":True,"invalid_policy":"whole_request_unresolved"}),
  "impermissible","M7",
  "M7/missing_side_condition: FIXED_SEQUENCE_SIDE_CONDITION_FAILED:stop_at_first_valid_nonrejection; boolean false.",
  mut("F31_C1","missing_side_condition",["evidence.metadata.stop_at_first_valid_nonrejection"],"stop_at_first_valid_nonrejection false")))

cases.append(case("F31_C4","F31",
  "Hypothetical: no_true_null_convention=false; M6 requires this convention.",
  rq("R31_C4","fixed_sequence_error_bound",S31,V31),
  ev("E31_C4","local_validity_family","local_node_bounds",S31,V31,
     ["truth_events_measurable","local_bounds_hold"],["truth_events_measurable","local_bounds_hold"],
     {"potential_tests_defined":True,"ordered_family":True,"stop_at_first_valid_nonrejection":True,"no_true_null_convention":False,"invalid_policy":"whole_request_unresolved"}),
  "impermissible","M7",
  "M7/missing_side_condition: FIXED_SEQUENCE_SIDE_CONDITION_FAILED:no_true_null_convention; boolean false.",
  mut("F31_C1","missing_side_condition",["evidence.metadata.no_true_null_convention"],"no_true_null_convention false")))

# ===========================================================================
# F32 — M3 empirical_rate: validity law_quantifier and sample_regime mismatches
# ===========================================================================
S32=sc("T32","informer_v1","arima_v7","RMSE",["elec_hourly_A"],[1,6,12,24],[0.25,0.25,0.25,0.25],"ev_elec_2025",[])
V32=vc("none","unconditional","fixed","design_unit","empirical","finite","pre_specified")
RM32={"design_mixture":"simple_random","denominator":200,"sample_range":"elec_hourly_2025_1_200","selection_record":"prereg_elec_2025_A"}
EM32={"design_mixture":"simple_random","denominator":200,"sample_range":"elec_hourly_2025_1_200","selection_record":"prereg_elec_2025_A"}

cases.append(case("F32_C1","F32",
  "Hypothetical: Informer v1 vs ARIMA on electricity hourly set A, RMSE, 4 horizons, 200 simple-random series.",
  rq("R32_C1","empirical_rate",S32,V32,RM32),
  ev("E32_C1","finite_design_empirical","empirical_rate",S32,V32,[],["design matches"],EM32),
  "permissible","M3","M3: all design parameters match; empirical rate licensed.",
  mut(None,"base",[],"")))

cases.append(case("F32_C2","F32",
  "Hypothetical: Same setup set B, idx 201-400; params updated.",
  rq("R32_C2","empirical_rate",m(S32,"members",["elec_hourly_B"]),V32,
     {"design_mixture":"simple_random","denominator":200,"sample_range":"elec_hourly_2025_201_400","selection_record":"prereg_elec_2025_B"}),
  ev("E32_C2","finite_design_empirical","empirical_rate",m(S32,"members",["elec_hourly_B"]),V32,
     [],["design matches"],
     {"design_mixture":"simple_random","denominator":200,"sample_range":"elec_hourly_2025_201_400","selection_record":"prereg_elec_2025_B"}),
  "permissible","M3","M3: alternate set; params consistent; licensed.",
  mut("F32_C1","variant",["scientific.members"],"")))

cases.append(case("F32_C3","F32",
  "Hypothetical: Request validity law_quantifier is universal; evidence is fixed; single validity coordinate mismatch.",
  rq("R32_C3","empirical_rate",S32,vc("none","unconditional","universal","design_unit","empirical","finite","pre_specified"),RM32),
  ev("E32_C3","finite_design_empirical","empirical_rate",S32,V32,[],[],EM32),
  "impermissible","M7",
  "M7: VALIDITY_SCOPE_MISMATCH:law_quantifier (universal in request vs fixed in evidence); single validity coordinate changed.",
  mut("F32_C1","single_coordinate",["request.validity.law_quantifier"],"law_quantifier changed to universal")))

cases.append(case("F32_C4","F32",
  "Hypothetical: Request validity sample_regime is infinite; evidence is finite; single validity coordinate mismatch.",
  rq("R32_C4","empirical_rate",S32,vc("none","unconditional","fixed","design_unit","empirical","infinite","pre_specified"),RM32),
  ev("E32_C4","finite_design_empirical","empirical_rate",S32,V32,[],[],EM32),
  "impermissible","M7",
  "M7: VALIDITY_SCOPE_MISMATCH:sample_regime (infinite in request vs finite in evidence); single validity coordinate changed.",
  mut("F32_C1","single_coordinate",["request.validity.sample_regime"],"sample_regime changed to infinite")))

# ===========================================================================
# F33 — M1 structural_identity: multi-coordinate invalids + error_event check
# ===========================================================================
S33=sc("T33","gpt4ts_v1","naive_v10","MASE",["finance_A"],[1,2,4,8,16],[0.2,0.2,0.2,0.2,0.2],"ev_finance_2026",[])
EV33={"indicator_id":"phi33","event_definition":"coverage_failure","upper_bound":0.05}
V33=vc("none","unconditional","fixed","single_application","exact","finite","pre_specified")
V33_ev=vc(EV33,"unconditional","fixed","single_application","exact","finite","pre_specified")

cases.append(case("F33_C1","F33",
  "Hypothetical: GPT4TS v1 and naive v10 produce identical 5-horizon financial forecasts on finance_A. Author claims structural identity under MASE.",
  rq("R33_C1","structural_identity",S33,V33),
  ev("E33_C1","structural_identity","structural_identity",S33,V33,
     ["predictions identical"],["predictions identical"],{"pointwise_identity":True}),
  "permissible","M1","M1: all coordinates match; pointwise_identity=true; structural identity licensed.",
  mut(None,"base",[],"")))

cases.append(case("F33_C2","F33",
  "Hypothetical: Same systems finance_B; identity confirmed.",
  rq("R33_C2","structural_identity",m(S33,"members",["finance_B"]),V33),
  ev("E33_C2","structural_identity","structural_identity",m(S33,"members",["finance_B"]),V33,
     ["predictions identical"],["predictions identical"],{"pointwise_identity":True}),
  "permissible","M1","M1: different member; identity confirmed; licensed.",
  mut("F33_C1","variant",["scientific.members"],"")))

cases.append(case("F33_C3","F33",
  "Hypothetical: Evidence comparator is arima_v8 (not naive_v10) AND loss is MAE (not MASE); two scientific coordinates changed — multi_coordinate.",
  rq("R33_C3","structural_identity",S33,V33),
  ev("E33_C3","structural_identity","structural_identity",
     sc("T33","gpt4ts_v1","arima_v8","MAE",["finance_A"],[1,2,4,8,16],[0.2,0.2,0.2,0.2,0.2],"ev_finance_2026",[]),
     V33,["predictions identical"],["predictions identical"],{"pointwise_identity":True}),
  "impermissible","M7",
  "M7: multiple scientific coordinates differ (comparator: arima_v8 vs naive_v10; loss: MAE vs MASE); multi_coordinate invalid.",
  mut("F33_C1","multi_coordinate",["evidence.scientific.comparator","evidence.scientific.loss"],"comparator and loss changed")))

cases.append(case("F33_C4","F33",
  "Hypothetical: Request validity error_event is a structured object but evidence validity error_event is 'none' (string); ERROR_EVENT_MISMATCH.",
  rq("R33_C4","structural_identity",S33,V33_ev),
  ev("E33_C4","structural_identity","structural_identity",S33,V33,
     ["predictions identical"],["predictions identical"],{"pointwise_identity":True}),
  "impermissible","M7",
  "M7: ERROR_EVENT_MISMATCH; request error_event is structured object but evidence error_event is string 'none'; single validity coordinate changed.",
  mut("F33_C1","single_coordinate",["request.validity.error_event"],"error_event changed to structured object in request")))

# ===========================================================================
# F34 — M5 coarsening: same-conditioning branch (treated as M4-like theorem)
# ===========================================================================
EV34={"indicator_id":"phi34","event_definition":"coverage_failure","upper_bound":0.05}
S34=sc("T34","spacetimeformer_v1","naive_v11","RMSE",["traffic_E"],[1,2,4,8],[0.25,0.25,0.25,0.25],"ev_traffic_2026",[0.0])
V34=vc(EV34,"full_history","fixed","single_application","exact","finite","pre_specified")
# When source==target conditioning, M5 branch treats as M4-like: checks premises only
M34_same={"declared_coarsenings":[],"same_joint_law":True,"same_error_event":True,"integrable_indicator":True,"bound_constant_or_coarser_measurable":True}

cases.append(case("F34_C1","F34",
  "Hypothetical: conditional_bound evidence with same conditioning as request (full_history == full_history). No coarsening occurs; checker applies M4-like verification: premises must be satisfied.",
  rq("R34_C1","probability_bound",S34,V34),
  ev("E34_C1","conditional_bound","probability_bound",S34,V34,
     ["full_history_measurability","iid_conditional"],
     ["full_history_measurability","iid_conditional"],M34_same),
  "permissible","M4",
  "M5/same-conditioning branch: source==target==full_history; checker treats as M4_THEOREM_INSTANTIATION after verifying premises; licensed.",
  mut(None,"base",[],"")))

cases.append(case("F34_C2","F34",
  "Hypothetical: Same structure traffic_F; same conditioning; premises verified.",
  rq("R34_C2","probability_bound",m(S34,"members",["traffic_F"]),V34),
  ev("E34_C2","conditional_bound","probability_bound",m(S34,"members",["traffic_F"]),V34,
     ["full_history_measurability","iid_conditional"],
     ["full_history_measurability","iid_conditional"],M34_same),
  "permissible","M4","M5/same-conditioning branch: different member; premises verified; licensed.",
  mut("F34_C1","variant",["scientific.members"],"")))

cases.append(case("F34_C3","F34",
  "Hypothetical: Same conditioning but iid_conditional declared in premises and absent from verified_assumptions.",
  rq("R34_C3","probability_bound",S34,V34),
  ev("E34_C3","conditional_bound","probability_bound",S34,V34,
     ["full_history_measurability","iid_conditional"],
     ["full_history_measurability"],M34_same),
  "impermissible","M7",
  "M7/missing_side_condition: UNVERIFIED_ASSUMPTION:iid_conditional in same-conditioning conditional_bound branch; premise declared but not verified.",
  mut("F34_C1","missing_side_condition",["evidence.verified_assumptions"],"iid_conditional not verified")))

cases.append(case("F34_C4","F34",
  "Hypothetical: Evidence scientific members is ['traffic_E','traffic_F'] but request specifies ['traffic_E'] only; single scientific coordinate mismatch.",
  rq("R34_C4","probability_bound",S34,V34),
  ev("E34_C4","conditional_bound","probability_bound",
     sc("T34","spacetimeformer_v1","naive_v11","RMSE",["traffic_E","traffic_F"],[1,2,4,8],[0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125],"ev_traffic_2026",[0.0]),
     V34,["full_history_measurability","iid_conditional"],["full_history_measurability","iid_conditional"],M34_same),
  "impermissible","M7",
  "M7: SCIENTIFIC_TARGET_MISMATCH:members (['traffic_E','traffic_F'] vs ['traffic_E']); single scientific coordinate changed.",
  mut("F34_C1","single_coordinate",["evidence.scientific.members","evidence.scientific.weights"],"members extended")))

# ===========================================================================
# F35 — Mixed: M3 empirical_rate type mismatch + M4 conclusion_type mismatch
# ===========================================================================
EV35={"indicator_id":"phi35","event_definition":"coverage_failure","upper_bound":0.05}
S35=sc("T35","patchtst_v2","ses_v4","MAE",["tourism_C"],[1,2,3,4,6,12],[1/6]*6,"ev_tourism_2025",[0.0,0.05])
V35_emp=vc("none","unconditional","fixed","design_unit","empirical","finite","pre_specified")
V35_prob=vc(EV35,"unconditional","fixed","single_application","exact","finite","pre_specified")
RM35={"design_mixture":"simple_random","denominator":300,"sample_range":"tourism_2025_1_300","selection_record":"prereg_tourism_2025_C"}
EM35={"design_mixture":"simple_random","denominator":300,"sample_range":"tourism_2025_1_300","selection_record":"prereg_tourism_2025_C"}

cases.append(case("F35_C1","F35",
  "Hypothetical: PatchTST v2 vs SES on monthly tourism set C, MAE, 6 horizons, 300 pre-registered series, simple random design.",
  rq("R35_C1","empirical_rate",S35,V35_emp,RM35),
  ev("E35_C1","finite_design_empirical","empirical_rate",S35,V35_emp,[],["design matches"],EM35),
  "permissible","M3","M3: all design parameters match; empirical rate licensed.",
  mut(None,"base",[],"")))

cases.append(case("F35_C2","F35",
  "Hypothetical: Same setup set D; params updated consistently.",
  rq("R35_C2","empirical_rate",m(S35,"members",["tourism_D"]),V35_emp,
     {"design_mixture":"simple_random","denominator":300,"sample_range":"tourism_2025_301_600","selection_record":"prereg_tourism_2025_D"}),
  ev("E35_C2","finite_design_empirical","empirical_rate",m(S35,"members",["tourism_D"]),V35_emp,
     [],["design matches"],
     {"design_mixture":"simple_random","denominator":300,"sample_range":"tourism_2025_301_600","selection_record":"prereg_tourism_2025_D"}),
  "permissible","M3","M3: alternate set; params consistent; licensed.",
  mut("F35_C1","variant",["scientific.members"],"")))

cases.append(case("F35_C3","F35",
  "Hypothetical: Request conclusion_type is fixed_sequence_error_bound; evidence is finite_design_empirical; EMPIRICAL_TO_THEOREM_FORBIDDEN fires.",
  rq("R35_C3","fixed_sequence_error_bound",S35,vc(EV35,"full_history","fixed","single_application","exact","finite","pre_specified"),RM35),
  ev("E35_C3","finite_design_empirical","empirical_rate",S35,V35_emp,[],[],EM35),
  "impermissible","M7",
  "M7/type_mismatch: EMPIRICAL_TO_THEOREM_FORBIDDEN; finite_design_empirical cannot license fixed_sequence_error_bound.",
  mut("F35_C1","type_mismatch",["request.conclusion_type","request.validity"],"request elevated to fixed_sequence_error_bound")))

cases.append(case("F35_C4","F35",
  "Hypothetical: Request conclusion_type is probability_bound with structured error_event; evidence is theorem but conclusion_type in evidence is empirical_rate; CONCLUSION_TYPE_MISMATCH.",
  rq("R35_C4","probability_bound",S35,V35_prob),
  ev("E35_C4","theorem","empirical_rate",S35,V35_prob,
     ["premise_one"],["premise_one"],{"theorem_id":"mislabeled_theorem"}),
  "impermissible","M7",
  "M7/type_mismatch: CONCLUSION_TYPE_MISMATCH; evidence conclusion_type empirical_rate vs required probability_bound for theorem evidence; single coordinate changed.",
  mut("F35_C1","type_mismatch",["evidence.kind","evidence.conclusion_type","request.conclusion_type","request.validity"],"evidence kind changed to theorem with wrong conclusion_type")))

# ===========================================================================
# OUTPUT
# ===========================================================================
assert len(cases) == 140, f"Expected 140 cases, got {len(cases)}"
ids = [c["case_id"] for c in cases]
assert len(set(ids)) == 140, "Duplicate case IDs"
fams = {}
for c in cases: fams.setdefault(c["family_id"],[]).append(c)
assert len(fams) == 35, f"Expected 35 families, got {len(fams)}"
assert all(len(v)==4 for v in fams.values()), "Not all families have 4 cases"

import collections
disp = collections.Counter(c["expected_disposition"] for c in cases)
rule = collections.Counter(c["primary_rule"] for c in cases)

with open(OUT,"w") as f:
    for c in cases:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")

print(f"Written {len(cases)} cases to {OUT}")
print("Disposition:", dict(disp))
print("Primary rule:", dict(rule))
print("Families:", len(fams))
