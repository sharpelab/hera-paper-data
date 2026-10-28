"""Runs 6 + 7 — SdH spot checks at D = 0 (sdh-spot-check): raw R(B) first, then onset + 1/B FFT vs F_L and the model."""
import warnings
from hera.analysis import sdh_onset

# Model reference (hera/models/tetralayer_fs_count/fs_count_b0.py, u_D = 0, run from hera_scratch/): F in T
MODEL = {+3.2: dict(ABAB=(7.31, 25.78), ABCA=33.09), -1.2: dict(ABAB=(5.86, 6.54), ABCA=12.41)}
SPOTS = [(6, +3.2, 1.0), (7, -1.2, 0.3)]    # (run, n [1e12 cm^-2], lowest well-sampled B: run 6 is 50 mT-coarse below 1 T)
I_FS = 50e-6                                 # sr1 sensitivity both runs (5 kOhm FS at 10 nA)

fig, ax = plt.subplots(2, 2, figsize=(12, 7.5))
for k, (rid, n12, b_ok) in enumerate(SPOTS):
    r = run(rid)
    B = r.col("magnet_field"); I = r.col("sr0_X") / -1e6; R = r.col("sr1_X") / I   # device-card channel arithmetic
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    FL = float(luttinger_frequency(n12 * 1e16))
    # raw first
    ax[0, k].plot(B, R, lw=0.7)
    ax[0, k].set(xlabel="B (T)", ylabel="R = V_sr1 / I_sr0 (Ohm)", title=f"run {rid} raw: n = {n12:+.1f}e12, D = 0")
    # onset (well-sampled record only) + FFT
    m = B >= b_ok
    with warnings.catch_warnings(record=True) as wl:
        warnings.simplefilter("always")
        on = sdh_onset(R[m], B[m], b_lo=b_ok, r_full_scale=I_FS / np.median(I))
    print(f"--- run {rid}  n = {n12:+.1f}e12  F_L = {FL:.1f} T  (model ABAB {MODEL[n12]['ABAB']}, ABCA {MODEL[n12]['ABCA']})")
    print(on.summary())
    for w in wl:
        print("   warn:", str(w.message)[:160])
    for lo in ((1.3, 2.0) if n12 > 0 else (0.7, 1.5)):
        f, s = sdh_fft(R[:, None], B, b_range=(lo, B.max()), bg_degree=5, nfft=4096)
        sp = s[0] / s[0][f > 2].max()
        ax[1, k].plot(f, sp, lw=0.8, label=f"B = {lo}-10 T")
    ax[1, k].axvline(FL, color="k", ls="--", lw=1, label=f"F_L (scale 1) {FL:.1f} T")
    for fm in MODEL[n12]["ABAB"]:
        ax[1, k].axvline(fm, color="r", ls=":", lw=1)
    ax[1, k].set(xlim=(0, 2.2 * FL if n12 > 0 else 3 * FL), ylim=(0, 1.1), xlabel="F (T)",
                 title="FFT in 1/B (deg-5 B-space bg); red: ABAB model pair")
    ax[1, k].legend(fontsize=7)
fig.tight_layout()
plt.show()
