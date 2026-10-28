import sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft

d = sys.argv[1] if len(sys.argv) > 1 else "data/1"
F_L = float(sys.argv[2]) if len(sys.argv) > 2 else 35.2   # Tesla, the Luttinger line
r = open_run(d)
B = np.asarray(r.col("magnet_field"))
gain = r.meta["measurement_config"]["sr0_gain"]
I = np.asarray(r.col("sr0_X")) / gain                      # measured drain current
R = {ch: np.asarray(r.col(f"{ch}_X")) / I for ch in ["sr1", "sr2"]}
print(f"run {d}: {len(B)} pts, B [{B.min():.3f}, {B.max():.3f}] T, I~{np.median(I)*1e9:.1f} nA, F_L={F_L:.1f} T")

fig, axes = plt.subplots(2, 2, figsize=(13, 8))
for col, ch in enumerate(["sr1", "sr2"]):
    Rxx = R[ch]
    good = np.isfinite(Rxx) & (B > 0)
    Bc, Rc = B[good], Rxx[good]
    # onset
    try:
        on = sdh_onset(Rc, Bc, b_lo=0.1)
        onset_b = float(on.onset_b); cutoff = max(onset_b, 0.0)
        print(f"{ch}: onset_b={onset_b:.3f} T  consensus_freq={getattr(on,'consensus_freq',float('nan')):.1f} T")
    except Exception as e:
        onset_b, cutoff = 0.3, 0.3
        print(f"{ch}: sdh_onset failed ({e}); using cutoff=0.3 T")
    # FFT over [cutoff, Bmax]
    try:
        freqs, spec = sdh_fft(Rc.reshape(-1, 1), Bc, b_range=(max(cutoff, 0.12), Bc.max()), bg_degree=5)
        mag = spec[0]
        # peak pick (ignore DC band)
        m = freqs > 3
        order = np.argsort(mag[m])[::-1]
        top = [(float(freqs[m][i]), float(mag[m][i])) for i in order[:6]]
        print(f"{ch}: top FFT peaks (T): " + ", ".join(f"{f:.1f}({a:.2f})" for f, a in top))
        print(f"{ch}:   vs F_L={F_L:.1f} T  | F_L sum-check: do peaks sum to F_L?")
    except Exception as e:
        freqs = mag = None
        print(f"{ch}: sdh_fft failed ({e})")
    # plots: raw Rxx(B) and FFT
    ax = axes[0, col]; ax.plot(Bc, Rc, lw=0.6); ax.set_xlabel("B (T)"); ax.set_ylabel(f"R_{ch} (Ω)")
    ax.set_title(f"{ch} raw Rxx(B)")
    ax.axvline(onset_b, color="r", ls=":", lw=1, label=f"onset {onset_b:.2f}T"); ax.legend(fontsize=7)
    ax = axes[1, col]
    if freqs is not None:
        ax.plot(freqs, mag); ax.axvline(F_L, color="g", ls="--", label=f"F_L={F_L:.0f}T")
        ax.set_xlim(0, max(F_L * 1.6, 60)); ax.set_xlabel("SdH freq (T)"); ax.set_ylabel("FFT mag")
        ax.set_title(f"{ch} 1/B FFT"); ax.legend(fontsize=7)
plt.tight_layout(); plt.savefig("hera_scratch/sdh_hole.png", dpi=110)
print("saved hera_scratch/sdh_hole.png")
