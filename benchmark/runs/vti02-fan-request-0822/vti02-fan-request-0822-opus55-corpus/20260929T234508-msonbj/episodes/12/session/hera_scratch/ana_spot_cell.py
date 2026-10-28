# Runs 6-7 — sdh-spot-check read (raw first, then onset + FFT vs F_L and the FS-count model).
import sys, os, warnings
from hera.analysis import sdh_onset, resolve_channels
sys.path.insert(0, os.path.expanduser("~/measurement_env/hera/models/tetralayer_fs_count"))
import fs_count_b0 as fsm

def rxx(i):
    r = run(i); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); R = (r.col("sr1_X") / ch["sr1"].gain) / (r.col("sr0_X") / ch["sr0"].gain)
    o = np.argsort(B); return r, B[o], R[o]

spots = [(6, +3.2, 1.0), (7, -1.2, 0.5)]   # (run, n [1e12], onset-analysis b_lo: run 6 below 1 T is 50 mT = sub-Nyquist for a 7 T tone)
fig, ax = plt.subplots(2, 3, figsize=(16, 8))
for k, (rid, n12, blo) in enumerate(spots):
    r, B, R = rxx(rid)
    FL = float(luttinger_frequency(abs(n12) * 1e16)); fs = 50e-6 / 9.9e-9
    print(f"run {rid}: n = {n12:+.1f}e12, D = 0, T {np.nanmean(r.col('T_sample')):.2f} K, R {R.min():.0f}..{R.max():.0f} Ohm (FS {fs:.0f}), F_L = {FL:.1f} T, interrupted={r.interrupted}")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore"); on = sdh_onset(R, B, b_lo=blo, r_full_scale=fs)
    print(on.summary())
    ab = fsm.abab_mstar(n12 * 1e16); ca = fsm.abca_mstar(n12 * 1e16)
    print("  model ABAB (F, m*): " + ", ".join(f"({F:.1f} T, {m:.3f})" for F, m in ab) + f";  ABCA ({ca[0]:.1f} T, {ca[1]:.3f})\n")
    ax[k, 0].plot(B, R, lw=.7); ax[k, 0].set(xlabel="B (T)", ylabel="Rxx B_1-B_2 (Ohm)", title=f"run {rid} raw, n = {n12:+.1f}e12, D = 0")
    sel = B > 1.5; dR = R[sel] - np.polyval(np.polyfit(B[sel], R[sel], 5), B[sel])
    ax[k, 1].plot(1 / B[sel], dR, lw=.7); ax[k, 1].set(xlabel="1/B (1/T)", ylabel="dR (Ohm)", title="deg-5 B-space background removed, B > 1.5 T")
    for lo in ((1.0, 1.8, 3.0) if rid == 6 else (0.7, 1.5, 2.5)):
        f, s = sdh_fft(R[:, None], B, b_range=(lo, 10.0), bg_degree=5, log=False)
        m = f > 1.5; ax[k, 2].plot(f, s[0] / s[0][m].max(), label=f"[{lo}, 10] T")
    ax[k, 2].axvline(FL, color="k", ls="--", label="F_L")
    for F, _ in ab: ax[k, 2].axvline(F, color="C3", ls=":", lw=1)
    ax[k, 2].axvline(ca[0], color="C2", ls="-.", lw=1)
    ax[k, 2].set(xlim=(0, 2 * FL), ylim=(0, 1.05), xlabel="F (T)", title="FFT (red dotted ABAB, green ABCA, black F_L)"); ax[k, 2].legend(fontsize=7)
fig.tight_layout(); plt.show()
