"""Fan A design: D = 0 line, n fast, B slow (1 -> 10 T), hybrid 1/B-uniform + B-uniform grid."""
import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import luttinger_frequency

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG, BG = (-0.3, 1.0), (-1.3, 2.0)

def v(n, D=0.0):
    return calc_gate_voltages(n, D, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])

# D = 0 window
for n in (-1.30, -1.27, -1.25, 3.25, 3.27, 3.30):
    print(n, [round(float(x), 4) for x in v(n)])

N_LO, N_HI, DN = -1.25, 3.25, 0.05
n_vec = np.round(np.arange(N_LO, N_HI + DN / 2, DN), 4)
Vtg, Vbg = map(np.asarray, zip(*[v(n) for n in n_vec]))
Vtg, Vbg = np.array(Vtg, float), np.array(Vbg, float)
print(f"n: {len(n_vec)} pts {n_vec[0]}..{n_vec[-1]}; Vtg {Vtg.min():+.4f}..{Vtg.max():+.4f}; Vbg {Vbg.min():+.4f}..{Vbg.max():+.4f}")
print(f"max step Vtg {np.abs(np.diff(Vtg)).max()*1e3:.1f} mV, Vbg {np.abs(np.diff(Vbg)).max()*1e3:.1f} mV")

# B grid: uniform 1/B at d(1/B) = DINV, switch to uniform-B DB where that is denser
B_LO, B_HI, DINV, DB = 1.0, 10.0, 1 / 120, 0.2
Bx = np.sqrt(DB / DINV)
inv = np.arange(1 / B_LO, 1 / Bx, -DINV)
B1 = 1 / inv
B2 = np.arange(B1[-1] + DB, B_HI + 1e-9, DB)
B_vec = np.round(np.hstack((B1, B2)), 4)
B_vec[-1] = min(B_vec[-1], B_HI)
if B_vec[-1] < B_HI - 1e-6:
    B_vec = np.append(B_vec, B_HI)
print(f"B: {len(B_vec)} rows, crossover {Bx:.2f} T ({len(B1)} 1/B rows + {len(B_vec)-len(B1)} B rows); "
      f"first {B_vec[:4]}, last {B_vec[-4:]}; max dB {np.diff(B_vec).max():.3f} T; "
      f"max d(1/B) {np.abs(np.diff(1/B_vec)).max():.4f} -> F_nyq {1/(2*np.abs(np.diff(1/B_vec)).max()):.0f} T; "
      f"dF (1-10 T) {1/(1/B_LO-1/B_HI):.2f} T")
assert (np.diff(B_vec) > 0).all()

# price (calibrated: run 5 gatemap 1.10 s/pt at fast_delay 1.0; run 6 field ramp 0.137 T/min + 3 s settle)
per_pt = 1.10 + 0.04          # + second-gate co-set
flyback = abs(Vtg[-1] - Vtg[0]) / 0.005 * 0.006 + abs(Vbg[-1] - Vbg[0]) / 0.005 * 0.006
slow_delay = 3.0
row = len(n_vec) * per_pt + flyback + slow_delay + 3.0 + 1.0   # + magnet settle + comm
ramp = B_HI / 0.137 * 60
tot = len(B_vec) * row + ramp
print(f"row {row:.0f} s (flyback {flyback:.1f} s); ramp 0->10 T {ramp/60:.0f} min; total {tot/3600:.2f} h; +8% {tot*1.08/3600:.2f} h")
# checkpoint rows
for Bc in (1.5, 2.0, 3.0, 4.9, 7.0):
    k = int(np.searchsorted(B_vec, Bc))
    t = k * row + B_vec[k] / 0.137 * 60
    print(f"  row {k} at B={B_vec[k]:.2f} T reached after ~{t/3600:.2f} h")
for n in (-1.2, 1.0, 3.2):
    print(f"F_L(n={n}) = {float(luttinger_frequency(abs(n)*1e16)):.1f} T")
np.savez("hera_scratch/fanA_grid.npz", n=n_vec, Vtg=Vtg, Vbg=Vbg, B=B_vec)
print("B_vec =", repr(B_vec))
