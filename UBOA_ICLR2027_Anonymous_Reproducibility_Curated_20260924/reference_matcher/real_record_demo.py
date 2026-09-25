#!/usr/bin/env python3
"""Retrospective matcher demonstration using only hand-authored saved-record metadata."""
from __future__ import annotations
import copy, json
from matcher import match

def request(conclusion="probability_bound", support="finite_sample_exact"):
    return {"request_id":"REAL_DEMO","conclusion_type":conclusion,
      "scientific":{"target_id":"selected_rule_relative_loss","selected_object":"mean_last_three","comparator":"last_value","loss":"absolute_error","members":["frozen_scope"],"horizons":["frozen_horizons"],"weights":[1.0],"evaluation_law":"saved_real_record_law","thresholds":[0.0,0.02,0.05]},
      "validity":{"error_event":"any_false_promotion_in_request","conditioning":"full_history","law_quantifier":"saved_application_law","coverage_unit":"one_request","support_mode":support,"sample_regime":"saved_real_record","selection_mechanism":"selected_procedure"}}

def evidence(method_retained=True):
    r=request()
    return {"evidence_id":"SAVED_OBSERVED_DECISION","kind":"observed_decision","conclusion_type":"observed_decision","scientific":copy.deepcopy(r["scientific"]),"validity":{**copy.deepcopy(r["validity"]),"support_mode":"observed_record"},"premises":[],"verified_assumptions":[],"metadata":{"reached_nodes_only":True,"method_retained":method_retained,"boundary_retained":True}}

def main():
    out=[]
    for app in ("Weather","ETTm2"):
        r=request(); r["request_id"]=app+"_FULL_HISTORY"
        out.append({"application":app,"case":"observed_to_full_history_guarantee","result":match(r,evidence(True))})
        r=request("observed_decision","observed_record"); r["request_id"]=app+"_ORIGINAL_METHOD_COPY"
        out.append({"application":app,"case":"original_method_copy","result":match(r,evidence(False))})
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
