"""Run 8 Verify suite: B-window split (F_L-tone origin) + partition trajectory.

Two tests the investigation makes mandatory before an ABAB call:

(1) F_L-TONE ORIGIN. A pair summing to F_L is necessary, not sufficient: an ABAB
    magnetic-breakdown orbit through both pockets lands at exactly F_L and mimics
    an ABCA singleton. Discriminator: a breakdown/mixing tone STRENGTHENS with B
    relative to the fundamentals; a real pocket keeps its own Dingle envelope.
    Uniform-1/B sampling makes this readable -- splitting at the 1/B midpoint
    gives both halves EQUAL dF, so tones resolvable in one are resolvable in both.

(2) PARTITION TRAJECTORY + ADJACENT-N. Compare measured (f_lo, f_hi) against the
    ABAB-4L curves AND the trilayer ML+BL curves across density. Magnitude alone
    cannot decide; the trajectory can.
"""
import importlib.util
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.constants as cst
from scipy.signal import find_peaks

from hera.analysis import (open_run, fan_grids, resistance_grids, sdh_fft,
                           luttinger_frequency)

BASE = "C:/Users/DGG/VTI_local_data/zack/20260825-vti-02/data"
SCRATCH = "C:/Users/DGG/VTI_local_data/zack/20260825-vti-02/hera_scratch"
MODELS = "C:/Users/DGG/measurement_env/hera/models"
DN_DVTG, DN_DVBG, V_TG_CNP = 1.570e12, 1.307e12, 0.0203


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


T4 = _load("t4", MODELS + "/tetralayer_fs_count/fs_count_b0.py")
T3 = _load("t3", MODELS + "/trilayer_fs_count/fs_count_b0.py")

fg = fan_grids(open_run(f"{BASE}/8"))
def G(n): return fg.data[:, fg.cols.index(n)].reshape(fg.nrows, fg.nfast)
rg = resistance_grids(fg, channels=["sr1"])
R = np.abs(rg.R["sr1"]); B = G("magnet_field")[:, 0]
ncol = (DN_DVTG * (G("k_2400_tg_volt")[0] - V_TG_CNP)
        + DN_DVBG * G("k_2400_bg_volt")[0]) / 1e12
ib = 1.0 / B
ib_lo, ib_hi = ib.min(), ib.max()          # ib_lo = high field
mid = 0.5 * (ib_lo + ib_hi)
B_mid = 1.0 / mid
WIN = {"full": (B.min(), B.max()),
       "highB": (B_mid, B.max()),          # small 1/B
       "lowB": (B.min(), B_mid)}           # large 1/B
print(f"record: B {B.min():.3f}..{B.max():.3f} T, 1/B {ib_lo:.4f}..{ib_hi:.4f}")
for k, (a, b) in WIN.items():
    print(f"  {k:>6}: B {a:.3f}-{b:.3f} T -> d(1/B) span {1/a-1/b:.4f}, "
          f"dF = {1/(1/a-1/b):.2f} T")


def tones(tr, blo, bhi, deg=5, npk=6):
    f, sp = sdh_fft(tr[:, None], B, b_range=(blo, bhi), bg_degree=deg)
    p = sp[0]
    k = f > 2.0
    f, p = f[k], p[k]
    dF = 1.0 / (1.0 / blo - 1.0 / bhi)
    d = max(1, int(round(dF / (f[1] - f[0]))))
    pk, pr = find_peaks(p, distance=d, prominence=0.10 * np.ptp(p))
    if not len(pk):
        return np.array([]), np.array([])
    o = np.argsort(pr["prominences"])[::-1][:npk]
    return f[pk[o]], pr["prominences"][o]


def amp_at(f, a, target, tol):
    """Amplitude of the tone nearest `target` within tol, else 0."""
    if not len(f):
        return 0.0
    i = int(np.argmin(np.abs(f - target)))
    return float(a[i]) if abs(f[i] - target) <= tol else 0.0


# ---------------- (1) F_L-tone origin, per column ----------------
print()
print("=== (1) F_L-tone origin: does the sum tone strengthen with B? ===")
print("    ratio = amp(sum tone) / amp(heavy fundamental), per half")
print(f"{'n(e12)':>7} {'f_lo':>6} {'f_hi':>6} {'f_sum':>6} | {'lowB':>7} {'highB':>7} "
      f"{'high/low':>9}  verdict")
ratios = []
for j in range(fg.nfast):
    F_L = luttinger_frequency(abs(ncol[j]) * 1e16)
    f, a = tones(R[:, j], *WIN["full"])
    if len(f) < 3:
        continue
    # identify the pair that closes the Luttinger sum, and the sum tone
    best = None
    for p in range(len(f)):
        for q in range(p + 1, len(f)):
            ssum = f[p] + f[q]
            e = abs(ssum / F_L - 1.0)
            if best is None or e < best[0]:
                best = (e, min(f[p], f[q]), max(f[p], f[q]), ssum)
    e, flo, fhi, fsum = best
    if e > 0.08:
        continue
    tol = 2.5
    if amp_at(f, a, fsum, tol) == 0.0:
        continue                       # no tone at the sum -> nothing to test
    r = {}
    for w in ("lowB", "highB"):
        fw, aw = tones(R[:, j], *WIN[w])
        As = amp_at(fw, aw, fsum, tol)
        Ah = amp_at(fw, aw, fhi, tol)
        r[w] = As / Ah if Ah > 0 else np.nan
    if not np.isfinite(r["lowB"]) or not np.isfinite(r["highB"]) or r["lowB"] <= 0:
        continue
    g = r["highB"] / r["lowB"]
    ratios.append(g)
    v = "breakdown" if g > 1.3 else ("pocket" if g < 0.77 else "flat")
    print(f"{ncol[j]:>7.2f} {flo:>6.1f} {fhi:>6.1f} {fsum:>6.1f} | {r['lowB']:>7.2f} "
          f"{r['highB']:>7.2f} {g:>9.2f}  {v}")
ratios = np.array(ratios)
if len(ratios):
    nb = (ratios > 1.3).sum(); npo = (ratios < 0.77).sum()
    print(f"\n  {len(ratios)} columns testable; median high/low ratio {np.median(ratios):.2f}")
    print(f"  breakdown-like (>1.3): {nb}   pocket-like (<0.77): {npo}   "
          f"flat: {len(ratios)-nb-npo}")
    print("  breakdown-like majority => the F_L tone is an inter-block orbit, "
          "NOT an ABCA singleton")

# ---------------- (2) partition trajectory vs both model families ----------------
print()
print("=== (2) partition trajectory: measured vs ABAB-4L vs trilayer ML+BL ===")
print(f"{'n(e12)':>7} {'meas f_lo':>10} {'meas frac':>10} | {'ABAB f_lo':>10} {'frac':>7} | "
      f"{'3L f_lo':>8} {'frac':>7}")
rowsout = []
for j in range(0, fg.nfast, max(1, fg.nfast // 12)):
    n = ncol[j]
    if n <= 0:
        continue
    F_L = luttinger_frequency(n * 1e16)
    f, a = tones(R[:, j], *WIN["full"])
    if len(f) < 2:
        continue
    best = None
    for p in range(len(f)):
        for q in range(p + 1, len(f)):
            ssum = f[p] + f[q]
            e = abs(ssum / F_L - 1.0)
            if best is None or e < best[0]:
                best = (e, min(f[p], f[q]), max(f[p], f[q]), ssum)
    e, flo, fhi, fsum = best
    if e > 0.08:
        continue
    ab = [x for x, _ in T4.abab_fs(n * 1e16)[1]]
    tr = [x for x, _ in T3.aba_fs(n * 1e16)[1]]
    rowsout.append((n, flo, flo / fsum, min(ab), min(ab) / sum(ab), min(tr), min(tr) / sum(tr)))
    print(f"{n:>7.2f} {flo:>10.2f} {flo/fsum:>10.3f} | {min(ab):>10.2f} {min(ab)/sum(ab):>7.3f} | "
          f"{min(tr):>8.2f} {min(tr)/sum(tr):>7.3f}")
if rowsout:
    A = np.array(rowsout)
    dab = np.abs(A[:, 2] - A[:, 4]).mean()
    d3l = np.abs(A[:, 2] - A[:, 6]).mean()
    print(f"\n  mean |measured frac - model frac|:  ABAB-4L {dab:.3f}   trilayer {d3l:.3f}")
    print(f"  -> tracks {'ABAB-4L' if dab < d3l else 'trilayer'} by "
          f"{max(dab,d3l)/max(min(dab,d3l),1e-9):.1f}x")
    print(f"  measured partner fraction rises {A[0,2]:.3f} -> {A[-1,2]:.3f} over n "
          f"{A[0,0]:.2f} -> {A[-1,0]:.2f}; ABAB predicts {A[0,4]:.3f} -> {A[-1,4]:.3f}")
np.save(f"{SCRATCH}/fan8_verify.npy", np.array(rowsout) if rowsout else np.zeros((0, 7)))
print("\nVERIFY SUITE: done")
