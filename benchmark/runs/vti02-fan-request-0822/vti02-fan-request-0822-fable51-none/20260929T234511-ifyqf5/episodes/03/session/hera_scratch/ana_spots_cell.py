"""Runs 6/7 — sdh-spot-check at D = 0: raw R(B), oscillatory part vs 1/B, tone read (FFT + sdh_onset) vs the 4-fold Luttinger frequency."""
from hera.analysis import sdh_onset, SdhOnsetError
from scipy.signal import find_peaks
spots = {6: +3.2, 7: -1.2}   # run id -> n (1e12 cm^-2) on the run-5 calibration
fig, ax = plt.subplots(2, 3, figsize=(16, 8))
for k, (rid, n12) in enumerate(spots.items()):
    r = run(rid); print(summarize_run(r).splitlines()[0], "|", r.tags[0][:70])
    B = r.col("magnet_field"); R = r.col("sr1_X") / (r.col("sr0_X") / -1e6); T = r.col("T_sample")
    o = np.argsort(B); B, R, T = B[o], R[o], T[o]
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"run {rid}: n = {n12:+.2f}e12 -> F_L(4-fold) = {FL:.1f} T; R(B<0.35) = {np.median(R[B < 0.35]):.0f} Ohm, "
          f"R_max = {R.max():.0f} Ohm at {B[np.argmax(R)]:.2f} T; T_sample {T.mean():.3f} +- {T.std():.3f} K")
    ax[k, 0].plot(B, R, lw=0.7); ax[k, 0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=f"run {rid}: n = {n12:+.2f}e12, D = 0 - raw")
    m = B > 1.0; bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax[k, 1].plot(1 / B[m], R[m] - bg, lw=0.7); ax[k, 1].set(xlabel="1/B (1/T)", ylabel="dR (Ohm)", title="oscillatory part (deg-5 B-space bg, B > 1 T)")
    ytop = ax[k, 1].get_ylim()[1] * 0.85
    for nu in range(4, 41, 4):
        x = nu * 2.418e10 / (abs(n12) * 1e12)
        if 0.1 < x < 1: ax[k, 1].axvline(x, color="r" if nu % 8 == 0 else "0.6", ls=":", lw=0.6); ax[k, 1].text(x, ytop, str(nu), fontsize=6)
    for blo, c in ((1.5, "C0"), (3.0, "C1")):
        mm = B >= blo; f, sp = sdh_fft(R[mm][:, None], B[mm], nfft=4096, bg_degree=5, log=False); sp = sp[0]; sel = (f > 2) & (f < 80)
        ax[k, 2].plot(f[sel], sp[sel] / sp[sel].max(), c, lw=1, label=f"{blo:.1f}-10 T")
        pk, _ = find_peaks(sp[sel], prominence=0.1 * sp[sel].max())
        print(f"  FFT {blo:.1f}-10 T peaks: " + ", ".join(f"{f[sel][p]:.1f} T ({sp[sel][p] / sp[sel].max():.2f})" for p in pk))
    ax[k, 2].axvline(FL, color="r", ls="--", label=f"F_L = {FL:.1f} T"); ax[k, 2].axvline(FL / 2, color="g", ls=":", label="F_L/2"); ax[k, 2].axvline(FL / 4, color="g", ls=":", lw=0.6, label="F_L/4")
    ax[k, 2].set(xlabel="F (T)", ylabel="|FFT| (norm)", title="SdH spectrum in 1/B"); ax[k, 2].legend(fontsize=7)
    try:
        so = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
        print("  " + "\n  ".join(so.summary().splitlines()[:6]))
    except SdhOnsetError as e:
        print("  sdh_onset:", e)
fig.tight_layout(); plt.show()
