"""Refined spot-check read. Run 6's 0.5-10 T window is polluted by the huge
high-field structure (R 0 -> 520 Ohm above 7.5 T) that a degree-5 poly cannot
absorb; and below ~0.85 T the 50 mT grid aliases the fast tones
(d(1/B) = dB/B^2 = 0.05/0.72 = 0.069 > 1/(2*22 T)). Re-read on well-sampled,
background-tractable windows, and screen 3x-harmonic vs real heavy tone."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

I_BIAS = 1.0 / 100e6
SENS = 50e-6

def load(fid):
    r = open_run(f"data/{fid}")
    return r, r.col("magnet_field"), np.abs(r.col("sr1_X") / I_BIAS)

def peaks(f, s, fmin=2.0, fmax=None, k=6):
    sel = (f > fmin) & (f < (fmax if fmax else f.max()))
    fs, ss = f[sel], s[sel]
    idx = [i for i in range(1, len(ss) - 1) if ss[i] > ss[i-1] and ss[i] > ss[i+1]]
    idx.sort(key=lambda i: -ss[i])
    return [(fs[i], ss[i] / ss[idx[0]]) for i in idx[:k]]

# ---------- run 6, electron, windows ----------
r6, B6, R6 = load(6)
FL6 = float(luttinger_frequency(3.20e12 * 1e4))
print(f"run 6: F_L(nominal n=3.2e12) = {FL6:.2f} T")
print("  d(1/B) per step:  0.05 T grid at B=1.0 -> %.4f;  0.01 T grid at B=2 -> %.4f, at B=10 -> %.5f"
      % (0.05 / 1.0**2, 0.01 / 2**2, 0.01 / 10**2))
print("  Nyquist needs d(1/B) <= 1/(2*F). F=22 T -> %.4f; F=30 T -> %.4f" % (1/44, 1/60))
print("  => the 50 mT leg (B<1 T) aliases everything above ~7 T; use B >= 1.0 T.\n")

WINDOWS = [(1.0, 7.4, "1.0-7.4 T (below the light-pocket QL feature)"),
           (1.0, 10.0, "1.0-10.0 T (full well-sampled record)"),
           (1.5, 7.4, "1.5-7.4 T"),
           (2.0, 10.0, "2.0-10.0 T (high-B half)"),
           (1.0, 4.5, "1.0-4.5 T (low-B half)")]
fig, axes = plt.subplots(2, 3, figsize=(16, 8))
ax = axes[0, 0]
ax.plot(B6, R6, lw=0.8); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
ax.set_title("run 6 raw — electron n=+3.2e12, D=0")
ax.axvline(7.4, color="r", ls=":", lw=0.8)

ax = axes[0, 1]
for b_lo, b_hi, lab in WINDOWS:
    f, spec = sdh_fft(R6[:, None], B6, b_range=(b_lo, b_hi), bg_degree=5, log=False, nfft=4096)
    s = spec[0]
    sel = f < 45
    ax.plot(f[sel], s[sel] / s[(f > 2) & (f < 45)].max(), lw=0.9, label=lab.split(" ")[0])
    dF = 1.0 / (1.0 / b_lo - 1.0 / b_hi)
    print(f"  window {lab}: dF = {dF:.2f} T")
    for pf, pa in peaks(f, s, 2.0, 45):
        print(f"      f = {pf:7.2f} T  amp {pa:.3f}   f/F_L = {pf/FL6:.3f}")
    print()
for x, c, l in [(FL6, "k", "F_L"), (0.773 * FL6, "g", None), (0.227 * FL6, "g", None)]:
    ax.axvline(x, color=c, ls="--", lw=0.8)
ax.set_xlim(0, 45); ax.set_ylim(0, 1.3); ax.legend(fontsize=7)
ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm, f>2 T)"); ax.set_title("run 6 FFT window ladder")

# harmonic screen: is 22.06 exactly 3x 7.35?
f, spec = sdh_fft(R6[:, None], B6, b_range=(1.0, 7.4), bg_degree=5, log=False, nfft=8192)
s = spec[0]
pk = peaks(f, s, 2.0, 45, k=8)
print("run 6 (1.0-7.4 T, nfft 8192) peak table:")
f1 = pk[0][0]
for pf, pa in sorted(pk):
    print(f"   f = {pf:7.3f} T  amp {pa:.3f}  f/f1 = {pf/f1:6.3f}  f/F_L = {pf/FL6:.3f}")

ax = axes[0, 2]
m = (B6 >= 1.0) & (B6 <= 7.4)
p = np.polyfit(B6[m], R6[m], 5)
ax.plot(1 / B6[m], R6[m] - np.polyval(p, B6[m]), lw=0.9)
ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm)"); ax.set_title("run 6 bg-removed, 1.0-7.4 T")

# ---------- run 7, hole ----------
r7, B7, R7 = load(7)
FL7 = float(luttinger_frequency(1.20e12 * 1e4))
print(f"\nrun 7: F_L(nominal n=-1.2e12) = {FL7:.2f} T; grid 20 mT uniform, "
      f"d(1/B) at B=0.7 = {0.02/0.49:.4f} (Nyquist for 12.4 T needs <= {1/24.8:.4f})")
axes[1, 0].plot(B7, R7, lw=0.8); axes[1, 0].set_xlabel("B (T)"); axes[1, 0].set_ylabel("Rxx (Ohm)")
axes[1, 0].set_title("run 7 raw — hole n=-1.2e12, D=0")
ax = axes[1, 1]
for b_lo, b_hi in [(0.75, 10.0), (0.75, 6.0), (1.5, 10.0)]:
    f, spec = sdh_fft(R7[:, None], B7, b_range=(b_lo, b_hi), bg_degree=5, log=False, nfft=4096)
    s = spec[0]
    sel = f < 25
    ax.plot(f[sel], s[sel] / s[(f > 1.5) & (f < 25)].max(), lw=0.9, label=f"{b_lo}-{b_hi} T")
    print(f"  window {b_lo}-{b_hi} T: dF = {1/(1/b_lo-1/b_hi):.2f} T")
    for pf, pa in peaks(f, s, 1.5, 25):
        print(f"      f = {pf:7.2f} T  amp {pa:.3f}   f/F_L = {pf/FL7:.3f}")
    print()
ax.axvline(FL7, color="k", ls="--", lw=0.8)
ax.set_xlim(0, 25); ax.legend(fontsize=7); ax.set_xlabel("F (T)"); ax.set_title("run 7 FFT window ladder")

ax = axes[1, 2]
m = (B7 >= 0.75)
p = np.polyfit(B7[m], R7[m], 5)
ax.plot(1 / B7[m], R7[m] - np.polyval(p, B7[m]), lw=0.9)
ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm)"); ax.set_title("run 7 bg-removed, >0.75 T")

# ---------- onset on the well-sampled leg only ----------
print("\n--- sdh_onset restricted to the 10 mT leg (run 6) ---")
try:
    on = sdh_onset(R6, B6, b_lo=1.0, r_full_scale=SENS / I_BIAS)
    print(on.summary())
except SdhOnsetError as e:
    print("SdhOnsetError:", e)
print("\n--- sdh_onset run 6, full record incl. 50 mT leg, b_lo=0.35 ---")
try:
    on2 = sdh_onset(R6, B6, b_lo=0.35, b_hi=7.4, r_full_scale=SENS / I_BIAS)
    print(on2.summary())
except SdhOnsetError as e:
    print("SdhOnsetError:", e)

plt.tight_layout(); plt.savefig("hera_scratch/spot_fft2.png", dpi=110)
print("\nwrote hera_scratch/spot_fft2.png")
