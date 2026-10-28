import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run
import scipy.constants as cst

c_tg=cst.epsilon_0*3/23.6e-9; c_bg=cst.epsilon_0*3/20e-9
n_offset=-c_bg*0.0259/cst.e
def nD(vtg,vbg):
    n=((c_tg*vtg+c_bg*vbg)/cst.e+n_offset)*1e-4
    D=((c_tg*vtg-c_bg*vbg)/(2*cst.epsilon_0))*1e-9
    return n,D

for fid in (3,4):
    try:
        r=open_run(f"data/{fid}")
    except Exception as e:
        print(f"run {fid}: not available ({e})"); continue
    cfg=json.load(open(f"data/{fid}/metadata.json"))["measurement_config"]
    print(f"\n=== run {fid} === {summarize_run(r)}")
    print("comment:", cfg.get("comment"))
    vtg=r.col("k_tg_volt"); vbg=r.col("k_bg_volt")
    I=r.col("sr830_1_X")/cfg["sr1_gain"]
    X4=r.col("sr830_3_X"); V4=X4/cfg["sr3_gain"]
    Rxx=V4/I
    n,D=nD(vtg,vbg)
    clip=np.abs(X4)>5.0e-6*0.98   # near 5uV over-range
    print(f"D={np.median(D):.3f} V/nm  n=[{n.max()/1e11:+.2f},{n.min()/1e11:+.2f}]e11")
    print(f"clipped (|X3|>~5uV): {clip.sum()}/{len(X4)} pts")
    u=Rxx[~clip]; print("Rxx unclipped: "+("n=0" if u.size==0 else f"min={np.nanmin(u):.1f} median={np.nanmedian(u):.1f} max={np.nanmax(u):.1f} Ω"))
    fig,ax=plt.subplots(2,1,figsize=(7,7),sharex=True)
    ax[0].plot(n/1e11,Rxx,'.-',ms=3); ax[0].plot(n[clip]/1e11,Rxx[clip],'rx',ms=5,label='clipped(>~50Ω)')
    ax[0].set_ylabel("4T Rxx (Ω)"); ax[0].set_title(f"run {fid}: D={np.median(D):.2f} V/nm"); ax[0].legend(); ax[0].axhline(0,c='gray',lw=.5)
    ax[0].set_ylim(-10,120)
    ax[1].plot(n/1e11,r.col("sr830_3_P"),'.-',ms=3); ax[1].set_ylabel("4T phase (deg)"); ax[1].set_xlabel("n (1e11 cm^-2)")
    plt.tight_layout(); plt.savefig(f"hera_scratch/run{fid}.png",dpi=110); print(f"saved run{fid}.png")
