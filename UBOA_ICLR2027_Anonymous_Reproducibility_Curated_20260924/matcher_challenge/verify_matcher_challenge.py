#!/usr/bin/env python3
import json, importlib.util, pathlib, collections, hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
CH=pathlib.Path(__file__).resolve().parent

def load_mod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def schema_presence(c):
    r,e=c['request'],c['evidence']
    if not isinstance(r,dict) or not isinstance(e,dict): return False
    for k in ('request_id','conclusion_type','scientific','validity'):
        if k not in r:return False
    for k in ('evidence_id','kind','conclusion_type','scientific','validity','premises','verified_assumptions','metadata'):
        if k not in e:return False
    sf=('target_id','selected_object','comparator','loss','members','horizons','weights','evaluation_law','thresholds')
    vf=('error_event','conditioning','law_quantifier','coverage_unit','support_mode','sample_regime','selection_mechanism')
    return all(k in r['scientific'] and k in e['scientific'] for k in sf) and all(k in r['validity'] and k in e['validity'] for k in vf)

def coord_equal(c):
    if not schema_presence(c): return False
    sf=('target_id','selected_object','comparator','loss','members','horizons','weights','evaluation_law','thresholds')
    vf=('error_event','conditioning','law_quantifier','coverage_unit','support_mode','sample_regime','selection_mechanism')
    r,e=c['request'],c['evidence']
    return all(r['scientific'][k]==e['scientific'][k] for k in sf) and all(r['validity'][k]==e['validity'][k] for k in vf)

cases=[json.loads(x) for x in (CH/'CHALLENGE_V3_FROZEN.jsonl').read_text().splitlines() if x.strip()]
final=load_mod('final_matcher',ROOT/'matcher_final'/'matcher.py')
original=load_mod('original_matcher',ROOT/'reference_matcher_original'/'matcher.py')
systems={
 'finalized_matcher':lambda c: final.match(c['request'],c['evidence'])['status']=='ESTABLISHED',
 'original_matcher':lambda c: original.match(c['request'],c['evidence'])['status']=='ESTABLISHED',
 'schema_presence':schema_presence,
 'coordinate_equality':coord_equal,
}
summary={}
for name,fn in systems.items():
    tp=tn=fp=fnn=0; errors=[]
    for c in cases:
        pred=bool(fn(c)); gold=c['expected_disposition']=='permissible'
        if gold and pred: tp+=1
        elif gold and not pred: fnn+=1; errors.append(c['case_id'])
        elif not gold and pred: fp+=1; errors.append(c['case_id'])
        else: tn+=1
    summary[name]={'TP':tp,'TN':tn,'FA':fp,'FR':fnn,'exact_accuracy':(tp+tn)/len(cases),'error_case_ids':errors}
report={
 'challenge_sha256':hashlib.sha256((CH/'CHALLENGE_V3_FROZEN.jsonl').read_bytes()).hexdigest(),
 'final_matcher_sha256':hashlib.sha256((ROOT/'matcher_final'/'matcher.py').read_bytes()).hexdigest(),
 'n_cases':len(cases),
 'gold_counts':dict(collections.Counter(c['expected_disposition'] for c in cases)),
 'systems':summary,
}
(CH/'INDEPENDENT_RECHECK.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps(report,indent=2,sort_keys=True))
