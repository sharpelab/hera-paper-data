"""Final fan arithmetic: gate line, worst-corner R (sensitivity sizing), wall-clock."""
import numpy as np, scipy.constants as cst
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import open_run, fan_grids, resistance_grids

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN, TG_MAX, BG_MIN, BG_MAX = -0.3, 1.0, -1.3, 2.0

n_lo, n_hi, N_n = 1.60, 3.20, 33
ns = np.linspace(n_hi, n_lo, N_n)          # high -> low n
Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"n-line: {N_n} pts, n {ns[0]:+.2f} -> {ns[-1]:+.2f} e12 (dn = {abs(ns[1]-ns[0]):.4f}e12)")
print(f"  Vtg {Vtgs.min():+.4f} .. {Vtgs.max():+.4f} V   (limits {TG_MIN}, {TG_MAX})")
print(f"  Vbg {Vbgs.min():+.4f} .. {Vbgs.max():+.4f} V   (limits {BG_MIN}, {BG_MAX})")
print(f"  in range: {Vtgs.min()>=TG_MIN and Vtgs.max()<=TG_MAX and Vbgs.min()>=BG_MIN and Vbgs.max()<=BG_MAX}")

# --- R along the n-line at B = 0, from gatemap run 5 (sensitivity anchor) ---
fg = fan_grids("data/5")
rg = resistance_grids(fg)
ch = [c for c in rg.R] if hasattr(rg, "R") else None
print("\nResistanceGrids fields:", [a for a in dir(rg) if not a.startswith("_")])
Rg = rg.R if hasattr(rg, "R") else None
print("channels:", list(Rg.keys()) if isinstance(Rg, dict) else type(Rg))
vtg = fg.fast[0] if hasattr(fg, "fast") else None
print("fan_grids fields:", [a for a in dir(fg) if not a.startswith("_")])
