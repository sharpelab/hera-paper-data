import numpy as np, json, os
from hera.analysis import open_run
run = open_run("data/1")
bg = run.col('k_2400_volt'); tg = run.col('DC_bias')
I  = run.col('sr0_X')/(-1e6)
R1 = run.col('sr1_X')/I; R2 = run.col('sr2_X')/I; R3 = run.col('sr3_X')/I
ibg = run.col('k_2400_curr'); isi = run.col('k_2410_curr')
TG_LO, TG_HI = -6.0, 7.0

def ridge_per_row(R, edge_guard=0.4):
    rows = np.unique(np.round(bg,3))
    bb=[]; vv=[]; flags=[]
    for b in rows:
        m = np.abs(bg-b)<1e-4
        if m.sum()<20: continue
        t = tg[m]; r = R[m]; o=np.argsort(t); t=t[o]; r=r[o]
        rmax = r.max()
        top = t[r >= 0.92*rmax]          # plateau / peak region
        center = np.median(top)          # robust for clipped flat-tops
        # edge guard: plateau touches TG window edge -> position biased
        edge = (top.min() <= TG_LO+edge_guard) or (top.max() >= TG_HI-edge_guard)
        bb.append(b); vv.append(center); flags.append(edge)
    return np.array(bb), np.array(vv), np.array(flags)

print("== per-channel CNP-line fit (V_tg = slope*V_bg + b ; slope = -c_bg/c_tg) ==")
fits={}
for nm,R in [('sr1 T3-T4',R1),('sr2 B4-B5',R2)]:
    b,v,edge = ridge_per_row(R)
    keep = ~edge
    p,cov = np.polyfit(b[keep], v[keep], 1, cov=True)
    resid = v[keep]-np.polyval(p,b[keep])
    fits[nm]=(p, b[keep].size, np.std(resid))
    print(f"  {nm}: slope={p[0]:+.4f}  intcpt={p[1]:+.4f}  c_bg/c_tg={-p[0]:.4f}  "
          f"rows_used={keep.sum()}/{len(b)} (edge-dropped {edge.sum()})  resid_std={np.std(resid)*1000:.1f} mV")
print(f"  geometry prior c_bg/c_tg = 15.6/12 = {15.6/12:.4f}")

# leakage (Verify)
print(f"\n== leakage (Verify) ==")
print(f"  |I_bg|max = {np.abs(ibg).max()*1e12:.0f} pA   |I_si|max = {np.abs(isi).max()*1e12:.0f} pA  (1 nA soft ceiling)")
print(f"  drain I: {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA;  rows {run.col('sr0_X').size}")

# GateCalibration API
from hera.analysis import GateCalibration
import inspect
print("\n== GateCalibration methods ==")
print([m for m in dir(GateCalibration) if not m.startswith('_')])
