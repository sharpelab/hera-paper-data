"""Runs 6/7 sdh-spot-check read: raw MR, onset (sdh_onset), FFT vs F_L + model templates."""
import sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as m
SPOT = {6: +3.2, 7: -1.2}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, rid in enumerate([6, 7]):
    r = open_run(f"data/{rid}"); print(summarize_run(r))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    sens = r.meta.get("instruments", {})
    print(f"run {rid}: I_drain {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; R {R.min():.0f}-{R.max():.0f} Ohm; B {B.min():.3f}-{B.max():.3f}; "
          f"T {np.nanmin(r.col('T_sample')):.3f}-{np.nanmax(r.col('T_sample')):.3f} K; itg {np.ptp(r.col('k_2400_tg_curr'))*1e12:.0f} pA ptp")
    n = SPOT[rid]; FL = float(luttinger_frequency(n * 1e16))
    ab = m.abab_fs(n); abm = m.abab_mstar(n); ac = m.abca_fs(n)
    print(f"  F_L = {FL:.2f} T; ABAB orbits {[round(f,2) for f,_ in ab[1]]} m* {[round(x,3) for _,x in abm]}; ABCA F {ac[4]:.2f}")
    on = None
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
        print(on.summary())
    except Exception as e:
        print("  sdh_onset:", type(e).__name__, e)
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_title(f"run {rid} raw Rxx, n={n:+.1f}e12 D=0"); ax[0, j].set_xlabel("B (T)")
    # bg-subtracted dR above ~1 T
    sel = B > 1.0
    cf = np.polyfit(B[sel], R[sel], 5); dR = R[sel] - np.polyval(cf, B[sel])
    ax[1, j].plot(1 / B[sel], dR, lw=0.6); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_title("dR (poly5 in B), B>1 T")
    lo = on.onset_b if on is not None else 2.0
    for blo in sorted({max(lo, 1.5), 3.0, 5.0}):
        fr, sp = sdh_fft(R[:, None], B, b_range=(blo, B.max()), bg_degree=5)
        s = sp[0]; ax[2, j].plot(fr, s / s[fr > 1].max(), lw=0.8, label=f"B>{blo:.1f}")
        k = np.argsort(s * (fr > 1.5))[::-1]
        pk = []
        for i in k:
            if all(abs(fr[i] - p) > 1.5 for p in pk): pk.append(fr[i])
            if len(pk) == 5: break
        print(f"  FFT B>{blo:.2f}: top peaks {[round(p,2) for p in pk]}  (dF={1/(1/blo-1/B.max()):.2f} T)")
    for f, _ in ab[1]: ax[2, j].axvline(f, color="g", ls=":", lw=1)
    ax[2, j].axvline(FL, color="r", ls="--", lw=1); ax[2, j].set_xlim(0, 2.2 * FL); ax[2, j].legend(fontsize=7)
    ax[2, j].set_xlabel("F (T)"); ax[2, j].set_title("FFT (log R, poly5 in B); red F_L, green ABAB model")
fig.tight_layout(); fig.savefig("hera_scratch/spot_runs67.png", dpi=110)
