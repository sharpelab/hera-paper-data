"""Spot checks runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12): raw MR, onset, FFT vs F_L + model."""
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError
sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))

D = Path(__file__).resolve().parent.parent / "data"
out = Path(__file__).resolve().parent
runs = {6: (+3.2, 50e-6), 7: (-1.2, 50e-6)}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
res = {}
for j, (rid, (n12, sens)) in enumerate(runs.items()):
    r = open_run(D / str(rid))
    B = r.col("magnet_field"); v = r.col("sr1_X"); i = r.col("sr0_X") / -1e6
    R = v / i
    Ibias = np.median(np.abs(i))
    o = np.argsort(B); B, R, T = B[o], R[o], r.col("T_sample")[o]
    FL = float(luttinger_frequency(n12 * 1e16))
    print(f"=== run {rid}: n={n12:+.1f}e12  F_L={FL:.2f} T  pts={len(B)}  B {B.min():.3f}-{B.max():.3f}  "
          f"R {np.abs(R).min():.1f}-{np.abs(R).max():.1f} Ohm  I {Ibias*1e9:.2f} nA  "
          f"max|X|/sens={np.abs(v).max()/sens:.3f}  T {T.min():.3f}-{T.max():.3f}  "
          f"Ileak tg {np.abs(r.col('k_2400_tg_curr')).max():.2e} bg {np.abs(r.col('k_2400_bg_curr')).max():.2e}")
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_title(f"run {rid} raw Rxx, n={n12:+.1f}e12"); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("R (Ohm)")
    try:
        on = sdh_onset(np.abs(R), B, r_full_scale=sens / Ibias)
        print(on.summary())
        res[rid] = on
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); on = None
    # background-subtracted
    m = B > 1.0
    cf = np.polyfit(B[m], np.abs(R[m]), 5); dR = np.abs(R[m]) - np.polyval(cf, B[m])
    ax[1, j].plot(1 / B[m], dR, lw=0.6); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_ylabel("dR (Ohm), deg-5 bg >1 T")
    if on is not None: ax[1, j].axvline(1 / on.onset_b, color="r", ls="--", label=f"onset {on.onset_b:.2f} T"); ax[1, j].legend()
    for lo in ([1.5, 2.0, 3.0] if on is None else sorted({max(on.onset_b, 1.0), 2.0, 3.0})):
        f, sp = sdh_fft(np.abs(R)[:, None], B, b_range=(lo, B.max()), bg_degree=5, log=False, nfft=4096)
        ax[2, j].plot(f, sp[0] / sp[0][f > 2].max(), lw=0.8, label=f"window {lo:.2f}-{B.max():.1f} T")
        pk = [(f[k], sp[0][k]) for k in range(1, len(f) - 1) if sp[0][k] > sp[0][k-1] and sp[0][k] > sp[0][k+1] and f[k] > 2]
        pk = sorted(pk, key=lambda x: -x[1])[:6]
        print(f"  FFT {lo:.2f}-{B.max():.1f} T: dF={1/(1/lo-1/B.max()):.2f} T  peaks " + ", ".join(f"{a:.2f}({b/pk[0][1]:.2f})" for a, b in sorted(pk)))
    ax[2, j].axvline(FL, color="k", ls="--", label=f"F_L {FL:.1f}"); ax[2, j].set_xlim(0, 2.2 * FL); ax[2, j].legend(fontsize=7)
    ax[2, j].set_xlabel("F (T)")
    try:
        import fs_count_b0 as M
        ab = M.abab_fs(n12); am = M.abab_mstar(n12); ac = M.abca_fs(n12)
        print(f"  model ABAB tones: {[round(x[0],2) for x in ab[1]]}  m*: {[round(x[1],3) for x in am]}; ABCA F={ac[4]:.2f} topo={ac[1]}")
        for fz, _ in ab[1]: ax[2, j].axvline(abs(fz), color="b", ls=":", lw=0.8)
    except Exception as e:
        print("model err", e)
fig.tight_layout(); fig.savefig(out / "spot_runs67.png", dpi=90)
