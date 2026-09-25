from fractions import Fraction
from itertools import product
import math

RHO = Fraction(1,2)
HS = (1,3,6)
DS = Fraction(1,10)


def eta_values(h):
    out=[]
    for signs in product((-1,1), repeat=h):
        x=Fraction(0,1)
        for k,s in enumerate(signs, start=1):
            x += (RHO ** (h-k))*s
        out.append(x)
    return out


def mae_risk(delta):
    return sum(sum(abs(x-delta) for x in eta_values(h))/len(eta_values(h)) for h in HS)/len(HS)

selected = mae_risk(DS)
fixtures = [
    (Fraction(0,1), Fraction(-1,1280)),
    (Fraction(289,784), Fraction(1,50)),
    (Fraction(5875,10336), Fraction(1,20)),
    (Fraction(2747,3680), Fraction(2,25)),
    (Fraction(541,328), Fraction(2,5)),
]
for db, target in fixtures:
    theta = 1-selected/mae_risk(db)
    assert theta == target, (db, theta, target)

# QB comparator values were frozen from stationary second-moment design labels only.
a=0.5
stat=1/(1-a*a)
q=sum((1-a**(2*h))/(1-a*a) for h in HS)/len(HS)
gs=0.1
rs=q+gs*gs*stat
for target, expected in [
    (0.02,0.16971626701134285),
    (0.05,0.24185434428325728),
    (0.08,0.3001994920954194),
    (0.40,0.7900957550090582),
]:
    got=math.sqrt(((rs/(1-target))-q)/stat)
    assert abs(got-expected) <= 5e-16*(1+abs(expected)), (target,got,expected)

print('PREREG_DETERMINISTIC_CHECKS=PASS')
print('B1_SELECTED_MAE_RISK=', selected)
