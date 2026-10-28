"""Run 6/7 careful FFT + onset read, restricted to the properly-sampled grid.

Run 6 grid: 50 mT below 1 T, 10 mT above. Below ~0.9 T the 50 mT leg
undersamples any tone above ~F_L/4, so tone claims there are alias-prone.
Restrict the frequency read to B >= 1.0 T (uniform 10 mT).
Run 7 grid: uniform 20 mT over 0.3-10 T -> Nyquist F = B^2/(2*dB):
at B = 1 T -> 25 T; at 0.5 T -> 6.25 T.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import hera.analysis as A
from hera.analysis import open_run, sdh_onset, sdh_fft, resolve_channels, current_channel

BASE = "/home/hera/measurements/zack/20260822-vti-02/data"
h, e = 6.62607015e-34, 1.602176634e-19
FL = lambda n_cm2: h / (4 * e) * abs(n_cm2) * 1e4


def load(fid):
    run = open_run(f"{BASE}/{fid}")
    ch = resolve_channels(run.meta)
    cur = current_channel(ch)
    c1 = [c for c in ch if c.cid == "sr1"][0]
    B = run.col("magnet_field")
    I = run.col(cur.col) / cur.gain
    R = (run.col(c1.col) / c1.gain) / I
    o = np.argsort(B)
    return B[o], R[o]


def nyq_f(B, dB):
    """Max unaliased frequency for a uniform-B grid at field B."""
    return B ** 2 / (2 * dB)


def peaks(f, s, fmin=2.0, fmax=60.0, nkeep=8):
    m = (f >= fmin) & (f <= fmax)
    ff, ss = f[m], s[m]
    out = []
    for i in range(1, len(ff) - 1):
        if ss[i] > ss[i - 1] and ss[i] >= ss[i + 1]:
            # parabolic refine
            d = ss[i - 1] - 2 * ss[i] + ss[i + 1]
            dx = 0.5 * (ss[i - 1] - ss[i + 1]) / d if d != 0 else 0.0
            out.append((ff[i] + dx * (ff[1] - ff[0]), ss[i]))
    out.sort(key=lambda t: -t[1])
    return out[:nkeep]


print("#" * 78)
print("# RUN 6 — electron, n = +3.20e12 cm^-2, F_L = %.2f T" % FL(3.2e12))
print("#" * 78)
B6, R6 = load(6)
print("grid: dB below 1 T = %.3f T; above = %.3f T"
      % (np.median(np.diff(B6[B6 < 1.0])), np.median(np.diff(B6[B6 > 1.0]))))
for b in (0.4, 0.6, 0.8, 1.0):
    dB = 0.05 if b < 1.0 else 0.01
    print(f"   alias-free up to F = {nyq_f(b, dB):6.1f} T at B = {b} T (dB {dB})")

print("\n-- onset on the clean (B >= 1.0 T, uniform 10 mT) record --")
m = B6 >= 1.0
on6 = sdh_onset(R6[m], B6[m], b_lo=1.0, r_full_scale=5050.0)
print(on6.summary())

print("\n-- onset on the full record (low leg included; alias-prone) --")
on6f = sdh_onset(R6, B6, b_lo=0.3, r_full_scale=5050.0)
print("onset_b = %.2f T (headline)" % on6f.onset_b)

F_L6 = FL(3.2e12)
print("\n-- FFT stability, clean record, zero-padded (nfft 8192) --")
for cut in (1.0, 1.2, 1.5, 2.0, 2.5, 3.0):
    for bg in (3, 5, 7):
        f, spec = sdh_fft(R6[:, None], B6, b_range=(cut, 10.0), bg_degree=bg,
                          nfft=8192, log=False)
        pk = peaks(f, spec[0])
        dF = 1.0 / (1.0 / cut - 1.0 / 10.0)
        print(f"  cut {cut:4.1f} bg{bg}  dF={dF:5.2f} T | "
              + "  ".join(f"{p:5.2f}T({p/F_L6:.2f}FL)" for p, _ in pk[:5]))

print("\n#" * 1 + "=" * 78)
print("# RUN 7 — hole, n = -1.20e12 cm^-2, F_L = %.2f T" % FL(1.2e12))
B7, R7 = load(7)
print("grid: dB = %.3f T uniform" % np.median(np.diff(B7)))
for b in (0.4, 0.6, 0.8, 1.0, 1.5):
    print(f"   alias-free up to F = {nyq_f(b, 0.02):6.1f} T at B = {b} T")
on7 = sdh_onset(R7, B7, b_lo=0.7, r_full_scale=5060.0)
print(on7.summary())
F_L7 = FL(1.2e12)
for cut in (0.8, 1.0, 1.5, 2.0):
    for bg in (3, 5, 7):
        f, spec = sdh_fft(R7[:, None], B7, b_range=(cut, 10.0), bg_degree=bg,
                          nfft=8192, log=False)
        pk = peaks(f, spec[0], fmin=1.5, fmax=40)
        dF = 1.0 / (1.0 / cut - 1.0 / 10.0)
        print(f"  cut {cut:4.1f} bg{bg}  dF={dF:5.2f} T | "
              + "  ".join(f"{p:5.2f}T({p/F_L7:.2f}FL)" for p, _ in pk[:5]))

# ---- figure: clean-record FFT for both, plus low-B zoom of run 6 raw
fig, ax = plt.subplots(2, 2, figsize=(13, 8))
f, spec = sdh_fft(R6[:, None], B6, b_range=(1.2, 10.0), bg_degree=5, nfft=8192, log=False)
ax[0, 0].plot(f, spec[0])
for lbl, v, c in (("F_L", F_L6, "k"), ("ABAB heavy 25.8", 25.78, "r"), ("ABAB light 7.31", 7.31, "b")):
    ax[0, 0].axvline(v, ls="--", color=c, lw=1, label=lbl)
ax[0, 0].set_xlim(0, 60); ax[0, 0].legend(fontsize=7)
ax[0, 0].set_title("run 6 FFT, B 1.2-10 T, bg5"); ax[0, 0].set_xlabel("F (T)")

mm = B6 <= 2.5
p = np.polyfit(B6[mm], R6[mm], 5)
ax[0, 1].plot(B6[mm], R6[mm] - np.polyval(p, B6[mm]), ".-", ms=2, lw=0.6)
ax[0, 1].axvline(1.0, color="r", ls=":")
ax[0, 1].set_title("run 6 low-B zoom, bg-subtracted (red = 10 mT grid starts)")
ax[0, 1].set_xlabel("B (T)")

f7, spec7 = sdh_fft(R7[:, None], B7, b_range=(1.0, 10.0), bg_degree=5, nfft=8192, log=False)
ax[1, 0].plot(f7, spec7[0])
for lbl, v, c in (("F_L", F_L7, "k"), ("ABAB 6.54", 6.54, "r"), ("ABAB 5.86", 5.86, "b")):
    ax[1, 0].axvline(v, ls="--", color=c, lw=1, label=lbl)
ax[1, 0].set_xlim(0, 40); ax[1, 0].legend(fontsize=7)
ax[1, 0].set_title("run 7 FFT, B 1.0-10 T, bg5"); ax[1, 0].set_xlabel("F (T)")

mm7 = B7 <= 3.0
p7 = np.polyfit(B7[mm7], R7[mm7], 5)
ax[1, 1].plot(B7[mm7], R7[mm7] - np.polyval(p7, B7[mm7]), ".-", ms=2, lw=0.6)
ax[1, 1].set_title("run 7 low-B zoom, bg-subtracted"); ax[1, 1].set_xlabel("B (T)")
plt.tight_layout()
plt.savefig("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot67_fine.png", dpi=110)
print("saved spot67_fine.png")
