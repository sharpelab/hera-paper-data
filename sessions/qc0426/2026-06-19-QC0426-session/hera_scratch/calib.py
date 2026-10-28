import numpy as np
from hera.analysis import open_run, GateCalibration
run = open_run("data/1")
bg = run.col('k_2400_volt'); tg = run.col('DC_bias')
I  = run.col('sr0_X')/(-1e6)
R1 = run.col('sr1_X')/I; R2 = run.col('sr2_X')/I
TG_LO,TG_HI=-6.0,7.0; RAIL=4.2e3

def ridge(R):
    rows=np.unique(np.round(bg,3)); bb=[];vv=[];pk=[];edge=[]
    for b in rows:
        m=np.abs(bg-b)<1e-4
        if m.sum()<20: continue
        t=tg[m]; r=R[m]; o=np.argsort(t); t=t[o]; r=r[o]
        rmax=r.max(); top=t[r>=0.92*rmax]; c=np.median(top)
        bb.append(b); vv.append(c); pk.append(rmax)
        edge.append(top.min()<=TG_LO+0.4 or top.max()>=TG_HI-0.4)
    return map(np.array,(bb,vv,pk,edge))

b1,v1,pk1,e1=ridge(R1); b2,v2,pk2,e2=ridge(R2)
# pooled device fit (both channels, edge-dropped)
B=np.concatenate([b1[~e1],b2[~e2]]); V=np.concatenate([v1[~e1],v2[~e2]])
p=np.polyfit(B,V,1); slope,intc=p
ratio=-slope
print(f"pooled fit: V_tg = {slope:+.4f} V_bg {intc:+.4f}   c_bg/c_tg(data)={ratio:.4f}  geom=1.3000")

# --- D=0 from CNP-R minimum (unclipped rows only) along sr1 ridge ---
unclip = pk1 < RAIL
print(f"\nD=0 locator: unclipped CNP rows BG = {b1[unclip]}")
print(f"  CNP-R peak there (kOhm): {np.round(pk1[unclip]/1e3,2)}")
if unclip.sum()>=2:
    j=np.argmin(pk1[unclip]); bg_D0=b1[unclip][j]; vtg_D0=v1[unclip][j]
    print(f"  CNP-R minimum at BG={bg_D0:+.2f}, V_tg={vtg_D0:+.2f}  -> D=0 locus")
else:
    bg_D0,vtg_D0=0.0,intc

# --- refined calibration: geometry t_tg, t_bg from data ratio ---
t_tg=15.6e-9; t_bg_eff=t_tg/ratio
cal=GateCalibration.from_thicknesses(t_tg,t_bg_eff,0.0)
# set offsets so CNP line -> n=0, and D=0 at the located minimum
cal.n_offset=0.0; cal.D_offset=0.0
n0,D0=cal.n_D(intc,0.0)           # density at CNP intercept (V_bg=0) before offset
cal.n_offset=-cal.density(intc,0.0)
# D offset: make D=0 at the CNP-R-minimum point (bg_D0, vtg_D0)
cal.D_offset=-cal.displacement_field(vtg_D0,bg_D0)
# closure check along fitted CNP line
vbg_test=np.linspace(-4,4,17); vtg_test=slope*vbg_test+intc
n_line=np.array([cal.density(a,b) for a,b in zip(vtg_test,vbg_test)])
D_at_D0=cal.displacement_field(vtg_D0,bg_D0)
print(f"\nclosure: |n| along fitted CNP line max = {np.abs(n_line).max():.3e} m^-2 (want ~0)")
print(f"  D at the D=0 locator = {D_at_D0:.3e} V/m (want 0)")

# --- max |n| reach at D=0 within validators ---
# D=0 line: dV_tg = ratio*dV_bg through (vtg_D0,bg_D0)
def on_D0(vbg): return vtg_D0+ratio*(vbg-bg_D0)
for vbg in [-4.5,-4.0,4.0,4.5]:
    vtg=on_D0(vbg)
    ok = TG_LO<=vtg<=TG_HI
    n=cal.density(vtg,vbg); D=cal.displacement_field(vtg,vbg)
    print(f"  D0 line: V_bg={vbg:+.2f} V_tg={vtg:+.2f} {'OK' if ok else 'OUT'}  n={n:+.3e} m^-2 ({n/1e16:+.2f}e12 cm^-2)  D={D:.2e}")

import pickle
pickle.dump(dict(slope=slope,intc=intc,ratio=ratio,t_tg=t_tg,t_bg_eff=t_bg_eff,
                 bg_D0=bg_D0,vtg_D0=vtg_D0,n_offset=cal.n_offset,D_offset=cal.D_offset),
            open("hera_scratch/calib.pkl","wb"))
print("\nsaved calib.pkl")
