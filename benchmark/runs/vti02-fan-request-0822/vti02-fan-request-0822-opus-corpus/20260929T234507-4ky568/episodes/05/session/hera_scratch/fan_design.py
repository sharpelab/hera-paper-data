"""Fan design numbers: n-line gate voltages + limits, R along the D=0 line (run 5),
MR factor (runs 6/7) -> worst-corner sensitivity, grid Nyquist, wall-clock."""
import numpy as np
from pathlib import Path
from hera.analysis import open_run, fan_grids, resistance_grids, luttinger_frequency, field_invB
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

D = Path("/home/hera/measurements/zack/20260822-vti-02/data")
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN, TG_MAX = -0.3, 1.0
BG_MIN, BG_MAX = -1.3, 2.0

# --- where does the D = 0 line hit the TG limit?
for n in np.arange(3.0, 3.45, 0.01):
    vt, vb = calc_gate_voltages(n, 0.0, **CAL)
    if vt > TG_MAX:
        print(f"D=0 line leaves TG window above n = {n-0.01:.2f}e12 (Vtg {calc_gate_voltages(n-0.01,0,**CAL)[0]:.4f})")
        break

N_LO, N_HI = 1.30, 3.24
for n in (N_LO, 2.0, 2.6, N_HI):
    vt, vb = calc_gate_voltages(n, 0.0, **CAL)
    print(f"n={n:+.2f}e12 D=0 -> Vtg {vt:+.4f} (hdrm {TG_MAX-vt:+.4f}), Vbg {vb:+.4f} (hdrm {BG_MAX-vb:+.4f}); "
          f"roundtrip {calc_nD(vt, vb, **CAL)}  F_L {float(luttinger_frequency(n*1e16)):.2f} T")

# --- R along the D = 0 line from run 5 (worst corner = lowest n)
g = fan_grids(D / "5"); rg = resistance_grids(g)
R5 = np.abs(rg.R["sr1"]); Vbg5 = g.slow
fs = g.meta["fast_setpoints"]; Vtg5 = np.asarray(fs[0] if isinstance(fs[0], list) else fs)
print(f"\nrun 5 grid {R5.shape}, Vtg {Vtg5.min():.2f}..{Vtg5.max():.2f}, Vbg {Vbg5.min():.2f}..{Vbg5.max():.2f}")
print("R(B=0) along the D=0 line (run 5, nearest grid point):")
for n in (N_LO, 1.6, 2.0, 2.4, 2.8, N_HI):
    vt, vb = calc_gate_voltages(n, 0.0, **CAL)
    i = int(np.argmin(np.abs(Vbg5 - vb))); j = int(np.argmin(np.abs(Vtg5 - vt)))
    if abs(Vbg5[i] - vb) < 0.05 and abs(Vtg5[j] - vt) < 0.03:
        print(f"  n={n:+.2f}: R = {R5[i, j]:6.1f} Ohm  at (Vtg {Vtg5[j]:+.3f}, Vbg {Vbg5[i]:+.3f})")
    else:
        print(f"  n={n:+.2f}: outside run-5 grid (Vtg {vt:+.3f}, Vbg {vb:+.3f})")

# --- MR factor from the spot checks
for rid, lab in ((6, "electron n=+3.2"), (7, "hole n=-1.2")):
    r = open_run(D / str(rid))
    B = r.col("magnet_field"); I = r.col("sr0_X") / -1e6; R = np.abs(r.col("sr1_X") / I)
    o = np.argsort(B); B, R = B[o], R[o]
    lo = R[(B > 0.25) & (B < 0.65)]
    print(f"run {rid} ({lab}): R(0.25-0.65 T) med {np.median(lo):.0f} Ohm; R_max {R.max():.0f} Ohm at "
          f"B={B[np.argmax(R)]:.2f} T -> MR x{R.max()/np.median(lo):.1f}")

# --- grid + wall-clock
B_LO, B_HI, N_B = 0.60, 10.0, 121
N_N = 71
B_vec = field_invB(B_LO, B_HI, N_B)
dinv = np.diff(1 / B_vec)
F_max = float(luttinger_frequency(N_HI * 1e16))
print(f"\nB grid: {N_B} rows, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {abs(dinv[0]):.5f} 1/T (uniform)")
print(f"  Nyquist vs F_L(n_max)={F_max:.1f} T: need <= {1/(2*F_max):.5f} (2x) / {1/(3*F_max):.5f} (3x) "
      f"-> ratio {1/(2*F_max)/abs(dinv[0]):.2f}x over the 2x floor")
print(f"  dF = 1/(1/B_lo - 1/B_hi) = {1/(1/B_LO - 1/B_HI):.2f} T")
print(f"  coarsest B step = {np.diff(B_vec).max():.3f} T at the top; finest {np.diff(B_vec).min():.4f} T")
dn = (N_HI - N_LO) / (N_N - 1)
ray = 4 * 1.602176634e-19 / 6.62607015e-34 * B_LO / 1e16
print(f"n grid: {N_N} pts, {N_LO} -> {N_HI}e12, dn = {dn:.4f}e12; ray spacing at B_lo = {ray:.4f}e12 "
      f"-> {ray/dn:.2f} pts/ray (floor 2)")

vt_hi, _ = calc_gate_voltages(N_HI, 0.0, **CAL); vt_lo, _ = calc_gate_voltages(N_LO, 0.0, **CAL)
flyback = abs(vt_hi - vt_lo) / 5e-3 * 6e-3
for t_pt, lab in ((1.8 + 0.25, "6tau"), (1.2 + 0.25, "4tau")):
    grid = N_B * N_N * t_pt
    trav = (B_HI - B_LO) / 0.137 * 60
    row = N_B * (3.0 + flyback + 1.0)
    tot = grid + trav + row
    print(f"cost @{lab} ({t_pt:.2f} s/pt): grid {grid/3600:.2f} h + traverse {trav/3600:.2f} h + "
          f"row overhead {row/3600:.2f} h = {tot/3600:.2f} h (+10% -> {tot*1.1/3600:.2f} h)")
print(f"flyback/row = {flyback:.2f} s (TG span {abs(vt_hi-vt_lo):.3f} V at 5 mV/6 ms)")
