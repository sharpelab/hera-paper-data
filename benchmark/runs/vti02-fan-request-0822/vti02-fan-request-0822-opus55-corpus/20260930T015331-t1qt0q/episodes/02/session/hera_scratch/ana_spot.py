"""Runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12): raw MR, onset, FFT vs F_L + model tones."""
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, sys
from hera.analysis import open_run, summarize_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as m
spots = {6: 3.2, 7: -1.2}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n) in enumerate(spots.items()):
    r = open_run(f"data/{rid}")
    print(summarize_run(r))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    o = np.argsort(B); B, R = B[o], R[o]
    sens = 50e-6; Ib = np.median(np.abs(I)); rfs = sens / Ib
    print(f"run {rid}: B {B.min():.3f}-{B.max():.3f}, R {R.min():.1f}-{R.max():.1f} Ohm, FS {rfs:.0f} Ohm, "
          f"max frac {R.max()/rfs:.2f}, I {Ib*1e9:.2f} nA, T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f}")
    FL = luttinger_frequency(n) if True else None
    print(f"  F_L = {FL}")
    try:
        on = sdh_onset(R, B, r_full_scale=rfs)
        print(on.summary())
        blo = on.onset_b
    except Exception as e:
        print("  onset error:", repr(e)); blo = 2.0
    ax[0, j].plot(B, R, lw=.7); ax[0, j].set_title(f"run {rid} n={n:+}e12 raw"); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("Rxx (Ohm)")
    for cut in sorted({round(blo, 2), 2.0, 3.0, 4.0}):
        if cut >= B.max() - 1: continue
        f, S = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=5, log=False)
        s = S[0]; k = np.argsort(s)[::-1]
        # top peaks
        from scipy.signal import find_peaks
        pk, _ = find_peaks(s); pk = pk[np.argsort(s[pk])[::-1]][:6]
        print(f"  FFT cut {cut:.2f}-{B.max():.1f} T (dF={1/(1/cut-1/B.max()):.2f} T): peaks " +
              ", ".join(f"{f[p]:.1f}T({s[p]/s[pk[0]]:.2f})" for p in sorted(pk)))
        ax[1, j].plot(f, s / s.max(), lw=.8, label=f"cut {cut:.2f} T")
    ax[1, j].axvline(abs(FL), color="k", ls="--", label="F_L")
    try:
        EF, orbs = m.abab_fs(n); ms = m.abab_mstar(n)
        print("  ABAB orbits:", [(round(F, 2)) for F, kf in orbs], "m*:", [(round(F,2), round(mm,3)) for F, mm in ms])
        for F, kf in orbs: ax[1, j].axvline(F, color="C3", ls=":", lw=1)
        a = m.abca_fs(n); am = m.abca_mstar(n)
        print("  ABCA:", a[1:], "m*", am)
        ax[1, j].axvline(a[4], color="C2", ls=":", lw=1.5)
    except Exception as e:
        print("  model err", e)
    ax[1, j].set_xlim(0, 3 * abs(FL)); ax[1, j].legend(fontsize=7); ax[1, j].set_xlabel("F (T)")
    # background-subtracted vs 1/B
    sel = B > 1.0
    c = np.polyfit(B[sel], R[sel], 5); d = R[sel] - np.polyval(c, B[sel])
    ax[2, j].plot(1 / B[sel], d, lw=.6); ax[2, j].set_xlabel("1/B (1/T)"); ax[2, j].set_ylabel("dR (Ohm), poly5 in B >1T")
fig.tight_layout(); fig.savefig("hera_scratch/spot_runs67.png", dpi=90)
