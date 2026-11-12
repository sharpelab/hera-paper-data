"""Landau-fan design numbers: n-line gate voltages, D=0 R(n) anchor from run 5, run-5 timing, 1/B grid, price."""
import numpy as np, json
from hera.analysis import open_run, fan_grids, resistance_grids, field_invB
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
# --- n-line
for N_n, n_lo, n_hi in [(49, 1.0, 3.3), (61, 1.0, 3.3), (49, 1.0, 3.35)]:
    ns = np.linspace(n_lo, n_hi, N_n); Vt, Vb = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
    print(f"N_n={N_n} n {n_lo}->{n_hi}: dn={ns[1]-ns[0]:.4f}e12; Vtg {Vt.min():+.4f}..{Vt.max():+.4f} (lim -0.3..1.0), Vbg {Vb.min():+.4f}..{Vb.max():+.4f} (lim -1.3..2.0); dVtg/pt {np.diff(Vt).mean()*1e3:.1f} mV")
# --- R(n, B=0) along D=0 from run 5
g = fan_grids("data/5"); rg = resistance_grids(g); R = np.abs(rg.R["sr1"]); Vbg = g.slow
fs = g.meta["fast_setpoints"]; Vtg = np.asarray(fs[0] if isinstance(fs[0], list) else fs)
from scipy.interpolate import RegularGridInterpolator
f = RegularGridInterpolator((Vbg, Vtg), R, bounds_error=False)
ns = np.array([0.3, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 3.2])
Vt, Vb = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print("R(n, D=0, B=0) from run 5:", ", ".join(f"n={n:.2f}:{r:.0f}Ohm" for n, r in zip(ns, f(np.c_[Vb, Vt]))))
# --- timing from run 5 (megasweep 63 x 66, fast_delay 1.0, slow_delay 3.0)
r5 = open_run("data/5"); t = r5.col("time"); nf = g.nfast; nr = g.nrows
tt = t[:nr*nf].reshape(nr, nf); in_row = np.diff(tt, axis=1).mean(); turn = (tt[1:, 0] - tt[:-1, -1]).mean()
print(f"run 5: {nr}x{nf}; per-point {in_row:.3f} s (fast_delay 1.0 -> overhead {in_row-1.0:.3f} s); row turnaround {turn:.1f} s (slow_delay 3 + flyback {Vtg.ptp():.2f} V); wall {(t[-1]-t[0])/3600:.2f} h")
# --- run 6 per-point overhead on the field axis (delay 0): time per 10 mT step minus ramp
r6 = open_run("data/6"); t6 = r6.col("time"); B6 = r6.col("magnet_field"); m = B6 > 1.05
dt = np.diff(t6[m]); print(f"run 6: per 10 mT step {np.median(dt):.2f} s (bare ramp 10 mT = {0.01/0.137*60:.2f} s) -> per-set overhead ~{np.median(dt)-0.01/0.137*60:.2f} s")
# --- B grid: two-segment uniform-1/B
def seg(b0, b1, dinv):
    N = int(np.ceil(abs(1/b0 - 1/b1)/dinv)) + 1; return field_invB(b0, b1, N)
FMAX = 4.135667e-15/4*3.3e16
print(f"F_L(3.3e12) = {FMAX:.1f} T; Nyquist d(1/B) <= {1/(2*FMAX):.4f}, prefer {1/(3*FMAX):.4f}")
A = seg(0.3, 1.2, 0.030); Bseg = seg(1.2, 10.0, 1/(3*FMAX))
B_vec = np.unique(np.round(np.hstack((A, Bseg)), 5))
print(f"segment A 0.3-1.2 T d(1/B)=0.030: {len(A)} rows, dB {np.diff(A).min()*1e3:.1f}-{np.diff(A).max()*1e3:.1f} mT; segment B 1.2-10 T: {len(Bseg)} rows, dB {np.diff(Bseg).min()*1e3:.0f}-{np.diff(Bseg).max()*1e3:.0f} mT; total {len(B_vec)} rows")
json.dump({"B_vec": B_vec.tolist()}, open("hera_scratch/fan_bvec.json", "w"))
# --- price
for N_n, fd in [(49, 2.0), (61, 2.0), (49, 1.5)]:
    ppt = fd + (in_row - 1.0); row = N_n*ppt + turn + 3.0  # +3 s magnet settle per row
    grid = len(B_vec)*row/3600; ramp = 9.7/0.137/60
    print(f"N_n={N_n}, fast_delay={fd}: {ppt:.2f} s/pt, {row:.0f} s/row grid -> {grid:.2f} h + traverse {ramp:.2f} h = {grid+ramp:.2f} h  (x1.08 -> {(grid+ramp)*1.08:.2f} h)")
# rays Nyquist on n axis at B=1 T
print(f"ray spacing dn at 1 T = {4*1.0/4.135667e-15/1e16:.4f}e12; at 0.5 T {4*0.5/4.135667e-15/1e16:.4f}e12")
