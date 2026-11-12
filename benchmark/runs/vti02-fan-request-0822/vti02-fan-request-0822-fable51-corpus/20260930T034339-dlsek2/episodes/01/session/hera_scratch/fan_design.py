"""Landau-fan design numbers (recipe step 1, binding): grid, Nyquist both axes, dynamic range, cost."""
import numpy as np, scipy.constants as c
from hera.analysis import field_invB
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG = (-0.3, 1.0); BG = (-1.3, 2.0)
FL = lambda n: c.h/(4*c.e)*abs(n)*1e16
n_lo, n_hi, N_n = 1.0, 3.24, 61
B_lo, B_hi = 1.2, 10.0
F_max = FL(n_hi); dinvB = 1/(4*F_max)
N_B = int(np.ceil((1/B_lo - 1/B_hi)/dinvB)) + 1
B_vec = field_invB(B_lo, B_hi, N_B); d = np.diff(1/B_vec)
print(f"F_L(n_hi={n_hi}) = {F_max:.2f} T; Delta(1/B) = 1/(4 F_L) = {dinvB:.5f} 1/T -> N_B = {N_B}; realized {abs(d.mean()):.5f} (fs = {1/abs(d.mean()):.1f} T, Nyquist {0.5/abs(d.mean()):.1f} T)")
print(f"B rows: {B_vec[:3]} ... {B_vec[-3:]}; dB at low end {B_vec[1]-B_vec[0]:.4f} T, at high end {B_vec[-1]-B_vec[-2]:.3f} T")
ns = np.linspace(n_lo, n_hi, N_n); dn = ns[1]-ns[0]
Vt, Vb = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"n-line: {N_n} pts, dn = {dn:.4f}e12; Vtg {Vt.min():+.4f}..{Vt.max():+.4f}, Vbg {Vb.min():+.4f}..{Vb.max():+.4f}; inside validators: {Vt.min()>=TG[0] and Vt.max()<=TG[1] and Vb.min()>=BG[0] and Vb.max()<=BG[1]}")
nn, DD = calc_nD(Vt, Vb, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]); print(f"roundtrip n {nn.min():.3f}..{nn.max():.3f}, |D| max {abs(DD).max():.2e}")
ray = 4*c.e/c.h*B_lo*1e-16   # e12 cm^-2 per nu=4 ray at B_lo
print(f"n-axis Nyquist: ray spacing at B_lo = {ray:.4f}e12 -> {ray/dn:.2f} pts/period (floor 2, prefer 3); at 3 T: {ray*2.5/dn:.1f}")
# periods & dF
rec = 1/B_lo - 1/B_hi
for f, lab in ((7.2,"light@3.2"),(3.55,"ABAB light@n=2 (model)"),(22.3,"22T tone"),(29.4,"sum/F_L'"),(25.8,"ABAB heavy@3.2 model")):
    print(f"  {lab:28s} f={f:5.1f} T: periods in record {f*rec:.1f}; 5-period B_lo would be {1/(0.1+5/f):.2f} T")
print(f"record 1/B = {rec:.3f} 1/T -> dF = {1/rec:.2f} T; from 1.8 T (sum-tone onset): dF = {1/(1/1.8-0.1):.2f} T")
# cost
tau, k = 0.3, 6; fast_delay = k*tau; t_read = 0.17; settle = 3.0; slow_delay = 1.0
flyback = (np.ptp(Vt)/0.005)*0.006
row = N_n*(fast_delay+t_read) + flyback + slow_delay + settle
ramp = (B_hi - B_lo)/0.137*60 + B_lo/0.137*60
tot = N_B*row + ramp
print(f"fast_delay {fast_delay} s ({k} tau), per-pt ~{fast_delay+t_read:.2f} s; row {row:.0f} s; N_B*row = {N_B*row/60:.0f} min; ramps {ramp/60:.0f} min (incl. 0->{B_lo} T positioning); total {tot/3600:.2f} h; +8% -> {tot*1.08/3600:.2f} h")
# alias table for harmonics of the top tones (scale 0.9 observed)
fs = 1/abs(d.mean())
for F in (30.0, 33.6, 7.2):
    al = [(k*F, min(k*F % fs, fs - k*F % fs)) for k in (2,3,4)]
    print(f"  harmonics of {F} T alias to: " + ", ".join(f"{k}x={kf:.0f}->{a:.0f} T" for (k,(kf,a)) in zip((2,3,4), al)))
