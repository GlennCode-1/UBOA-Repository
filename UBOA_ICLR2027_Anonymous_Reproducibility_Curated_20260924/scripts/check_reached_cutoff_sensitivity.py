#!/usr/bin/env python3
import json, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
R=ROOT/'historical_existing_evidence'/'PUBLIC_EVIDENCE'/'C07_REACHED_STATISTICS'
old=5.298829753159216
ideal=5.322679900530264
rows=[]
for p in sorted(R.rglob('reached_node_records.json')):
    for i,r in enumerate(json.loads(p.read_text())):
        rows.append({'source':str(p.relative_to(ROOT)),'index':i,'stat':float(r['test_statistic'])})
for p in sorted(R.rglob('reached_node_records.jsonl')):
    for i,line in enumerate(p.read_text().splitlines()):
        if line.strip():
            r=json.loads(line); rows.append({'source':str(p.relative_to(ROOT)),'index':i,'stat':float(r['test_statistic'])})
for r in rows:
    r['historical_reject']=r['stat']>=old
    r['ideal_cutoff_reject']=r['stat']>=ideal
    r['between_cutoffs']=old<=r['stat']<ideal
report={
 'n_reached_nodes':len(rows),
 'historical_cutoff':old,
 'ideal_continuous_q95':ideal,
 'between_cutoffs_count':sum(x['between_cutoffs'] for x in rows),
 'decision_changes_if_only_cutoff_replaced':sum(x['historical_reject']!=x['ideal_cutoff_reject'] for x in rows),
 'min_stat':min(x['stat'] for x in rows),
 'rows':rows,
}
out=ROOT/'derived'/'reached_cutoff_sensitivity.json'
out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
