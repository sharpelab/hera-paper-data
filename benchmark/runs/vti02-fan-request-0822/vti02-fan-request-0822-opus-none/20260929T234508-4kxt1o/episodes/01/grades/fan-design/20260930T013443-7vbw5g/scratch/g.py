import numpy as np


def _invB_grid(b_lo, b_hi, d_invB, db_max):
    out, b = [b_hi], b_hi
    while b > b_lo:
        nb = 1.0 / (1.0 / b + d_invB)
        if b - nb > db_max:
            nb = b - db_max
        b = nb
        out.append(b)
    return np.round(np.array(sorted(x for x in out if x >= b_lo - 1e-9)), 4)


B = _invB_grid(0.5, 10.0, 0.0125, 0.25)
print(len(B), B[0], B[-1])
d = np.diff(1 / B)
print("d(1/B) min/max", d.min(), d.max())
dB = np.diff(B)
print("dB min/max", dB.min(), dB.max())
print(B[:5], B[-5:])
