"""Runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12) sdh-spot-check read:
raw MR, onset (sdh_onset), FFT vs F_L and the FS-count model templates."""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency

sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
import fs_count_b0 as M

HERE = Path(__file__).resolve().parent.parent
SPOTS = {6: +3.2, 7: -1.2}      # n in 1e12 cm^-2 (run-5 calibration)
SENS = 50e-6                    # sr1 sensitivity both runs (V)


def load(rid):
    r = open_run(HERE / "data" / str(rid))
    B = r.col("magnet_field")
    I = r.col("sr0_X") / -1e6              # measured drain current (A)
    R = r.col("sr1_X") / I                 # sr1 gain 1
    o = np.argsort(B)
    return r, B[o], R[o], I[o], r.col("sr1_X")[o], r.col("T_sample")[o]


out = {}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for k, (rid, n12) in enumerate(SPOTS.items()):
    r, B, R, I, X, T = load(rid)
    FL = float(luttinger_frequency(n12 * 1e16))
    Ib = np.median(np.abs(I))
    print(f"\n=== run {rid}: n = {n12:+.1f}e12, F_L = {FL:.2f} T; B {B.min():.3f}..{B.max():.3f} ({len(B)} pts); "
          f"I = {Ib*1e9:.2f} nA; R(0) = {np.median(R[B<0.1]):.1f}, R(Bmax) = {R[-5:].mean():.1f} Ohm, "
          f"R range {R.min():.1f}..{R.max():.1f}; sr1 X max {np.abs(X).max()*1e6:.2f} uV (FS 50 uV -> {np.abs(X).max()/SENS:.2f}); "
          f"T {T.min():.3f}..{T.max():.3f} K")
    ab = M.abab_fs(n12)[1]; am = M.abab_mstar(n12); ca = M.abca_fs(n12); cm = M.abca_mstar(n12)
    print(f"model ABAB orbits F = {[round(f,2) for f,_ in ab]}  m* = {[round(m,3) for _,m in am]};  ABCA F = {ca[4]:.2f} m* {cm[1]:.3f}")
    try:
        on = sdh_onset(np.abs(R), B, b_lo=0.3, r_full_scale=SENS / Ib)
        print(on.summary())
        out[rid] = on
    except Exception as e:
        print("sdh_onset:", type(e).__name__, e)
        on = None
    ax[0, k].plot(B, R, lw=0.7); ax[0, k].set_title(f"run {rid} raw Rxx, n={n12:+.1f}e12"); ax[0, k].set_xlabel("B (T)"); ax[0, k].set_ylabel("R (Ohm)")
    # background-subtracted in B (deg 5) over [cut, Bmax]
    cut = max(on.onset_b if on else 1.0, 1.0)
    for bl, bh, ls in ((cut, B.max(), "-"), (cut, 0.5 * (cut + B.max()), ":"), (0.5 * (cut + B.max()), B.max(), "--")):
        for deg in (3, 5, 7):
            f, S = sdh_fft(np.abs(R)[:, None], B, b_range=(bl, bh), bg_degree=deg, nfft=4096)
            s = S[0]
            if deg == 5:
                ax[2, k].plot(f, s / s[(f > 1)].max(), ls, lw=0.9, label=f"[{bl:.1f},{bh:.1f}] T")
            pk = [(f[i], s[i]) for i in range(1, len(s) - 1) if s[i] > s[i-1] and s[i] > s[i+1] and f[i] > 1.5 and f[i] < 3 * FL]
            pk = sorted(pk, key=lambda t: -t[1])[:6]
            srel = s[(f > 1.5)].max()
            print(f"  FFT [{bl:.2f},{bh:.2f}] deg{deg}: " + ", ".join(f"{fp:.2f}T({sp/srel:.2f})" for fp, sp in sorted(pk)))
    m = (B >= cut)
    cf = np.polyfit(B[m], np.abs(R)[m], 5)
    ax[1, k].plot(1 / B[m], np.abs(R)[m] - np.polyval(cf, B[m]), lw=0.6); ax[1, k].set_xlabel("1/B (1/T)"); ax[1, k].set_ylabel("dR (Ohm)")
    ax[1, k].set_title(f"bg-sub (deg5 in B), B >= {cut:.2f} T")
    for fm, lab, c in [(FL, "F_L", "k")] + [(fa, "ABAB", "r") for fa, _ in ab if fa > 0.5] + [(ca[4], "", "k")]:
        ax[2, k].axvline(fm, color=c, ls="--", lw=0.8)
    ax[2, k].set_xlim(0, 2.2 * FL); ax[2, k].set_xlabel("F (T)"); ax[2, k].legend(fontsize=7)
    ax[2, k].set_title(f"FFT (deg5) — black F_L = {FL:.1f} T, red ABAB model")
fig.tight_layout(); fig.savefig(HERE / "hera_scratch" / "spot_runs67.png", dpi=110)
