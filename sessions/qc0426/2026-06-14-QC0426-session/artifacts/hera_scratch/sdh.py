import json, gzip, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from sharpelab_nb.gates import stack_capacitance, calc_nD
from hera.analysis import fan_grids, resistance_grids, sdh_fft

c_tg = stack_capacitance([(15.6,3)]); c_bg = 1.3136*c_tg; n_off, D_off = -0.225, 0.0
m = json.load(open("data/20/metadata.json")); ci={c:i for i,c in enumerate(m["columns"])}
d = np.loadtxt(gzip.open("data/20/data.tsv.gz")); nf=len(m["fast_setpoints"][0])
B0=np.array(m["slow_setpoints"][0]); nb=len(B0); d=d[:nb*nf]
tgc=d[:,ci["DC_bias"]].reshape(nb,nf); bgc=d[:,ci["k_bg_volt"]].reshape(nb,nf)
n_axis=calc_nD(tgc,bgc,c_tg,c_bg,n_off,D_off)[0][0]

fg=fan_grids("data/20"); rg=resistance_grids(fg); B=fg.slow
for chan in ["sr1","sr2"]:
    R=np.abs(rg.R[chan])
    freqs,spec=sdh_fft(R, B, b_range=(3.0,8.0))   # spec (nfast, nfreq)
    fig,ax=plt.subplots(1,2,figsize=(13,5))
    sel=(n_axis>0.3)&(n_axis<4)
    im=ax[0].pcolormesh(n_axis[sel], freqs, spec[sel].T, shading="nearest", cmap="viridis")
    ax[0].set_xlabel("n (1e12 cm^-2)"); ax[0].set_ylabel("SdH freq (T)"); ax[0].set_ylim(0,60)
    ax[0].set_title(f"{chan} SdH-FFT (B 3-8T)")
    # expected single-band line: f = n*h/(g e), g=4
    h=6.626e-34; e=1.602e-19
    for g,lab in [(4,"g=4"),(2,"g=2")]:
        ax[0].plot(n_axis[sel], n_axis[sel]*1e16*h/(g*e), "w--", lw=0.8);
    fig.colorbar(im,ax=ax[0])
    # peak count per column
    print(f"\n=== {chan}: peaks per n-column (B 3-8T FFT) ===")
    onef=twof=0
    for j in np.where(sel)[0]:
        s=spec[j]; s=s/ (s.max()+1e-9)
        pk,_=find_peaks(s, height=0.35, distance=max(2,int(len(freqs)*0.04)))
        pk=[p for p in pk if 3<freqs[p]<55]
        if len(pk)>=2: twof+=1
        elif len(pk)==1: onef+=1
        if j%6==0:
            fpk=" ".join(f"{freqs[p]:.0f}" for p in pk)
            ftot=n_axis[j]*1e16*h/(4*e)
            print(f"  n={n_axis[j]:+.2f}: peaks@T=[{fpk}]  (f_tot g=4 = {ftot:.0f} T)")
    print(f"  columns with 1 peak: {onef}, with >=2 peaks: {twof}")
    # representative single-column FFT
    j=int(np.argmin(np.abs(n_axis-2.0)))
    ax[1].plot(freqs, spec[j]/spec[j].max()); ax[1].set_xlim(0,60)
    ax[1].set_xlabel("freq (T)"); ax[1].set_ylabel("norm |FFT|"); ax[1].set_title(f"{chan} FFT @ n=2.0")
    fig.tight_layout(); fig.savefig(f"hera_scratch/sdh_{chan}.png", dpi=100)
    print(f"  saved sdh_{chan}.png")
