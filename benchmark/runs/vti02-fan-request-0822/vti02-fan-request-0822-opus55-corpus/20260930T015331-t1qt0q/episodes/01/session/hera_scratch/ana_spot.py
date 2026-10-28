"""SdH spot checks runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12): raw MR, onset, FFT vs F_L + model."""
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as fm

h, e = 6.62607015e-34, 1.602176634e-19
FL = lambda n12: abs(n12) * 1e16 * h / (4 * e)
SENS = 50e-6

out = {}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for col, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    run = open_run(f"data/{rid}")
    B = run.col("magnet_field"); V = run.col("sr1_X"); I = run.col("sr0_X") / -1e6
    Ib = np.median(I)
    R = V / I
    o = np.argsort(B); B, R, V, I = B[o], R[o], V[o], I[o]
    print(f"\n=== run {rid}: n = {n12:+.2f}e12, F_L = {FL(n12):.2f} T; I median {Ib*1e9:.3f} nA (spread {np.ptp(I)/Ib*100:.2f}%), "
          f"R(B~0) {R[B<0.35].mean():.1f} Ohm, R max {R.max():.0f} Ohm at {B[np.argmax(R)]:.2f} T; |V|max/sens {np.abs(V).max()/SENS:.2f}; "
          f"T {run.col('T_sample').min():.3f}-{run.col('T_sample').max():.3f} K; Itg max {np.abs(run.col('k_2400_tg_curr')).max()*1e12:.0f} pA")
    try:
        ab = fm.abab_fs(n12*1e16); print("  model ABAB orbits:", [(round(f, 2)) for f, k in ab[1]], " masses:", [(round(f, 1), round(m, 3)) for f, m in fm.abab_mstar(n12*1e16)])
        ac = fm.abca_fs(n12*1e16); print(f"  model ABCA: topo {ac[1]} F_total {ac[4]:.2f}, m* {fm.abca_mstar(n12*1e16)[1]:.3f}")
    except Exception as ex:
        print("  model err", ex)
    try:
        on = sdh_onset(R, B, r_full_scale=SENS / Ib)
        print(on.summary())
        out[rid] = on
    except Exception as ex:
        print("  sdh_onset:", type(ex).__name__, ex); on = None
    ax[0, col].plot(B, R, lw=0.8); ax[0, col].set_title(f"run {rid} raw Rxx, n={n12:+.1f}e12 D=0"); ax[0, col].set_xlabel("B (T)"); ax[0, col].set_ylabel("R (Ohm)")
    # background-subtracted vs 1/B
    for lo in ([1.5, 2.5, 4.0] if rid == 6 else [1.5, 2.5, 4.0]):
        m = B >= lo
        cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
        if lo == 2.5: ax[1, col].plot(1 / B[m], dR, lw=0.7)
        u = np.linspace(1/B.max(), 1/lo, 2048); yi = np.interp(u, np.sort(1/B[m]), dR[np.argsort(1/B[m])])
        s = np.abs(np.fft.rfft(yi*np.hanning(len(u)), n=16*len(u))); fr = np.fft.rfftfreq(16*len(u), u[1]-u[0]); ax[2, col].plot(fr, s / s[fr > 2].max(), lw=0.9, label=f"B>{lo} T")
        # top peaks
        from scipy.signal import find_peaks
        pk, _ = find_peaks(s, prominence=0.05 * s[fr > 2].max())
        pk = [p for p in pk if fr[p] > 2]
        pk = sorted(pk, key=lambda p: -s[p])[:6]
        dF = 1 / (1 / lo - 1 / B.max())
        print(f"  FFT B>{lo}: dF={dF:.2f} T; peaks " + ", ".join(f"{fr[p]:.2f}T({s[p]/s[pk[0]]:.2f})" for p in sorted(pk)))
    ax[1, col].set_xlabel("1/B (1/T)"); ax[1, col].set_ylabel("dR (Ohm), B>2.5T, bg5")
    ax[2, col].axvline(FL(n12), color="k", ls="--", label="F_L")
    try:
        for f, k in fm.abab_fs(n12*1e16)[1]: ax[2, col].axvline(f, color="C3", ls=":", lw=1)
    except Exception: pass
    ax[2, col].set_xlim(0, 3 * FL(n12)); ax[2, col].legend(fontsize=7); ax[2, col].set_xlabel("F (T)")
fig.tight_layout(); fig.savefig("hera_scratch/spot_runs67.png", dpi=90)
