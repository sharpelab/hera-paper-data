"""Spot checks runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12): raw MR, onset, FFT vs F_L."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

here = Path(__file__).resolve().parent
dd = here.parent / "data"

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
SPOT = {6: ("electron", +3.2), 7: ("hole", -1.2)}

fig, axes = plt.subplots(2, 3, figsize=(16, 8))
out = {}
for k, rid in enumerate([6, 7]):
    r = open_run(dd / str(rid))
    print("=" * 70)
    print(f"run {rid}", summarize_run(r))
    print("cols:", r.cols)
    B = r.col("magnet_field")
    Vx = r.col("sr1_X")            # gain 1
    I = r.col("sr0_X") / -1e6      # transimpedance gain
    T = r.col("T_sample")
    itg, ibg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    R = Vx / I
    o = np.argsort(B)
    B, R, Vx, I, T = B[o], R[o], Vx[o], I[o], T[o]
    side, n12 = SPOT[rid]
    FL = luttinger_frequency(n12 * 1e16) if abs(n12) > 1 else None
    print(f"N={len(B)} B {B.min():.3f}..{B.max():.3f} T; R {R.min():.1f}..{R.max():.1f} Ohm; "
          f"I {np.median(I)*1e9:.3f} nA (ptp {np.ptp(I)*1e9:.3f}); T {T.min():.3f}-{T.max():.3f} K; "
          f"|I_tg|max {np.abs(itg).max():.2e} |I_bg|max {np.abs(ibg).max():.2e}")
    print(f"F_L({n12:+.2f}e12) = {float(np.atleast_1d(FL)[0]):.2f} T")
    print(f"sr1_X: {Vx.min()*1e6:.2f}..{Vx.max()*1e6:.2f} uV (FS 50 uV -> {100*np.abs(Vx).max()/50e-6:.1f}% of FS)")

    ax = axes[k, 0]
    ax.plot(B, R, lw=0.7)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    ax.set_title(f"run {rid} raw — {side}, n={n12:+.2f}e12, D=0")

    # onset (r_full_scale = sens/I for soft-clip truncation)
    r_fs = 50e-6 / np.median(np.abs(I))
    try:
        on = sdh_onset(R, B, b_lo=0.3, r_full_scale=r_fs)
        print(on.summary())
        out[rid] = dict(onset_b=on.onset_b, onset_freq=on.onset_freq, clip_high_b=on.clip_high_b,
                        tones=[dict(freq=t.freq, onset_b=t.onset_b, snr_max=float(np.nanmax(t.snr)),
                                    dF=t.delta_f(on.clip_high_b), censored=bool(t.censored),
                                    marginal=bool(t.marginal),
                                    harmonic_of=t.harmonic_of) for t in on.tones],
                        untracked=[(float(f), s) for f, s in on.untracked])
        ax2 = axes[k, 2]
        for t in on.tones:
            ax2.plot(t.b_centers, t.snr, ".-", ms=3, label=f"{t.freq:.1f} T")
        ax2.axhline(5, color="k", ls=":")
        ax2.set_xlabel("B window center (T)"); ax2.set_ylabel("SNR"); ax2.set_yscale("log")
        ax2.legend(fontsize=7); ax2.set_title(f"run {rid} per-tone SNR vs B (onset {on.onset_b:.2f} T)")
    except SdhOnsetError as e:
        print(f"SdhOnsetError: {e}")
        out[rid] = dict(error=str(e))

    # FFT over a few cutoffs
    ax3 = axes[k, 1]
    for cut in (1.0, 1.5, 2.0, 3.0):
        if cut >= B.max() - 0.5:
            continue
        f, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=5, nfft=2048, log=False)
        s = spec[0] / spec[0].max()
        ax3.plot(f, s, lw=0.9, label=f"B {cut}-{B.max():.0f} T")
        pk = f[1:-1][(s[1:-1] > s[:-2]) & (s[1:-1] > s[2:]) & (s[1:-1] > 0.08)]
        print(f"  FFT cutoff {cut}: peaks (T) {np.round(pk, 2)[:10]}")
    if FL is not None:
        ax3.axvline(float(np.atleast_1d(FL)[0]), color="r", ls="--", label="F_L")
    ax3.set_xlim(0, 60); ax3.set_xlabel("F (T)"); ax3.set_ylabel("|FFT| (norm)")
    ax3.legend(fontsize=7); ax3.set_title(f"run {rid} 1/B FFT")

fig.tight_layout()
fig.savefig(here / "spot_runs67.png", dpi=110)
json.dump(out, open(here / "spot_onset.json", "w"), indent=1, default=float)
print("saved", here / "spot_runs67.png")
