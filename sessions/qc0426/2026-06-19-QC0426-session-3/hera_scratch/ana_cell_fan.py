# Run 4 — electron Landau fan (D=0): per-column 1/B FFT map F(n), high-F ridge vs F_L + Onsager
# model overlay, detrend-stability of the ridge. The FS-count Step-4/5 read.
import numpy as np, json, sys
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, luttinger_frequency
sys.path.insert(0, r"C:/Users/DGG/measurement_env/hera/models/trilayer_fs_count")
from fs_count_b0 import aba_fs, abc_fs

run = open_run("data/4"); md = json.load(open("data/4/metadata.json"))
cols=md["columns"]; ci={c:i for i,c in enumerate(cols)}
NB=len(md["slow_setpoints"][0]); NF=len(md["fast_setpoints"][0])
A=np.column_stack([run.col(c) for c in cols]).reshape(NB,NF,len(cols))
B=A[:,0,ci["magnet_mag"]]; I=A[:,:,ci["sr0_X"]]/1e6
c_tg,c_bg,n_off=1.7027e-3,2.2004e-3,-1.581e15
n_des=(c_tg*A[0,:,ci["DC_bias"]]+c_bg*A[0,:,ci["k_2400_volt"]])/1.602176634e-19+n_off
F_L=luttinger_frequency(np.abs(n_des))
print("leakage |I_bg|max=%.2e |I_si|max=%.2e A; not interrupted=%s"%(
    np.abs(A[:,:,ci['k_2400_curr']]).max(), np.abs(A[:,:,ci['k_2410_curr']]).max(), not run.interrupted))
lo,hi=1.0,4.0
def fftmap(ch,detrend=5):
    Rg=np.abs(A[:,:,ci[f"{ch}_X"]]/I); clip=Rg.max(axis=0)>540
    f,spec=sdh_fft(Rg,B,b_range=(lo,hi),detrend=detrend,window="hann",log=False)
    return f,spec,clip
def hi_ridge(ch,detrend=5):
    f,spec,clip=fftmap(ch,detrend); Fhi=np.full(NF,np.nan)
    for j in range(NF):
        if clip[j]: continue
        band=(f>0.6*F_L[j])&(f<1.3*F_L[j])
        if band.sum(): Fhi[j]=f[band][np.argmax(spec[j][band])]
    return Fhi
nmod=np.linspace(1.0e16,3.5e16,14); fML=[];fBL=[];fABC=[]
for n in nmod:
    _,fs=aba_fs(n); Fs=sorted(F for F,_ in fs); fML.append(Fs[0] if len(Fs)>1 else np.nan); fBL.append(Fs[-1])
    fABC.append(abc_fs(n)[4])
fML,fBL,fABC=map(np.array,(fML,fBL,fABC))

fig=plt.figure(figsize=(16,9));
for i,ch in enumerate(("sr1","sr2")):
    ax=fig.add_subplot(2,2,i+1); f,spec,clip=fftmap(ch)
    S=np.array([spec[j]/spec[j].max() if (not clip[j] and spec[j].max()>0) else spec[j]*0 for j in range(NF)])
    sel=f<=70; im=ax.pcolormesh(n_des/1e16,f[sel],S[:,sel].T,shading="auto",cmap="magma")
    ax.plot(n_des/1e16,F_L,"c--",lw=1.1,label="F_L"); fig.colorbar(im,ax=ax,label="FFT (col-norm)")
    ax.set_xlabel("n (1e12)"); ax.set_ylabel("F (T)"); ax.set_title(f"{ch} per-column FFT map"); ax.legend(fontsize=8)
ax=fig.add_subplot(2,2,3)
for ch,c in (("sr1","C0"),("sr2","C1")): ax.plot(n_des/1e16,hi_ridge(ch),"o",ms=4,color=c,label=f"{ch} F_high")
ax.plot(n_des/1e16,F_L,"k--",lw=1,label="F_L"); ax.plot(nmod/1e16,fBL,"-",color="C3",label="ABA f_BL"); ax.plot(nmod/1e16,fABC,":",color="C2",label="ABC F_tot"); ax.plot(nmod/1e16,fML,"-",color="C4",label="ABA f_ML")
ax.set_ylim(0,55); ax.set_xlabel("n (1e12)"); ax.set_ylabel("F (T)"); ax.set_title("High-F ridge vs F_L + Onsager model"); ax.legend(fontsize=7); ax.grid(alpha=.3)
ax=fig.add_subplot(2,2,4)
for d,c in ((3,"C0"),(5,"C3"),(7,"C4")): ax.plot(n_des/1e16,hi_ridge("sr1",d),"o-",ms=3,lw=.5,color=c,label=f"detrend {d}")
ax.plot(n_des/1e16,F_L,"k--",lw=1); ax.set_ylim(0,55); ax.set_xlabel("n (1e12)"); ax.set_ylabel("F_high (T)"); ax.set_title("Ridge detrend-stability (sr1) — stable=real"); ax.legend(fontsize=7); ax.grid(alpha=.3)
fig.suptitle("Run 4 — electron Landau fan, FS-count read"); fig.tight_layout(); plt.show()
Fhi=hi_ridge("sr1"); ok=np.isfinite(Fhi)
print(f"sr1 F_high(n): linear F={np.polyfit(n_des[ok]/1e16,Fhi[ok],1)[0]:.2f}*n; F_high/F_L median={np.nanmedian(Fhi/F_L):.2f}")
print(f"model n=3.5e12: ABA f_BL={fBL[-1]:.1f} f_ML={fML[-1]:.1f}; ABC F_tot={fABC[-1]:.1f}; F_L={luttinger_frequency(3.5e16):.1f}")
