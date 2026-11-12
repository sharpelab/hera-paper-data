"""landau-fan-vti design: n-line, 1/B grid, Nyquist both axes, dynamic range, price. Numbers land in the proposal markdown."""
import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_lo, n_hi, dn = 1.0, 3.2, 0.05
ns = np.round(np.arange(n_lo, n_hi + 1e-9, dn), 3); N_n = len(ns)
Vt, Vb = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"n-line: {N_n} pts, n {ns[0]}..{ns[-1]} step {dn}; Vtg {Vt.min():+.4f}..{Vt.max():+.4f} (lim -0.3..1.0), Vbg {Vb.min():+.4f}..{Vb.max():+.4f} (lim -1.3..2.0)")
print("in range:", (Vt >= -0.3).all() and (Vt <= 1.0).all() and (Vb >= -1.3).all() and (Vb <= 2.0).all())
nn, DD = calc_nD(Vt, Vb, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]); print(f"roundtrip max|dn| {np.abs(nn-ns).max():.2e}, max|D| {np.abs(DD).max():.2e}")
# field grid uniform in 1/B
B_lo, B_hi, dinv = 0.7, 10.0, 1/90
N_B = int(np.floor((1/B_lo - 1/B_hi) / dinv)) + 1
inv = np.linspace(1/B_lo, 1/B_lo - (N_B-1)*dinv, N_B); B_vec = 1/inv
print(f"B grid: {N_B} rows, {B_vec[0]:.4f} -> {B_vec[-1]:.4f} T, d(1/B) = {dinv:.5f} (Nyquist F = {1/(2*dinv):.1f} T; 1/3-rule F = {1/(3*dinv):.1f} T)")
print("B steps near top:", np.round(np.diff(B_vec)[-4:], 3), "near bottom:", np.round(np.diff(B_vec)[:3], 4))
for Bq in (1.0, 1.5, 2.0, 3.0, 5.0): print(f"  rows below {Bq} T: {(B_vec < Bq).sum()}")
h_e = 4.1357e-15  # T m^2
FL = lambda n: h_e * n * 1e16 / 4
print(f"F_L: n=1.0 {FL(1.0):.1f}, 2.0 {FL(2.0):.1f}, 3.2 {FL(3.2):.1f} T; x1.2 scale at 3.2: {1.2*FL(3.2):.1f} T")
# n-axis ray Nyquist: dn_ray = 4 e B / h  (1e12 cm^-2 per T)
dn_ray = lambda B: 4 * B / h_e / 1e16
for Bq in (0.7, 1.0, 1.5, 2.0): print(f"  ray spacing at {Bq} T: {dn_ray(Bq):.3f}e12 -> {dn_ray(Bq)/dn:.1f} columns per ray period")
# resolution
for Bon in (0.7, 1.0, 1.33): print(f"  dF for onset {Bon} T to 10 T: {1/(1/Bon - 0.1):.2f} T")
# light-tone periods (model): n=2.0 -> 3.55 T, 2.5 -> 5.09, 3.2 -> 7.31
for n_, f in ((2.0, 3.55), (2.5, 5.09), (3.2, 7.31)): print(f"  light tone n={n_}: {f} T -> {(1/B_lo-0.1)*f:.1f} periods in record")
# price: run 5 gatemap 1.17 s/pt at fast_delay 1.0 -> overhead 0.17 s; ramp 0.137 T/min; per-row settle 3 s + slow_delay 1 s + flyback ~1 s
fast_delay = 2.0; pt = fast_delay + 0.17; row = N_n * pt + 5.0
ramp_min = (B_hi - 0.0) / 0.137
tot_min = ramp_min + N_B * row / 60
print(f"price: {N_n}x{N_B} = {N_n*N_B} pts; {pt:.2f} s/pt -> {row:.0f} s/row; grid {N_B*row/60:.0f} min + ramp {ramp_min:.0f} min = {tot_min:.0f} min = {tot_min/60:.2f} h; x1.08 -> {tot_min*1.08/60:.2f} h")
# checkpoint clocks (minutes from start): first rows; B=1,2,5 T
for Bq in (1.0, 2.0, 5.0):
    k = (B_vec < Bq).sum(); t = (B_lo/0.137) + k * row/60 + (Bq - B_lo)/0.137
    print(f"  row {k} (B={Bq} T) lands at ~{t:.0f} min")
np.save("hera_scratch/fan_ns.npy", ns); np.save("hera_scratch/fan_B.npy", B_vec)
