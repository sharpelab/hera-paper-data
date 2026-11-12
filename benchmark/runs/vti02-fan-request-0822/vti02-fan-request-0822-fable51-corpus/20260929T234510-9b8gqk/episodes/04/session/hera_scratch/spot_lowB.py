"""Low-B focus on run 6 (electron) and run 7 (hole): onset from the 10 mT leg only, bg-subtracted dR vs B and vs 1/B below 3 T, FFT window variants."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError
def load(rid):
    r=open_run(f"data/{rid}"); B=r.col("magnet_field"); R=np.abs(r.col("sr1_X")/(r.col("sr0_X")/(-1e6)))
    o=np.argsort(B); return B[o],R[o]
fig,axs=plt.subplots(3,2,figsize=(14,11))
for j,(rid,blo_fine) in enumerate(((6,1.0),(7,0.3))):
    B,R=load(rid)
    for blo in (0.3, blo_fine, 1.5):
        try:
            on=sdh_onset(R,B,b_lo=blo,r_full_scale=5000); print(f"run {rid} b_lo={blo}: onset_b={on.onset_b:.2f} T (tone {on.onset_freq:.1f} T)")
            for t in on.tones: print(f"    {t.freq:5.1f} T onset {t.onset_b:.2f} snr {max(t.snr):.0f} censored={t.censored} marginal={t.marginal} harm_of={t.harmonic_of}")
        except SdhOnsetError as ex: print(f"run {rid} b_lo={blo}: SdhOnsetError {ex}")
    m=(B>=0.3)&(B<=3.0); cf=np.polyfit(B[m],R[m],4); dR=R[m]-np.polyval(cf,B[m])
    ax=axs[0,j]; ax.plot(B[m],R[m],'.-',ms=3,lw=0.6); ax.set_title(f"run {rid} raw R, 0.3-3 T"); ax.set_xlabel("B (T)")
    ax=axs[1,j]; ax.plot(1/B[m],dR,'.-',ms=3,lw=0.6); ax.set_xlabel("1/B"); ax.set_title("dR (deg-4 bg) vs 1/B, 0.3-3 T"); ax.axvline(1.0,color='r',ls=':')
    ax=axs[2,j]
    for lab,rng in (("1-10",(1.0,10)),("1-4",(1.0,4.0)),("1.5-6",(1.5,6.0)),("0.5-3",(0.5,3.0)),("3-10",(3.0,10))):
        try:
            f,sp=sdh_fft(R[:,None],B,b_range=rng,bg_degree=5,log=False); sp=sp[0]/sp[0][f>2].max()
            ax.plot(f,sp,lw=0.8,label=lab); ip,_=find_peaks(sp,height=0.08,prominence=0.04); ip=ip[f[ip]>1.5]
            print(f"  run {rid} FFT {lab} T: "+", ".join(f"{f[i]:.1f}({sp[i]:.2f})" for i in ip[:12]))
        except Exception as ex: print("fft fail",lab,ex)
    ax.set_xlim(0,40); ax.legend(fontsize=7); ax.set_xlabel("F (T)")
plt.tight_layout(); plt.savefig("hera_scratch/spot_lowB.png",dpi=110)
