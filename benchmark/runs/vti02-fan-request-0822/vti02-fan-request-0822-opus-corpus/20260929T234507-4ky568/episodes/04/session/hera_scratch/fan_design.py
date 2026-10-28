"""Landau-fan design arithmetic (electron side, D = 0). Prices the grid from
this session's own measured timing constants (runs 5, 6)."""
import sys
import numpy as np
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M
from hera.analysis import field_invB
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

h, e = 6.62607015e-34, 1.602176634e-19
FL = lambda n12: h / (4 * e) * abs(n12) * 1e16

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN, TG_MAX, BG_MIN, BG_MAX = -0.3, 1.0, -1.3, 2.0

# ---- measured timing constants, this session -------------------------------
T_PT_OVERHEAD = 0.098      # run 5: 1.098 s/pt at fast_delay 1.0 (same fp set)
RAMP_T_PER_MIN = 0.137     # T/min, fixed driver rate
MAG_SETTLE = 3.0           # s, driver settle_s (run 6: dt = dB/rate + 3 s)
GATE_STEP = 5e-3           # V, Keithley volt.step
GATE_WRITE = 6e-3          # s per step (rig card)

N_MIN, N_MAX = 2.0, 3.2    # 1e12 cm^-2
B_LO, B_HI = 0.7, 10.0
TAU = 0.3
FAST_DELAY = 6 * TAU       # 1.8 s -- recipe step 7, per-column SdH-FFT fan
SLOW_DELAY = 3.0           # 10 tau after the row-start gate flyback

print("=== model F(n), electron side, over the fan window ===")
print(" n     F_L    ABAB light  ABAB heavy  ratio   ABCA    f_hv/F_L")
for n in np.arange(N_MIN, N_MAX + 1e-9, 0.2):
    Ef, orbs = M.abab_fs(n * 1e16)
    f1, f2 = sorted(f for f, k in orbs)
    Fa, ma = M.abca_mstar(n * 1e16)
    print(f"{n:+4.1f} {FL(n):7.2f}  {f1:8.2f}  {f2:9.2f}  {f2/f1:6.2f}  {Fa:7.2f}  {f2/FL(n):6.3f}")

FLmax = FL(N_MAX)
print(f"\nF_L(n_max) = {FLmax:.2f} T")

# ---- B grid ---------------------------------------------------------------
# Delta(1/B): Nyquist on F_L is 1/(2 F_L); the run-6 spectrum carries real
# harmonic content of the 29.4 T tone out to 3f ~ 88 T, so pick f_Nyq = 2 F_L
# (= 66.2 T): 2f (58.8 T) lands in band, 3f (88.2 T) aliases to 45 T, clear of
# every fundamental.
dinvB = 0.00746
print(f"Delta(1/B) = {dinvB} 1/T -> f_Nyq = {1/(2*dinvB):.1f} T = {1/(2*dinvB)/FLmax:.2f} F_L")
print(f"   Nyquist floor 1/(2F_L) = {1/(2*FLmax):.5f};  prefer-1/3 {1/(3*FLmax):.5f}")
span = 1 / B_LO - 1 / B_HI
N_B = int(round(span / dinvB)) + 1
B_vec = field_invB(B_LO, B_HI, N_B)
print(f"N_B = {N_B} rows, B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, "
      f"d(1/B) = {np.median(-np.diff(1/B_vec)):.5f}")
print(f"   row dB: min {np.min(np.diff(B_vec))*1e3:.1f} mT, max {np.max(np.diff(B_vec)):.3f} T")
print(f"   dF = 1/(1/B_lo - 1/B_hi) = {1/span:.2f} T")

# ---- n grid: ray-Nyquist at B_lo ------------------------------------------
dn_ray = 4 * e / h * B_LO / 1e16   # 1e12 cm^-2 per LL ray at B_lo
print(f"\nLL ray spacing at B_lo: dn = {dn_ray:.4f}e12 cm^-2; Nyquist floor dn_grid <= {dn_ray/2:.4f}e12")
N_n = int(np.ceil((N_MAX - N_MIN) / (dn_ray / 2))) + 1
print(f"   ray-Nyquist floor N_n = {N_n}")
N_n = 37
ns = np.linspace(N_MIN, N_MAX, N_n)
print(f"   using N_n = {N_n}, dn = {ns[1]-ns[0]:.4f}e12 (>=2 pts/ray: "
      f"{dn_ray/(ns[1]-ns[0]):.2f})")

Vtgs, Vbgs = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"],
                                CAL["n_offset"], CAL["D_offset"])
print(f"   Vtg {Vtgs.min():+.4f} .. {Vtgs.max():+.4f} (limit {TG_MIN}..{TG_MAX}); "
      f"headroom {TG_MAX - Vtgs.max():+.4f} V")
print(f"   Vbg {Vbgs.min():+.4f} .. {Vbgs.max():+.4f} (limit {BG_MIN}..{BG_MAX})")
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX
nD = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"   roundtrip: n {np.min(nD[0]):+.3f}..{np.max(nD[0]):+.3f}, |D| max {np.max(np.abs(nD[1])):.2e}")

# ---- periods / resolvability per column -----------------------------------
print("\n=== per-column resolvability (B 1.0-10 T, dF = %.2f T) ===" % (1 / span))
print("  n      f_light  periods   f_heavy  F_L-f_hv  (need >=5 periods, gap >= 2 dF)")
for n in np.arange(N_MIN, N_MAX + 1e-9, 0.2):
    Ef, orbs = M.abab_fs(n * 1e16)
    f1, f2 = sorted(f for f, k in orbs)
    print(f"{n:+5.1f}  {f1:7.2f}  {span*f1:7.2f}   {f2:7.2f}  {FL(n)-f2:8.2f}"
          + ("   OK" if span * f1 >= 5 and FL(n) - f2 >= 2 / span else "   partner short" if span * f1 < 5 else ""))

# ---- cost -----------------------------------------------------------------
flyback = (np.ptp(Vtgs) / GATE_STEP + np.ptp(Vbgs) / GATE_STEP) * GATE_WRITE
t_pt = FAST_DELAY + T_PT_OVERHEAD
traverse = (B_vec[-1] - B_vec[0]) / RAMP_T_PER_MIN * 60
per_row_fixed = MAG_SETTLE + flyback + SLOW_DELAY
row_meas = N_n * t_pt
total = traverse + N_B * (per_row_fixed + row_meas)
print(f"\n=== cost ===")
print(f"  t_pt         = {t_pt:.2f} s  (fast_delay {FAST_DELAY:.1f} = 7tau + {T_PT_OVERHEAD} measured)")
print(f"  gate flyback = {flyback:.2f} s/row")
print(f"  row fixed    = {per_row_fixed:.2f} s (mag settle + flyback + slow_delay)")
print(f"  row meas     = {row_meas:.1f} s")
print(f"  traverse     = {traverse/60:.1f} min (sum of row ramps, {B_vec[-1]-B_vec[0]:.1f} T at {RAMP_T_PER_MIN} T/min)")
print(f"  TOTAL        = {total/3600:.2f} h   ({N_B} x {N_n} = {N_B*N_n} points)")
print(f"  +10% (session evidence: actuals run 5-10% over) = {total*1.10/3600:.2f} h")

# ---- dynamic range --------------------------------------------------------
print("\n=== dynamic range (fixed sensitivity, worst corner = n_min x B_max) ===")
print("  run 6 (n=+3.2): R(0) = 52 Ohm, R(10 T) = 530 Ohm -> MR x10")
print("  run 7 (n=-1.2): R(0) = 148 Ohm, R(10 T) = 587 Ohm -> MR x4")
R0_nmin = 52 * (3.2 / N_MIN)
print(f"  n = {N_MIN}: R(0) ~ {R0_nmin:.0f} Ohm (1/n scaling from run 6); "
      f"x12 MR -> R(10 T) ~ {R0_nmin*12:.0f} Ohm")
for sens in (20e-6, 50e-6):
    print(f"  sens {sens*1e6:.0f} uV -> FS {sens/10e-9:.0f} Ohm; worst corner = "
          f"{R0_nmin*12/(sens/10e-9)*100:.0f}% FS; n_max low-B point "
          f"{52/(sens/10e-9)*100:.1f}% FS")

# ---- B-window split halves ------------------------------------------------
mid = 0.5 * (1 / B_LO + 1 / B_HI)
print(f"\nB-window split (Verify): 1/B midpoint {mid:.3f} -> B = {1/mid:.2f} T; "
      f"low half {B_LO}-{1/mid:.2f} T, high half {1/mid:.2f}-{B_HI} T "
      f"({N_B//2} rows each, dF = {1/(0.5*span):.2f} T per half)")
