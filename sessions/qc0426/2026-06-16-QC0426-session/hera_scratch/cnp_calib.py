import numpy as np, json
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import scipy.constants as cst

m=json.load(open("data/1/metadata.json")); idx={c:i for i,c in enumerate(m["columns"])}
d=np.loadtxt("data/1/data.tsv.gz")
nfast=101; nr=d.shape[0]//nfast; d=d[:nr*nfast].reshape(nr,nfast,-1)
bg=d[:,0,idx["k_bg_volt"]]; tg=d[0,:,idx["DC_bias"]]
I_bias=5e-9
print(f"map {nr} BG rows x {nfast} TG pts; BG[{bg.min():.2f},{bg.max():.2f}] TG[{tg.min():.2f},{tg.max():.2f}]")

# Geometry-prior capacitances (SiO2 term zeroed) — c_tg anchored to stack prior.
eps0=cst.epsilon_0; kap=3.0
c_tg = eps0*kap/15.6e-9
c_bg_geom = eps0*kap/12e-9
print(f"geom: c_tg={c_tg:.4e} F/m^2  c_bg_geom={c_bg_geom:.4e}  ratio_geom(c_bg/c_tg)={c_bg_geom/c_tg:.3f}")

def ridge(Rname):
    R=np.abs(d[:,:,idx[Rname]])/I_bias
    tg_cnp=np.full(nr,np.nan)
    pred=-1.30*bg   # geometry-prior seed for continuity window
    for r in range(nr):
        sm=gaussian_filter1d(R[r],2.0)
        # continuity window: +/-2V around prediction (avoid competing maxima)
        win=np.abs(tg-pred[r])<2.0
        if win.sum()<5: continue
        j=np.where(win)[0][np.argmax(sm[win])]
        if j<=1 or j>=nfast-2:   # edge-clipped -> exclude
            continue
        tg_cnp[r]=tg[j]
    return tg_cnp,R

res={}
fig,ax=plt.subplots(1,2,figsize=(13,5))
for k,(nm,col) in enumerate([("sr1 T3-T4","sr1_X"),("sr2 B4-B5","sr2_X")]):
    tg_cnp,R=ridge(col)
    ok=~np.isnan(tg_cnp)
    p=np.polyfit(bg[ok],tg_cnp[ok],1)   # tg_cnp = p[0]*bg + p[1]
    resid=tg_cnp[ok]-np.polyval(p,bg[ok])
    ratio=-p[0]
    res[nm]=dict(slope=p[0],intercept=p[1],ratio=ratio,rms=resid.std(),n=ok.sum())
    print(f"\n{nm}: rows used {ok.sum()}/{nr}  slope dVtg/dVbg={p[0]:.4f} intercept={p[1]:+.4f} V")
    print(f"   -> c_bg/c_tg = -slope = {ratio:.3f}  (geom 1.30)  ridge-fit RMS={resid.std()*1e3:.1f} mV")
    im=ax[k].pcolormesh(bg,tg,np.log10(np.clip(R.T,1,None)),shading="auto",cmap="viridis")
    ax[k].plot(bg[ok],tg_cnp[ok],"r.",ms=4,label="CNP ridge")
    ax[k].plot(bg,np.polyval(p,bg),"w--",lw=1,label=f"fit slope {p[0]:.2f}")
    ax[k].set_xlabel("BG (V)"); ax[k].set_ylabel("TG / DC_bias (V)")
    ax[k].set_title(f"{nm}  log10 Rxx"); ax[k].legend(loc="upper right",fontsize=8)
fig.tight_layout(); fig.savefig("hera_scratch/gatemap_cnp.png",dpi=110)
print("\nsaved hera_scratch/gatemap_cnp.png")

# Cross-channel agreement
rr=[res[k]["ratio"] for k in res]
print(f"\ncross-channel ratio: {rr[0]:.3f} vs {rr[1]:.3f}  (delta {abs(rr[0]-rr[1]):.3f})")

# Adopt averaged ratio (channels agree); derive c_bg; offsets from sr1 fit.
ratio=np.mean(rr); c_bg=ratio*c_tg
def calc_nD(Vtg,Vbg,n_off=0,D_off=0):
    n=(c_tg*Vtg+c_bg*Vbg)/cst.e + n_off
    D=0.5*(c_tg*Vtg-c_bg*Vbg)/eps0 + D_off
    return n,D
b_int=res["sr1 T3-T4"]["intercept"]   # Vtg at Vbg=0 on the CNP line
n_off=-calc_nD(b_int,0)[0]
print(f"\nadopted ratio {ratio:.3f}  c_bg={c_bg:.4e}  n_offset={n_off:.3e} m^-2")
# closure: n along fitted ridge ~ 0
tg_line=np.polyval([res["sr1 T3-T4"]["slope"],b_int],bg)
nline,Dline=calc_nD(tg_line,bg,n_off)
print(f"closure: max|n| on ridge = {np.abs(nline).max():.3e} m^-2 ({np.abs(nline).max()/1e16:.3f}e12 cm^-2)")
print(f"n per V along D=0: {2*c_tg/cst.e/1e4:.3e} cm^-2/V (TG, D=0 matched)")
