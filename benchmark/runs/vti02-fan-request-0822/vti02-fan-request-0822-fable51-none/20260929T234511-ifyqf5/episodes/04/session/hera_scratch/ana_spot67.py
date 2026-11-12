"""sdh-spot-check read, runs 6 (electron, n = +3.2e12) and 7 (hole, n = -1.2e12), D = 0:
raw R(B) first, then R vs 1/B, per-tone onsets (sdh_onset) and the FFT in 1/B (sdh_fft, poly-5 bg in B)."""
from hera.analysis import resolve_channels, current_channel, sdh_onset
from scipy.signal import find_peaks, savgol_filter

h_e = cst.h / cst.e                      # T m^2 per filling factor: nu = n h / (e B)
FS_R = 50e-6 / 10e-9                     # sr1 50 uV at 10 nA -> 5 kOhm full scale
fig, axes = plt.subplots(2, 3, figsize=(16, 8))
for k, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = run(rid)
    print(summarize_run(r))
    chans = resolve_channels(r.meta); cur = current_channel(chans)
    v = [c for c in chans if not c.is_current][0]
    I = r.col(cur.col) / cur.gain
    R = (r.col(v.col) / v.gain) / I
    B = r.col("magnet_field")
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    F_L = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"run {rid}: I_drain {I.mean()*1e9:.2f} nA; R {R.min():.0f}..{R.max():.0f} Ohm (max {R.max()/FS_R:.2f} of 5 kOhm FS); "
          f"F_L(|n| = {abs(n12)}e12, single 4-fold FS) = {F_L:.1f} T; nu(cal) at 10 T = {abs(n12)*1e16*h_e/10:.1f}")
    so = sdh_onset(R, B, b_lo=0.5, r_full_scale=FS_R)
    print(so.summary())
    m = B > 2.5; Rs = savgol_filter(R[m], 9, 2)
    mins, _ = find_peaks(-Rs, prominence=0.15 * (Rs.max() - Rs.min()))
    print("  deep minima B (T) / nu(cal):", [(round(float(B[m][i]), 2), round(float(abs(n12)*1e16*h_e/B[m][i]), 1)) for i in mins])
    ax = axes[k]
    ax[0].plot(B, R, lw=0.8); ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("Rxx (Ohm)")
    ax[0].set_title(f"run {rid}: n = {n12:+.1f}e12, D = 0 — raw Rxx(B)")
    ax[1].plot(1 / B[B > 0.8], R[B > 0.8], lw=0.8); ax[1].set_xlabel("1/B (1/T)"); ax[1].set_ylabel("Rxx (Ohm)"); ax[1].set_title("raw vs 1/B")
    for lo, hi, c in [(1.5, 10.0, "k"), (3.0, 10.0, "C1")]:
        f, spec = sdh_fft(R[:, None], B, b_range=(lo, hi), nfft=2048, bg_degree=5, log=False)
        sp = spec[0]; sel = (f > 1.0) & (f < 60)
        ax[2].plot(f[sel], sp[sel] / sp[sel].max(), c, lw=1, label=f"{lo}-{hi} T (dF = {1/(1/lo-1/hi):.1f} T)")
    ax[2].axvline(F_L, color="r", ls="--", label=f"F_L(n) = {F_L:.1f} T"); ax[2].axvline(F_L / 2, color="r", ls=":", label="F_L/2")
    ax[2].set_xlabel("F (T)"); ax[2].set_ylabel("|FFT| (norm)"); ax[2].set_title("SdH FFT in 1/B (poly-5 bg in B)"); ax[2].legend(fontsize=7)
fig.tight_layout(); plt.show()
