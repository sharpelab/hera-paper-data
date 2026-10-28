"""Spot checks runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12): raw MR, onset, FFT vs F_L + model."""
import sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M

I_NOM = 1.0 / 100e6
SENS = 50e-6
out = {}
fig, axs = plt.subplots(3, 2, figsize=(12, 11))
for col, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field"); V = r.col("sr1_X"); I = r.col("sr0_X") / -1e6
    R = V / I
    o = np.argsort(B); B, R, V, I = B[o], R[o], V[o], I[o]
    T = r.col("T_sample")
    itg, ibg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    FL = float(luttinger_frequency(n12 * 1e16))
    print(f"\n=== run {rid}  n={n12:+.2f}e12  F_L={FL:.2f} T")
    print(f"I drain: med {np.median(I)*1e9:.3f} nA (min {I.min()*1e9:.3f}, max {I.max()*1e9:.3f}); R(0)~{R[B<0.4].mean():.1f}, R max {R.max():.1f} at B={B[R.argmax()]:.2f}")
    print(f"sr1_X max {np.abs(V).max()*1e6:.2f} uV of {SENS*1e6} uV FS ({np.abs(V).max()/SENS:.2f}); T {T.min():.3f}-{T.max():.3f}; |Itg| max {np.abs(itg).max()*1e12:.0f} pA |Ibg| max {np.abs(ibg).max()*1e12:.0f} pA")
    rfs = SENS / np.median(I)
    try:
        on = sdh_onset(R, B, r_full_scale=rfs, b_lo=max(0.3, B.min()))
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); on = None; onset = None
    # model
    if n12 > 0:
        _, orb = M.abab_fs(n12); ms = M.abab_mstar(n12)
        ab = M.abca_fs(n12); abm = M.abca_mstar(n12)
    else:
        _, orb = M.abab_fs(n12); ms = M.abab_mstar(n12)
        ab = M.abca_fs(n12); abm = M.abca_mstar(n12)
    print("model ABAB orbits (F,kF):", [(round(f, 2)) for f, k in orb], "m*:", [(round(f, 2), round(m, 3)) for f, m in ms])
    print("model ABCA:", ab, "m*", abm)
    ax = axs[0, col]; ax.plot(B, R, lw=0.7); ax.set_title(f"run {rid} raw R (n={n12:+.1f}e12, D=0)"); ax.set_xlabel("B (T)"); ax.set_ylabel("R (Ohm)")
    # background-subtracted
    ffts = {}
    for lo in ([onset] if onset else []) + [1.5, 2.0, 3.0]:
        if lo is None: continue
        for deg in (3, 5, 7):
            f, s = sdh_fft(R[:, None], B, b_range=(lo, B.max()), bg_degree=deg, nfft=4096)
            sp = s[0]
            m = f > 1.0
            # top peaks
            idx = [i for i in range(1, len(sp) - 1) if m[i] and sp[i] > sp[i - 1] and sp[i] > sp[i + 1]]
            idx = sorted(idx, key=lambda i: -sp[i])[:6]
            ffts[(round(lo, 2), deg)] = [(round(float(f[i]), 2), round(float(sp[i] / sp[m].max()), 3)) for i in idx]
            if deg == 5:
                axs[1, col].plot(f, sp / sp[m].max(), lw=0.8, label=f"B>{lo:.2f}")
    for k, v in ffts.items():
        print("fft window/deg", k, "peaks (F, rel):", v)
    ax = axs[1, col]
    ax.axvline(FL, color="k", ls="--", label="F_L")
    for fm, _ in orb:
        ax.axvline(fm, color="r", ls=":", lw=1)
    ax.set_xlim(0, max(3 * FL, 40)); ax.set_ylim(0, 1.1); ax.set_xlabel("F (T)"); ax.legend(fontsize=7)
    ax.set_title("FFT (bg deg 5); red: ABAB model, dashed F_L")
    # dR vs 1/B
    lo = onset or 1.5
    sel = B >= lo
    p = np.polyfit(B[sel], R[sel], 5)
    axs[2, col].plot(1 / B[sel], R[sel] - np.polyval(p, B[sel]), lw=0.6)
    axs[2, col].set_xlabel("1/B (1/T)"); axs[2, col].set_title(f"dR (deg-5 bg) B>{lo:.2f} T")
    out[rid] = dict(n12=n12, FL=FL, onset=onset, ffts={str(k): v for k, v in ffts.items()},
                    R0=float(R[B < 0.4].mean()), Rmax=float(R.max()), Imed=float(np.median(I)))
fig.tight_layout(); fig.savefig("hera_scratch/spot_runs67.png", dpi=110)
json.dump(out, open("hera_scratch/spot_runs67.json", "w"), indent=1, default=str)
