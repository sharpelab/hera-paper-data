import numpy as np, json, sys
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
sys.path.insert(0, r"C:/Users/DGG/measurement_env/hera/models/trilayer_fs_count")
import fs_count_b0 as M

RUN="data/3"; m=json.load(open(f"{RUN}/metadata.json")); ci={c:i for i,c in enumerate(m["columns"])}
try: d=np.loadtxt(f"{RUN}/data.tsv.gz")
except OSError: d=np.loadtxt(f"{RUN}/data.tsv")
nfast=36; nr=d.shape[0]//nfast; g=d[:nr*nfast].reshape(nr,nfast,-1)
B=g[:,0,ci["magnet_mag"]]; I_bias=5e-9; n_vec=np.linspace(-1.4e12,-5.0e12,nfast)
print(f"rows {nr}/79  B {B[0]:.2f}->{B[-1]:.2f}  interrupted={m['interrupted']}")
BLO,BHI=2.0,8.0; sel=(B>=BLO)&(B<=BHI)
print(f"window B[{BLO},{BHI}] {sel.sum()} rows  dF_res~{1/(1/B[sel].min()-1/B[sel].max()):.1f} T")

def spectrum(col, j, detr=("poly",6), N=4096):
    x=1/B[sel]; r=g[sel,j,ci[col]]/I_bias; o=np.argsort(x); x,r=x[o],r[o]
    xu=np.linspace(x.min(),x.max(),N); ru=np.interp(xu,x,r); dx=xu[1]-xu[0]
    ru=(ru-np.polyval(np.polyfit(xu,ru,detr[1]),xu)) if detr[0]=="poly" else (ru-gaussian_filter1d(ru,detr[1]/dx))
    F=np.fft.rfftfreq(N,d=dx); A=np.abs(np.fft.rfft(ru*np.hanning(N)))
    return F,A

def analyze(col):
    F0,_=spectrum(col,0); Fmask=(F0>3)&(F0<70); Fax=F0[Fmask]
    SP=np.zeros((nfast,Fmask.sum())); dom=np.full(nfast,np.nan); doms=[]
    ridge_band=(Fax>12)&(Fax<62)                    # above the non-dispersing low-F artifact
    for j in range(nfast):
        _,A=spectrum(col,j); a=A[Fmask]; SP[j]=a/a.max()
        asm=gaussian_filter1d(a,2.0)
        dom[j]=Fax[ridge_band][np.argmax(asm[ridge_band])]   # main dispersing ridge
        doms.append(round(dom[j],1))
    return Fax,SP,dom,doms

# model curves (valid |n|<=3.5e12)
nn=np.abs(n_vec)*1e4; F_ml=[];F_bl=[];F_abc=[]
for x in nn:
    _,fs=M.aba_fs(x); fr=sorted(F for F,_ in fs)
    F_ml.append(fr[0] if len(fr)>=2 else np.nan); F_bl.append(fr[-1] if fr else np.nan); F_abc.append(M.abc_fs(x)[4])
F_ml=np.array(F_ml);F_bl=np.array(F_bl);F_abc=np.array(F_abc)
F_lutt=nn*6.62607e-34/(4*1.602177e-19); valid=np.abs(n_vec)<=3.5e12

fig,ax=plt.subplots(1,2,figsize=(14,5.5))
for k,col in enumerate(["sr1_X","sr2_X"]):
    Fax,SP,dom,doms=analyze(col)
    absn=np.abs(n_vec)/1e12
    ax[k].pcolormesh(absn,Fax,SP.T,shading="auto",cmap="inferno")
    ax[k].plot(absn,dom,"co",ms=4,mfc="none",label="dominant peak")
    ax[k].plot(absn[valid],F_lutt[valid],"g--",lw=1.4,label="full-density n·h/4e")
    ax[k].plot(absn[valid],F_bl[valid],"m:",lw=1.2,label="ABA BL (model)")
    ax[k].plot(absn[valid],F_ml[valid],"r:",lw=1.2,label="ABA ML (model)")
    ax[k].plot(absn[valid],F_abc[valid],"c-",lw=1.0,alpha=.6,label="ABC single (model)")
    ax[k].set_xlabel("|n| (1e12 cm^-2)");ax[k].set_ylabel("F (T)");ax[k].set_ylim(0,70)
    ax[k].set_title(f"{col}: SdH FFT(n) [model valid |n|<=3.5]");ax[k].legend(fontsize=7,loc="upper left")
    print(f"\n{col} dominant F(n) vs full-density:")
    for j in range(0,nfast,4):
        r=dom[j]/F_lutt[j] if F_lutt[j]>0 else np.nan
        print(f"  n={n_vec[j]/1e12:+.2f}  F_dom={dom[j]:5.1f}  full={F_lutt[j]:5.1f}  ratio={r:.2f}  peaks={doms[j]}")
plt.tight_layout(); plt.savefig("hera_scratch/fan_final.png",dpi=120); print("\nsaved hera_scratch/fan_final.png")
