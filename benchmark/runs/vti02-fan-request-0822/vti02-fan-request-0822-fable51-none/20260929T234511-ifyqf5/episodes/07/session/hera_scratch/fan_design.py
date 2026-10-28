"""Landau-fan design: D=0 gate line inside validators, n grid, timing; plus filling-factor hypotheses for run-6 minima."""
import numpy as np
from scipy.signal import argrelmin
from scipy.ndimage import gaussian_filter1d
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import open_run, resolve_channels
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG = (-0.3, 1.0); BG = (-1.3, 2.0)
ns = np.linspace(-2, 4, 6001); Vt, Vb = calc_gate_voltages(ns, 0.0, **CAL)
ok = (Vt >= TG[0]) & (Vt <= TG[1]) & (Vb >= BG[0]) & (Vb <= BG[1])
n_lo, n_hi = ns[ok].min(), ns[ok].max()
print(f"D=0 line inside validators: n = {n_lo:+.3f} .. {n_hi:+.3f} e12; Vtg {Vt[ok].min():+.4f}..{Vt[ok].max():+.4f}, Vbg {Vb[ok].min():+.4f}..{Vb[ok].max():+.4f}")
for N in (80, 100, 120):
    n_vec = np.linspace(n_lo + 0.005, n_hi - 0.005, N); Vtgs, Vbgs = calc_gate_voltages(n_vec, 0.0, **CAL)
    print(f"N={N}: dn={n_vec[1]-n_vec[0]:.4f}e12, dVtg={(Vtgs[1]-Vtgs[0])*1e3:.1f} mV, dVbg={(Vbgs[1]-Vbgs[0])*1e3:.1f} mV; Vtg {Vtgs[0]:+.4f}..{Vtgs[-1]:+.4f} Vbg {Vbgs[0]:+.4f}..{Vbgs[-1]:+.4f}")
# nu lines: n = nu e B / h  (1e12 cm^-2 per T per nu)
eh = 1.602e-19 / 6.626e-34 * 1e-4 / 1e12  # 1e12 cm^-2 / T per unit nu
print(f"n per nu per T: {eh:.4f}e12 -> at 10 T: nu=4 -> {4*eh*10:.2f}, nu=8 -> {8*eh*10:.2f}, nu=12 -> {12*eh*10:.2f}; nu=-4 -> {-4*eh*10:.2f}")
print(f"hole edge n={n_lo:.2f}: nu=-8 line reaches it at B={abs(n_lo)/(8*eh):.1f} T; nu=-4 at {abs(n_lo)/(4*eh):.1f} T; e-edge n={n_hi:.2f}: nu=12 at {n_hi/(12*eh):.1f} T, nu=16 at {n_hi/(16*eh):.1f} T")
# timing (run 5 calibration: 4158 pts, 63 rows, 4873 s, fast_delay 1 s, slow_delay 3 s)
for N, rows, dB in ((100, 91, 0.1), (80, 91, 0.1), (100, 61, 0.15)):
    pp = 1.10; row = N * pp + 1.6 + 2.0 + 4.0 + dB / 0.137 * 60 + 3.0
    tot = rows * row + 1.0 / 0.137 * 60
    print(f"N={N} rows={rows} dB={dB}: row {row:.0f} s, total {tot/3600:.2f} h (x1.08 -> {tot*1.08/3600:.2f} h)")
# run-6 minima -> filling factors under two scale hypotheses
r = open_run("data/6"); ch = {c.cid: c for c in resolve_channels(r.meta)}
B = r.col("magnet_field"); R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / (r.col("sr0_X") / ch["sr0"].gain))
o = np.argsort(B); B, R = B[o], R[o]; Rs = gaussian_filter1d(R, 2)
m = B > 2.5; idx = argrelmin(Rs[m], order=15)[0]; Bm = B[m][idx]; Rm = Rs[m][idx]
nh_e = 3.2 * 41.357  # T, nu = nh/(eB) with n=3.2e12 -> n h/e = 132.3 T
print("run 6 minima (B>2.5 T):", ", ".join(f"{b:.2f}T({rr:.0f}Ω) nu={nh_e/b:.1f}|{1.087*nh_e/b:.1f}" for b, rr in zip(Bm, Rm)))
r = open_run("data/7"); B = r.col("magnet_field"); R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / (r.col("sr0_X") / ch["sr0"].gain))
o = np.argsort(B); B, R = B[o], R[o]; Rs = gaussian_filter1d(R, 1.5)
m = B > 1.0; idx = argrelmin(Rs[m], order=8)[0]; Bm = B[m][idx]; Rm = Rs[m][idx]
print("run 7 minima (B>1 T):", ", ".join(f"{b:.2f}T({rr:.0f}Ω) nu={1.2*41.357/b:.1f}" for b, rr in zip(Bm, Rm)))
