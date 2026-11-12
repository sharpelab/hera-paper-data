import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB, luttinger_frequency
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG = (-0.3, 1.0); BG = (-1.3, 2.0)
for n in (3.2, 3.25, 3.26, 3.27, 1.6, 1.8):
    print(n, calc_gate_voltages(n, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]))
n_lo, n_hi, N_n = 1.6, 3.25, 38
B_lo, B_hi = 1.0, 7.5
FLmax = float(luttinger_frequency(n_hi * 1e16)); dinv = 1 / (3 * FLmax)
N_B = int(np.ceil((1 / B_lo - 1 / B_hi) / dinv)) + 1
B_vec = field_invB(B_lo, B_hi, N_B)
print(f"F_L(n_hi)={FLmax:.2f} T, dinvB target {dinv:.5f}, N_B={N_B}, realized dinvB {(1/B_lo-1/B_hi)/(N_B-1):.5f} -> Nyquist F {1/(2*(1/B_lo-1/B_hi)/(N_B-1)):.1f} T")
ns = np.linspace(n_lo, n_hi, N_n); dn = ns[1] - ns[0]
print(f"dn={dn:.4f}e12; LL spacing at B_lo {4*2.418e10*B_lo/1e12:.4f}e12 -> {4*2.418e10*B_lo/1e12/dn:.2f} pts/LL")
Vt, Vb = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"Vtg {Vt.min():+.4f}..{Vt.max():+.4f}, Vbg {Vb.min():+.4f}..{Vb.max():+.4f}; dVtg {np.diff(Vt)[0]*1e3:.2f} mV dVbg {np.diff(Vb)[0]*1e3:.2f} mV")
dF_light = 1 / (1 / B_lo - 1 / B_hi); dF_heavy = 1 / (1 / 1.78 - 1 / B_hi)
print(f"dF light-tone record {dF_light:.2f} T, heavy-tone record (onset 1.78) {dF_heavy:.2f} T")
# price: calibrated run 5 (1.10 s/pt at fast_delay 1.0, NPLC 1, same fp set) and run 6/7 (0.137 T/min, 3 s settle)
FD, SD = 1.0, 2.0
flyback = (abs(Vt[-1]-Vt[0]) + abs(Vb[-1]-Vb[0])) / 5e-3 * 6e-3
pos = B_lo / 0.137 * 60
trav = (B_hi - B_lo) / 0.137 * 60
rows = N_B * (3.0 + SD + flyback + 0.1)
pts = N_B * N_n * (FD + 0.10)
tot = pos + 20 + trav + rows + pts
print(f"flyback {flyback:.1f}s/row; positioning {pos/60:.1f} min, traverse {trav/60:.1f}, row overhead {rows/60:.1f}, points {N_B*N_n} x {FD+0.1:.2f}s = {pts/60:.1f} min -> total {tot/60:.1f} min (+7%: {tot*1.07/60:.0f} min)")
# cumulative time vs row for checkpoints
t = np.cumsum(np.r_[pos + 20, np.abs(np.diff(B_vec)) / 0.137 * 60] + 3.0 + SD + flyback + 0.1 + N_n * (FD + 0.1))
for B in (1.1, 1.5, 2.0, 3.0, 4.0, 5.5, 7.5):
    i = np.searchsorted(B_vec, B); i = min(i, N_B - 1); print(f"  row {i:3d} B={B_vec[i]:.3f} T at t+{t[i]/60:.0f} min")
