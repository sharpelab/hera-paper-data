# Runs 6 / 7 — sdh-spot-check at D = 0 (run-5 calibration): raw Rxx(B), then the 1/B FFT per window.
from scipy.signal import find_peaks
from hera.analysis import resolve_channels, sdh_onset
fig, ax = plt.subplots(2, 2, figsize=(12, 7))
for j, (rid, lab) in enumerate([(6, "n = +3.2e12 (electron)"), (7, "n = -1.2e12 (hole)")]):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col_at(r.col_indices("magnet_field")[0])
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / (r.col("sr0_X") / ch["sr0"].gain))
    o = np.argsort(B); B, R = B[o], R[o]
    print(f"run {rid} {lab}: R(B<1 T) median {np.median(R[B < 1]):.0f} Ohm, max {R.max():.0f} Ohm at {B[np.argmax(R)]:.2f} T; "
          f"T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K; |I_tg|,|I_bg| max "
          f"{np.abs(r.col('k_2400_tg_curr')).max()*1e12:.0f}, {np.abs(r.col('k_2400_bg_curr')).max()*1e12:.0f} pA")
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("|Rxx| B_1-B_2 (Ohm)"); ax[0, j].set_title(f"run {rid} raw — {lab}")
    for br in [(1.5, 10), (3, 10)]:
        f, sp = sdh_fft(R[:, None], B, b_range=br, nfft=4096, bg_degree=5); sp = sp[0]
        m = f > 2; p, _ = find_peaks(sp, prominence=0.08 * sp[m].max())
        p = sorted([q for q in p if 2 < f[q] < 120], key=lambda q: -sp[q])[:6]
        print(f"   FFT {br[0]}-{br[1]} T (dF {1/(1/br[0]-1/br[1]):.1f} T): " + ", ".join(f"{f[q]:.1f} T ({sp[q]/sp[m].max():.2f})" for q in p))
        ax[1, j].plot(f, sp / sp[m].max(), label=f"{br[0]}-{br[1]} T")
    ax[1, j].set_xlim(0, 80); ax[1, j].set_xlabel("F (T)"); ax[1, j].set_ylabel("|FFT| (norm)"); ax[1, j].legend()
    on = sdh_onset(R, B, r_full_scale=50e-6 / 1e-8)
    print(f"   onset (sdh_onset): {on.onset_b:.2f} T via {on.onset_freq:.1f} T tone; robust tones: " +
          ", ".join(f"{t.freq:.1f}@{t.onset_b:.2f}T" for t in on.tones if not t.marginal))
    print(f"   F_L(prior c scale) = {float(luttinger_frequency((3.2 if rid == 6 else 1.2) * 1e16)):.1f} T")
fig.suptitle("vti-02 sdh-spot-check, D = 0 (run-5 cal), T = 1.2-1.3 K, sr1 50 uV"); fig.tight_layout(); plt.show()
