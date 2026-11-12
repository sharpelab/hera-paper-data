"""Landau-fan design arithmetic (landau-fan / landau-fan-vti step 1) + model F(n)."""
import sys, importlib.util
import numpy as np
from hera.analysis import field_invB, luttinger_frequency
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN, TG_MAX = -0.3, 1.0
BG_MIN, BG_MAX = -1.3, 2.0

# ---------------- levers ----------------
N_HI, N_LO = 3.2, 0.8          # 1e12 cm^-2, electron side
B_LO, B_MAX = 1.0, 10.0        # T
TAU = 0.3                      # s, sr1 (24 dB/oct)
FAST_DELAY = 6 * TAU           # per-column-FFT fan -> 6 tau (base recipe step 7)
PT_OVERHEAD = 0.098            # s, measured: run 5 within-row 1.098 s at fast_delay 1.0
SLOW_DELAY = 3.0
RAMP = 0.137                   # T/min

FL_hi = float(luttinger_frequency(N_HI * 1e12 * 1e4))
FL_lo = float(luttinger_frequency(N_LO * 1e12 * 1e4))
print(f"F_L({N_HI}e12) = {FL_hi:.2f} T ; F_L({N_LO}e12) = {FL_lo:.2f} T")

# --- B axis: Nyquist. Plain F_L needs d(1/B) <= 1/(2 F_L); the observed harmonic
#     comb (run 6: 2x..18x of 7.3 T, i.e. real content to ~130 T) forces finer.
d_inv_FL = 1 / (2 * FL_hi)
D_INV = 0.0075                 # chosen: Nyquist = 66.7 T ~ 2 F_L
print(f"d(1/B): Nyquist-on-F_L {d_inv_FL:.4f}, prefer-1/3 {1/(3*FL_hi):.4f}, CHOSEN {D_INV:.4f} "
      f"-> Nyquist {1/(2*D_INV):.1f} T = {1/(2*D_INV)/FL_hi:.2f} F_L")
span_inv = 1 / B_LO - 1 / B_MAX
N_B = int(np.ceil(span_inv / D_INV)) + 1
B_vec = field_invB(B_LO, B_MAX, N_B)
d_inv_act = np.abs(np.diff(1 / B_vec)).max()
print(f"N_B = {N_B} rows, actual max d(1/B) = {d_inv_act:.5f} -> Nyquist {1/(2*d_inv_act):.1f} T")
dF = 1 / (1 / B_LO - 1 / B_MAX)
print(f"dF (record resolution) = {dF:.2f} T ; 2*dF = {2*dF:.2f} T")

# --- n axis: ray Nyquist at B_LO
e, h = 1.602176634e-19, 6.62607015e-34
dn_ray = 4 * e / h * B_LO * 1e-4 / 1e12      # 1e12 cm^-2 per LL ray at B_LO
print(f"ray spacing at {B_LO} T: {dn_ray:.4f}e12 cm^-2 ; >=2 pts/ray -> step <= {dn_ray/2:.4f}e12")
N_N = 61
ns = np.linspace(N_HI, N_LO, N_N)
step_n = abs(ns[1] - ns[0])
print(f"N_n = {N_N}, step {step_n:.4f}e12 -> {dn_ray/step_n:.2f} pts/ray at {B_LO} T  "
      f"({dn_ray/step_n >= 2 and 'PASS' or 'FAIL'})")

Vtgs, Vbgs = calc_gate_voltages(ns, 0.0 * ns, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"V_tg {Vtgs.min():+.4f} .. {Vtgs.max():+.4f} (limits {TG_MIN},{TG_MAX})  "
      f"V_bg {Vbgs.min():+.4f} .. {Vbgs.max():+.4f} (limits {BG_MIN},{BG_MAX})")
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX
print("roundtrip at ends:", calc_nD(Vtgs[0], Vbgs[0], CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]),
      calc_nD(Vtgs[-1], Vbgs[-1], CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]))

# --- cost
t_pt = FAST_DELAY + PT_OVERHEAD
traverse = (B_MAX - B_LO) / RAMP * 60
flyback = (abs(Vtgs[-1] - Vtgs[0]) / 0.005) * 0.006       # TG 5 mV step, 6 ms/write
grid = N_B * N_N * t_pt
turn = N_B * (SLOW_DELAY + flyback + 3.0)                  # slow_delay + gate flyback + magnet settle_s
tot = traverse + grid + turn
print(f"\nper-point {t_pt:.3f} s (fast_delay {FAST_DELAY:.2f} = 6 tau + {PT_OVERHEAD} measured overhead)")
print(f"traverse {traverse/3600:.2f} h | grid {grid/3600:.2f} h ({N_B*N_N} pts) | turnaround {turn/3600:.2f} h "
      f"(flyback {flyback:.2f} s/row)")
print(f"TOTAL {tot/3600:.2f} h  (+10% honesty margin -> {tot*1.10/3600:.2f} h)")

# --- forward model F(n) at the fan endpoints
spec = importlib.util.spec_from_file_location(
    "fs", "/home/hera/measurement_env/hera/models/tetralayer_fs_count/fs_count_b0.py")
fs = importlib.util.module_from_spec(spec); spec.loader.exec_module(fs)
print("\n n[1e12]   F_L     ABAB (light, heavy)        ABCA      ABAB m*")
for n in (0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2):
    FL = float(luttinger_frequency(n * 1e12 * 1e4))
    try:
        _, orbs = fs.abab_fs(n)
        ab = ", ".join(f"{F:6.2f}" for F, _ in orbs)
        ms = ", ".join(f"{m:.3f}" for _, m in fs.abab_mstar(n))
    except Exception as ex:
        ab, ms = f"<{ex}>", ""
    try:
        r = fs.abca_fs(n); Fc = r[-1]
    except Exception as ex:
        Fc = float('nan')
    print(f"  {n:4.1f}  {FL:6.2f}   [{ab}]   {Fc:6.2f}   [{ms}]")
