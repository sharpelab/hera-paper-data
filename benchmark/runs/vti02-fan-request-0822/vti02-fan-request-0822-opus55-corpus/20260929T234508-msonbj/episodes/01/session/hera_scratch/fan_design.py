import numpy as np
from hera.analysis import field_invB
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
h, e = 6.62607015e-34, 1.602176634e-19
n_hi, n_lo, B_lo, B_hi = 3.25, 2.00, 0.85, 6.0
FL = lambda n12: n12 * 1e16 * h / (4 * e)
dnLL = 4 * e * B_lo / h / 1e16          # 1e12 cm^-2, physical (scale 1, conservative)
N_n = int(np.ceil((n_hi - n_lo) / (dnLL / 2))) + 1
dinv = 0.0075
N_B = int(np.ceil((1 / B_lo - 1 / B_hi) / dinv)) + 1
B_vec = field_invB(B_lo, B_hi, N_B); d = np.diff(1 / B_vec)
ns = np.linspace(n_hi, n_lo, N_n)
Vt, Vb = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"dn_LL(B_lo) {dnLL:.4f}e12 -> N_n {N_n} (step {abs(ns[1]-ns[0]):.4f})")
print(f"N_B {N_B}: dinvB {abs(d).mean():.5f} (f_N {1/(2*abs(d).mean()):.1f} T), dB {B_vec[1]-B_vec[0]:.4f} at B_lo .. {B_vec[-1]-B_vec[-2]:.3f} at B_hi")
print(f"F_L(n_hi) {FL(n_hi):.1f} T (Nyquist-only dinv {1/(2*FL(n_hi)):.4f}); dF = {1/(1/B_lo-1/B_hi):.2f} T")
print(f"Vtg {Vt.min():+.4f}..{Vt.max():+.4f}  Vbg {Vb.min():+.4f}..{Vb.max():+.4f}")
t_pt, row_ovh = 1.8 + 0.1, 3.0 + 3.0 + 0.6   # fast_delay+read ; slow_delay + settle_s + flyback
rows = N_B * (N_n * t_pt + row_ovh) / 60; trav = (B_hi - B_lo) / 0.137; init = B_lo / 0.137
print(f"rows {rows:.0f} min + traverse {trav:.1f} + initial {init:.1f} = {rows+trav+init:.0f} min; pts {N_B*N_n}")
cum = np.cumsum([(N_n * t_pt + row_ovh) / 60 + abs(B_vec[i] - (B_vec[i-1] if i else 0)) / 0.137 for i in range(N_B)])
for k in (0, 2, 30, 60, 90, 110, 125, N_B - 1):
    print(f"  row {k:3d}: B {B_vec[k]:.3f} T, t+{cum[k]:.0f} min")
