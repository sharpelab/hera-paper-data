"""Landau-fan design: model trajectories (ABAB vs ABCA vs trilayer ML+BL),
Nyquist / period-count / dF arithmetic, timing calibration, cost."""
import numpy as np, importlib.util

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

T4 = _load("t4", "/home/hera/measurement_env/hera/models/tetralayer_fs_count/fs_count_b0.py")
T3 = _load("t3", "/home/hera/measurement_env/hera/models/trilayer_fs_count/fs_count_b0.py")
abab_fs, abca_fs = T4.abab_fs, T4.abca_fs

h, e = 6.62607015e-34, 1.602176634e-19
FL = lambda n12: abs(n12) * 1e16 * h / (4 * e)

# ---------- 1. model trajectories over the candidate windows ----------
print("=== ABAB vs ABCA vs trilayer(ABA ML+BL) partition trajectory, electron side ===")
print("trilayer module fns:", [x for x in dir(T3) if x.endswith("_fs") or x.endswith("_mstar")])
print(f"{'n(e12)':>7} {'F_L':>7} | {'ABAB f_s':>8} {'f_b':>7} {'frac_s':>7} | {'ABA f_s':>8} {'f_b':>7} {'frac_s':>7}")
rows = []
for n12 in [1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.27]:
    n = n12 * 1e16
    _, orbs = abab_fs(n); fs = sorted(o[0] for o in orbs)
    fb, fsm = fs[-1], fs[-2]
    try:
        r3 = T3.aba_fs(n)
        orbs3 = r3[1] if isinstance(r3, tuple) else r3
        f3 = sorted((o[0] if isinstance(o,(tuple,list)) else o) for o in orbs3)
        b3, s3 = f3[-1], f3[-2]
        t3 = f"{s3:8.2f} {b3:7.2f} {s3/(s3+b3):7.3f}"
    except Exception as ex:
        t3 = f"  (trilayer failed: {type(ex).__name__})"
    print(f"{n12:7.2f} {FL(n12):7.2f} | {fsm:8.2f} {fb:7.2f} {fsm/(fsm+fb):7.3f} | {t3}")
    rows.append((n12, fsm, fb))

# ---------- 2. design arithmetic ----------
print("\n=== design candidates ===")
DINVB = 0.010          # 1/T, inherited from run 6 spot check (10 mT at 1 T); Nyquist/3 on F_L(3.27)=33.8 T
print(f"Nyquist on fastest tone F_L(3.27e12) = {FL(3.27):.1f} T -> d(1/B) <= {1/(2*FL(3.27)):.4f} (prefer {1/(3*FL(3.27)):.4f}); using {DINVB}")

def fs_model(n12):
    _, orbs = abab_fs(n12 * 1e16); f = sorted(o[0] for o in orbs); return f[-2], f[-1]

for n_lo, B_lo in [(1.5, 0.39), (1.8, 0.55), (2.0, 0.65), (2.2, 0.75)]:
    n_hi = 3.27
    f_s, f_b = fs_model(n_lo)
    span = 1/B_lo - 1/10.0
    periods = span * f_s
    dF = 1/span
    sep = FL(n_lo) - f_b                      # heavy tone vs Luttinger (ABAB vs ABCA)
    N_B = int(np.ceil(span/DINVB)) + 1
    dn_ray = 4*(e/h)*B_lo/1e16                # e12 cm^-2 ray spacing at B_lo
    N_n = int(np.ceil((n_hi-n_lo)/(dn_ray/2))) + 1
    pts = N_B*N_n
    print(f"n {n_lo}-{n_hi}e12, B {B_lo}-10 T: f_s(n_lo)={f_s:5.2f} T, periods={periods:5.2f} (>=5), "
          f"dF={dF:4.2f} T, heavy-vs-F_L sep={sep:5.2f} T (need>2dF={2*dF:4.2f}) | "
          f"N_B={N_B:3d} N_n={N_n:3d} pts={pts:6d}")

# ---------- 3. timing calibration from run 5 ----------
print("\n=== timing calibration, run 5 (gatemap, fast_delay=1.0, slow_delay=3.0, 66x63) ===")
from hera.analysis import open_run
r5 = open_run("/home/hera/measurements/zack/20260822-vti-02/data/5")
t = r5.col("time"); vbg = r5.col("k_2400_bg_volt")
nfast = 66
rowstarts = np.arange(0, len(t), nfast)
rowdur = np.diff(t[rowstarts])
print(f"rows: {len(rowstarts)}, row duration med {np.median(rowdur):.2f} s (min {rowdur.min():.2f}, max {rowdur.max():.2f})")
dt = np.diff(t); intra = dt[np.mod(np.arange(len(dt)), nfast) != nfast-1]
print(f"intra-row per-point dt: med {np.median(intra):.3f} s  -> read overhead = {np.median(intra)-1.0:.3f} s on top of fast_delay=1.0")
flyback = np.median(rowdur) - nfast*np.median(intra)
print(f"row turnaround (slow_delay + flyback + field/gate settle) = {flyback:.2f} s")
OVH = np.median(intra) - 1.0
print(f"\n=> t_pt(fan) = fast_delay + {OVH:.3f} s  (2 Keithley writes/pt vs 1 in the gatemap: add ~6 ms, in the noise)")
