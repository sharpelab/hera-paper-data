from scipy.ndimage import gaussian_filter1d
import os
# --- load damage-check map (file_id 4); actual condition Si=+50 V (operator) ---
m4 = load_meta(4); ci = {c: i for i, c in enumerate(m4['columns'])}
fn = f"{file_path}/4/data.tsv.gz" if os.path.exists(f"{file_path}/4/data.tsv.gz") else f"{file_path}/4/data.tsv"
raw = np.loadtxt(fn)
dc = raw[:, ci['DC_bias']]
drops = np.where(np.diff(dc) < -1.0)[0]          # fast-axis resets between rows
nfast = int(drops[0] + 1) if len(drops) else len(dc)
nr = raw.shape[0] // nfast
g = raw[:nr*nfast].reshape(nr, nfast, -1)
bg = g[:, 0, ci['k_bg_volt']]; tg = g[0, :, ci['DC_bias']]; I_bias = 5e-9
print(f"file_id 4: nfast={nfast}, rows {nr}; BG[{bg.min():.1f},{bg.max():.1f}] TG[{tg.min():.1f},{tg.max():.1f}]")
print(f"leakage: k_bg max {np.abs(g[:,:,ci['k_bg_curr']]).max():.2e} A ; k_2410 max {np.abs(g[:,:,ci['k_2410_curr']]).max():.2e} A")

def ridge(col):
    R = np.abs(g[:, :, ci[col]]) / I_bias
    pred = -1.30 * bg; out = np.full(nr, np.nan)
    for r in range(nr):
        win = np.abs(tg - pred[r]) < 2.0
        if win.sum() < 5: continue
        j = np.where(win)[0][np.argmax(gaussian_filter1d(R[r], 1.5)[win])]
        if 1 < j < nfast - 2: out[r] = tg[j]
    return out, R

fig, ax = plt.subplots(1, 2, figsize=(13, 5))
for k, (nm, col) in enumerate([('sr1 T3-T4', 'sr1_X'), ('sr2 B4-B5', 'sr2_X')]):
    rc, R = ridge(col); ok = ~np.isnan(rc)
    if ok.sum() >= 2:
        p = np.polyfit(bg[ok], rc[ok], 1)
        print(f"{nm}: CNP slope {p[0]:.3f} (file-1 baseline -1.30), intercept {p[1]:+.3f} V, peak Rxx {R.max():.0f} ohm")
    else:
        p = None
    ax[k].pcolormesh(bg, tg, np.log10(np.clip(R.T, 1, None)), shading='auto', cmap='viridis')
    if ok.sum(): ax[k].plot(bg[ok], rc[ok], 'r.', ms=5, label='CNP ridge')
    if p is not None: ax[k].plot(bg, np.polyval(p, bg), 'w--', lw=1, label=f'fit {p[0]:.2f}')
    ax[k].plot(bg, -1.30*bg + 0.067, 'c:', lw=1, label='file-1 baseline')
    ax[k].set_xlabel('BG (V)'); ax[k].set_ylabel('TG / DC_bias (V)')
    ax[k].set_title(f'{nm}  log10 Rxx — damage check (Si=+50 V)'); ax[k].legend(fontsize=8, loc='upper right')
plt.tight_layout(); plt.show()
print("Compare to file-1: slope ~-1.30, CNP near TG~0, Rxx scale ~kohm, leakage <1 nA -> device unchanged.")
