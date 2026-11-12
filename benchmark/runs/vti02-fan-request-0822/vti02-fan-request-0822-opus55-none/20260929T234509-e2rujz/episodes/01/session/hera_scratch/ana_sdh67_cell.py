"""Runs 6-7 — sdh-spot-check at D = 0 (run-5 cal): raw R(B) first, then sdh_onset tone table + FFT in 1/B."""
from hera.analysis import resolve_channels, sdh_onset
import warnings
spots = {6: +3.2, 7: -1.2}      # nominal n (1e12 cm^-2, prior scale)
fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for j, (rid, n12) in enumerate(spots.items()):
    r = run(rid)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs(r.col("sr1_X") / ch["sr1"].gain / I)
    o = np.argsort(B); B, R = B[o], R[o]
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    # raw first
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("|Rxx| B_1-B_2 (Ohm)")
    ax[0, j].set_title(f"run {rid} raw: n = {n12:+.1f}e12 (prior), D = 0, T {r.col('T_sample').mean():.2f} K")
    # tones
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        on = sdh_onset(R, B, b_lo=0.5, r_full_scale=50e-6 / 10e-9)
    print(f"--- run {rid}: n = {n12:+.1f}e12 (prior scale), F_L(prior) = {FL:.1f} T, R {R.min():.1f}-{R.max():.1f} Ohm")
    print(on.summary())
    f, sp = sdh_fft(R[:, None], B, b_range=(2.0, B.max()), nfft=4096, bg_degree=5, log=True)
    ax[1, j].plot(f, sp[0] / sp[0][(f > 1)].max(), lw=0.8, label="FFT log R, B 2-10 T")
    for t in on.tones:
        if not t.marginal:
            ax[1, j].axvline(t.freq, color="r" if t.harmonic_of is None else "0.6", ls="--", lw=0.8)
    ax[1, j].axvline(FL, color="k", ls=":", lw=1, label="F_L (prior density)")
    ax[1, j].set_xlim(0, 2.2 * FL); ax[1, j].set_xlabel("F (T)"); ax[1, j].legend(fontsize=7)
    ax[1, j].set_title(f"run {rid}: tones (red = fundamental, grey = flagged harmonic)")
fig.tight_layout(); plt.show()
