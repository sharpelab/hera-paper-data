# Run 6 — SdH spot check, electron side, n = +3.2e12 at D = 0, B 0 -> 10 T. Raw first, then onset + FFT vs F_L.
from hera.analysis import resolve_channels, sdh_onset, SdhOnsetError
r = run(6); ch = {c.cid: c for c in resolve_channels(r.meta)}
B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain; R = (r.col("sr1_X") / ch["sr1"].gain) / I; T = r.col("T_sample")
print(summarize_run(r)); print(f"R {R.min():.1f}..{R.max():.1f} Ohm; T {T.min():.3f}-{T.max():.3f} K (Cernox MR shifts it); I_drain {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA")
n12 = 3.2; FL = luttinger_frequency(n12 * 1e16); print(f"F_L(n = {n12}e12, g = 4) = {FL:.1f} T")
m = B >= 0.3; B, R = B[m], R[m]
on = sdh_onset(R, B, b_lo=0.5, r_full_scale=50e-6 / 10e-9); print(on.summary())
lo = 1.0
fig, ax = plt.subplots(3, 1, figsize=(11, 11))
ax[0].plot(B, R, lw=0.7); ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("R = X/I (Ohm)"); ax[0].set_title("run 6 raw — Rxx(B_1−B_2) with a ρxy admixture (corner pair)")
sel = B >= lo; cf = np.polyfit(B[sel], R[sel], 5); dR = R[sel] - np.polyval(cf, B[sel])
ax[1].plot(1 / B[sel], dR, lw=0.7); ax[1].set_xlabel("1/B (1/T)"); ax[1].set_ylabel("ΔR (Ohm)"); ax[1].set_title(f"background removed (deg-5 in B), B ≥ {lo} T")
peaks = {}
for (blo, bhi, lab, c) in [(lo, B.max(), "full", "k"), (lo, 3.0, "low-B [1,3] T", "b"), (3.0, B.max(), "high-B [3,10] T", "r")]:
    f, spec = sdh_fft(R[:, None], B, b_range=(blo, bhi), bg_degree=5, log=False, nfft=4096)
    s = spec[0] / spec[0][f > 2].max(); ax[2].plot(f, s, c, lw=0.8, label=f"{lab}, δF = {1/(1/blo-1/bhi):.1f} T")
    pk = [(f[i], s[i]) for i in range(2, len(f) - 1) if s[i] > s[i-1] and s[i] > s[i+1] and s[i] > 0.12 and f[i] > 2]
    peaks[lab] = pk; print(f"FFT {lab} [{blo:.1f},{bhi:.1f}] T (δF {1/(1/blo-1/bhi):.2f} T): " + ", ".join(f"{a:.1f} T ({b:.2f})" for a, b in pk[:10]))
for frac, lab in [(1, "F_L"), (0.77, "0.77 F_L"), (0.23, "0.23 F_L")]:
    ax[2].axvline(frac * FL, color="gray", ls=":", lw=0.8); ax[2].text(frac * FL, 1.02, lab, fontsize=7, ha="center")
ax[2].set_xlim(0, 1.6 * FL); ax[2].set_xlabel("F (T)"); ax[2].set_ylabel("|FFT| (norm.)"); ax[2].legend(fontsize=7)
fig.tight_layout(); plt.show()
# Luttinger check on the resolved pair
fp = sorted(peaks["full"], key=lambda p: -p[1])
print("pair sum check: candidates", [round(a, 1) for a, _ in fp[:6]])
