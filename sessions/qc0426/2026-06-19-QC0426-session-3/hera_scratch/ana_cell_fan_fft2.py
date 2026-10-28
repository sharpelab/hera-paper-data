# Run 4 — ENHANCED fan FFT to bring out the tones (presentation only; no re-measure).
# Lever 1: smooth the FFT-power along n (F(n) varies slowly -> neighbour-column averaging lifts SNR).
# Lever 2: log power. Lever 3: stronger detrend (order 7) to suppress the ~5 T low-F residual band.
# Note: the fan ran at fast_delay=1.0 s (~3 tau) vs the spot checks' 2.2 s (~7 tau) -> attenuated SdH
# AMPLITUDE (not frequency). So tones are inherently weaker here than in runs 2/3; this is the trade.
import numpy as np, json
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from hera.analysis import open_run, sdh_fft, luttinger_frequency

run = open_run("data/4"); md=json.load(open("data/4/metadata.json"))
cols=md["columns"]; ci={c:i for i,c in enumerate(cols)}
NB=len(md["slow_setpoints"][0]); NF=len(md["fast_setpoints"][0])
A=np.column_stack([run.col(c) for c in cols]).reshape(NB,NF,len(cols))
B=A[:,0,ci["magnet_mag"]]; I=A[:,:,ci["sr0_X"]]/1e6
c_tg,c_bg,n_off=1.7027e-3,2.2004e-3,-1.581e15
n12=((c_tg*A[0,:,ci["DC_bias"]]+c_bg*A[0,:,ci["k_2400_volt"]])/1.602176634e-19+n_off)/1e16
F_L=luttinger_frequency(np.abs(n12)*1e16)

def emap(ch,detrend):
    Rg=np.abs(A[:,:,ci[f"{ch}_X"]]/I); clip=Rg.max(0)>540
    f,spec=sdh_fft(Rg,B,b_range=(1.0,4.0),detrend=detrend,window="hann",log=False)
    S=spec.copy()
    for j in range(NF): S[j]=spec[j]/spec[j].max() if (not clip[j] and spec[j].max()>0) else 0
    S=gaussian_filter1d(S,1.2,axis=0)              # smooth power along n
    return f,S,clip

fig,ax=plt.subplots(1,2,figsize=(15,5.2),constrained_layout=True)
for a,ch in zip(ax,("sr1","sr2")):
    f,S,clip=emap(ch,7); sel=(f>=6)&(f<=60)          # hide the <6 T low-F detrend-artifact band
    Z=S[:,sel].T
    vmax=np.percentile(Z[Z>0],99)                     # contrast clip: suppress noise floor
    im=a.pcolormesh(n12,f[sel],Z,shading="auto",cmap="magma",vmin=0.25*vmax,vmax=vmax)
    a.plot(n12,F_L,"c--",lw=1.2,label="F_L (BL+ML total)")
    a.plot(n12,0.89*F_L,"w:",lw=1.0,label="0.89 F_L (BL ridge)")
    fig.colorbar(im,ax=a,label="FFT power (n-smoothed, linear)")
    a.set_xlabel("n (1e12 cm^-2)"); a.set_ylabel("SdH freq F (T)"); a.set_title(f"{ch}: enhanced fan FFT (n-smoothed, contrast-clipped, detrend7)")
    a.legend(fontsize=8,loc="upper left"); a.set_ylim(6,60)
fig.suptitle("Run 4 — enhanced fan FFT (F>6 T shown). BL ridge tracks ~0.89 F_L; ML partner (~8 T) sits in the hidden low-F band -> see spot checks for it.")
plt.show()
