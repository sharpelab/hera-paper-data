import numpy as np
from sharpelab_nb.gates import calc_gate_voltages
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN, TG_MAX = -0.3, 1.0
BG_MIN, BG_MAX = -1.3, 1.2
_ns = np.linspace(-2, 4, 6001)
_Vt, _Vb = calc_gate_voltages(_ns, 0.0, **CAL)
_ok = (_Vt >= TG_MIN) & (_Vt <= TG_MAX) & (_Vb >= BG_MIN) & (_Vb <= BG_MAX)
n = np.linspace(_ns[_ok].min() + 0.005, _ns[_ok].max() - 0.005, 100)
print(n[0], n[-1], len(n))
V = calc_gate_voltages(n, 0.0, **CAL)
print(V[0][0], V[0][-1], V[1][0], V[1][-1])
B = np.round(np.arange(1.0, 10.0001, 0.1), 4)
print(B[0], B[-1], len(B))
