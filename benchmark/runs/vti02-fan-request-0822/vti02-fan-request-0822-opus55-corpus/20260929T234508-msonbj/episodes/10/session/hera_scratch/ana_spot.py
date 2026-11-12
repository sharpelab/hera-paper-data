"""Spot checks runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12): raw MR, onset, FFT vs F_L + model."""
import sys, warnings
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency

sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M

SPOTS = {6: 3.2, 7: -1.2}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n) in enumerate(SPOTS.items()):
    r = open_run(f"data/{rid}")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field")
    I = r.col("sr0_X") / ch["sr0"].gain
    V = r.col("sr1_X") / ch["sr1"].gain
    R = np.abs(V / I)
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    T = r.col("T_sample")
    itg, ibg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    dt = np.diff(np.sort(r.col("time")))
    sens = r.meta["instruments"]["sr1"]["snapshot"]["parameters"]["sensitivity"]["value"]
    amp = r.meta["instruments"]["sr1"]["snapshot"]["parameters"]["amplitude"]["value"]
    Ib = amp / 100e6
    FL = luttinger_frequency(abs(n) * 1e16) if True else None
    print(f"=== run {rid}: n = {n:+.2f}e12, F_L = {FL:.2f} T; rows {len(B)}; B {B.min():.3f}-{B.max():.3f}")
    print(f"  R {R.min():.1f}-{R.max():.1f} Ohm (R(B~0) {R[0]:.1f}, R(Bmax) {R[-1]:.1f}); full scale {sens/Ib:.0f} Ohm -> max {R.max()/(sens/Ib)*100:.1f}% FS")
    print(f"  I_drain {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; T {T.min():.3f}-{T.max():.3f} K; I_tg {itg.min()*1e12:+.0f}..{itg.max()*1e12:+.0f} pA; I_bg {ibg.min()*1e12:+.0f}..{ibg.max()*1e12:+.0f} pA")
    print(f"  wall {(r.col('time').max()-r.col('time').min())/60:.1f} min; median dt {np.median(dt):.2f} s/pt")
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            on = sdh_onset(R, B, r_full_scale=sens / Ib)
        for ww in w: print("  warn:", ww.message)
        print(on.summary())
    except Exception as e:
        print("  onset error:", type(e).__name__, e); on = None
    # model
    try:
        ab = M.abab_fs(n)[1]; abm = M.abab_mstar(n)
        ac = M.abca_fs(n); acm = M.abca_mstar(n)
        print("  model ABAB:", [(round(f, 2)) for f, k in ab], "m*", [round(m, 3) for f, m in abm])
        print(f"  model ABCA: F {ac[4]:.2f} topo {ac[1]} m* {acm[1]:.3f}")
    except Exception as e:
        print("  model err", e)
    # raw
    a = ax[0, j]; a.plot(B, R, lw=0.8); a.set_xlabel("B (T)"); a.set_ylabel("Rxx (Ohm)")
    a.set_title(f"run {rid}: n={n:+.1f}e12 D=0 raw Rxx(B)")
    # bg subtracted
    for lo in ([on.onset_b] if on else []) + [2.0, 3.0, 4.0]:
        pass
    blo = max(on.onset_b if on else 1.0, 0.5)
    m = B >= blo
    cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    ax[1, j].plot(1 / B[m], dR, lw=0.7); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_ylabel("ΔRxx (Ohm), poly5 in B removed")
    ax[1, j].set_title(f"bg-subtracted, B ≥ {blo:.2f} T")
    for cut in sorted(set([round(blo, 2), 1.5, 2.0, 3.0])):
        if cut >= B.max() - 2: continue
        f, S = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=5, log=False)
        s = S[0]
        pk = [i for i in range(2, len(f) - 1) if s[i] > s[i - 1] and s[i] > s[i + 1] and f[i] > 2]
        pk = sorted(pk, key=lambda i: -s[i])[:5]
        print(f"  FFT cut {cut:.2f}-{B.max():.1f} T (dF {1/(1/cut-1/B.max()):.2f} T): peaks " + ", ".join(f"{f[i]:.2f}T({s[i]/s[pk[0]]:.2f})" for i in sorted(pk)))
        ax[2, j].plot(f, s / s.max(), lw=0.8, label=f"cut {cut:.2f} T")
    ax[2, j].axvline(FL, color="k", ls="--", lw=1, label=f"F_L {FL:.1f}")
    try:
        for f0, k in ab: ax[2, j].axvline(f0, color="C3", ls=":", lw=1)
        ax[2, j].axvline(ac[4], color="C2", ls="-.", lw=1)
    except Exception: pass
    ax[2, j].set_xlim(0, 2.2 * FL); ax[2, j].set_xlabel("F (T)"); ax[2, j].legend(fontsize=7)
    ax[2, j].set_title("FFT (red: ABAB model, green: ABCA, black: F_L)")
fig.tight_layout(); fig.savefig("hera_scratch/spot_runs67.png", dpi=90)
