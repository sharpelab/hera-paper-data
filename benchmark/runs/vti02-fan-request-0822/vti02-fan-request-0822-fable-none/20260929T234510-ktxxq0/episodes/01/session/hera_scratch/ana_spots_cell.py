# Runs 6 + 7 — SdH spot checks (raw first, then tones)
from hera.analysis import sdh_onset, SdhOnsetError

R_FS_SPOT = 50e-6 / 10e-9   # sr1 50 uV at 10 nA -> 5 kOhm full scale
onsets = {}
fig, axes = plt.subplots(2, 2, figsize=(13, 8))
for k, (rid, side, n12) in enumerate([(6, "electron", +3.2), (7, "hole", -1.2)]):
    r = run(rid)
    B = r.col("magnet_field")
    I = r.col("sr0_X") / -1e6                 # measured drain current, A
    R = np.abs(r.col("sr1_X") / I)            # 4-probe Rxx (sr1 gain 1)
    order = np.argsort(B)
    B, R = B[order], R[order]
    F_L = luttinger_frequency(n12 * 1e16)     # full-density Onsager freq, T
    print(f"\n=== run {rid} ({side}, n = {n12:+.2f}e12, F_L = {F_L:.1f} T) === "
          f"rows {r.rows}, B {B.min():.2f}-{B.max():.2f} T, R {R.min():.1f}-{R.max():.1f} Ohm")
    try:
        on = sdh_onset(R, B, r_full_scale=R_FS_SPOT)
        print(on.summary())
        onsets[rid] = on
    except SdhOnsetError as e:
        print(f"sdh_onset FAILED: {e}")
        on = None
    # FFT in 1/B over the 3-10 T window (dF = 1/(1/3 - 1/10) = 4.3 T -- spot resolution)
    freqs, spec = sdh_fft(R[:, None], B, b_range=(3.0, B.max()), nfft=2048, log=False)
    axes[k, 0].plot(B, R, lw=0.6)
    axes[k, 0].set_xlabel("B (T)"); axes[k, 0].set_ylabel("Rxx (Ohm)")
    axes[k, 0].set_title(f"run {rid} {side}: n = {n12:+.2f}e12, D = 0 — raw Rxx(B)")
    axes[k, 1].plot(freqs, spec[0], lw=0.8)
    axes[k, 1].axvline(F_L, color="r", ls="--", lw=1, label=f"F_L = {F_L:.1f} T")
    if on is not None:
        for t in on.tones:
            axes[k, 1].axvline(t.freq, color="0.6" if (t.marginal or t.harmonic_of) else "g", ls=":", lw=1)
    axes[k, 1].set_xlim(0, 1.6 * F_L)
    axes[k, 1].set_xlabel("F (T)"); axes[k, 1].set_ylabel("FFT mag (3-10 T window)")
    axes[k, 1].legend(fontsize=8); axes[k, 1].set_title("FFT in 1/B (green = fundamental, grey = harmonic/marginal)")
plt.tight_layout(); plt.show()
