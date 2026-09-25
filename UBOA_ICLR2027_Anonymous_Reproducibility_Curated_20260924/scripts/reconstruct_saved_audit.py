#!/usr/bin/env python3
"""Deterministic, post hoc reconstruction from SAVED histories and count records.

No RNG call, stochastic replay, model fitting or external data access is performed.
This is an independent implementation of the displayed formulas, not an import of
certificate_b1.py/certificate_qb.py. Future paths were not archived; their individual
rejections cannot be independently replayed by this script. Original files stay read-only.
"""
from __future__ import annotations
import argparse, csv, hashlib, itertools, json, math, platform
from collections import Counter
from fractions import Fraction
from pathlib import Path
import numpy as np
import scipy
from scipy.stats import binom, beta

ROOT=Path(__file__).resolve().parents[1]
F=ROOT/'frozen_study'; RUN=F/'09_OUTPUTS'/'confirmatory_run'
R=(Fraction(0),Fraction(1,50),Fraction(1,20)); HZ=(1,3,6)
EXPECTED_H_SHA='5229432f2384a80b2cde4097c68cf08e383cdacbf67642f8de12537895c0e8c9'
EXPECTED_F2_SHA='0f9d5bb9e6b19a1cffa3e1fbe38d34054a0c2328a03f12ea56efe6bf35ca285c'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def canonical(d): return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def close(a,b): return math.isclose(float(a),float(b),rel_tol=1e-10,abs_tol=1e-10*(1+abs(float(a))))
def dump(p,d): Path(p).write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+'\n')
def tsv(p,rows):
 with Path(p).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)

def exact_mae(d):
 risks=[]
 for h in HZ:
  vals=[sum(Fraction(1,2)**(h-j)*e for j,e in enumerate(bits,1)) for bits in itertools.product((-1,1),repeat=h)]
  risks.append(sum(abs(v-d) for v in vals)/len(vals))
 return sum(risks)/3

def bounded_coefficients(r):
 n=512;o=np.repeat(np.arange(n),3);h=np.tile(np.array(HZ),n);j=np.arange(1,n+6)[None,:]
 # A_i is origin-state Lipschitz coefficient; B_i is target-state coefficient.
 Ai=(2-float(r))*np.power(.5,h); Bi=np.full(len(o),2-float(r))
 go=np.where(j<=o[:,None],np.power(.5,np.maximum(0,o[:,None]-j)),0.)
 gt=np.where(j<=(o+h)[:,None],np.power(.5,np.maximum(0,(o+h)[:,None]-j)),0.)
 c=2*(Ai[:,None]*go+Bi[:,None]*gt).sum(axis=0)/(3*n)
 C=float(c@c);threshold=math.sqrt(C*math.log(20)/2)
 return dict(origin=o,horizon=h,weights=np.full(len(o),1/(3*n)),A_i=Ai,B_i=Bi,c=c,C=np.array(C),rho=np.array(.5),D=np.array(2.),threshold=np.array(threshold))

def gaussian_components(gamma,y0):
 n=256;tmax=n-1+6;o=np.repeat(np.arange(n),3);h=np.tile(np.array(HZ),n);j=np.arange(1,tmax+1)[None,:]
 past=np.where(j<=o[:,None],np.power(.5,np.maximum(0,o[:,None]-j)),0.)
 noise=np.where((j>o[:,None])&(j<=(o+h)[:,None]),np.power(.5,np.maximum(0,(o+h)[:,None]-j)),0.)
 vectors=noise-gamma*past;offsets=-gamma*y0*np.power(.5,o)
 weight=1/(3*n)
 return weight*(vectors.T@vectors),weight*(vectors.T@offsets),weight*float(offsets@offsets)

def check_selection(history):
 x=np.asarray(history['state_path_through_325'],dtype=float)
 assert len(x)==326 and x[0]==0 and x[-1]==history['terminal_state']
 o=np.arange(256,320); scores={}
 for s in [-.1,.1]:
  errors=[]
  for h in HZ:
   pred=(.5**h)*x[o]+s if history['branch']=='B1' else (.5**h+s)*x[o]
   e=x[o+h]-pred;errors.extend((abs(e) if history['branch']=='B1' else e*e).tolist())
  scores[f'{s:+.1f}']=sum(errors)/len(errors)
 assert all(close(scores[k],v) for k,v in history['validation_scores'].items())
 winner=-.1 if scores['-0.1']<=scores['+0.1'] else .1
 assert winner==history['selected_parameter']
 if history['branch']=='B1':
  innovations=x[1:]-.5*x[:-1];assert np.allclose(abs(innovations),1,atol=1e-12,rtol=0)
 return scores

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'derived');ap.add_argument('--certificates',type=Path,default=ROOT/'certificates');args=ap.parse_args()
 out=args.output.resolve();cert=args.certificates.resolve()
 if out==RUN or RUN in out.parents or cert==RUN or RUN in cert.parents:raise ValueError('Refusing to write to frozen run')
 out.mkdir(parents=True,exist_ok=True);cert.mkdir(parents=True,exist_ok=True)
 hdoc=load(RUN/'H_FREEZE_MANIFEST.json');hs=hdoc['histories'];rs=load(RUN/'HISTORY_RESULTS.json');results={r['history_id']:r for r in rs}
 assert sha(RUN/'H_FREEZE_MANIFEST.json')==EXPECTED_H_SHA
 assert sha(F/'10_IMPLEMENTATION'/'IMPLEMENTATION_FREEZE.json')==EXPECTED_F2_SHA
 fr=load(F/'10_IMPLEMENTATION'/'IMPLEMENTATION_FREEZE.json');f1=load(F/'01_FREEZE'/'SCIENTIFIC_FREEZE_MANIFEST.json')
 assert sha(F/'01_FREEZE'/'SCIENTIFIC_FREEZE_MANIFEST.json')==fr['scientific_protocol_manifest_sha256']
 for rel,want in f1['files_sha256'].items():assert sha(F/rel)==want,rel
 for field in ['executable_source_sha256','schema_sha256','dry_run_artifact_sha256']:
  for rel,want in fr[field].items():assert sha(F/'10_IMPLEMENTATION'/rel)==want,rel
 assert len(hs)==len(rs)==80 and len(results)==80
 assert Counter(h['cell_id'] for h in hs)=={k:8 for k in set(h['cell_id'] for h in hs)}
 finite=[h for h in hs if h['first_true_null'] is not None]; m=len(finite);assert m==46
 pvals={h['history_id']:float(binom.sf(results[h['history_id']]['false_promotions']-1,4096,.05)) for h in finite}
 ordered=sorted(pvals,key=lambda k:(pvals[k],k));adj={};v=0
 for rank,k in enumerate(ordered):v=max(v,min(1,(m-rank)*pvals[k]));adj[k]=v
 stored=load(RUN/'ANALYSIS_SUMMARY.json')['analysis']['primary_holm_audit']
 assert adj==stored['adjusted_pvalues'] and not any(p<=.01 for p in adj.values())
 bcoeff={};cmanifest=[];history_rows=[];node_rows=[]
 for ri,r in enumerate(R):
  bcoeff[ri]=bounded_coefficients(r);fn=f'mae_node_{ri+1}.npz';np.savez_compressed(cert/fn,**bcoeff[ri])
 for idx,h in enumerate(hs,1):
  name=h['history_id'];res=results[name];label=f'H{idx:02d}'
  hc=dict(h);storedhash=hc.pop('record_sha256');assert canonical(hc)==storedhash==res['history_record_sha256']
  assert res['implementation_freeze_sha256']==EXPECTED_F2_SHA and res['inner_denominator']==4096
  assert res['outer_index']==h['outer_index'] and res['cell_id']==h['cell_id']
  assert res['truth_by_node']==h['truth_by_node'] and res['first_true_null']==h['first_true_null']
  check_selection(h)
  y0=float(h['terminal_state']);sg=float(h['selected_parameter'])
  if h['branch']=='B1':
   lb=exact_mae(Fraction(h['baseline_parameter']));ls=exact_mae(Fraction(str(sg)));theta=1-ls/lb
   assert str(theta)==h['theta_exact'];means=[float((1-r)*lb-ls) for r in R];truths=[theta<=r for r in R]
   lb_f,ls_f=float(lb),float(ls)
  else:
   bg=float(h['baseline_parameter']);ab,gb,kb=gaussian_components(bg,y0);a_s,g_s,k_s=gaussian_components(sg,y0)
   n=256;qbar=sum((1-.25**hz)/.75 for hz in HZ)/3
   m2bar=sum(.25**o*y0*y0+(1-.25**o)/.75 for o in range(n))/n
   lb_f=qbar+bg*bg*m2bar;ls_f=qbar+sg*sg*m2bar;theta=1-ls_f/lb_f
   means=[(1-float(r))*lb_f-ls_f for r in R];truths=[mu<=0 for mu in means]
   assert close(theta,h['theta_exact_H_conditional'])
  ftn=next((j for j,t in enumerate(truths) if t),None);assert ftn==h['first_true_null'] and truths==h['truth_by_node']
  for ri,r in enumerate(R):
   if h['branch']=='B1':
    cf=bcoeff[ri];th=float(cf['threshold']);mu=means[ri];fn=f'mae_node_{ri+1}.npz';variance='';norm=float(cf['C'])
   else:
    A=(1-float(r))*ab-a_s;g=(1-float(r))*gb-g_s;k=(1-float(r))*kb-k_s
    mu=k+float(np.trace(A));variance=2*float(np.sum(A*A))+4*float(g@g);norm='';th=math.sqrt(19*variance)
    assert np.allclose(A,A.T,atol=1e-13) and close(mu,means[ri]) and close(variance,h['gaussian_variance_crosschecks'][ri])
    fn=f'{label}_node_{ri+1}.npz';np.savez_compressed(cert/fn,A=A,g=g,k=np.array(k),V=np.array(variance),mu=np.array(mu),threshold=np.array(th))
   assert close(mu,h['mu_by_node'][ri]) and close(th,h['certificate_thresholds'][ri])
   assert close(mu-th,res['informativeness_margin_mu_minus_threshold'][ri])
   cmanifest.append(dict(history=label,original_history_id=name,node=ri+1,r=str(r),file=fn,sha256=sha(cert/fn),reconstruction='post hoc deterministic from saved H; not a preregistered matrix file'))
   node_rows.append(dict(history=label,original_history_id=name,cell=h['cell_id'],node=ri+1,r=str(r),mu=mu,null_true=truths[ri],threshold=th,mu_minus_threshold=mu-th,C=norm,V=variance,local_reject_count=res['local_reject_counts'][ri],reached_count=res['reached_counts'][ri],denominator=4096,certificate_file=fn))
  term=res['terminal_report_counts'];assert sum(term.values())==4096 and res['invalid_count']==0
  depths={'NONE':0,'0':1,'1/50':2,'ABOVE_0.05':3}
  fp=sum(count for key,count in term.items() if ftn is not None and depths[key]>ftn)
  assert fp==res['false_promotions']
  reached=[sum(count for key,count in term.items() if depths[key]>=j) for j in range(3)]
  assert reached==res['reached_counts']
  if ftn is not None:assert fp<=res['local_reject_counts'][ftn]
  assert res['pathwise_invariant_violations']==0
  cp=float(beta.ppf(1-.01/m,fp+1,4096-fp)) if ftn is not None else 0.
  history_rows.append(dict(history=label,original_history_id=name,cell=h['cell_id'],outer_index=h['outer_index'],selected_parameter=sg,y0=y0,baseline_risk=lb_f,selected_risk=ls_f,theta=float(theta),theta_rational=str(theta) if h['branch']=='B1' else '',first_true_node='' if ftn is None else ftn+1,false_promotions=fp,denominator=4096,binomial_p=pvals.get(name,''),holm_adjusted_p=adj.get(name,''),posthoc_99pct_simultaneous_upper=cp,upper_bound_type='Bonferroni exact-binomial over 46 pre-specified eligible histories' if ftn is not None else 'zero by absence of a true ladder null',terminal_none=term.get('NONE',0),terminal_0=term.get('0',0),terminal_2pct=term.get('1/50',0),terminal_5pct=term.get('ABOVE_0.05',0),record_sha256=storedhash,inner_batch_sha256=res['inner_batch_sha256']))
 tsv(out/'history_audit_80.tsv',history_rows);tsv(out/'node_certificates_240.tsv',node_rows);dump(out/'certificate_file_index.json',cmanifest)
 cells=[]
 for cid in dict.fromkeys(h['cell_id'] for h in hs):
  rows=[v for v in history_rows if v['cell']==cid];nr=[v for v in node_rows if v['cell']==cid]
  cells.append(dict(cell=cid,histories=len(rows),finite_true_null=sum(v['first_true_node']!='' for v in rows),theta_min=min(v['theta'] for v in rows),theta_max=max(v['theta'] for v in rows),false_promotions=sum(v['false_promotions'] for v in rows),futures=32768,terminal_5pct=sum(v['terminal_5pct'] for v in rows),terminal_5pct_rate=sum(v['terminal_5pct'] for v in rows)/32768,positive_margin_nodes=sum(v['mu_minus_threshold']>0 for v in nr),total_history_nodes=len(nr),rejection_0=sum(v['local_reject_count'] for v in nr if v['node']==1)/32768,rejection_2pct=sum(v['local_reject_count'] for v in nr if v['node']==2)/32768,rejection_5pct=sum(v['local_reject_count'] for v in nr if v['node']==3)/32768))
 tsv(out/'cell_results_10.tsv',cells)
 cutoff=next(k for k in range(4097) if binom.sf(k-1,4096,.05)<=.01/46)
 powers=[dict(true_error_probability=p,count_cutoff=cutoff,first_step_detection_probability=float(binom.sf(cutoff-1,4096,p))) for p in [.05,.055,.06,.065,.075,.1]]
 tsv(out/'holm_first_step_power.tsv',powers)
 summary=dict(original_H_sha256=EXPECTED_H_SHA,original_F2_sha256=EXPECTED_F2_SHA,all_36_F1_hashes_verified=len(f1['files_sha256']),F2_source_files_verified=len(fr['executable_source_sha256']),histories=80,history_node_records=240,unique_coefficient_files=len(list(cert.glob('*.npz'))),finite_first_true_null_histories=46,conditional_continuations_recorded=80*4096,conditional_continuations_in_primary_family=46*4096,retained_false_promotions=1,recorded_invariant_violations=0,independent_recomputed_aggregate_first_true_null_inclusion_violations=0,independent_pathwise_replay='NOT_PERFORMED: individual future paths/decisions not retained; original runtime counts only',holm_rejections=0,posthoc_99pct_simultaneous_upper_max=max(v['posthoc_99pct_simultaneous_upper'] for v in history_rows),posthoc_99pct_simultaneous_upper_zero_count=float(beta.ppf(1-.01/46,1,4096)),holm_first_step_count_cutoff=cutoff,stochastic_execution=False,rng_calls=0,new_paths_generated=0,analysis_role='deterministic reconstruction and post hoc secondary analysis; does not replace original confirmation',environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__))
 dump(out/'RECONSTRUCTION_REPORT.json',summary)
 print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
