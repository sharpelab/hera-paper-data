"""Runs 6-7 — sdh-spot-check at D = 0 (run-5 cal): raw Rxx(B) first, then FFT in 1/B and the Rxx-minima filling ladder."""
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
from hera.analysis import resolve_channels, sdh_onset

spots = [(6, +3.2), (7, -1.2)]          # (run, n in 1e12 cm^-2 on the geometry-prior scale)
fig, ax = plt.subplots(2, 3, figsize=(16, 8))
ladder = {}
for k, (rid, n12) in enumerate(spots):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I); o = np.argsort(B); B, R = B[o], R[o]
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"run {rid}: n = {n12:+.1f}e12 (prior scale), F_L(prior) = {FL:.1f} T; R {R.min():.1f}-{R.max():.1f} Ohm; "
          f"I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; |I_tg|max {np.abs(r.col('k_2400_tg_curr')).max()*1e12:.0f} pA, "
          f"|I_bg|max {np.abs(r.col('k_2400_bg_curr')).max()*1e12:.0f} pA; T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K")
    ax[k, 0].plot(B, R, lw=0.7); ax[k, 0].set_xlabel("B (T)"); ax[k, 0].set_ylabel("|Rxx| B_1-B_2 (Ohm)")
    ax[k, 0].set_title(f"run {rid} raw — n = {n12:+.1f}e12, D = 0")
    on = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9); print(on.summary())
    f, sp = sdh_fft(R[:, None], B, b_range=(1.0, 10.0), nfft=4096, bg_degree=5); sp = sp[0]
    ax[k, 1].plot(f, sp / sp[f > 2].max()); ax[k, 1].axvline(FL, color="r", ls="--", label=f"F_L prior {FL:.1f} T")
    ax[k, 1].set_xlim(0, 60); ax[k, 1].set_xlabel("F (T)"); ax[k, 1].set_title(f"FFT in 1/B, B [1, 10] T (dF 1.1 T)"); ax[k, 1].legend()
    pk, _ = find_peaks(-gaussian_filter1d(R, 2), prominence=8, distance=5); pk = pk[B[pk] > 0.8]
    nuB = abs(n12) * 1e16 * cst.h / cst.e
    ladder[rid] = (B[pk], nuB / B[pk], R[pk])
# filling ladder of run-6 minima: find the density-scale s that puts nu = s * nu_prior on multiples of 4
Bm, nup, Rm = ladder[6]
ss = np.arange(0.80, 1.05, 0.001); cost = [np.sqrt(np.mean((s * nup / 4 - np.round(s * nup / 4)) ** 2)) for s in ss]
s_best = ss[int(np.argmin(cost))]; nu_true = s_best * nup
print(f"\nrun 6 minima ladder: best density scale s = {s_best:.3f} (rms {min(cost)*4:.2f} in nu) -> F_L(true) = {s_best*33.1:.1f} T")
print("  B (T):  " + "  ".join(f"{b:5.2f}" for b in Bm)); print("  nu:     " + "  ".join(f"{v:5.1f}" for v in nu_true))
present = sorted(set(int(4 * round(v / 4)) for v in nu_true)); print(f"  4k minima present: {present}; missing in 16-80: {[v for v in range(16, 84, 4) if v not in present]}")
ax[0, 2].plot(nu_true, Rm, "o"); [ax[0, 2].axvline(v, color="0.85", lw=0.8) for v in range(4, 92, 4)]
ax[0, 2].set_xlabel(f"nu = {s_best:.3f} x nu_prior"); ax[0, 2].set_ylabel("R at minimum (Ohm)"); ax[0, 2].set_title("run 6 Rxx minima vs filling (grid: nu = 4k)")
ax[1, 2].plot(ss, np.array(cost) * 4); ax[1, 2].axvline(s_best, color="r", ls="--"); ax[1, 2].set_xlabel("density scale s"); ax[1, 2].set_ylabel("rms off 4k (nu)")
ax[1, 2].set_title("ladder fit — run 6")
fig.suptitle("vti-02 SdH spot checks, runs 6 (e) / 7 (h), D = 0, T = 1.17-1.29 K, 10 nA"); fig.tight_layout(); plt.show()
