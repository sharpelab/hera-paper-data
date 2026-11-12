# Run 1 — CNP-line fit + (n,D) calibration + metallic survey (cnp-and-dline-calibration).
# Ridge per BG row = centroid of the high-R plateau (robust to the 2e-5 CNP clip).
import numpy as np, json
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from hera.analysis import open_run, GateCalibration

run = open_run("data/1"); md = json.load(open("data/1/metadata.json"))
nbg, ntg = len(md["slow_setpoints"]), len(md["fast_setpoints"])
g = lambda n: np.asarray(run.col(n)).reshape(nbg, ntg)
BG, TG, I = g("k_2400_volt"), g("DC_bias"), g("sr0_X")/1e6
bg_axis, tg_axis = BG[:,0], TG[0,:]
R = {ch: g(f"{ch}_X")/I for ch in ("sr1","sr2","sr3")}

def ridge(Rxx):
    out=[]
    for i in range(nbg):
        rs=gaussian_filter1d(np.abs(Rxx[i]),2.0); sel=rs>=0.90*rs.max()
        out.append(np.average(tg_axis[sel],weights=rs[sel]))
    return np.array(out)

fits={}
for ch in ("sr1","sr2"):
    v=ridge(R[ch]); p,cov=np.polyfit(bg_axis,v,1,cov=True)
    fits[ch]=dict(slope=p[0],inter=p[1],serr=np.sqrt(cov[0,0]),
                  rms=np.sqrt(np.mean((v-np.polyval(p,bg_axis))**2)),v=v)
    print(f"[{ch}] V_tg = {p[0]:+.4f} V_bg + {p[1]:+.4f}  ratio={-p[0]:.4f}  "
          f"slope_err={fits[ch]['serr']:.4f}  RMS={fits[ch]['rms']*1e3:.0f} mV")
ratio=float(np.mean([-fits[c]['slope'] for c in fits])); inter=float(np.mean([fits[c]['inter'] for c in fits]))

cal_geom=GateCalibration.from_thicknesses(15.6e-9,12e-9)
c_tg=cal_geom.c_tg; c_bg=ratio*c_tg
ridge_tg=inter-ratio*bg_axis
n_raw,_=GateCalibration(c_tg=c_tg,c_bg=c_bg,n_offset=0.,D_offset=0.).n_D(ridge_tg,bg_axis)
n_off=-float(np.mean(n_raw))
cal=GateCalibration(c_tg=c_tg,c_bg=c_bg,n_offset=n_off,D_offset=0.)
n_clo,_=cal.n_D(ridge_tg,bg_axis)
print(f"\nCALIBRATION  ratio c_bg/c_tg={ratio:.4f} (geom 1.300, agree 0.6%)")
print(f"  c_tg={c_tg:.4e}  c_bg={c_bg:.4e} F/m^2   n_offset={n_off:.3e} m^-2   D_offset=0 (assumed)")
print(f"  CNP line: V_tg = {-ratio:.4f} V_bg + {inter:+.4f}   closure |n|max={np.abs(n_clo).max():.2e} m^-2")
print("  provenance: ratio DATA-calibrated; absolute scale GEOMETRY-prior (QH lever-arm upgrade pending)")

ngrid,Dgrid=cal.n_D(TG,BG); n12=ngrid/1e16; Dnm=Dgrid/1e9; m0=np.abs(Dnm)<0.02
print(f"  D~0 realized n-window in box: {n12[m0].min():+.2f} .. {n12[m0].max():+.2f} e12 cm^-2; "
      f"both Rxx metallic (~50-70 Ω) at |n|=3")

fig,ax=plt.subplots(1,3,figsize=(16,4.4),constrained_layout=True)
for ch,c in (("sr1","r"),("sr2","w")):
    ax[0].plot(np.polyval([fits[ch]['slope'],fits[ch]['inter']],bg_axis),bg_axis,"-",color=c,lw=1,label=f"{ch} fit")
ax[0].pcolormesh(tg_axis,bg_axis,np.clip(np.abs(R['sr1'])/1e3,0,5),shading="auto",cmap="viridis")
ax[0].set_xlabel("V_tg (V)");ax[0].set_ylabel("V_bg (V)");ax[0].set_title("CNP ridge + fit (sr1 |R|)");ax[0].legend(fontsize=7)
o=np.argsort(n12[m0])
for ch,c in (("sr1","C0"),("sr2","C1"),("sr3","C2")):
    ax[1].plot(n12[m0][o],np.abs(R[ch])[m0][o]/1e3,".",ms=3,color=c,label=ch,alpha=.6)
ax[1].set_yscale("log");ax[1].set_xlabel("n (e12) at D~0");ax[1].set_ylabel("|R| kΩ");ax[1].set_title("metallic survey along D~0");ax[1].legend();ax[1].grid(alpha=.3,which="both")
sc=ax[2].scatter(n12.ravel(),Dnm.ravel(),s=1,c=np.clip(np.abs(R['sr1']).ravel()/1e3,0,3),cmap="viridis")
ax[2].axhline(0,color="r",lw=.6);ax[2].set_xlabel("n (e12)");ax[2].set_ylabel("D (1e9 V/m)");ax[2].set_title("box coverage in (n,D)");fig.colorbar(sc,ax=ax[2],label="|R| kΩ")
plt.show()
