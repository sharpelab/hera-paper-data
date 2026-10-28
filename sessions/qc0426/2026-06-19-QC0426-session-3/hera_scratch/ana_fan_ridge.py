import numpy as np, json, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, luttinger_frequency
sys.path.insert(0, "/c/Users/DGG/measurement_env/hera/models/trilayer_fs_count".replace("/c/","C:/"))
from fs_count_b0 import aba_fs, abc_fs

run = open_run("data/4"); md = json.load(open("data/4/metadata.json"))
cols = md["columns"]; ci={c:i for i,c in enumerate(cols)}
NB=len(md["slow_setpoints"][0]); NF=len(md["fast_setpoints"][0])
A=np.column_stack([run.col(c) for c in cols]).reshape(NB,NF,len(cols))
B=A[:,0,ci["magnet_mag"]]; I=A[:,:,ci["sr0_X"]]/1e6
c_tg,c_bg,n_off=1.7027e-3,2.2004e-3,-1.581e15
n_des=(c_tg*A[0,:,ci["DC_bias"]]+c_bg*A[0,:,ci["k_2400_volt"]])/1.602176634e-19+n_off
F_L=luttinger_frequency(np.abs(n_des))

def hi_ridge(ch, detrend, lo=1.0, hi=4.0):
    Rg=np.abs(A[:,:,ci[f"{ch}_X"]]/I); clip=Rg.max(axis=0)>540
    f,spec=sdh_fft(Rg,B,b_range=(lo,hi),detrend=detrend,window="hann",log=False)
    Fhi=np.full(NF,np.nan)
    for j in range(NF):
        if clip[j]: continue
        band=(f>0.6*F_L[j])&(f<1.3*F_L[j])
        if band.sum()==0: continue
        Fhi[j]=f[band][np.argmax(spec[j][band])]
    return Fhi, clip

# model curves (valid n<=3.5e12)
nmod=np.linspace(1.0e16,3.5e16,14)
fML=[]; fBL=[]; fABC=[]
for n in nmod:
    _,fs=aba_fs(n); Fs=sorted(F for F,_ in fs)
    fML.append(Fs[0] if len(Fs)>1 else np.nan); fBL.append(Fs[-1])
    _,_,_,_,Ft=abc_fs(n); fABC.append(Ft)
fML,fBL,fABC=map(np.array,(fML,fBL,fABC))

fig,ax=plt.subplots(1,2,figsize=(14,5),constrained_layout=True)
# (1) high-F ridge vs F_L + model
for ch,c in (("sr1","C0"),("sr2","C1")):
    Fhi,clip=hi_ridge(ch,5)
    ax[0].plot(n_des/1e16,Fhi,"o",ms=4,color=c,label=f"{ch} F_high")
ax[0].plot(n_des/1e16,F_L,"k--",lw=1,label="F_L=(h/4e)n")
ax[0].plot(nmod/1e16,fBL,"-",color="C3",lw=1.5,label="ABA f_BL (model)")
ax[0].plot(nmod/1e16,fABC,":",color="C2",lw=1.5,label="ABC F_tot (model)")
ax[0].plot(nmod/1e16,fML,"-",color="C4",lw=1.5,label="ABA f_ML (model)")
ax[0].set_xlabel("n (1e12)"); ax[0].set_ylabel("F (T)"); ax[0].set_title("Fan high-F ridge vs F_L + Onsager model"); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3); ax[0].set_ylim(0,55)
# (2) detrend stability of the high-F ridge (sr1)
for d,c in ((3,"C0"),(5,"C3"),(7,"C4")):
    Fhi,_=hi_ridge("sr1",d); ax[1].plot(n_des/1e16,Fhi,"o-",ms=3,lw=.6,color=c,label=f"detrend={d}")
ax[1].plot(n_des/1e16,F_L,"k--",lw=1,label="F_L")
ax[1].set_xlabel("n (1e12)"); ax[1].set_ylabel("F_high (T)"); ax[1].set_title("sr1 high-F ridge — detrend stability"); ax[1].legend(fontsize=8); ax[1].grid(alpha=.3); ax[1].set_ylim(0,55)
fig.savefig("hera_scratch/fan_ridge.png",dpi=115)

# numbers: linear fit F_high vs n (should pass ~origin with slope ~ F_L/n if = density pocket)
Fhi,_=hi_ridge("sr1",5); ok=np.isfinite(Fhi)
p=np.polyfit(n_des[ok]/1e16,Fhi[ok],1)
print(f"sr1 F_high(n) linear fit: F = {p[0]:.2f}*n + {p[1]:.1f}  (F_L slope = {F_L[-1]/(n_des[-1]/1e16):.2f} T per e12)")
print(f"  F_high/F_L ratio (median over unclipped): {np.nanmedian(Fhi/F_L):.2f}")
print(f"model at n=3.5e12: f_BL={fBL[-1]:.1f}  f_ML={fML[-1]:.1f}  ABC F_tot={fABC[-1]:.1f}  F_L={luttinger_frequency(3.5e16):.1f}")
print("saved hera_scratch/fan_ridge.png")
