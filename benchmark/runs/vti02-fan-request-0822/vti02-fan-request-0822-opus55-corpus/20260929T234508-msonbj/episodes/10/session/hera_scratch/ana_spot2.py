"""Spot checks 6/7, pass 2: model tables (m^-2 units), step check, windowed FFTs, low-B zoom."""
import sys, warnings
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M
sys.path.insert(0, "/home/hera/measurement_env/hera/models/trilayer_fs_count")

print("model tables (u_D = 0):")
for n in (-1.2, -1.0, 1.0, 1.5, 2.0, 2.5, 3.0, 3.2):
    nn = n * 1e16
    ab = M.abab_fs(nn)[1]; abm = M.abab_mstar(nn)
    ac = M.abca_fs(nn); acm = M.abca_mstar(nn)
    print(f"  n {n:+.1f}: F_L {luttinger_frequency(nn):.2f}; ABAB F {[round(f,2) for f,k in ab]} m* {[round(m,3) for f,m in abm]}; "
          f"ABCA F {ac[4]:.2f} ({ac[1]}) m* {acm[1]:.3f}")

def load(rid):
    r = open_run(f"data/{rid}")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    V = r.col("sr1_X") / ch["sr1"].gain
    R = np.abs(V / I); P1 = r.col("sr1_P"); P0 = r.col("sr0_P")
    o = np.argsort(B)
    return B[o], R[o], I[o], P1[o], P0[o], r

fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n, wins) in enumerate([(6, 3.2, [(0.5, 7.4), (1.0, 7.4), (2.0, 7.4), (0.5, 3.0), (3.0, 7.4)]),
                                    (7, -1.2, [(0.7, 10.0), (0.7, 5.0), (1.0, 5.0), (2.0, 10.0), (0.4, 2.0)])]):
    B, R, I, P1, P0, r = load(rid)
    FL = luttinger_frequency(abs(n) * 1e16)
    # step check around 7.5-8.2 T for run 6
    if rid == 6:
        for b0 in (7.0, 7.4, 7.6, 7.7, 7.8, 8.0, 8.5, 9.5):
            k = np.argmin(abs(B - b0))
            print(f"  run6 B={B[k]:.2f}: R {R[k]:.0f} Ohm, I_drain {I[k]*1e9:.3f} nA, sr1 P {P1[k]:+.1f} deg, sr0 P {P0[k]:+.1f} deg")
    print(f"=== run {rid} n={n:+.1f} F_L={FL:.2f} T; sr1 phase {np.percentile(P1,5):+.1f}..{np.percentile(P1,95):+.1f}; I_drain {I.min()*1e9:.2f}-{I.max()*1e9:.2f}")
    for lo, hi in wins:
        f, S = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, log=False, nfft=2048)
        s = S[0]
        pk = [i for i in range(2, len(f) - 1) if s[i] > s[i - 1] and s[i] > s[i + 1] and f[i] > 1.0]
        pk = sorted(pk, key=lambda i: -s[i])[:6]
        print(f"  FFT [{lo},{hi}] T dF {1/(1/lo-1/hi):.2f} T: " + ", ".join(f"{f[i]:.2f}({s[i]/s[pk[0]]:.2f})" for i in sorted(pk)))
    for lo, hi in wins[:3]:
        f, S = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, log=False, nfft=2048)
        ax[2, j].plot(f, S[0] / S[0].max(), lw=0.8, label=f"[{lo},{hi}] T")
    ax[2, j].axvline(FL, color="k", ls="--", label=f"F_L {FL:.1f}")
    ab = M.abab_fs(n * 1e16)[1]
    for f0, k in ab: ax[2, j].axvline(f0, color="C3", ls=":")
    ax[2, j].set_xlim(0, 1.5 * FL); ax[2, j].legend(fontsize=7); ax[2, j].set_xlabel("F (T)")
    ax[2, j].set_title(f"run {rid} FFT; red dotted ABAB model, black F_L")
    # onset on the step-free window
    bh = 7.4 if rid == 6 else 10.0
    m = B <= bh
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            on = sdh_onset(R[m], B[m], r_full_scale=5000.0); print(on.summary())
        except Exception as e: print("onset err", e)
        for ww in w: print("  warn:", ww.message)
    # low-B zoom: local savgol bg
    ml = (B >= 0.3) & (B <= 3.0)
    Bl, Rl = B[ml], R[ml]
    win = max(5, int(0.4 / np.median(np.diff(Bl))) | 1)
    dR = Rl - savgol_filter(Rl, win, 2)
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_title(f"run {rid} raw Rxx (n={n:+.1f}e12)"); ax[0, j].set_xlabel("B (T)")
    ax[1, j].plot(1 / Bl, dR, lw=0.7); ax[1, j].set_xlabel("1/B"); ax[1, j].set_title(f"low-B 0.3-3 T, savgol({win}) removed")
fig.tight_layout(); fig.savefig("hera_scratch/spot_runs67_b.png", dpi=90)
