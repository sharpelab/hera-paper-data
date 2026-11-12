from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, summarize_run

# Raw data first, preserving signed Rxx; no rectification before FFT.
spot_records = {}
for rid in (6, 7):
    r = open_run(Path('data') / str(rid))
    ch = {c.cid:c for c in resolve_channels(r.meta)}
    B = r.col('magnet_field'); I = r.col('sr0_X') / ch['sr0'].gain
    R = r.col('sr1_X') / ch['sr1'].gain / I
    order = np.argsort(B); B, R = B[order], R[order]
    spot_records[rid] = (B, R)
    print(summarize_run(r))
    print(f'Rxx {R.min():.2f}..{R.max():.2f} ohm; I {I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA; T {r.col("T_sample").min():.3f}..{r.col("T_sample").max():.3f} K')
    print('max |gate current| pA:', {c:float(np.max(np.abs(r.col(c)))*1e12) for c in ['k_2400_tg_curr','k_2400_bg_curr']})
    print(f'Duration {(r.col("time")[-1]-r.col("time")[0])/60:.2f} min')
    fig, ax = plt.subplots(2,2,figsize=(10,6))
    ax[0,0].plot(B,R); ax[0,0].set(ylabel='Rxx B1–B2 (ohm)',xlabel='B (T)')
    ax[0,1].plot(r.col('magnet_field'),I*1e9); ax[0,1].set(ylabel='Drain current (nA)',xlabel='B (T)')
    for c in ['k_2400_tg_curr','k_2400_bg_curr']: ax[1,0].plot(r.col('magnet_field'),r.col(c)*1e12,label=c)
    ax[1,0].set(ylabel='Gate current (pA)',xlabel='B (T)'); ax[1,0].legend()
    ax[1,1].plot(r.col('magnet_field'),r.col('T_sample')); ax[1,1].set(ylabel='Sample T (K)',xlabel='B (T)')
    fig.suptitle(f'Run {rid}: raw data'); fig.tight_layout(); plt.show()

# Explicitly retain the extraction fork: the global 0.3–10 T polynomial
# leaks background into slow matched-filter tracks. Never use its censored
# 0.3 T headline as a measured onset.
B,R = spot_records[6]
for hi,deg in [(10,5),(4,5),(8,7)]:
    on=sdh_onset(R,B,b_hi=hi,bg_degree=deg,r_full_scale=5000)
    print(f'Electron onset sensitivity: B_hi={hi}, polynomial degree={deg}\n{on.summary()}')
    if (hi,deg)==(8,7): electron_design_onset=on.onset_b
print('Hole onset:',sdh_onset(*reversed(spot_records[7]),r_full_scale=5000).summary())
fig,ax=plt.subplots(1,2,figsize=(12,4))
for j,rid in enumerate((6,7)):
    B,R=spot_records[rid]
    for cutoff in (1.0,1.5,2.0):
        for degree in (3,5,7):
            f,S=sdh_fft(R[:,None],B,b_range=(cutoff,10),bg_degree=degree,nfft=4096,log=False)
            S=S[0]; use=(f>=3)&(f<=65)
            ax[j].plot(f[use],S[use]/max(S[use]),label=f'B≥{cutoff}, deg {degree}',alpha=.65)
    ax[j].set(xlabel='Frequency (T)',ylabel='Normalized FFT (native resolution)',title=f'Run {rid} extraction sensitivity')
    ax[j].legend(fontsize=6)
fig.tight_layout(); plt.show()
print(f'Fan low edge uses uncensored helper onset {electron_design_onset:.4f} T (rounded down to 0.90 T); short-window check is 1.03 T. Onset uncertainty remains approximately 0.9–1.05 T.')
