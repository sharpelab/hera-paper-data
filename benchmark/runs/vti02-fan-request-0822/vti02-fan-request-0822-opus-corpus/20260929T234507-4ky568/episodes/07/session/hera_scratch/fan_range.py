"""Dynamic-range sizing: R along the D=0 line at B=0 (run 5) x measured MR."""
import numpy as np
from pathlib import Path
from hera.analysis import open_run, fan_grids, resistance_grids
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

DATA = Path(__file__).resolve().parent.parent / "data"
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
I_BIAS = 10e-9

g = fan_grids(str(DATA / "5"))
rg = resistance_grids(g)
R = rg.R["sr1"]                       # (63 rows=BG, 66 fast=TG)
vbg = np.asarray(g.slow, float)
vtg = np.asarray(g.grid("k_2400_tg_volt"), float)[0]
print("cols:", g.cols)
print("vbg", vbg[0], "->", vbg[-1], len(vbg), "| vtg", vtg[0], "->", vtg[-1], len(vtg))

# D=0 line inside the map, sample R at each n
ns = np.arange(0.6, 3.25, 0.2)
Vtgs, Vbgs = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print("\n n[e12]  Vtg      Vbg      R(B=0) [Ohm]")
Rb0 = {}
for n, vt, vb in zip(ns, Vtgs, Vbgs):
    if not (vbg.min() <= vb <= vbg.max()) or not (vtg.min() <= vt <= vtg.max()):
        print(f" {n:5.2f}  {vt:+.4f}  {vb:+.4f}   (outside map)")
        continue
    i = int(np.argmin(abs(vbg - vb))); j = int(np.argmin(abs(vtg - vt)))
    Rb0[round(float(n), 2)] = float(R[i, j])
    print(f" {n:5.2f}  {vt:+.4f}  {vb:+.4f}   {R[i,j]:8.1f}")

# measured MR factor from the spot checks
for rid, nlab in ((6, "+3.2e12"), (7, "-1.2e12")):
    r = open_run(DATA / str(rid))
    B = np.asarray(r.col("magnet_field"), float); Rx = np.asarray(r.col("sr1_X"), float) / I_BIAS
    o = np.argsort(B); B, Rx = B[o], Rx[o]
    lo = Rx[(B > 0.0) & (B < 0.35)]
    print(f"\nrun {rid} (n={nlab}): R(B<0.35 T) med {np.median(lo):.1f} Ohm ; "
          f"R_max {Rx.max():.1f} at B={B[np.argmax(Rx)]:.2f} T -> MR x{Rx.max()/max(np.median(lo),1):.0f}")

print("\n--- worst-corner projection for the fan (n_min = 0.8e12, B = 10 T) ---")
r0 = Rb0.get(0.8)
print(f"R(n=0.8e12, B=0) from gatemap = {r0:.1f} Ohm" if r0 else "n=0.8 outside map")
r32 = Rb0.get(3.2)
if r0 and r32:
    print(f"R(n=3.2e12, B=0) = {r32:.1f} Ohm ; run-6 peak at 10 T = 522.5 -> MR x{522.5/r32:.0f}")
    print(f"scaling that MR factor to n=0.8: R_peak ~ {r0*522.5/r32:.0f} Ohm")
for sens in (50e-6, 100e-6, 200e-6):
    print(f"  sens {sens*1e6:5.0f} uV -> FS {sens/I_BIAS/1e3:.1f} kOhm ; "
          f"worst-corner fill {(r0*522.5/r32)/(sens/I_BIAS) if r0 and r32 else float('nan'):.2f} ; "
          f"R=15 Ohm fills {15/(sens/I_BIAS):.4f}")
