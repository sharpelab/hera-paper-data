"""Spot checks runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12): raw MR, onset, FFT vs F_L + model."""
import json, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

I_BIAS = 1.0 / 100e6
out = {}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for k, (rid, n) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field"); R = r.col("sr1_X") / 1.0 / I_BIAS
    o = np.argsort(B); B, R = B[o], R[o]
    T = r.col("T_sample"); itg = r.col("k_2400_tg_curr"); ibg = r.col("k_2400_bg_curr")
    FL = float(luttinger_frequency(abs(n)))
    sens = r.metadata.get("instruments", {})
    print(f"=== run {rid}  n={n:+.2f}e12  F_L={FL:.2f} T  R {R.min():.0f}..{R.max():.0f} Ohm  "
          f"T {T.min():.3f}-{T.max():.3f} K  |Itg|max {np.abs(itg).max():.2e} |Ibg|max {np.abs(ibg).max():.2e}")
    rfs = 50e-6 / I_BIAS
    ax[0, k].plot(B, R, lw=.7); ax[0, k].set_title(f"run {rid} raw Rxx, n={n:+.1f}e12"); ax[0, k].set_xlabel("B (T)")
    try:
        on = sdh_onset(R, B, r_full_scale=rfs)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); on = None; onset = 1.0
    res = {"F_L": FL, "onset": float(onset)}
    for lo in sorted({max(onset, 0.5), max(onset, 1.0), 1.5, 2.0, 3.0}):
        for deg in (3, 5, 7):
            f, s = sdh_fft(R[:, None], B, b_range=(lo, B.max()), bg_degree=deg, log=False, nfft=4096)
            sp = s[0]; m = f > 2.0
            # peaks
            idx = [i for i in range(1, len(sp) - 1) if m[i] and sp[i] > sp[i - 1] and sp[i] >= sp[i + 1]]
            idx = sorted(idx, key=lambda i: -sp[i])[:6]
            pk = sorted([(round(float(f[i]), 2), round(float(sp[i] / sp[m].max()), 2)) for i in idx])
            dF = 1 / (1 / lo - 1 / B.max())
            print(f"  cutoff {lo:.2f} T deg {deg}: dF={dF:.2f} T  peaks (F/F_L, rel): " +
                  ", ".join(f"{p[0]:.2f}T({p[0]/FL:.2f},{p[1]:.2f})" for p in pk))
            if deg == 5 and lo == max(onset, 1.0):
                ax[1, k].plot(f, sp / sp[m].max(), lw=.8, label=f"cut {lo:.2f}")
                res["peaks"] = pk
    ax[1, k].axvline(FL, color="k", ls="--", label="F_L")
    ax[1, k].set_xlim(0, 2.5 * FL); ax[1, k].set_xlabel("F (T)"); ax[1, k].legend(fontsize=7)
    # bg-subtracted vs 1/B
    sel = B > max(onset, 1.0)
    p = np.polyfit(B[sel], R[sel], 5); dR = R[sel] - np.polyval(p, B[sel])
    ax[2, k].plot(1 / B[sel], dR, lw=.7); ax[2, k].set_xlabel("1/B (1/T)"); ax[2, k].set_title("dR (deg-5 bg in B)")
    out[rid] = res
fig.tight_layout(); fig.savefig("hera_scratch/spot_fft.png", dpi=110)
json.dump(out, open("hera_scratch/spot_fft.json", "w"), indent=1, default=str)
