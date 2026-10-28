import numpy as np
from hera.analysis import field_invB
N_HI = 3.24
F_MAX = 4.135667e-15 / 4 * N_HI * 1e16
def _seg(b0, b1, dinv):
    return field_invB(b0, b1, int(np.ceil(abs(1 / b0 - 1 / b1) / dinv)) + 1)
s1 = _seg(0.3, 1.2, 0.030)
s2 = _seg(1.2, 10.0, 1 / (3 * F_MAX))
B_vec = np.unique(np.round(np.hstack((s1, s2)), 4))
print(F_MAX, 1 / (3 * F_MAX))
print(len(s1), len(s2), len(B_vec), B_vec[0], B_vec[-1])
print(list(B_vec))
