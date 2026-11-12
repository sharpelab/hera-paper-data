import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
ns = np.linspace(1.0, 3.24, 48)
Ds = np.zeros_like(ns)
Vtg, Vbg = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(Vtg.min(), Vtg.max(), Vbg.min(), Vbg.max())
print(calc_nD(Vtg[-1], Vbg[-1], CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]))
print(calc_gate_voltages.__doc__)
