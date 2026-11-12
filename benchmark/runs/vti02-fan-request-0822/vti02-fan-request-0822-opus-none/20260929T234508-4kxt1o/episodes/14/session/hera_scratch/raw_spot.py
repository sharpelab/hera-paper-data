import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel
fig, ax = plt.subplots(2, 2, figsize=(12, 7))
for j, rid in enumerate((6, 7)):
    r = open_run(f"data/{rid}"); chs = resolve_channels(r.meta); cur = current_channel(chs)
    B = r.col('magnet_field'); I = r.col_at(cur.idx)/cur.gain
    ch = [c for c in chs if c.cid == 'sr1'][0]
    R = (r.col_at(ch.idx)/ch.gain)/I
    P = r.col('sr1_P'); T = r.col('T_sample')
    itg, ibg = r.col('k_2400_tg_curr'), r.col('k_2400_bg_curr')
    o = np.argsort(B)
    ax[0, j].plot(B[o], R[o], lw=0.7)
    ax[0, j].set(title=f"run {rid}  R_xx(sr1) vs B", xlabel="B (T)", ylabel="R (Ohm)")
    ax[1, j].plot(B[o], P[o], lw=0.7, label='sr1 phase (deg)')
    ax[1, j].plot(B[o], I[o]*1e9, lw=0.7, label='I (nA)')
    ax[1, j].plot(B[o], T[o], lw=0.7, label='T_sample (K)')
    ax[1, j].set(xlabel="B (T)"); ax[1, j].legend(fontsize=7)
    print(f"run {rid}: R[first5]={np.round(R[o][:5],1)}  R<1 count={np.sum(np.abs(R)<1)}")
    print(f"   phase {P.min():.1f}..{P.max():.1f} deg (std {P.std():.2f}); I {I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA")
    print(f"   T {T.min():.3f}..{T.max():.3f} K; |I_tg|max {np.abs(itg).max():.2e} |I_bg|max {np.abs(ibg).max():.2e} A")
    print(f"   sr1_X max {np.abs(r.col_at(ch.idx)).max():.3e} V")
plt.tight_layout(); plt.savefig("hera_scratch/raw_spot67.png", dpi=110)
