"""Run 6 onset on the Nyquist-valid record, B-window split, low-field look; model F(n) table for fan design."""
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as fm
h, e = 6.62607015e-34, 1.602176634e-19
FL = lambda n12: abs(n12) * 1e16 * h / (4 * e)

def load(rid):
    run = open_run(f"data/{rid}")
    B = run.col("magnet_field"); R = run.col("sr1_X") / (run.col("sr0_X") / -1e6)
    o = np.argsort(B); return B[o], R[o], np.median(run.col("sr0_X") / -1e6)

def fft(B, R, lo, hi, deg=5, pad=16):
    m = (B >= lo) & (B <= hi)
    dR = R[m] - np.polyval(np.polyfit(B[m], R[m], deg), B[m])
    u = np.linspace(1 / hi, 1 / lo, 2048); x = 1 / B[m]; o = np.argsort(x)
    yi = np.interp(u, x[o], dR[o])
    s = np.abs(np.fft.rfft(yi * np.hanning(len(u)), n=pad * len(u))); f = np.fft.rfftfreq(pad * len(u), u[1] - u[0])
    return f, s

def peaks(f, s, fmin=2, k=6):
    pk, _ = find_peaks(s, prominence=0.05 * s[f > fmin].max()); pk = [p for p in pk if f[p] > fmin]
    pk = sorted(pk, key=lambda p: -s[p])[:k]; ref = max(s[p] for p in pk)
    return ", ".join(f"{f[p]:.1f}({s[p]/ref:.2f})" for p in sorted(pk))

B, R, Ib = load(6)
print("=== run 6 onset, record restricted to the 10 mT segment (B >= 1.0 T) ===")
on = sdh_onset(R, B, b_lo=1.0, b_hi=7.3, r_full_scale=50e-6 / Ib); print(on.summary())
print("=== run 6 onset, B >= 0.85 (50 mT Nyquist-valid for F <= 7.2 T only) ===")
try:
    on2 = sdh_onset(R, B, b_lo=0.85, b_hi=7.3, r_full_scale=50e-6 / Ib); print(on2.summary())
except Exception as ex: print(type(ex).__name__, ex)
print("\n=== run 6 B-window split / stability (bg deg 5 in B) ===")
for lo, hi in [(1.0, 7.3), (1.4, 7.3), (1.0, 3.0), (3.0, 7.3), (1.4, 4.0), (2.0, 7.3), (1.4, 5.5)]:
    for deg in (4, 5, 7):
        f, s = fft(B, R, lo, hi, deg)
        print(f"  [{lo:.1f},{hi:.1f}] deg{deg} dF={1/(1/lo-1/hi):.2f}: {peaks(f, s)}")

print("\n=== model F(n) table, electron side, u_D = 0 ===")
print("  n12   F_L    ABAB_light  ABAB_heavy  ratio  light_frac  m*_l  m*_h   ABCA  m*_ABCA")
for n12 in [1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.24, 3.67]:
    ab = [f for f, k in fm.abab_fs(n12 * 1e16)[1]]; ms = [m for f, m in fm.abab_mstar(n12 * 1e16)]
    ac = fm.abca_fs(n12 * 1e16)[4]; mac = fm.abca_mstar(n12 * 1e16)[1]
    print(f"  {n12:4.2f} {FL(n12):6.2f}   {ab[0]:6.2f}     {ab[-1]:6.2f}    {ab[-1]/ab[0]:5.2f}   {ab[0]/FL(n12):.3f}   {ms[0]:.3f} {ms[-1]:.3f}  {ac:6.2f}  {mac:.3f}  (orbits {len(ab)})")

# low-field look
fig, ax = plt.subplots(2, 1, figsize=(10, 7))
for rid, a in ((6, ax[0]), (7, ax[1])):
    Bx, Rx, _ = load(rid); m = (Bx >= 0.3) & (Bx <= 2.0)
    dR = Rx[m] - np.polyval(np.polyfit(Bx[m], Rx[m], 4), Bx[m])
    a.plot(Bx[m], dR, ".-", ms=3, lw=0.6); a.set_title(f"run {rid} low-field dR (bg4 over 0.3-2 T)"); a.set_xlabel("B (T)")
fig.tight_layout(); fig.savefig("hera_scratch/spot_lowfield.png", dpi=90)
