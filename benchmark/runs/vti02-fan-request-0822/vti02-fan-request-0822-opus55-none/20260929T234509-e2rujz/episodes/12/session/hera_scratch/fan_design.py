import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.linspace(-1.25, 3.25, 151), 4)
Vt, Vb = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print("Vtg", Vt.min().round(4), Vt.max().round(4), " Vbg", Vb.min().round(4), Vb.max().round(4))
print("in validators:", (Vt.min() >= -0.3) and (Vt.max() <= 1.0) and (Vb.min() >= -1.3) and (Vb.max() <= 2.0))
# field grid: uniform 1/B (d=0.007 T^-1) from 1.25 T up to 5 T, then 0.2 T to 10 T
invB = np.arange(1/1.25, 1/5.0 - 1e-9, -0.007)
B_lo = 1/invB
B_hi = np.arange(5.0, 10.0001, 0.2)
B_vec = np.unique(np.round(np.hstack((B_lo[B_lo < 5.0 - 1e-6], B_hi)), 4))
print("rows", len(B_vec), "first", B_vec[:4], "last", B_vec[-4:], "n(B<2)", (B_vec < 2).sum(), "n(B<3)", (B_vec<3).sum())
print("max dB step", np.diff(B_vec).max().round(3), "max d(1/B)", np.abs(np.diff(1/B_vec)).max().round(4))
t_row = 151 * 1.17 + 3 + 3 + 3.5
ramp = (10 - 1.25) / 0.137 * 60 + 1.25 / 0.137 * 60
tot = len(B_vec) * t_row + ramp
print(f"row {t_row:.0f} s; rows {len(B_vec)*t_row/3600:.2f} h; ramp {ramp/60:.0f} min; total {tot/3600:.2f} h; +7% {1.07*tot/3600:.2f} h")
# cumulative time to reach B
cum = np.cumsum([t_row + (b - a)/0.137*60 for a, b in zip(np.r_[0, B_vec[:-1]], B_vec)])
for b in (1.5, 2.0, 2.5, 3.0, 5.0, 7.0):
    k = np.searchsorted(B_vec, b); print(f"  B={b}: row {k}, t={1.07*cum[k]/3600:.2f} h")
h, e = 6.62607015e-34, 1.602176634e-19
print("F_L at n ends:", [round(abs(x)*1e16*h/(4*e), 1) for x in (-1.25, 3.25)])
print("Luttinger LL spacing (1e12) at 1.25 T:", round(4*e*1.25/h/1e16, 3), " pts/period at dn=0.03:", round(4*e*1.25/h/1e16/0.03, 1))
print("FFT res best 1/(1/1.25-1/10):", round(1/(1/1.25-0.1), 2), "T; Nyquist of 0.007:", round(1/(2*0.007), 1), "T")
np.save("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/fan_Bvec.npy", B_vec)
print(repr(B_vec[:6]))
