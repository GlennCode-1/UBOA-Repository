#!/usr/bin/env python3
"""Deterministic ideal-reference calculation. No random samples or historical edits.
Q=int_0^1 (B(u)-u B(1))^2 du; B(1) independent of the bridge.
The KL eigenvalues of the bridge are 1/(pi*k)^2, giving
L_Q(s)=(sqrt(2s)/sinh(sqrt(2s)))**(1/2).
Combining this with a Gaussian-tail angular integral gives the code below.
Numerical precision checks are not certified interval arithmetic and do not
recover the unknown historical Monte Carlo generator or discretization.
"""
import json
import argparse
from pathlib import Path
import mpmath as mp

ROOT=Path(__file__).resolve().parents[1]
HISTORICAL='5.2988297532'

def tail_angle(q):
    def f(t):
        if not t: return mp.mpf('0')
        x=q/mp.sin(t)
        return mp.sqrt(x/mp.sinh(x))
    return mp.quad(f,[0,mp.pi/8,mp.pi/4,mp.pi/2])/mp.pi

def tail_cot(q):
    return mp.quad(lambda u: mp.sqrt(q*mp.sqrt(1+u*u)/mp.sinh(q*mp.sqrt(1+u*u)))/(1+u*u),[0,1,4,16,mp.inf])/mp.pi

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'derived'/'brownian_reference_quadrature.json')
    args=parser.parse_args()
    output=args.output.resolve()
    if ROOT/'frozen_study' in output.parents:
        raise ValueError('Refusing to write within frozen study')
    output.parent.mkdir(parents=True,exist_ok=True)
    records=[]
    for digits in (40,65):
        mp.mp.dps=digits
        q=mp.findroot(lambda x:tail_angle(x)-mp.mpf('.05'),(mp.mpf('5.2'),mp.mpf('5.4')))
        old=tail_angle(mp.mpf(HISTORICAL))
        cross=tail_cot(mp.mpf(HISTORICAL))
        assert abs(old-cross)<mp.mpf(10)**(-digits+8)
        records.append({'decimal_precision':digits,'ideal_upper_0.95_quantile':mp.nstr(q,32),'ideal_tail_at_historical_cutoff':mp.nstr(old,32),'alternative_integral_difference':mp.nstr(abs(old-cross),8)})
    result={'role':'post hoc deterministic reference diagnostic; not original calibration regeneration',
            'historical_cutoff_unchanged':HISTORICAL,'calculations':records,'new_random_paths':0,
            'original_decisions_recomputed':False,'limitations':['Does not recover original Monte Carlo/discretization error.','Does not establish finite-sample size of the historical time-series test.','No saved historical statistics were available to measure changed decisions.','High precision convergence is not a rigorous interval certificate.']}
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
