from scipy.ndimage import gaussian_filter1d

# --- load the 0 T gate map (file_id 1) ---
mD = load_meta(1); cols = mD['columns']; ci = {c: i for i, c in enumerate(cols)}
raw = load1d(1); nfast = 101; nr = raw.shape[0] // nfast
g = raw[:nr*nfast].reshape(nr, nfast, -1)
bg = g[:, 0, ci['k_bg_volt']]; tg = g[0, :, ci['DC_bias']]
I_bias = 5e-9

def ridge(col):
    """Smoothed-argmax CNP ridge per BG row, windowed to the continuous ridge
    (geometry-prior seed) and excluding edge-clipped rows."""
    R = np.abs(g[:, :, ci[col]]) / I_bias
    pred = -1.30 * bg; out = np.full(nr, np.nan)
    for r in range(nr):
        win = np.abs(tg - pred[r]) < 2.0
        j = np.where(win)[0][np.argmax(gaussian_filter1d(R[r], 2.0)[win])]
        if 1 < j < nfast - 2:
            out[r] = tg[j]
    return out, R

fits = {}
fig, ax = plt.subplots(1, 2, figsize=(13, 5))
for k, (nm, col) in enumerate([('sr1 T3-T4', 'sr1_X'), ('sr2 B4-B5', 'sr2_X')]):
    rc, R = ridge(col); ok = ~np.isnan(rc)
    p = np.polyfit(bg[ok], rc[ok], 1); ratio = -p[0]
    rms = (rc[ok] - np.polyval(p, bg[ok])).std()
    fits[nm] = (p[0], p[1], ratio, rms)
    print(f"{nm}: slope {p[0]:.4f}  intercept {p[1]:+.4f} V  c_bg/c_tg={ratio:.3f}"
          f"  RMS {rms*1e3:.1f} mV  (rows {ok.sum()}/{nr})")
    ax[k].pcolormesh(bg, tg, np.log10(np.clip(R.T, 1, None)), shading='auto', cmap='viridis')
    ax[k].plot(bg[ok], rc[ok], 'r.', ms=4, label='CNP ridge')
    ax[k].plot(bg, np.polyval(p, bg), 'w--', lw=1, label=f'fit {p[0]:.2f}')
    ax[k].set_xlabel('BG (V)'); ax[k].set_ylabel('TG / DC_bias (V)')
    ax[k].set_title(f'{nm}  log10 Rxx + CNP fit'); ax[k].legend(loc='upper right', fontsize=8)
plt.tight_layout(); plt.show()

# --- adopt calibration: RATIO data-calibrated; SCALE geometry-prior ---
ratio = float(np.mean([fits[k][2] for k in fits]))
c_tg_cal = calc_ctg(15.6e-9)               # anchored to 15.6 nm hBN stack prior
c_bg_cal = ratio * c_tg_cal
b_int = fits['sr1 T3-T4'][1]
n_offset_cal = -calc_nD(b_int, 0, c_tg_cal, c_bg_cal)[0]
D_offset_cal = 0.0
print(f"\ncross-channel ratio agreement: {fits['sr1 T3-T4'][2]:.3f} vs {fits['sr2 B4-B5'][2]:.3f}")
print(f"ADOPTED  c_bg/c_tg={ratio:.3f}  c_tg={c_tg_cal:.4e}  c_bg={c_bg_cal:.4e} F/m^2")
print(f"         n_offset={n_offset_cal:.3e} m^-2  D_offset={D_offset_cal}")
print("provenance: RATIO data-calibrated (file_id 1); SCALE geometry prior (15.6 nm hBN),"
      " pending QH lever-arm upgrade from the fan")
tg_line = np.polyval([fits['sr1 T3-T4'][0], b_int], bg)
n_ridge = calc_nD(tg_line, bg, c_tg_cal, c_bg_cal, n_offset_cal)[0]
print(f"closure: max|n| on fitted ridge = {np.abs(n_ridge).max():.2e} m^-2"
      f" ({np.abs(n_ridge).max()/1e16:.3f}e12 cm^-2)")
print(f"density lever (D=0): {2*c_tg_cal/cst_e/1e4:.3e} cm^-2 per V (TG, BG matched)")
