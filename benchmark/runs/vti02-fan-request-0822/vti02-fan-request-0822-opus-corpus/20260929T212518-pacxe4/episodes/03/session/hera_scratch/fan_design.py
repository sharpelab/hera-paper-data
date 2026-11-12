"""Landau-fan design arithmetic — landau-fan(-vti) step 1 cost-floor procedure.

Inputs: run 5 calibration, run 6 (electron spot check) onset + tone set,
this session's measured timing model.
"""
import numpy as np
from hera.analysis import open_run, sdh_fft, luttinger_frequency, field_invB
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from scipy.signal import find_peaks

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN, TG_MAX = -0.3, 1.0
BG_MIN, BG_MAX = -1.3, 2.0

# ---------- 1. how far up in frequency does run 6 carry real content? ----------
run = open_run("data/6")
mc = run.meta["measurement_config"]
B = run.col("magnet_field")
R = np.abs((run.col("sr1_X") / 1.0) / (run.col("sr0_X") / mc["sr0_gain"]))
k = B > 0.05
B, R = B[k], R[k]
o = np.argsort(B); B, R = B[o], R[o]
f, s = sdh_fft(R[:, None], B, b_range=(1.0, 10.0), bg_degree=5, nfft=4096)
s = s[0]
floor = np.median(s[f > 200])
print(f"spectral floor (F > 200 T) = {floor:.3f}")
p, _ = find_peaks(s, height=4 * floor)
p = p[f[p] > 2]
print("run 6 tones above 4x floor, F < 400 T:")
for i in p[np.argsort(f[p])]:
    if f[i] < 400:
        print(f"   {f[i]:7.1f} T   amp {s[i]:.3f}  ({s[i]/floor:.0f}x floor)")
f_top = max(f[i] for i in p if f[i] < 400)
print(f"-> highest tracked content ~ {f_top:.0f} T")

# ---------- 2. aliasing table for candidate Nyquist choices ----------
TONES = [7.3, 14.8, 22.3, 29.4, 41.5, 58.3, 90.5, 118.2]
BAND = (3.0, 40.0)   # classification band: light / heavy / F_L tones + first sidebands
print("\naliasing check (alias = fold of f about k*2*f_Nyq):")
for f_nyq in (40, 50, 60, 80, 100, 125):
    d_invB = 1.0 / (2 * f_nyq)
    bad = []
    for t in TONES:
        a = abs(t - 2 * f_nyq * round(t / (2 * f_nyq)))
        if t > f_nyq and BAND[0] <= a <= BAND[1]:
            bad.append(f"{t:.0f}->{a:.1f}")
    n_rows = int(np.ceil((1 / 1.0 - 1 / 10.0) / d_invB)) + 1
    print(f"  f_Nyq {f_nyq:4d} T  d(1/B) {d_invB:.5f}  N_B {n_rows:4d}   "
          f"folds into {BAND}: {bad if bad else 'none'}")

# ---------- 3. the n-line ----------
F_L_at = lambda n12: float(luttinger_frequency(abs(n12) * 1e16))
N_LO, N_HI = 1.6, 3.2
B_LO, B_HI = 1.0, 10.0
span_invB = 1 / B_LO - 1 / B_HI
print(f"\n1/B span {span_invB:.3f} /T  ->  Rayleigh dF = {1/span_invB:.2f} T")
print("per-column expectations (tones scaled from run 6: 7.3 / 22.3 / 29.4 T at n = 3.2):")
for n12 in (1.6, 2.0, 2.4, 2.8, 3.2):
    sc = n12 / 3.2
    fl, fh, fs_ = 7.3 * sc, 22.3 * sc, 29.4 * sc
    print(f"  n {n12:.2f}e12: F_L {F_L_at(n12):5.1f} T | light {fl:5.2f} ({fl*span_invB:.1f} periods) "
          f"| heavy {fh:5.2f} | F_L-tone {fs_:5.2f} | split/dF {(fh-fl)/(1/span_invB):.1f}")

# n-axis Nyquist: LL ray spacing at B_LO
dn_ray = 4 * (1.602176634e-19 / 6.62607015e-34) * B_LO * 1e-4 / 1e12   # 1e12 cm^-2
print(f"\nLL ray spacing at B_lo = {B_LO} T: dn = {dn_ray:.4f}e12 cm^-2")
for N_n in (41, 49, 51, 61):
    dn = (N_HI - N_LO) / (N_n - 1)
    print(f"  N_n {N_n:3d}: dn {dn:.4f}e12 -> {dn_ray/dn:.2f} pts per ray spacing")

# ---------- 4. gate voltages, limits, margins ----------
N_N = 51
ns = np.linspace(N_LO, N_HI, N_N)
Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"\nn-line ({N_N} pts, n {N_LO} -> {N_HI}e12 at D = 0):")
print(f"  V_tg {Vtgs.min():+.4f} .. {Vtgs.max():+.4f} V  (limits {TG_MIN} / {TG_MAX}; "
      f"margin {TG_MAX - Vtgs.max():+.4f} / {Vtgs.min() - TG_MIN:+.4f})")
print(f"  V_bg {Vbgs.min():+.4f} .. {Vbgs.max():+.4f} V  (limits {BG_MIN} / {BG_MAX}; "
      f"margin {BG_MAX - Vbgs.max():+.4f} / {Vbgs.min() - BG_MIN:+.4f})")
print(f"  dV_tg per column {np.diff(Vtgs)[0]*1e3:.2f} mV, dV_bg {np.diff(Vbgs)[0]*1e3:.2f} mV")
print(f"  roundtrip n,D at ends: {calc_nD(Vtgs[0], Vbgs[0], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}, "
      f"{calc_nD(Vtgs[-1], Vbgs[-1], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")
assert TG_MIN <= Vtgs.min() and Vtgs.max() <= TG_MAX
assert BG_MIN <= Vbgs.min() and Vbgs.max() <= BG_MAX

# ---------- 5. dynamic range: worst corner = low n x high B ----------
g5 = open_run("data/5")
mc5 = g5.meta["measurement_config"]
vtg5, vbg5 = g5.col("k_2400_tg_volt"), g5.col("k_2400_bg_volt")
R5 = np.abs((g5.col("sr1_X") / 1.0) / (g5.col("sr0_X") / mc5["sr0_gain"]))
n5, D5 = calc_nD(vtg5, vbg5, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print("\nB = 0 resistance along the n-line (run 5 gatemap, |D| < 0.02 V/nm):")
for n12 in (1.6, 2.0, 2.4, 3.2):
    m = (np.abs(D5) < 0.02) & (np.abs(n5 - n12) < 0.06)
    if m.any():
        print(f"  n {n12:.2f}e12: R(B=0) = {np.median(R5[m]):.1f} Ohm  ({m.sum()} pts)")
r6_mr = R[np.argmin(np.abs(B - 10.0))] / R[np.argmin(np.abs(B - 0.1))]
print(f"  run 6 MR factor R(10 T)/R(0.1 T) at n = 3.2: {r6_mr:.1f}x "
      f"(R10 = {R[np.argmin(np.abs(B-10.0))]:.0f} Ohm)")
I_bias = np.median(np.abs(g5.col("sr0_X") / mc5["sr0_gain"]))
for sens in (50e-6, 100e-6):
    print(f"  sr1 {sens*1e6:.0f} uV -> full scale {sens/9.9e-9:.0f} Ohm")

# ---------- 6. wall clock, from this session's measured timing ----------
# measured: per-point = fast_delay + 0.10 s (run 5: fast_delay 1.0, median dt 1.098 s, NPLC 1)
#           magnet blocking set = ramp + 3.0 s settle (runs 6/7: 3.06-3.08 s/pt at delay 0)
#           bare ramp 0.137 T/min
READ = 0.10
SETTLE = 3.0
RAMP = 0.137
print("\nwall clock (measured timing model):")
for f_nyq in (80, 100):
    d_invB = 1.0 / (2 * f_nyq)
    N_B = int(np.ceil(span_invB / d_invB)) + 1
    Bv = field_invB(B_LO, B_HI, N_B)
    for fd in (1.8, 2.1):
        flyback = (Vtgs.max() - Vtgs.min()) / 5e-3 * 6e-3
        slow_d = 3.0
        grid = N_B * N_N * (fd + READ)
        rows = N_B * (SETTLE + flyback + slow_d)
        trav = (B_HI - B_LO) / RAMP * 60
        tot = grid + rows + trav
        print(f"  f_Nyq {f_nyq} (N_B {N_B:3d}) x N_n {N_N} @ fast_delay {fd}s: "
              f"grid {grid/3600:.2f} h + rows {rows/3600:.2f} h + traverse {trav/3600:.2f} h "
              f"= {tot/3600:.2f} h  ({tot/3600*1.08:.2f} h at +8%)")

# chosen
f_nyq = 80
d_invB = 1.0 / (2 * f_nyq)
N_B = int(np.ceil(span_invB / d_invB)) + 1
Bv = field_invB(B_LO, B_HI, N_B)
print(f"\nCHOSEN: N_B = {N_B}, d(1/B) = {d_invB:.5f} /T (f_Nyq {f_nyq} T), "
      f"B {Bv[0]:.3f} -> {Bv[-1]:.3f} T")
print(f"  dB steps: {np.diff(Bv).min()*1e3:.1f} mT (low end) .. {np.diff(Bv).max()*1e3:.0f} mT (high end)")
print(f"  d(1/B) actual: {np.diff(1/Bv).min():.6f} .. {np.diff(1/Bv).max():.6f} /T")
print(f"  total points = {N_B*N_N}")
