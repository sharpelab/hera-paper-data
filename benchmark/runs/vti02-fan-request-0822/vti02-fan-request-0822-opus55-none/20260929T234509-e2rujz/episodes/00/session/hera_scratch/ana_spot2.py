import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import find_peaks, savgol_filter
from hera.analysis import open_run, resolve_channels
h_e = 4.135667e-15
nominal = {6: 3.2e16, 7: 1.2e16}
fig, ax = plt.subplots(2, 2, figsize=(14, 8))
for k, rid in enumerate([6, 7]):
    r = open_run(f"data/{rid}"); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col_at(1); R = (r.col("sr1_X")/ch["sr1"].gain)/(r.col("sr0_X")/ch["sr0"].gain)
    o = np.argsort(B); B, R = B[o], R[o]
    Rs = savgol_filter(R, 9, 2)
    for lo, hi in [(1.0, 10), (1.5, 6), (3, 10)]:
        m = (B >= lo) & (B <= hi); x = 1/B[m]; y = Rs[m] - np.polyval(np.polyfit(B[m], Rs[m], 4), B[m])
        xu = np.linspace(x.min(), x.max(), 2048); yu = np.interp(xu, x[::-1], y[::-1]) if x[0] > x[-1] else np.interp(xu, x, y)
        yu = (yu - yu.mean()) * np.hanning(len(yu)); N = 2**16
        sp = np.abs(np.fft.rfft(yu, N)); f = np.fft.rfftfreq(N, xu[1]-xu[0])
        s = (f > 1.5) & (f < 80); pk, _ = find_peaks(sp[s], prominence=sp[s].max()*0.08)
        top = sorted(pk, key=lambda p: -sp[s][p])[:7]
        print(f"run {rid} [{lo},{hi}] T: res {1/(x.max()-x.min()):.2f} T; peaks " + ", ".join(f"{f[s][p]:.1f}({sp[s][p]/sp[s].max():.2f})" for p in sorted(top)))
        if (lo, hi) == (1.0, 10): ax[k, 1].plot(f[s], sp[s], label=f"[{lo},{hi}]")
        else: ax[k, 1].plot(f[s], sp[s]/sp[s].max()*sp[(f>1.5)&(f<80)].max() if False else sp[s], label=f"[{lo},{hi}]", alpha=0.7)
    ax[k,1].legend(); ax[k,1].set_xlabel("F (T)"); ax[k,1].axvline(nominal[rid]*h_e/4, color="k", ls=":", label="F_L")
    # minima positions and nominal nu
    mn, _ = find_peaks(-Rs, prominence=15, distance=5)
    print(f"run {rid} R minima (B, R, nu_nominal=nh/eB):", ", ".join(f"{B[j]:.2f}T/{Rs[j]:.0f}/{nominal[rid]*h_e/B[j]:.1f}" for j in mn if B[j] > 0.8))
    ax[k,0].plot(1/B[B>0.8], Rs[B>0.8], lw=0.7); ax[k,0].set_xlabel("1/B (1/T)"); ax[k,0].set_title(f"run {rid} R vs 1/B")
fig.tight_layout(); fig.savefig("hera_scratch/spot_runs67_fft.png", dpi=90)
