"""SdH spot checks runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12): raw, onset, FFT vs model."""
import sys, json
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError

D = Path(__file__).resolve().parent.parent
out = {}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for k, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    run = open_run(D / "data" / str(rid))
    B = run.col("magnet_field"); X = run.col("sr1_X"); I = 1.0 / 100e6
    amp = run.meta["measurement_config"]
    R = X / 1.0 / 1e-8
    o = np.argsort(B); B, R = B[o], R[o]
    FL = 4.1357e-15 * abs(n12) * 1e16 / 4
    sens = 50e-6
    ax[0, k].plot(B, R, lw=0.7); ax[0, k].set_title(f"run {rid}: n={n12:+.1f}e12 D=0  F_L={FL:.1f} T  (raw Rxx)")
    ax[0, k].set_xlabel("B (T)"); ax[0, k].set_ylabel("Rxx (Ohm)")
    # nu markers
    for nu in range(4, 80, 4):
        b = FL * 4 / nu
        if B.min() < b < B.max():
            ax[0, k].axvline(b, color="0.8", lw=0.5)
            ax[0, k].text(b, ax[0, k].get_ylim()[1] * 0.95, str(nu), fontsize=6, ha="center")
    try:
        on = sdh_onset(R, B, b_lo=max(0.5, B.min()), r_full_scale=sens / 1e-8)
        print(f"=== run {rid} ===\n" + on.summary())
        out[rid] = dict(onset=on.onset_b, tones=[(t.freq, t.onset_b, t.censored, t.marginal) for t in on.tones])
    except SdhOnsetError as e:
        print(f"run {rid}: SdhOnsetError {e}"); out[rid] = dict(err=str(e))
    # FFT windows
    for (lo, hi), c in [((1.5, 10), "C0"), ((2.5, 10), "C1"), ((1.5, 5.5), "C2"), ((5.5, 10), "C3")]:
        try:
            f, s = sdh_fft(R[:, None], B, b_range=(lo, hi), log=False, bg_degree=5, nfft=4096)
            ax[1, k].plot(f, s[0] / s[0][f > 2].max(), c, lw=0.8, label=f"{lo}-{hi} T")
            pk = [(f[i], s[0][i]) for i in range(1, len(f) - 1) if s[0][i] > s[0][i - 1] and s[0][i] > s[0][i + 1] and f[i] > 2 and f[i] < 3 * FL]
            pk = sorted(pk, key=lambda x: -x[1])[:6]
            print(f"run {rid} FFT {lo}-{hi} T peaks (F, rel):", ", ".join(f"{p[0]:.1f}:{p[1]/pk[0][1]:.2f}" for p in pk))
        except Exception as e:
            print(f"run {rid} FFT {lo}-{hi}: {e}")
    ax[1, k].axvline(FL, color="k", ls="--", lw=0.8, label="F_L")
    ax[1, k].set_xlim(0, 2.5 * FL); ax[1, k].legend(fontsize=7); ax[1, k].set_xlabel("F (T)")
    # dR vs 1/B after bg
    sel = B > 1.0
    p = np.polyfit(B[sel], R[sel], 5); dR = R[sel] - np.polyval(p, B[sel])
    ax[2, k].plot(1 / B[sel], dR, lw=0.7); ax[2, k].set_xlabel("1/B (1/T)"); ax[2, k].set_ylabel("dRxx (deg-5 bg in B)")
    T = run.col("T_sample"); print(f"run {rid}: T {np.nanmin(T):.3f}-{np.nanmax(T):.3f} K; R range {R.min():.1f}..{R.max():.1f}; fs max {R.max()/(sens/1e-8):.2f}")
fig.tight_layout(); fig.savefig(D / "hera_scratch" / "spot_runs67.png", dpi=110)
json.dump(out, open(D / "hera_scratch" / "spot_runs67.json", "w"), indent=1, default=float)
