import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import find_peaks, savgol_filter
from scipy.interpolate import interp1d
from hera.analysis import open_run, resolve_channels
h_e = 4.135667e-15
def load(rid):
    r = open_run(f"data/{rid}"); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X")/ch["sr0"].gain; R = np.abs(r.col("sr1_X")/ch["sr1"].gain/I)
    o = np.argsort(B); return B[o], R[o]
def fft_win(B, R, lo, hi, deg=3, pad=16):
    m = (B >= lo) & (B <= hi); b, y = B[m], R[m]
    y = y - np.polyval(np.polyfit(b, y, deg), b)   # linear R detrend (no log: R->0 in QH)
    x = 1/b; o = np.argsort(x); x, y = x[o], y[o]
    N = len(x); xu = np.linspace(x.min(), x.max(), N); yu = interp1d(x, y)(xu)*np.hanning(N)
    F = np.fft.rfftfreq(N*pad, xu[1]-xu[0]); S = np.abs(np.fft.rfft(yu, N*pad))
    return F, S, 1/(x.max()-x.min())
fig, ax = plt.subplots(2, 3, figsize=(17, 8))
for k, (rid, n) in enumerate([(6, 3.2), (7, -1.2)]):
    B, R = load(rid); nF = abs(n)*1e16*h_e   # n h/e in T  (nu = nF/B)
    print(f"\n=== run {rid}  n_nom {n:+.1f}e12 -> F_L = n h/4e = {nF/4:.1f} T, nu = {nF:.1f}/B")
    Rs = savgol_filter(R, 9, 2)
    mins, _ = find_peaks(-Rs, prominence=8); mins = mins[B[mins] > 1.0]
    print(" Rxx minima (B, R, nu_nom):", "; ".join(f"{B[i]:.2f}T {Rs[i]:.0f}Ω ν{nF/B[i]:.1f}" for i in mins))
    for lo, hi in [(0.8, 3.0), (1.0, 4.0), (1.5, 6.0), (3.0, 10.0)]:
        F, S, dF = fft_win(B, R, lo, hi); sel = (F > 1.5) & (F < 60)
        pk, _ = find_peaks(S[sel], prominence=0.1*S[sel].max())
        print(f" FFT B[{lo},{hi}] (dF {dF:.1f} T): " + ", ".join(f"{F[sel][j]:.1f}({S[sel][j]/S[sel].max():.2f})" for j in pk))
        ax[k,2].plot(F[sel], S[sel]/S[sel].max(), lw=.8, label=f"[{lo},{hi}] dF {dF:.1f}")
    ax[k,2].axvline(nF/4, color="k", ls=":", label="F_L nominal"); ax[k,2].legend(fontsize=7); ax[k,2].set_xlabel("F (T)")
    ax[k,0].plot(B, R, lw=.7); ax[k,0].plot(B[mins], Rs[mins], "rv", ms=4); ax[k,0].set_title(f"run {rid} Rxx(B), n_nom {n:+.1f}e12")
    for i in mins: ax[k,0].text(B[i], Rs[i]-15, f"{nF/B[i]:.0f}", fontsize=6, ha="center")
    m = B > 0.6; ax[k,1].plot(1/B[m], R[m] - savgol_filter(R, 101, 3)[m], lw=.6); ax[k,1].set_xlabel("1/B"); ax[k,1].set_title("R - smooth")
fig.tight_layout(); fig.savefig("hera_scratch/sdh_spots2.png", dpi=85)
