# Run 1 — 0 T TG-BG gatemap: raw re-formed per-channel Rxx maps (TSV, not monitor PNG)
import numpy as np, matplotlib.pyplot as plt
from hera.analysis import open_run
run = open_run("data/1")
bg = run.col('k_2400_volt'); tg = run.col('DC_bias'); I = run.col('sr0_X')/(-1e6)
chans = {'sr1 T3-T4': run.col('sr1_X')/I, 'sr2 B4-B5': run.col('sr2_X')/I, 'sr3 Hall T5-B6': run.col('sr3_X')/I}
BG = np.unique(np.round(bg,3)); TG = np.unique(np.round(tg,3))
bi = {b:i for i,b in enumerate(BG)}; ti = {t:i for i,t in enumerate(TG)}
def grid(v):
    g = np.full((len(BG),len(TG)), np.nan)
    for k in range(len(v)): g[bi[round(bg[k],3)], ti[round(tg[k],3)]] = v[k]
    return g
fig, ax = plt.subplots(1,3, figsize=(15,4.6), sharex=True, sharey=True)
for a,(nm,v) in zip(ax, chans.items()):
    g = grid(v)/1e3
    im = a.pcolormesh(TG, BG, g, shading='nearest', cmap='inferno', vmin=0, vmax=np.nanpercentile(g,98))
    a.set_title(nm); a.set_xlabel('V_tg (V)'); plt.colorbar(im, ax=a, label='R (kOhm)')
ax[0].set_ylabel('V_bg (V)')
plt.suptitle('QC0426 run 1 — 0 T gatemap, raw re-formed Rxx (R = sr_X / I_drain)')
plt.tight_layout(); plt.show()
print("Note: CNP ridge broadens/brightens toward high-|D| corners (D-induced gap), thins to faint")
print("line at center (D~0). Lock-ins clip at 4.37 kOhm (sens 2e-5 overload) on the gapped CNP;")
print("CNP-R(D) from this map is a LOWER BOUND at high |D|. Ridge POSITION unaffected.")
