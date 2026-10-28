"""Runs 6 + 7 (`sdh-spot-check`, D = 0): raw traces, 1/B view, per-tone onsets (sdh_onset), QH-minima filling factors,
and the density-scale check F_(dnu=4) vs F_L(geometry prior). Re-runnable in the ana kernel (uses run(), file_path)."""
from scipy.signal import find_peaks, savgol_filter
from hera.analysis import sdh_onset, SdhOnsetError

h_over_e = cst.h / cst.e   # T m^2
spots = [(6, +3.2, "electron"), (7, -1.2, "hole")]
fig, axs = plt.subplots(2, 2, figsize=(14, 8))
summary = {}
for k, (rid, n_geo, side) in enumerate(spots):
    g = run(rid)
    B = g.col("magnet_field"); I = g.col("sr0_X") / (-1e6); R = g.col("sr1_X") / I
    o = np.argsort(B); B, R = B[o], R[o]
    FL = luttinger_frequency(abs(n_geo) * 1e16)
    axs[0, k].plot(B, R, lw=0.7); axs[0, k].set_xlabel("B (T)"); axs[0, k].set_ylabel("Rxx (Ohm)")
    axs[0, k].set_title(f"run {rid} — {side}, n_geo = {n_geo:+.1f}e12, D = 0 (raw Rxx)")
    m = B >= 1.0
    axs[1, k].plot(1 / B[m], R[m], lw=0.7); axs[1, k].set_xlabel("1/B (1/T)"); axs[1, k].set_ylabel("Rxx (Ohm)")
    # QH-like minima above 1.5 T and their filling factor on the geometry-prior density
    Rs = savgol_filter(R[m], 7, 2)
    mins, _ = find_peaks(-Rs, prominence=max(5, 0.05 * Rs.max()))
    Bm, Rm = B[m][mins], Rs[mins]; keep = Bm > 1.5
    nu_geo = abs(n_geo) * 1e16 * h_over_e / Bm
    for b in Bm[keep]: axs[0, k].axvline(b, color="gray", lw=0.4, ls=":")
    print(f"=== run {rid} ({side}): n_geo = {n_geo:+.2f}e12 -> F_L(geo, g=4) = {FL:.1f} T; R(B_min) = {R[0]:.0f} Ohm, max {R.max():.0f} Ohm")
    print("  Rxx minima > 1.5 T: " + ", ".join(f"{b:.2f} T (R {r:.0f}, nu_geo {nu:.1f})" for b, r, nu in zip(Bm[keep], Rm[keep], nu_geo[keep])))
    # spacing of the minima in nu -> Delta-nu = 4 periodicity gives the true density scale
    dnu = -np.diff(nu_geo[keep]); dnu = dnu[(dnu > 2.5) & (dnu < 6)]   # adjacent minima only (skip missed ones)
    scale = 4.0 / np.median(dnu) if len(dnu) else np.nan
    print(f"  adjacent-minima spacing in nu_geo: median {np.median(dnu):.2f} (n={len(dnu)}) -> if these are dnu = 4 gaps, n_true/n_geo = {scale:.3f}")
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
        print(on.summary())
        summary[rid] = on
    except SdhOnsetError as e:
        print("  sdh_onset:", e)
fig.tight_layout(); plt.show()
