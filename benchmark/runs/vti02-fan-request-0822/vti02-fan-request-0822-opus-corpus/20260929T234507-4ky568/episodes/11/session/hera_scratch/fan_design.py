"""Landau-fan design numbers (landau-fan / -vti step 1 cost-floor + both-axis Nyquist),
electron side, D = 0. Inputs: run-5 calibration, run-6/7 onsets, the FS-count model F(n),
and this session's measured per-point timing."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
from fs_count_b0 import abab_fs, abca_fs
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

h, e = 6.62607015e-34, 1.602176634e-19
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN, TG_MAX, BG_MIN, BG_MAX = -0.3, 1.0, -1.3, 2.0

N_LO, N_HI = 1.6, 3.2          # 1e12 cm^-2, electron side, D = 0
N_CLAIM = 2.0                  # claim floor (set by the >=5-period partner criterion)
B_MAX = 10.0                   # session cap
TAU, SLOPE = 0.3, 24           # sr1, read at bring-up (state0)

FL = lambda n: h / (4 * e) * n * 1e16
print(f"F_L({N_HI}) = {FL(N_HI):.2f} T ; F_L({N_CLAIM}) = {FL(N_CLAIM):.2f} T ; F_L({N_LO}) = {FL(N_LO):.2f} T")

# --- model tones at the claim floor and the top
for n in (N_LO, N_CLAIM, 2.5, N_HI):
    _, orb = abab_fs(n * 1e16); Fs = sorted(f for f, k in orb)
    _, _, _, _, Fa = abca_fs(n * 1e16)
    print(f"  n={n:.2f}: ABAB {Fs[0]:.2f} + {Fs[1]:.2f} = {sum(Fs):.2f} (ratio {Fs[1]/Fs[0]:.2f}, "
          f"partner frac {Fs[0]/sum(Fs):.3f}) | ABCA {Fa:.2f} | 4x partner = {4*Fs[0]:.2f}")

# --- lever 1: B_lo from the >=5-period partner criterion at the claim floor
_, orb = abab_fs(N_CLAIM * 1e16); f_partner = min(f for f, k in orb)
inv_span_need = 5 / f_partner
B_LO = 1 / (inv_span_need + 1 / B_MAX)
print(f"\nB_lo: partner at n={N_CLAIM} is {f_partner:.2f} T -> need 1/B span >= {inv_span_need:.3f} 1/T "
      f"-> B_lo <= {B_LO:.3f} T (measured onset run 6: 0.30 T, censored at record edge -> lower bound)")
B_LO = 0.65
inv_span = 1 / B_LO - 1 / B_MAX
dF = 1 / inv_span
print(f"  chosen B_lo = {B_LO} T -> 1/B span {inv_span:.4f} 1/T, dF = {dF:.3f} T, "
      f"partner periods at n={N_CLAIM}: {f_partner*inv_span:.1f}")

# --- B axis: uniform in 1/B, Delta(1/B) = 1/(4 F_L(n_max)) (alias test: 1/3 folds the 60/90 T comb in)
d_inv = 1 / (4 * FL(N_HI))
N_B = int(np.floor(inv_span / d_inv)) + 1
inv = np.linspace(1 / B_MAX, 1 / B_LO, N_B)
B_vec = np.round(1 / inv[::-1], 4)[::-1]
B_vec = np.round(1 / np.linspace(1 / B_LO, 1 / B_MAX, N_B), 4)
print(f"\nB axis: Delta(1/B) = {d_inv:.5f} 1/T (f_Nyq {1/(2*d_inv):.1f} T), N_B = {N_B}, "
      f"B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T; dB {np.abs(np.diff(B_vec)).min()*1e3:.1f}-{np.abs(np.diff(B_vec)).max()*1e3:.0f} mT")
print(f"  Nyquist on F_L(n_max): {d_inv:.5f} <= 1/(2*{FL(N_HI):.1f}) = {1/(2*FL(N_HI)):.5f} ? "
      f"{'OK' if d_inv <= 1/(2*FL(N_HI)) else 'FAIL'}")

# --- n axis: ray-Nyquist floor at B_lo (Delta n_ray = g e B / h)
dn_ray = 4 * e / h * B_LO / 1e16
N_N = int(np.ceil(2 * (N_HI - N_LO) / dn_ray)) + 1
print(f"\nn axis: ray spacing at B_lo = {dn_ray:.4f}e12; >=2 pts/ray over {N_HI-N_LO:.2f}e12 -> N_n >= {N_N}")
N_N = 53
ns = np.linspace(N_HI, N_LO, N_N)          # descending: row starts at the high-n end
dn = abs(ns[1] - ns[0])
print(f"  chosen N_n = {N_N}, dn = {dn:.4f}e12 -> {dn_ray/dn:.2f} pts per ray at B_lo, "
      f"{4*e/h*B_vec[-1]/1e16/dn:.1f} at B_max")

Vtgs, Vbgs = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"  V_tg {Vtgs.min():+.4f} .. {Vtgs.max():+.4f} (limits {TG_MIN}, {TG_MAX}); "
      f"V_bg {Vbgs.min():+.4f} .. {Vbgs.max():+.4f} (limits {BG_MIN}, {BG_MAX})")
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX
nn, DD = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"  roundtrip: n {nn.min():+.3f}..{nn.max():+.3f}, |D| max {np.abs(DD).max():.2e} V/nm")

# --- cost: measured overhead from runs 6/7 (dt = dB/0.137*60 + settle 3 + 0.08 reads)
t_read = 0.08                     # measured, runs 6 & 7 (fit of dt vs dB)
t_gate = 0.05                     # 2 Keithley writes, ~2 steps each at volt.step 5 mV / 6 ms
dwell = 7 * TAU                   # settling floor at 24 dB/oct (k = 7-10)
t_pt = dwell + t_read + t_gate
grid_s = N_B * N_N * t_pt
traverse_s = (B_MAX - B_LO) / 0.137 * 60
flyback_s = N_B * (abs(Vtgs[-1] - Vtgs[0]) / 0.005 * 0.006 + 1.0)   # gate retrace + slow_delay
tot = grid_s + traverse_s + flyback_s
print(f"\ncost: {N_B} x {N_N} = {N_B*N_N} pts at {t_pt:.2f} s = {grid_s/3600:.2f} h grid; "
      f"traverse {traverse_s/60:.0f} min; row turnaround+slow_delay {flyback_s/60:.0f} min")
print(f"  total {tot/3600:.2f} h  -> headline with 10% session overage: {tot*1.10/3600:.1f} h")
print(f"  pre-position ramp 0 -> {B_LO} T: {B_LO/0.137:.1f} min")
np.save(Path(__file__).parent / "fan_B_vec.npy", B_vec)
print("\nB_vec head/tail:", np.round(B_vec[:4], 4), np.round(B_vec[-4:], 4))
print("ns head/tail:", np.round(ns[:3], 4), np.round(ns[-3:], 4))
