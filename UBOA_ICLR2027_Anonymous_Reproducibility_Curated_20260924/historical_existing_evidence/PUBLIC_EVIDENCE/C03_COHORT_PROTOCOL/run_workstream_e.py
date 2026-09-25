#!/usr/bin/env python3
"""Stage-36 Workstream E train/validation-only execution.

Opaque archives may contain the future suffix. This program decodes only the
frozen prefix ending at floor(0.8*N). It never seeks to or decodes later rows.
"""
from __future__ import annotations

import csv, gzip, hashlib, io, json, math, time, zipfile
from pathlib import Path
from typing import Iterable

import numpy as np
import torch
from torch import nn

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "iclr2027_redesign/36_parallel_strong_accept_program/E_prospective_real_cohort"
ARCH = OUT / "00_metadata_inventory/opaque_archives"
THRESHOLDS = (0.0, 0.02, 0.05)

SPECS = [
    dict(id="UCI374_APPLIANCES", zip="uci374.zip", n=19735, target="Appliances", lookback=144, horizons=(1,6,18), comparator="SEASONAL_NAIVE_LAG144", loss="MAE", patch=True),
    dict(id="UCI501_BEIJING_PM25", zip="uci501.zip", n=35064, target="PM2.5", lookback=48, horizons=(1,6,24), comparator="LAST_VALUE", loss="MAE", patch=False, panel=12),
    dict(id="UCI275_BIKE_HOURLY", zip="uci275.zip", n=17379, target="cnt", lookback=48, horizons=(1,6,24), comparator="SEASONAL_NAIVE_LAG24", loss="MAE", patch=True),
    dict(id="UCI235_HOUSEHOLD_POWER", zip="uci235.zip", n=2075259, target="Global_active_power", lookback=48, horizons=(1,6,24), comparator="SEASONAL_NAIVE_LAG24", loss="MSE", patch=False, aggregate_hourly=True),
    dict(id="UCI360_AIR_QUALITY_CO", zip="uci360.zip", n=9358, target="CO(GT)", lookback=48, horizons=(1,6,24), comparator="LAST_VALUE", loss="MSE", patch=True),
    dict(id="UCI492_METRO_TRAFFIC", zip="uci492.zip", n=48204, target="traffic_volume", lookback=48, horizons=(1,6,24), comparator="SEASONAL_NAIVE_LAG24", loss="MSE", patch=True),
]

def seed(key: str, purpose: str="MODEL_INIT") -> int:
    b=hashlib.sha256(f"UBOA_STAGE36|E|{key}|0|{purpose}".encode()).digest()[:8]
    return int.from_bytes(b,"big") & ((1<<63)-1)

def ffill(a: np.ndarray) -> np.ndarray:
    x=np.asarray(a,float).copy()
    x[~np.isfinite(x)]=np.nan
    good=np.flatnonzero(np.isfinite(x))
    if not len(good): return x
    x[:good[0]]=x[good[0]]
    for i in range(good[0]+1,len(x)):
        if not np.isfinite(x[i]): x[i]=x[i-1]
    return x

def prefix_reader(zpath: Path, member: str, rows: int, delimiter=",", encoding="utf-8", gzip_member=False):
    z=zipfile.ZipFile(zpath)
    raw=z.open(member)
    if gzip_member: raw=gzip.GzipFile(fileobj=raw)
    txt=io.TextIOWrapper(raw,encoding=encoding,errors="replace",newline="")
    reader=csv.DictReader(txt,delimiter=delimiter)
    for i,row in enumerate(reader):
        if i>=rows: break
        yield row
    txt.close(); z.close()

def load_prefix(spec):
    end=math.floor(.8*spec["n"]); train_raw=math.floor(.6*spec["n"])
    zpath=ARCH/spec["zip"]
    if spec["id"]=="UCI374_APPLIANCES":
        vals=[float(r["Appliances"]) for r in prefix_reader(zpath,"energydata_complete.csv",end)]
        return [ffill(np.array(vals))], train_raw, dict(decoded_rows=len(vals),member="energydata_complete.csv")
    if spec["id"]=="UCI275_BIKE_HOURLY":
        vals=[float(r["cnt"]) for r in prefix_reader(zpath,"hour.csv",end)]
        return [ffill(np.array(vals))], train_raw, dict(decoded_rows=len(vals),member="hour.csv")
    if spec["id"]=="UCI360_AIR_QUALITY_CO":
        vals=[]
        for r in prefix_reader(zpath,"AirQualityUCI.csv",end,delimiter=";",encoding="latin-1"):
            s=(r.get("CO(GT)") or "").strip().replace(",",".")
            try: v=float(s)
            except: v=np.nan
            if v<=-199: v=np.nan
            vals.append(v)
        return [ffill(np.array(vals))], train_raw, dict(decoded_rows=len(vals),member="AirQualityUCI.csv")
    if spec["id"]=="UCI492_METRO_TRAFFIC":
        vals=[float(r["traffic_volume"]) for r in prefix_reader(zpath,"Metro_Interstate_Traffic_Volume.csv.gz",end,gzip_member=True)]
        return [ffill(np.array(vals))], train_raw, dict(decoded_rows=len(vals),member="Metro_Interstate_Traffic_Volume.csv.gz")
    if spec["id"]=="UCI235_HOUSEHOLD_POWER":
        vals=[]
        for r in prefix_reader(zpath,"household_power_consumption.txt",end,delimiter=";"):
            s=(r.get("Global_active_power") or "").strip()
            try: vals.append(float(s))
            except: vals.append(np.nan)
        x=ffill(np.array(vals)); train_hour=train_raw//60
        usable=(len(x)//60)*60; x=x[:usable].reshape(-1,60).mean(1)
        return [x],train_hour,dict(decoded_rows=len(vals),normalized_hourly_rows=len(x),member="household_power_consumption.txt")
    if spec["id"]=="UCI501_BEIJING_PM25":
        outer=zipfile.ZipFile(zpath); nested=outer.read("PRSA2017_Data_20130301-20170228.zip"); outer.close()
        nz=zipfile.ZipFile(io.BytesIO(nested)); names=sorted(n for n in nz.namelist() if n.lower().endswith(".csv"))
        series=[]; counts=[]
        for name in names:
            txt=io.TextIOWrapper(nz.open(name),encoding="utf-8",errors="replace",newline="")
            vals=[]
            for i,r in enumerate(csv.DictReader(txt)):
                if i>=end: break
                try: vals.append(float(r["PM2.5"]))
                except: vals.append(np.nan)
            txt.close(); series.append(ffill(np.array(vals))); counts.append(len(vals))
        nz.close()
        if len(series)!=12: raise RuntimeError(f"expected 12 stations, got {len(series)}")
        m=min(map(len,series)); return [x[:m] for x in series],train_raw,dict(decoded_rows_per_member=counts,panel_members=names)
    raise KeyError(spec["id"])

def train_windows(series: list[np.ndarray], train_n: int, L: int, horizons: tuple[int,...], cap=4096):
    H=max(horizons); pairs=[]
    for mi,x in enumerate(series):
        for t in range(L, min(train_n,len(x))-H): pairs.append((mi,t))
    if len(pairs)>cap:
        idx=np.linspace(0,len(pairs)-1,cap,dtype=int); pairs=[pairs[i] for i in idx]
    X=np.stack([series[m][t-L:t] for m,t in pairs]); Y=np.stack([[series[m][t+h-1] for h in horizons] for m,t in pairs])
    return X,Y

def val_windows(series, train_n, L, horizons):
    H=max(horizons); end=min(map(len,series)); origins=np.arange(max(train_n,L),end-H)
    X=np.stack([[x[t-L:t] for t in origins] for x in series])
    Y=np.stack([[[x[t+h-1] for h in horizons] for t in origins] for x in series])
    return origins,X,Y

class DLinear(nn.Module):
    def __init__(self,L,H): super().__init__(); self.linear=nn.Linear(L,H)
    def forward(self,x): return self.linear(x)

class PatchTSTTiny(nn.Module):
    def __init__(self,L,H,patch=8,stride=4,d=16):
        super().__init__(); self.patch=patch; self.stride=stride; n=(L-patch)//stride+1
        self.proj=nn.Linear(patch,d); self.pos=nn.Parameter(torch.zeros(1,n,d))
        layer=nn.TransformerEncoderLayer(d_model=d,nhead=2,dim_feedforward=32,batch_first=True,dropout=0.0)
        self.enc=nn.TransformerEncoder(layer,1); self.out=nn.Linear(d,H)
    def forward(self,x):
        p=x.unfold(1,self.patch,self.stride); z=self.proj(p)+self.pos[:,:p.shape[1]]
        return self.out(self.enc(z).mean(1))

def fit_torch(model,X,Y,key,epochs):
    torch.manual_seed(seed(key)); torch.use_deterministic_algorithms(True)
    mu=float(np.mean(X)); sd=float(np.std(X) or 1); xt=torch.tensor((X-mu)/sd,dtype=torch.float32); yt=torch.tensor((Y-mu)/sd,dtype=torch.float32)
    opt=torch.optim.Adam(model.parameters(),lr=.001); bs=128
    for _ in range(epochs):
        for j in range(0,len(xt),bs):
            opt.zero_grad(); loss=((model(xt[j:j+bs])-yt[j:j+bs])**2).mean(); loss.backward(); opt.step()
    return model,mu,sd

def predict_torch(model,X,mu,sd):
    out=[]
    with torch.no_grad():
        for j in range(0,len(X),512): out.append(model(torch.tensor((X[j:j+512]-mu)/sd,dtype=torch.float32)).numpy()*sd+mu)
    return np.concatenate(out)

def loss_values(pred,y,loss):
    e=pred-y
    return np.abs(e) if loss=="MAE" else e*e

def descriptors(z, seasonal=24):
    z=np.asarray(z,float); z=z[np.isfinite(z)]; c=z-z.mean()
    def ac(k): return float(np.corrcoef(c[:-k],c[k:])[0,1]) if len(c)>k+5 and np.std(c[:-k])>0 and np.std(c[k:])>0 else 0.0
    q=max(8,len(z)//8); rv=float(max(np.var(z[i:i+q]) for i in range(0,len(z)-q+1,q))/max(1e-12,min(np.var(z[i:i+q]) for i in range(0,len(z)-q+1,q))))
    return dict(n=len(z),rho1=ac(1),seasonal_acf=ac(min(seasonal,max(1,len(z)//4))),rolling_variance_ratio=rv,mean=float(z.mean()),variance=float(z.var()))

def main():
    t0=time.time(); (OUT/"03_training_validation/checkpoints").mkdir(parents=True,exist_ok=True)
    selections=[]; failures=[]; resources=[]
    prov=[]
    for spec in SPECS:
        b=spec["id"]; st=time.time()
        try:
            series,train_n,meta=load_prefix(spec)
            if any(len(x)<train_n+spec["lookback"]+max(spec["horizons"])+512 for x in series): raise RuntimeError("insufficient validation prefix")
            missing_after=sum(int(np.sum(~np.isfinite(x[train_n:]))) for x in series)
            if missing_after: raise RuntimeError("nonfinite after causal prefix fill")
            Xtr,Ytr=train_windows(series,train_n,spec["lookback"],spec["horizons"])
            origins,Xv,Yv=val_windows(series,train_n,spec["lookback"],spec["horizons"])
            members,norig,L=Xv.shape; H=len(spec["horizons"]); flat=Xv.reshape(-1,L)
            preds={}
            if spec["comparator"].startswith("SEASONAL_NAIVE"):
                lag=int(spec["comparator"].split("LAG")[-1]); p=np.stack([np.repeat(x[origins-lag,None],H,axis=1) for x in series])
            else: p=np.stack([np.repeat(x[origins-1,None],H,axis=1) for x in series])
            preds[spec["comparator"]]=p
            preds["MEAN_LAST3_V1"]=np.stack([np.repeat(np.mean([x[tt-3:tt] for tt in origins],axis=1)[:,None],H,axis=1) for x in series])
            A=np.c_[np.ones(len(Xtr)),Xtr]; coef=np.linalg.solve(A.T@A+np.diag([0]+[1.0]*L),A.T@Ytr)
            preds["RIDGE_AR_V1"]=(np.c_[np.ones(len(flat)),flat]@coef).reshape(members,norig,H)
            np.savez(OUT/f"03_training_validation/checkpoints/{b}__RIDGE_AR_V1.npz",coef=coef)
            dl,mu,sd=fit_torch(DLinear(L,H),Xtr,Ytr,b+"|DLINEAR",20)
            preds["DLINEAR_CLASS_V1"]=predict_torch(dl,flat,mu,sd).reshape(members,norig,H)
            torch.save(dict(state=dl.state_dict(),mu=mu,sd=sd,seed=seed(b+"|DLINEAR")),OUT/f"03_training_validation/checkpoints/{b}__DLINEAR_CLASS_V1.pt")
            if spec["patch"]:
                pt,pm,ps=fit_torch(PatchTSTTiny(L,H),Xtr,Ytr,b+"|PATCHTST",12)
                preds["PATCHTST_CLASS_TINY_V1"]=predict_torch(pt,flat,pm,ps).reshape(members,norig,H)
                torch.save(dict(state=pt.state_dict(),mu=pm,sd=ps,seed=seed(b+"|PATCHTST")),OUT/f"03_training_validation/checkpoints/{b}__PATCHTST_CLASS_TINY_V1.pt")
            scores={}; lv={}
            for cid,pred in sorted(preds.items()):
                per=loss_values(pred,Yv,spec["loss"]).mean(axis=(0,2)); lv[cid]=per; scores[cid]=float(per.mean())
            chosen=sorted(scores,key=lambda k:(scores[k],k))[0]; structural=chosen==spec["comparator"]
            comp=lv[spec["comparator"]]; sel=lv[chosen]; z=comp-sel
            d=descriptors(z,144 if b=="UCI374_APPLIANCES" else 24)
            rec=dict(benchmark_id=b,selected_realization=chosen,comparator=spec["comparator"],primary_loss=spec["loss"],validation_origins=len(origins),validation_origin_first=int(origins[0]),validation_origin_last=int(origins[-1]),scores=scores,structural_route=structural,selection_rule="MIN_MEAN_PRIMARY_LOSS_THEN_CANDIDATE_ID",thresholds=list(THRESHOLDS),future_oos_origins_from_metadata=1024,train_prefix_hash=hashlib.sha256(np.concatenate(series).tobytes()).hexdigest(),validation_record_hash=hashlib.sha256(np.c_[comp,sel].tobytes()).hexdigest())
            rec["selection_lock_sha256"]=hashlib.sha256(json.dumps(rec,sort_keys=True,separators=(",",":")).encode()).hexdigest(); selections.append(rec)
            (OUT/f"04_selection_locks/{b}_SELECTION_LOCK.json").write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n")
            (OUT/f"05_pre_oos_diagnostics/{b}_diagnostics.json").write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
            np.savez_compressed(OUT/f"03_training_validation/{b}_validation_losses.npz",origin=origins,comparator=comp,selected=sel)
            prov.append(dict(benchmark_id=b,opaque_archive=spec["zip"],archive_byte_size=(ARCH/spec["zip"]).stat().st_size,decoded_prefix_only=True,oos_suffix_decoded=False,**meta))
            resources.append(dict(benchmark_id=b,wall_seconds=time.time()-st,train_windows=len(Xtr),validation_origins=len(origins),members=len(series)))
        except Exception as e:
            failures.append(dict(benchmark_id=b,phase="TRAIN_VALIDATION",error=repr(e),replacement_forbidden=True)); resources.append(dict(benchmark_id=b,wall_seconds=time.time()-st,error=repr(e)))
    def jl(path,rows): path.write_text("".join(json.dumps(x,sort_keys=True,separators=(",",":"))+"\n" for x in rows))
    jl(OUT/"03_training_validation/selection_registry.jsonl",selections); jl(OUT/"03_training_validation/raw_data_provenance.jsonl",prov); jl(OUT/"03_training_validation/failure_registry.jsonl",failures); jl(OUT/"03_training_validation/resource_report.jsonl",resources)
    (OUT/"03_training_validation/raw_record_schema.json").write_text(json.dumps({"unit":"time origin","fields":["origin","comparator_loss","selected_loss"],"panel_rule":"mean across members and horizons per origin","oos_fields":0},indent=2)+"\n")
    (OUT/"03_training_validation/code_manifest.json").write_text(json.dumps({"script":str(Path(__file__).relative_to(ROOT)),"script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"numpy":np.__version__,"torch":torch.__version__},indent=2)+"\n")
    (OUT/"03_training_validation/seed_ledger.jsonl").write_text("".join(json.dumps({"benchmark_id":s["id"],"dlinear_seed":seed(s["id"]+"|DLINEAR"),"patchtst_seed":seed(s["id"]+"|PATCHTST") if s["patch"] else None},sort_keys=True)+"\n" for s in SPECS))
    (OUT/"03_training_validation/summary_reconciliation.json").write_text(json.dumps({"frozen_applications":6,"terminal_selection_records":len(selections),"failures":len(failures),"oos_numerical_reads":0,"wall_seconds":time.time()-t0},indent=2)+"\n")
    return 0 if selections else 2

if __name__=="__main__": raise SystemExit(main())
