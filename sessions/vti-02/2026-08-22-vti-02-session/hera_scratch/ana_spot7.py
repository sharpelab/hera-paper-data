# Run 7 — SdH spot check, hole side: n_cal = -1.2e12 (D = 0), B 10 -> 0.3 T ride-down, 486 pts. Raw first.
from hera.analysis import resolve_channels, sdh_onset
r = run(7); ch = {c.cid: c for c in resolve_channels(r.meta)}
B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain; R = (r.col("sr1_X") / ch["sr1"].gain) / I
print(summarize_run(r)); print(f"R {R.min():.1f}..{R.max():.1f} Ohm")
o = np.argsort(B); B, R = B[o], R[o]
FLc = luttinger_frequency(1.2e16); print(f"F_L(n_cal = 1.2e12) = {FLc:.1f} T; at scale 0.886: {0.886*FLc:.1f} T")
fig, ax = plt.subplots(3, 1, figsize=(11, 11))
ax[0].plot(B, R, lw=0.7); ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("R = X/I (Ohm)"); ax[0].set_title("run 7 raw — hole side, n_cal = -1.2e12, D = 0")
m = B >= 1.0; cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
ax[1].plot(1 / B[m], dR, lw=0.7); ax[1].set_xlabel("1/B (1/T)"); ax[1].set_ylabel("ΔR (Ohm)"); ax[1].set_title("deg-5 background removed, B ≥ 1 T")
for (blo, bhi, lab, c) in [(1.0, 5.0, "SdH window [1,5] T", "k"), (1.0, 3.0, "[1,3] T", "b")]:
    f, spec = sdh_fft(R[:, None], B, b_range=(blo, bhi), bg_degree=5, log=False, nfft=4096); s = spec[0] / spec[0][f > 2].max()
    ax[2].plot(f, s, c, lw=0.8, label=f"{lab}, δF = {1/(1/blo-1/bhi):.1f} T")
    pk = [(f[i], s[i]) for i in range(2, len(f) - 1) if s[i] > s[i-1] and s[i] > s[i+1] and s[i] > 0.2 and f[i] > 2]
    print(f"FFT {lab}: " + ", ".join(f"{a:.1f} T ({b:.2f})" for a, b in pk[:8]))
ax[2].axvline(0.886 * FLc, color="gray", ls=":"); ax[2].text(0.886 * FLc, 1.02, "F_L x0.886", fontsize=7, ha="center")
ax[2].set_xlim(0, 30); ax[2].set_xlabel("F (T)"); ax[2].set_ylabel("|FFT| (norm.)"); ax[2].legend(fontsize=7)
fig.tight_layout(); plt.show()
# integer-QH ladder at high B: minima of dR for B > 4.5 T -> 1/B spacing -> n h/e
m2 = B >= 4.5; cf2 = np.polyfit(B[m2], R[m2], 3); d2 = R[m2] - np.polyval(cf2, B[m2]); b2 = B[m2]
from scipy.signal import find_peaks
mins, _ = find_peaks(-d2, prominence=15); Bm = b2[mins]; inv = np.sort(1 / Bm)
print("rho_xx minima above 4.5 T at B =", np.round(Bm, 2), "T; consecutive 1/B spacings:", np.round(np.diff(inv), 4))
dnu = np.median(np.diff(inv)); print(f"median spacing {dnu:.4f} 1/T per filling step -> n h/e = {1/dnu:.1f} T -> n = {1/dnu/41.36:.2f}e12 if Δν = 1 (lever-arm scale vs n_cal 1.2: {1/dnu/41.36/1.2:.3f})")
