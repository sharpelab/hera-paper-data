# Run 1 — CNP-line fit + (n,D) calibration (cnp-and-dline-calibration)
import numpy as np
from hera.analysis import open_run, GateCalibration
run = open_run("data/1")
bg = run.col('k_2400_volt'); tg = run.col('DC_bias'); I = run.col('sr0_X')/(-1e6)
R1 = run.col('sr1_X')/I; R2 = run.col('sr2_X')/I
TG_LO, TG_HI, RAIL = -6.0, 7.0, 4.2e3
def ridge(R):
    rows = np.unique(np.round(bg,3)); bb=[];vv=[];pk=[];edge=[]
    for b in rows:
        m = np.abs(bg-b)<1e-4
        if m.sum()<20: continue
        t=tg[m]; r=R[m]; o=np.argsort(t); t=t[o]; r=r[o]
        top = t[r >= 0.92*r.max()]          # plateau center (robust to clipped flat-tops)
        bb.append(b); vv.append(np.median(top)); pk.append(r.max())
        edge.append(top.min()<=TG_LO+0.4 or top.max()>=TG_HI-0.4)
    return map(np.array,(bb,vv,pk,edge))
b1,v1,pk1,e1 = ridge(R1); b2,v2,pk2,e2 = ridge(R2)
for nm,b,v,e in [('sr1 T3-T4',b1,v1,e1),('sr2 B4-B5',b2,v2,e2)]:
    p = np.polyfit(b[~e], v[~e], 1)
    print(f"{nm}: V_tg = {p[0]:+.4f} V_bg {p[1]:+.4f}   c_bg/c_tg = {-p[0]:.4f}  (rows {(~e).sum()}/{len(b)})")
B = np.concatenate([b1[~e1],b2[~e2]]); V = np.concatenate([v1[~e1],v2[~e2]])
slope,intc = np.polyfit(B,V,1); ratio = -slope
uc = pk1<RAIL; jmin = np.argmin(pk1[uc]); bgD0=float(b1[uc][jmin]); vtgD0=float(v1[uc][jmin])
print(f"\nPOOLED device CNP fit: V_tg = {slope:+.4f} V_bg {intc:+.4f}   c_bg/c_tg = {ratio:.4f}  (geom prior 1.300)")
print(f"D=0 located at CNP-R minimum: (V_tg, V_bg) = ({vtgD0:+.2f}, {bgD0:+.2f})  -> D_offset locator")
# refined calibration: data ratio, geometry scale-anchor (t_tg=15.6 nm hBN)
t_tg = 15.6e-9; t_bg_eff = t_tg/ratio
c0 = GateCalibration.from_thicknesses(t_tg, t_bg_eff, 0.0)
n_off = -float(c0.density(intc,0.0)); D_off = -float(c0.displacement_field(vtgD0,bgD0))
cal = GateCalibration.from_thicknesses(t_tg, t_bg_eff, 0.0, n_offset=n_off, D_offset=D_off)
vbg = np.linspace(-4,4,17); n_line = cal.density(slope*vbg+intc, vbg)
print(f"closure: |n|max on CNP line = {np.abs(n_line).max():.2e} m^-2 (~0); effective t_bg = {t_bg_eff*1e9:.2f} nm")
print(f"\nProvenance: ratio (c_bg/c_tg={ratio:.4f}) DATA-calibrated; absolute n,D scale GEOMETRY-PRIOR")
print("(t_tg=15.6 nm hBN), pending a quantum-Hall lever-arm upgrade. n,D magnitudes carry ~10-15%.")
print("\nMax |n| reach at D=0 (within validators):")
for s,vb in [('hole',-4.5),('elec',4.5)]:
    vt = vtgD0 + ratio*(vb-bgD0)
    print(f"  {s}: (V_tg,V_bg)=({vt:+.2f},{vb:+.2f})  n = {cal.density(vt,vb)/1e16:+.2f}e12 cm^-2")
