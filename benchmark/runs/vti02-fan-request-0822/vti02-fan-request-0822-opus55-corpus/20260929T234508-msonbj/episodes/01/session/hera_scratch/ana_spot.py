"""Spot-check reads: runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12). Onset + FFT vs F_L + model."""
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency
sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
import fs_count_b0 as M

D = Path(__file__).resolve().parent.parent / "data"
out = {}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(D / str(rid))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    T = r.col("T_sample")
    itg, ibg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    sens = 50e-6; Ib = np.median(np.abs(I)); rfs = sens / Ib
    print(f"=== run {rid} n={n12:+.1f}e12: {len(B)} pts B {B.min():.3f}-{B.max():.3f}; R {R.min():.1f}-{R.max():.1f} Ohm "
          f"(FS {rfs:.0f}); R(B<0.1) {R[B<0.1].mean():.1f}; I {Ib*1e9:.2f} nA; T {T.min():.3f}-{T.max():.3f}; "
          f"Itg {itg.min()*1e12:+.0f}..{itg.max()*1e12:+.0f} pA Ibg {ibg.min()*1e12:+.0f}..{ibg.max()*1e12:+.0f} pA")
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    ab = M.abab_fs(n12); abm = M.abab_mstar(n12)
    ac = M.abca_fs(n12); acm = M.abca_mstar(n12)
    print(f"F_L {FL:.2f} T; ABAB orbits {[round(f,2) for f,_ in ab[1]]} m* {[round(m,3) for _,m in abm]}; ABCA F {ac[4]:.2f} m* {acm[1]:.3f} topo {ac[1]}")
    try:
        on = sdh_onset(R, B, b_lo=0.3, r_full_scale=rfs)
        print(on.summary())
        onset = on.onset_b
    except Exception as e:
        print("SdhOnset:", type(e).__name__, e); onset = None
    out[rid] = dict(B=B, R=R, FL=FL, onset=onset, ab=ab, ac=ac)
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_title(f"run {rid} raw Rxx, n={n12:+.1f}e12"); ax[0, j].set_xlabel("B (T)")
    # FFT at several windows / bg degrees
    lo0 = max(onset or 1.0, 1.0)
    for lo in sorted(set([lo0, 1.5, 2.0, 3.0])):
        for deg in (3, 5):
            f, S = sdh_fft(R[:, None], B, b_range=(lo, B.max()), bg_degree=deg, nfft=4096)
            s = S[0]
            m = f > 2
            pk = [(f[i], s[i]) for i in range(1, len(f) - 1) if m[i] and s[i] > s[i-1] and s[i] > s[i+1]]
            pk = sorted(pk, key=lambda t: -t[1])[:6]
            print(f"  FFT [{lo:.2f},{B.max():.1f}] deg{deg}: dF={1/(1/lo-1/B.max()):.2f} T; peaks " +
                  ", ".join(f"{a:.1f}T({b/max(s[m]):.2f})" for a, b in pk))
            if deg == 5:
                ax[1, j].plot(f, s / s[m].max(), lw=0.8, label=f"lo {lo:.1f}")
    ax[1, j].axvline(FL, color="k", ls="--", label="F_L")
    for fa, _ in ab[1]: ax[1, j].axvline(fa, color="b", ls=":", lw=1)
    ax[1, j].set_xlim(0, 2.2 * FL); ax[1, j].legend(fontsize=7); ax[1, j].set_xlabel("F (T)"); ax[1, j].set_title("FFT (bg5); blue dotted ABAB, k-- F_L=ABCA")
    # bg-subtracted vs 1/B
    sel = B > lo0
    cf = np.polyfit(B[sel], R[sel], 5); dR = R[sel] - np.polyval(cf, B[sel])
    ax[2, j].plot(1 / B[sel], dR, lw=0.6); ax[2, j].set_xlabel("1/B (1/T)"); ax[2, j].set_title("dR (poly5 in B)")
fig.tight_layout(); fig.savefig(Path(__file__).parent / "spot_runs67.png", dpi=90)
