"""SdH spot-check analysis: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12).
Raw traces, per-tone onsets (sdh_onset), FFT in 1/B (sdh_fft), tone frequencies
vs the full-density Onsager frequency F_L = |n| h / 4e."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency

DATA = Path(__file__).resolve().parent.parent / "data"
R_FS = 50e-6 / 10e-9   # 5 kOhm full scale (sr1 50 uV, 10 nA)

RUNS = {6: ("electron", +3.2e12 * 1e4), 7: ("hole", -1.2e12 * 1e4)}  # n in m^-2

fig, axes = plt.subplots(2, 2, figsize=(13, 8))
for k, (rid, (side, n_si)) in enumerate(RUNS.items()):
    r = open_run(DATA / str(rid))
    B = r.col("magnet_field")
    I = r.col("sr0_X") / -1e6          # measured drain current, A
    R = np.abs(r.col("sr1_X") / I)     # 4-probe Rxx, Ohm (sr1 gain 1)
    order = np.argsort(B)
    B, R = B[order], R[order]
    F_L = luttinger_frequency(n_si)
    print(f"\n=== run {rid} ({side}, n = {n_si*1e-16:+.2f}e12 cm^-2, F_L = {F_L:.1f} T) ===")
    print(f"rows {r.rows}, B {B.min():.2f}..{B.max():.2f} T, R {R.min():.1f}..{R.max():.1f} Ohm, "
          f"I {np.abs(I).min()*1e9:.2f}..{np.abs(I).max()*1e9:.2f} nA")
    try:
        on = sdh_onset(R, B, r_full_scale=R_FS)
        print(on.summary())
        tones = [(t.freq, t.contrast, t.onset_b, t.marginal, t.harmonic_of) for t in on.tones]
    except SdhOnsetError as e:
        print(f"sdh_onset FAILED: {e}")
        tones = []
    # FFT over the upper 2/3 of the record
    b_lo_fft = max(1.5, B.max() * 0.3)
    freqs, spec = sdh_fft(R[:, None], B, b_range=(b_lo_fft, B.max()), nfft=2048, log=False)
    sp = spec[0]
    axes[k, 0].plot(B, R, lw=0.6)
    axes[k, 0].set_xlabel("B (T)"); axes[k, 0].set_ylabel("Rxx (Ohm)")
    axes[k, 0].set_title(f"run {rid} {side}: n = {n_si*1e-16:+.2f}e12, raw Rxx(B)")
    axes[k, 1].plot(freqs, sp, lw=0.8)
    axes[k, 1].axvline(F_L, color="r", ls="--", lw=1, label=f"F_L = {F_L:.1f} T")
    for f0, c, ob, marg, harm in tones:
        axes[k, 1].axvline(f0, color="g" if not marg else "0.6", ls=":", lw=1)
    axes[k, 1].set_xlim(0, min(1.2 * F_L * 1.6, freqs.max()))
    axes[k, 1].set_xlabel("F (T)"); axes[k, 1].set_ylabel("FFT mag")
    axes[k, 1].legend(fontsize=8)
    axes[k, 1].set_title(f"FFT in 1/B, window {b_lo_fft:.1f}-{B.max():.1f} T")
    # tone bookkeeping vs the stacking models
    if tones:
        fsum = sum(f for f, c, ob, marg, h in tones if not marg and h is None)
        print(f"non-marginal fundamental tone sum = {fsum:.1f} T vs F_L {F_L:.1f} T ({100*fsum/F_L:.0f}%)")
plt.tight_layout()
plt.savefig(Path(__file__).parent / "spots_67.png", dpi=110)
print("\nwrote spots_67.png")
