"""Landau-fan design arithmetic: timing calibration from this session's runs,
Nyquist floors on both axes, dynamic range, wall-clock."""
import numpy as np
import scipy.constants as cst
from pathlib import Path
from hera.analysis import open_run, fan_grids, resistance_grids, luttinger_frequency, field_invB
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

DATA = Path(__file__).resolve().parent.parent / "data"
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

print("=" * 70)
print("1. TIMING CALIBRATION — from this session's run 5 (gatemap, 2D)")
r5 = open_run(DATA / "5")
t = np.asarray(r5.col("time"), float)
vtg = np.asarray(r5.col("k_2400_tg_volt"), float)
n_fast = 66
n_rows = len(t) // n_fast
dt = np.diff(t)
# within-row deltas: exclude every n_fast-th (the flyback/row turnaround)
idx = np.arange(len(dt))
in_row = (idx % n_fast) != (n_fast - 1)
print(f"   run 5: {len(t)} pts, {n_rows} rows x {n_fast}, wall {t[-1]-t[0]:.0f} s")
print(f"   in-row per-point dt: median {np.median(dt[in_row]):.3f} s  mean {dt[in_row].mean():.3f} s")
print(f"   row turnaround dt:   median {np.median(dt[~in_row]):.2f} s")
T_PT = float(np.median(dt[in_row]))
TURN5 = float(np.median(dt[~in_row]))

print("\n   NOTE: run 5's fast axis moved ONE gate (k_tg). The fan's fast axis is a")
print("   paired (k_tg, k_bg) n-line -> one extra Keithley write per point.")
print("   Keithley write ~6 ms/step at volt.step=5 mV (rig card).")

print("=" * 70)
print("2. SPOT-CHECK INHERITANCE (run 6, electron n=+3.2e12)")
n_max = 3.2e12          # cm^-2, the D=0 line's electron reach (TG +1.0 V limit)
F_L_max = float(luttinger_frequency(n_max * 1e4))
B_LO = 1.00             # measured: Nyquist-valid low edge of run 6; carrying tone censored there
B_HI = 10.0             # session field cap
print(f"   F_L(n_max={n_max/1e12:.2f}e12) = {F_L_max:.2f} T")
print(f"   onset: carrying tone (7.3 T) CENSORED at the record's Nyquist-valid low edge")
print(f"          -> B_lo = {B_LO:.2f} T is a valid UPPER bound on the true onset (lower bound for design)")
d_invB_nyq = 1.0 / (2 * F_L_max)
d_invB_use = 1.0 / (3 * F_L_max)
print(f"   d(1/B) Nyquist <= {d_invB_nyq:.5f} 1/T ; preferred (1/3) <= {d_invB_use:.5f} 1/T")

print("=" * 70)
print("3. B AXIS — uniform in 1/B (per-column SdH-FFT fan, landau-fan step 4)")
span_invB = 1 / B_LO - 1 / B_HI
N_B_nyq = int(np.ceil(span_invB / d_invB_use)) + 1
print(f"   1/B span {span_invB:.4f} 1/T  ->  N_B(1/3 Nyquist) = {N_B_nyq}")
for N_B in (N_B_nyq, 101, 121):
    B_vec = field_invB(B_LO, B_HI, N_B)
    d = np.diff(1 / B_vec)
    print(f"   N_B={N_B:3d}: d(1/B)={abs(np.median(d)):.5f} -> F_nyq={1/(2*abs(np.median(d))):.1f} T "
          f"({1/abs(np.median(d))/F_L_max:.2f} samples/period at F_L) ; "
          f"dB at top row = {B_vec[-1]-B_vec[-2]:.3f} T")
N_B = 101
B_vec = field_invB(B_LO, B_HI, N_B)
print(f"   -> chose N_B = {N_B}; B from {B_vec[0]:.3f} to {B_vec[-1]:.3f} T")
print(f"      resolution dF = 1/(1/B_lo - 1/B_max) = {1/span_invB:.2f} T")
print(f"      tones to separate at n_max: light 7.3, 3x harmonic 21.9, ABAB heavy ~25.9, F_L {F_L_max:.1f}")
print(f"      closest pair 21.9 vs 25.9 -> {4.0/(1/span_invB):.1f} x dF   (need >2)")

print("=" * 70)
print("4. n AXIS — ray Nyquist at the lowest B read")
g_eh = 4 * cst.e / cst.h        # m^-2 per Tesla
print(f"   g*e/h = {g_eh:.4e} m^-2/T = {g_eh/1e4/1e12:.4f}e12 cm^-2/T")
dn_ray = g_eh / 1e4 / 1e12 * B_LO      # in 1e12 cm^-2
print(f"   ray spacing at B_lo={B_LO} T: dn = {dn_ray:.4f}e12 cm^-2 ; need >=2 pts -> dn_step <= {dn_ray/2:.4f}e12")
n_hi, n_lo = 3.20, 0.80
for N_n in (51, 61, 71):
    step = (n_hi - n_lo) / (N_n - 1)
    print(f"   N_n={N_n}: n {n_lo}->{n_hi}e12, step {step:.4f}e12 -> {dn_ray/step:.2f} pts/ray "
          f"({'OK' if step <= dn_ray/2 else 'UNDER'})")
N_n = 61
ns = np.linspace(n_hi, n_lo, N_n)
Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"   -> N_n = {N_n}; V_tg {Vtgs.min():+.4f}..{Vtgs.max():+.4f} V ; V_bg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V")
print(f"      (limits TG [-0.3,+1.0], BG [-1.3,+2.0])")
print(f"      fast-axis retrace span: TG {np.ptp(Vtgs):.4f} V, BG {np.ptp(Vbgs):.4f} V")
print(f"      F_L at the fan's low-n edge: {float(luttinger_frequency(n_lo*1e12*1e4)):.2f} T")

print("=" * 70)
print("5. DYNAMIC RANGE — worst corner is low n x high B")
g5 = fan_grids(str(DATA / "5")); rg5 = resistance_grids(g5)
print("   run-5 gatemap channels:", [c for c in rg5.__dict__ if not c.startswith('_')][:6])
try:
    R5 = rg5.R["sr1"] if isinstance(rg5.R, dict) else None
except Exception:
    R5 = None
print("   run 7 (hole n=-1.2e12) max R at 10 T: 576 Ohm (fs 0.115 at 5 kOhm FS)")
print("   run 6 (elec n=+3.2e12) max R at 10 T: 523 Ohm (fs 0.104)")

print("=" * 70)
print("6. WALL CLOCK")
t_pt_fan = T_PT + 0.006 * 1  # one extra Keithley write for the paired axis
n_pts = N_B * N_n
traverse_min = (B_HI - B_LO) / 0.137
retrace_s = max(np.ptp(Vtgs), np.ptp(Vbgs)) / 0.005 * 0.006
print(f"   per-point (run-5 calibrated {T_PT:.3f} s + paired-gate write) = {t_pt_fan:.3f} s")
print(f"   grid: {N_B} x {N_n} = {n_pts} pts -> {n_pts*t_pt_fan/3600:.2f} h")
print(f"   field traverse {B_HI-B_LO:.1f} T at 0.137 T/min = {traverse_min:.0f} min = {traverse_min/60:.2f} h")
print(f"   row turnaround: retrace {retrace_s:.1f} s + slow_delay + 3 s magnet settle")
for slow_delay in (1, 3):
    turn = retrace_s + slow_delay + 3
    tot = n_pts * t_pt_fan + traverse_min * 60 + N_B * turn
    print(f"     slow_delay={slow_delay}: turnaround {turn:.1f} s/row -> total {tot/3600:.2f} h")
    print(f"       + 10%% margin (session evidence: actuals ran 5-10%% over) = {tot*1.1/3600:.2f} h")
