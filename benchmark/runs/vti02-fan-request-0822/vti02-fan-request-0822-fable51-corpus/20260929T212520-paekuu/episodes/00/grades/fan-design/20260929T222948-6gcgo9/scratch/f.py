import numpy as np
from hera.analysis import field_invB
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
FL_MAX = 33.1
segs = [(0.6, 1.0, 1/(3*16.0)), (1.0, 3.5, 1/(3*FL_MAX)), (3.5, 10.0, 0.005)]
B_parts = [field_invB(a, b, int(np.ceil((1/a - 1/b)/d)) + 1) for a, b, d in segs]
B_vec = np.unique(np.round(np.hstack(B_parts), 5))
print(len(B_vec), B_vec.min(), B_vec.max())
print([(a, b, len(p)) for (a, b, _), p in zip(segs, B_parts)])
d = np.diff(1/B_vec)
print("d(1/B) min/max", d.min(), d.max())

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
ns = np.linspace(1.2, 3.2, 76)
Vtgs, Vbgs = calc_gate_voltages(ns, np.full_like(ns, 0.0), **CAL)
print("Vtg", Vtgs[0], Vtgs[-1], "Vbg", Vbgs[0], Vbgs[-1])
print(calc_gate_voltages.__doc__)
