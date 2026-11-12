# Runs 6 & 7 — sdh-spot-check, raw MR first (no background removal, no log)
import numpy as np, matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, summarize_run

def spot_trace(rid):
    run = open_run(f'data/{rid}')
    print(summarize_run(run))
    chs = resolve_channels(run.meta)
    cur = current_channel(chs)
    v = [c for c in chs if not c.is_current and c.cid == 'sr1'][0]
    B = run.col('magnet_field')
    I = run.col(cur.col) / cur.gain
    R = (run.col(v.col) / v.gain) / I
    o = np.argsort(B)
    return B[o], np.abs(R[o]), np.abs(I[o]), run

fig, axs = plt.subplots(1, 2, figsize=(12, 4))
for ax, (rid, lbl) in zip(axs, [(6, 'run 6: e-side n=+3.2e12, D=0, B 0->10 T'),
                                (7, 'run 7: h-side n=-1.2e12, D=0, B 10->0.3 T')]):
    B, R, I, _ = spot_trace(rid)
    ax.plot(B, R, lw=0.6)
    ax.set_xlabel('B (T)'); ax.set_ylabel('R_xx = (sr1/gain)/I_meas (Ohm)')
    ax.set_title(lbl, fontsize=10)
    print(f'run {rid}: R(low-B edge) = {np.median(R[B < B.min() + 0.2]):.0f} Ohm, R_max = {R.max():.0f} Ohm, '
          f'I_min = {I.min()*1e9:.2f} nA, |X|max/sens = {(R*I).max()/50e-6:.2f}')
fig.tight_layout()
