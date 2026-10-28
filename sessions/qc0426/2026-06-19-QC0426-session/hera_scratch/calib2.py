import numpy as np, pickle
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
        rmax=r.max(); top=t[r>=0.92*rmax]
        bb.append(b); vv.append(np.median(top)); pk.append(rmax)
        edge.append(top.min()<=TG_LO+0.4 or top.max()>=TG_HI-0.4)
    return map(np.array,(bb,vv,pk,edge))
b1,v1,pk1,e1=ridge(R1); b2,v2,pk2,e2=ridge(R2)
B=np.concatenate([b1[~e1],b2[~e2]]); V=np.concatenate([v1[~e1],v2[~e2]])
slope,intc=np.polyfit(B,V,1); ratio=-slope
uc=pk1<RAIL; j=np.argmin(pk1[uc]); bg_D0=float(b1[uc][j]); vtg_D0=float(v1[uc][j])

t_tg=15.6e-9; t_bg_eff=t_tg/ratio
cal0=GateCalibration.from_thicknesses(t_tg,t_bg_eff,0.0)
n_off=-float(cal0.density(intc,0.0))
D_off=-float(cal0.displacement_field(vtg_D0,bg_D0))
cal=GateCalibration.from_thicknesses(t_tg,t_bg_eff,0.0,n_offset=n_off,D_offset=D_off)
# closure
vbg=np.linspace(-4,4,17); vtg=slope*vbg+intc
n_line=cal.density(vtg,vbg)
print(f"pooled CNP fit: V_tg={slope:+.4f}*V_bg{intc:+.4f}  c_bg/c_tg={ratio:.4f}")
print(f"D=0 locus (CNP-R min): V_tg={vtg_D0:+.2f} V_bg={bg_D0:+.2f}")
print(f"closure |n|max on CNP line = {np.abs(n_line).max():.2e} m^-2 ; D at locus = {float(cal.displacement_field(vtg_D0,bg_D0)):.2e} V/m")
print(f"offsets: n_offset={n_off:.3e}  D_offset={D_off:.3e}")
# max |n| at D=0 within validators
def on_D0(x): return vtg_D0+ratio*(x-bg_D0)
print("\nmax-|n| reach at D=0:")
best={}
for side,vbg_e in [('hole',-4.5),('elec',+4.5)]:
    vt=on_D0(vbg_e); vt=max(TG_LO,min(TG_HI,vt))
    # if clipped by TG edge, back off vbg to stay in range
    vbg_use=vbg_e
    if not (TG_LO<=on_D0(vbg_e)<=TG_HI):
        vbg_use=(TG_HI-vtg_D0)/ratio+bg_D0 if vbg_e>0 else (TG_LO-vtg_D0)/ratio+bg_D0
    vt=on_D0(vbg_use)
    n=float(cal.density(vt,vbg_use)); D=float(cal.displacement_field(vt,vbg_use))
    print(f"  {side}: V_bg={vbg_use:+.3f} V_tg={vt:+.3f}  n={n:+.3e} ({n/1e16:+.2f}e12 cm^-2)  D={D:.1e}")
    best[side]=(vbg_use,vt,n)
pickle.dump(dict(slope=slope,intc=intc,ratio=ratio,t_tg=t_tg,t_bg_eff=t_bg_eff,
                 bg_D0=bg_D0,vtg_D0=vtg_D0,n_offset=n_off,D_offset=D_off,best=best),
            open("hera_scratch/calib.pkl","wb"))
print("saved calib.pkl")
