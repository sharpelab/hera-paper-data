"""landau-fan grid design: D = 0 density line (fast, co-swept TG+BG) x B (slow, hybrid 1/B + B grid).
Prints the realized windows, validator margins, Nyquist/resolution budget and the wall-clock price."""
import numpy as np
from scipy.constants import e, h
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN, TG_MAX = -0.3, 1.0
BG_MIN, BG_MAX = -1.3, 2.0
B_CAP = 10.0

# --- fast axis: D = 0, n from the TG-limited ends of the realized window ---
ns = np.linspace(-2.0, 4.0, 60001)
Vt, Vb = calc_gate_voltages(ns, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
ok = (Vt >= TG_MIN) & (Vt <= TG_MAX) & (Vb >= BG_MIN) & (Vb <= BG_MAX)
print(f"D=0 realized n-window inside validators: {ns[ok].min():+.3f} .. {ns[ok].max():+.3f} e12 cm^-2")

N_FAST = 121
n_vec = np.linspace(-1.24, 3.24, N_FAST)
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
dn = n_vec[1] - n_vec[0]
print(f"fast: {N_FAST} pts, n {n_vec[0]:+.3f}..{n_vec[-1]:+.3f} e12, dn = {dn*1e3:.1f}e9 cm^-2")
print(f"      Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} (limits {TG_MIN}/{TG_MAX}, margin {Vtg_vec.min()-TG_MIN:+.4f}/{TG_MAX-Vtg_vec.max():+.4f} V)")
print(f"      Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} (limits {BG_MIN}/{BG_MAX}, margin {Vbg_vec.min()-BG_MIN:+.4f}/{BG_MAX-Vbg_vec.max():+.4f} V)")
nr, Dr = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"      roundtrip: max|dn| {np.abs(nr-n_vec).max():.2e} e12, max|D| {np.abs(Dr).max():.2e} V/nm")
print(f"      gate spans: TG {np.ptp(Vtg_vec):.3f} V, BG {np.ptp(Vbg_vec):.3f} V; per-step dVtg {np.diff(Vtg_vec)[0]*1e3:.1f} mV, dVbg {np.diff(Vbg_vec)[0]*1e3:.1f} mV")

# --- slow axis: apex rows (visual only) + uniform-1/B core + uniform-B high-field cap ---
B_apex = np.array([0.25, 0.50, 0.75, 1.00])
B_LO, B_MID, B_HI = 1.2, 5.0, 10.0
DINVB = 0.0118                      # target 1/B step -> Nyquist
n_int = int(np.ceil((1/B_LO - 1/B_MID) / DINVB))
B_core = 1.0 / np.linspace(1/B_LO, 1/B_MID, n_int + 1)
B_high = np.arange(B_MID + 0.25, B_HI + 1e-9, 0.25)
B_vec = np.round(np.concatenate([B_apex, B_core, B_high]), 4)
assert np.all(np.diff(B_vec) > 0) and B_vec.max() <= B_CAP
N_ROWS = len(B_vec)
invb = 1 / B_vec
d_core = np.diff(1 / B_core)
print(f"\nslow: {N_ROWS} rows = {len(B_apex)} apex + {len(B_core)} core(1/B) + {len(B_high)} high(B)")
print(f"      apex {B_apex} T (visual only, excluded from FFT window)")
print(f"      core {B_core[0]:.3f}..{B_core[-1]:.3f} T, d(1/B) = {d_core.mean():.5f} -> F_Nyq = {1/(2*d_core.max()):.1f} T")
print(f"      high {B_high[0]:.2f}..{B_high[-1]:.2f} T at 0.25 T; max d(1/B) = {np.abs(np.diff(1/B_high)).max():.5f} -> F_Nyq = {1/(2*np.abs(np.diff(1/B_high)).max()):.1f} T")
print(f"      junction core->high d(1/B) = {1/B_core[-1]-1/B_high[0]:.5f} -> F_Nyq = {1/(2*(1/B_core[-1]-1/B_high[0])):.1f} T")
dF = 1 / (1/B_LO - 1/B_HI)
print(f"      FFT window {B_LO}-{B_HI} T: dF = {dF:.2f} T  (run-6 B>3T window was 4.29 T)")

# --- what the frequencies are ---
F = lambda n12: np.abs(n12) * 1e16 * h / (4 * e)
print(f"\nfull-density Onsager F at window ends: n={n_vec[0]:+.2f} -> {F(n_vec[0]):.1f} T; n={n_vec[-1]:+.2f} -> {F(n_vec[-1]):.1f} T")
print(f"  resolvable tone splittings at dF = {dF:.2f} T; ABAB-heavy 25.6 vs ABCA 33.1 at n=3.2 is a {33.1-25.6:.1f} T split")
print(f"  4-fold LL spacing in n: dn_LL = 4eB/h = {4*e*1.2/h*1e-16:.3f}e12 @1.2T, {4*e*5/h*1e-16:.3f}e12 @5T, {4*e*10/h*1e-16:.3f}e12 @10T")
print(f"  pts per 4-fold LL on the fast axis: {4*e*1.2/h*1e-16/dn:.1f} @1.2T, {4*e*5/h*1e-16/dn:.1f} @5T, {4*e*10/h*1e-16/dn:.1f} @10T")

# --- price (calibrated on run 5: 1.17 s/pt at fast_delay=1.0, nplci 1, 7 fp) ---
S_PT = 1.25          # +1 magnet readback fp, +1 co-swept Keithley write
FLYBACK = 3.5        # TG 1.26 V + BG 1.63 V at volt.step 5 mV, ~6 ms/write
SLOW_DELAY, SETTLE = 2.0, 3.0
row_s = N_FAST * S_PT + FLYBACK + SLOW_DELAY + SETTLE
ramp_min = (B_vec.max() - 0.0) / 0.137
total_min = N_ROWS * row_s / 60 + ramp_min
print(f"\nprice: row = {N_FAST}x{S_PT}s + {FLYBACK}+{SLOW_DELAY}+{SETTLE} = {row_s:.0f} s; {N_ROWS} rows = {N_ROWS*row_s/60:.0f} min")
print(f"       + bare ramp 0 -> {B_vec.max():.1f} T at 0.137 T/min = {ramp_min:.0f} min")
print(f"       TOTAL = {total_min:.0f} min = {total_min/60:.2f} h   (+10% = {total_min*1.1/60:.2f} h)")
print(f"       total points = {N_ROWS*N_FAST}")
np.save("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/fan_B_vec.npy", B_vec)
