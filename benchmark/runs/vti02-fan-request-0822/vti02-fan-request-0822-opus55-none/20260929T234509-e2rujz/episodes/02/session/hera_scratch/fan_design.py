import numpy as np, json
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
ns = np.linspace(-2, 4.5, 6501)
Vt, Vb = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
ok = (Vt >= -0.3) & (Vt <= 1.0) & (Vb >= -1.3) & (Vb <= 2.0)
print("D=0 n window:", ns[ok].min(), ns[ok].max())
for n in [-1.25,-1.2, 0, 3.25, 3.3]:
    print(n, calc_gate_voltages(n, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]))
# field grid: 1/B-uniform with dinvB, capped at dBmax
def grid(B_lo, B_hi, dinv, dBmax):
    B=[B_lo]
    while B[-1] < B_hi-1e-9:
        b=B[-1]; step=min(dBmax, 1/(1/b - dinv) - b if 1/b-dinv>0 else dBmax)
        B.append(min(B_hi, b+step))
    return np.round(np.array(B),4)
for (lo,dinv,dBmax) in [(1.0,0.009,0.2),(1.0,0.009,0.15),(1.0,0.010,0.2),(0.8,0.010,0.2)]:
    B=grid(lo,10.0,dinv,dBmax); dB=np.diff(B)
    for nf,dn in [(151,None),(126,None)]:
        tpt=1.2; row=nf*tpt+4+5+3
        tot=len(B)*row + (10-lo)/0.137*60 + lo/0.137*60
        print(f"lo {lo} dinv {dinv} cap {dBmax}: rows {len(B)}, crossover B {np.sqrt(dBmax/dinv):.2f}, nfast {nf}: {tot/3600:.2f} h  (row {row/60:.2f} min)")
