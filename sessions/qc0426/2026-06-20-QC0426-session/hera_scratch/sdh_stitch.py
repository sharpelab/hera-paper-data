import sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft

# stitch hole runs: run1 (0.1-2T) + run2 (2-8T) -> full 0.1-8T per Rxx channel
F_L = float(sys.argv[1]) if len(sys.argv) > 1 else 35.2
B_FFT_LO = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
B_FFT_HI = float(sys.argv[3]) if len(sys.argv) > 3 else 7.2

def load(d):
    r = open_run(d); mc = r.meta["measurement_config"]
    B = np.asarray(r.col("magnet_field")); I = np.asarray(r.col("sr0_X")) / mc["sr0_gain"]
    out = {"B": B, "I": I}
    for ch in ["sr1", "sr2"]:
        R = np.asarray(r.col(f"{ch}_X")) / I
        sens = mc.get(f"{ch}_sens", np.inf)
        R_rail = 0.88 * sens / np.median(np.abs(I))          # mask railed (lock-in near FS)
        bad = np.abs(np.asarray(r.col(f"{ch}_X"))) > 0.88 * sens
        out[ch] = np.where(bad, np.nan, R)
    return out

a1, a2 = load("data/1"), load("data/2")
B = np.concatenate([a1["B"], a2["B"]])
order = np.argsort(B); B = B[order]
R = {ch: np.concatenate([a1[ch], a2[ch]])[order] for ch in ["sr1", "sr2"]}
print(f"stitched: {len(B)} pts, B [{B.min():.3f},{B.max():.3f}] T | FFT window [{B_FFT_LO},{B_FFT_HI}] T, F_L={F_L:.1f}")

fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for col, ch in enumerate(["sr1", "sr2"]):
    g = np.isfinite(R[ch]); Bc, Rc = B[g], R[ch][g]
    # oscillation view: subtract smooth poly background (in B) over FFT window
    sel = (Bc >= B_FFT_LO) & (Bc <= B_FFT_HI)
    Bs, Rs = Bc[sel], Rc[sel]
    bg = np.polyval(np.polyfit(Bs, Rs, 6), Bs)
    ax[0, col].plot(1 / Bs, Rs - bg, lw=0.7)
    ax[0, col].set_xlabel("1/B (1/T)"); ax[0, col].set_ylabel(f"ΔR_{ch} (Ω)")
    ax[0, col].set_title(f"{ch}  ΔRxx vs 1/B  (bg-subtracted, B {B_FFT_LO}-{B_FFT_HI}T)")
    try:
        freqs, spec = sdh_fft(Rs.reshape(-1, 1), Bs, b_range=(B_FFT_LO, B_FFT_HI), bg_degree=5)
        mag = spec[0]; m = freqs > 3
        top = sorted([(float(freqs[m][i]), float(mag[m][i])) for i in np.argsort(mag[m])[::-1][:5]])
        print(f"{ch}: peaks(T): " + ", ".join(f"{f:.1f}({a:.2f})" for f, a in sorted(top, key=lambda t:-t[1])))
        ax[1, col].plot(freqs, mag); ax[1, col].axvline(F_L, color="g", ls="--", label=f"F_L={F_L:.0f}T")
        ax[1, col].set_xlim(0, 60); ax[1, col].set_xlabel("SdH freq (T)"); ax[1, col].set_ylabel("FFT mag")
        ax[1, col].set_title(f"{ch} 1/B FFT"); ax[1, col].legend(fontsize=7)
    except Exception as e:
        print(f"{ch}: sdh_fft failed ({e})")
plt.tight_layout(); plt.savefig("hera_scratch/sdh_stitch.png", dpi=110)
print("saved hera_scratch/sdh_stitch.png")
