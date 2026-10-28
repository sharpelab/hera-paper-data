# Runs 6-7 — SdH spot checks at D = 0 (region-A cal). Raw R(B) first, then a zero-padded 1/B FFT per trace.
from scipy.signal import find_peaks, savgol_filter
from hera.analysis import resolve_channels
h_e = cst.h / cst.e
spots = {6: +3.2e16, 7: -1.2e16}   # nominal n (m^-2), geometry-prior scale
fig, ax = plt.subplots(2, 3, figsize=(16, 8))
for k, rid in enumerate(spots):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col_at(1); R = (r.col("sr1_X") / ch["sr1"].gain) / (r.col("sr0_X") / ch["sr0"].gain)
    o = np.argsort(B); B, R = B[o], R[o]; Rs = savgol_filter(R, 9, 2)
    FL = abs(spots[rid]) * h_e / 4
    print(f"run {rid}: n_nom {spots[rid]*1e-16:+.1f}e12, F_L(nominal) {FL:.1f} T; B {B.min():.2f}-{B.max():.2f} T; R {R.min():.0f}..{R.max():.0f} Ohm; "
          f"T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K; I_tg {r.col('k_2400_tg_curr').min()*1e12:.0f}..{r.col('k_2400_tg_curr').max()*1e12:.0f} pA")
    ax[k, 0].plot(B, R, lw=0.6); ax[k, 0].set_xlabel("B (T)"); ax[k, 0].set_ylabel("Rxx B_1-B_2 (Ohm)"); ax[k, 0].set_title(f"run {rid} raw, n_nom {spots[rid]*1e-16:+.1f}e12")
    m = B > 0.8; ax[k, 1].plot(1 / B[m], Rs[m], lw=0.6); ax[k, 1].set_xlabel("1/B (1/T)"); ax[k, 1].set_title("R vs 1/B")
    for lo, hi in [(1.0, 10.0), (1.5, 6.0), (3.0, 10.0)]:
        m = (B >= lo) & (B <= hi); x = 1 / B[m]; y = Rs[m] - np.polyval(np.polyfit(B[m], Rs[m], 4), B[m])
        o2 = np.argsort(x); xu = np.linspace(x.min(), x.max(), 2048); yu = np.interp(xu, x[o2], y[o2])
        yu = (yu - yu.mean()) * np.hanning(len(yu)); sp = np.abs(np.fft.rfft(yu, 2**16)); f = np.fft.rfftfreq(2**16, xu[1] - xu[0])
        s = (f > 1.5) & (f < 60); pk, _ = find_peaks(sp[s], prominence=0.08 * sp[s].max())
        top = sorted(sorted(pk, key=lambda p: -sp[s][p])[:6])
        print(f"   FFT [{lo:.1f},{hi:.1f}] T (res {1/(x.max()-x.min()):.1f} T): " + ", ".join(f"{f[s][p]:.1f} T ({sp[s][p]/sp[s].max():.2f}, {f[s][p]/FL:.2f} F_L)" for p in top))
        ax[k, 2].plot(f[s], sp[s] / sp[s].max(), lw=1, label=f"[{lo:g},{hi:g}] T")
    ax[k, 2].axvline(FL, color="k", ls=":", label="F_L nominal"); ax[k, 2].set_xlabel("F (T)"); ax[k, 2].legend(fontsize=7)
fig.suptitle("vti-02 runs 6-7: SdH spot checks at D = 0 (sr1 = B_1-B_2), T = 1.17-1.29 K"); fig.tight_layout(); plt.show()
