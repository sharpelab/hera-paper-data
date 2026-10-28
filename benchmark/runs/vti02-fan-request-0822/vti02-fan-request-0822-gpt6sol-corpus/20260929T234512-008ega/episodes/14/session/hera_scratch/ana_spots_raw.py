from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, summarize_run

fig, ax = plt.subplots(2, 3, figsize=(14, 7), sharex='row')
for row, rid in enumerate((6, 7)):
    r = open_run(Path('data') / str(rid))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col('magnet_field')
    I = r.col('sr0_X') / ch['sr0'].gain
    R = (r.col('sr1_X') / ch['sr1'].gain) / I
    tg, bg = r.col('k_2400_tg_curr'), r.col('k_2400_bg_curr')
    print(summarize_run(r))
    print(f'raw: R {R.min():.1f}..{R.max():.1f} Ω; I_drain {I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA; '
          f'|I_tg| max {np.max(np.abs(tg))*1e12:.0f} pA, |I_bg| max {np.max(np.abs(bg))*1e12:.0f} pA; '
          f'T {r.col("T_sample").min():.3f}..{r.col("T_sample").max():.3f} K')
    ax[row,0].plot(B,R,'.-',ms=1,lw=.6); ax[row,0].set_ylabel(f'run {rid} Rxx (Ω)')
    ax[row,1].plot(B,I*1e9,lw=.8); ax[row,1].set_ylabel('I drain (nA)')
    ax[row,2].plot(B,tg*1e12,label='TG',lw=.7); ax[row,2].plot(B,bg*1e12,label='BG',lw=.7)
    ax[row,2].set_ylabel('gate current (pA)'); ax[row,2].legend()
    for a in ax[row]: a.set_xlabel('B (T)')
fig.suptitle('vti-02 raw SdH spot checks — fixed D ≈ 0, B₁–B₂')
fig.tight_layout(); plt.show()
