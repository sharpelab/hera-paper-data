"""Landau-fan design (step 4 of tetralayer-stacking-fs-count).

Computes, from the session calibration + the measured spot check:
  - the accessible D = 0 n-window inside the committed validators
  - model F(n) / m*(n): ABAB (pair), ABCA (singleton), trilayer ABA + ABC (adjacent-N)
  - the partner-fraction trajectory (the ABAB-vs-trilayer discriminator)
  - grid Nyquist (both axes), FFT resolution dF, partner period count
  - wall-clock from this session's own measured rates
"""
import numpy as np, sys, json, importlib.util

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m
    spec.loader.exec_module(m); return m

M4 = _load("fs4", "/home/hera/measurement_env/hera/models/tetralayer_fs_count/fs_count_b0.py")
try:
    tri = _load("fs3", "/home/hera/measurement_env/hera/models/trilayer_fs_count/fs_count_b0.py")
except Exception as e:
    tri = None; print("trilayer model load failed:", e)

from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import luttinger_frequency, field_invB

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN, TG_MAX = -0.3, 1.0
BG_MIN, BG_MAX = -1.3, 2.0
CM2 = 1e16

print("=== accessible D = 0 line inside the validators ===")
for n12 in np.arange(0.0, 3.6, 0.2):
    vtg, vbg = calc_gate_voltages(n12, 0.0, **CAL)
    ok = TG_MIN <= vtg <= TG_MAX and BG_MIN <= vbg <= BG_MAX
    if not ok:
        print(f"  n = {n12:+.2f}e12 -> ({vtg:+.4f}, {vbg:+.4f})  OUT OF RANGE")
        break
n_hi = None
for n12 in np.arange(3.40, 3.0, -0.005):
    vtg, vbg = calc_gate_voltages(n12, 0.0, **CAL)
    if TG_MIN <= vtg <= TG_MAX and BG_MIN <= vbg <= BG_MAX:
        n_hi = n12; break
print(f"  n_max on the D=0 line = {n_hi:.3f}e12 -> (Vtg,Vbg) = {calc_gate_voltages(n_hi,0.0,**CAL)}")
print(f"  chosen n_max = 3.20e12 -> {calc_gate_voltages(3.2,0.0,**CAL)}  (16 mV TG margin)")

print("\n=== model F(n), electron side (4L ABAB / ABCA, 3L ABA / ABC) ===")
print(f"{'n12':>6} {'F_L':>7} | {'ABAB f1':>8} {'f2':>7} {'frac1':>6} {'f2/f1':>6} | "
      f"{'ABCA F':>7} | {'ABA f1':>7} {'f2':>7} {'frac1':>6} | {'m*_l':>6} {'m*_h':>6}")
rows = []
for n12 in [1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2]:
    nSI = n12 * CM2
    FL = float(luttinger_frequency(nSI))
    orbs = M4.abab_fs(nSI)[1]; ms = M4.abab_mstar(nSI)
    f = sorted(F for F, _ in orbs); m = [mm for _, mm in sorted(ms)]
    f1, f2 = f[0], f[-1]
    Fa, ma = M4.abca_mstar(nSI)
    tf = [np.nan, np.nan]
    if tri is not None:
        try:
            to = tri.aba_fs(nSI)[1] if hasattr(tri, "aba_fs") else None
            if to: tf = sorted(F for F, _ in to)
        except Exception:
            pass
    rows.append(dict(n12=n12, FL=FL, f1=f1, f2=f2, frac1=f1 / FL, ratio=f2 / f1,
                     abca=Fa, tri=tf, m=m))
    print(f"{n12:6.2f} {FL:7.2f} | {f1:8.2f} {f2:7.2f} {f1/FL:6.3f} {f2/f1:6.3f} | "
          f"{Fa:7.2f} | {tf[0]:7.2f} {tf[-1]:7.2f} {tf[0]/FL if tf[0]==tf[0] else float('nan'):6.3f} | "
          f"{min(m):6.4f} {max(m):6.4f}")

print("\n=== discrimination: heavy tone vs harmonics of the light tone ===")
print(f"{'n12':>6} {'ABAB f2':>8} {'3x f1':>7} {'4x f1':>7} {'|f2-3f1|':>9} {'|f2-4f1|':>9} {'F_L':>7} {'F_L-f2':>7}")
for r in rows:
    print(f"{r['n12']:6.2f} {r['f2']:8.2f} {3*r['f1']:7.2f} {4*r['f1']:7.2f} "
          f"{abs(r['f2']-3*r['f1']):9.2f} {abs(r['f2']-4*r['f1']):9.2f} {r['FL']:7.2f} {r['FL']-r['f2']:7.2f}")

# ---------------- grid design ----------------
def design(n_lo, n_hi_, B_lo, B_hi=10.0, periods=5.0, nyq=3.0, ray=3.0):
    FLmax = float(luttinger_frequency(n_hi_ * CM2))
    F_alias = FLmax * 1.15          # cover the sum/breakdown tone + margin
    span = 1 / B_lo - 1 / B_hi
    dinvB = 1.0 / (nyq * F_alias)
    N_B = int(np.ceil(span / dinvB)) + 1
    dF = 1.0 / span
    r_lo = [r for r in rows if abs(r["n12"] - n_lo) < 0.051]
    f_part = r_lo[0]["f1"] if r_lo else 0.225 * float(luttinger_frequency(n_lo * CM2))
    nper = span * f_part
    dn_ray = 4 * (1.602176634e-19 / 6.62607015e-34) * B_lo / 1e16   # 1e12 cm^-2 per ray at B_lo
    N_n = int(np.ceil(ray * (n_hi_ - n_lo) / dn_ray)) + 1
    return dict(n_lo=n_lo, n_hi=n_hi_, B_lo=B_lo, span=span, dF=dF, N_B=N_B,
                dinvB=dinvB, F_alias=F_alias, f_part=f_part, nper=nper,
                dn_ray=dn_ray, N_n=N_n)

def price(d, fast_delay=1.8, per_pt_overhead=0.15, slow_delay=3.0, settle=3.0,
          ramp_rate=0.137, flyback=0.9):
    grid = d["N_B"] * d["N_n"] * (fast_delay + per_pt_overhead)
    rowover = d["N_B"] * (settle + slow_delay + flyback)
    traverse = (10.0 - d["B_lo"]) / ramp_rate * 60.0
    tot = grid + rowover + traverse
    return dict(grid_h=grid / 3600, row_h=rowover / 3600, trav_h=traverse / 3600, total_h=tot / 3600)

print("\n=== candidate designs (B_hi = 10 T, Nyquist 3 pts/period, 3 pts/ray, >=5 partner periods at n_lo) ===")
hdr = f"{'n_lo':>5} {'B_lo':>5} {'span':>6} {'dF':>5} {'N_B':>4} {'N_n':>4} {'pts':>6} {'f_part':>6} {'nper':>5} | {'grid':>5} {'row':>5} {'trav':>5} {'TOT h':>6}"
print(hdr)
cands = [(2.4, 1.00), (2.0, 0.85), (1.8, 0.75), (1.6, 0.68), (1.4, 0.60), (1.4, 0.65), (1.6, 0.60)]
for n_lo, B_lo in cands:
    d = design(n_lo, 3.2, B_lo)
    p = price(d)
    print(f"{n_lo:5.1f} {B_lo:5.2f} {d['span']:6.3f} {d['dF']:5.2f} {d['N_B']:4d} {d['N_n']:4d} "
          f"{d['N_B']*d['N_n']:6d} {d['f_part']:6.2f} {d['nper']:5.1f} | "
          f"{p['grid_h']:5.2f} {p['row_h']:5.2f} {p['trav_h']:5.2f} {p['total_h']:6.2f}")

print("\n(F_alias = 1.15 x F_L(n_max); dF = FFT resolution; nper = partner periods at n_lo)")
