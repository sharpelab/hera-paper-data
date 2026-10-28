import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
for nn in [-1.30,-1.27,-1.25,-1.24,3.24,3.25,3.27,3.30]:
    print(nn, calc_gate_voltages(nn, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]))
n = np.round(np.linspace(-1.24, 3.24, 150), 4)
Vt, Vb = calc_gate_voltages(n, np.zeros_like(n), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print("n step", n[1]-n[0], "TG", Vt.min(), Vt.max(), "BG", Vb.min(), Vb.max(), "dVtg", np.diff(Vt).mean(), "dVbg", np.diff(Vb).mean())
seg0 = [0.0, 0.5]
a = 1/np.arange(1/1.0, 1/1.5, -0.03)
b = 1/np.arange(1/1.5, 1/4.5, -0.012)
c = np.arange(4.5, 10.0001, 0.25)
B = np.unique(np.round(np.hstack((seg0, a, b, c)), 3))
print(len(a), len(b), len(c), "rows", len(B)); print(B)
dB = np.diff(B); print("max dB", dB.max(), "at", B[np.argmax(dB)], " dinvB at 4.5/4.75:", 1/4.5-1/4.75)
Nf = 150; per_pt = 1.10; row_fixed = 3.1 + 3.0 + 4.0
ramp = 10/0.137*60
tot = ramp + len(B)*(row_fixed + Nf*per_pt)
print(f"row {row_fixed+Nf*per_pt:.0f}s, total {tot/3600:.2f} h (ramp {ramp/60:.0f} min)")
cum = ramp*np.hstack(([0],np.cumsum(dB)))/10 + np.arange(len(B))*(row_fixed+Nf*per_pt)
for bb in [1.0,1.5,2.0,3.0,4.5,6.0,8.0,10.0]:
    k = np.argmin(abs(B-bb)); print(f"  reach B={B[k]:.2f} T (row {k}) at +{cum[k]/60:.0f} min")
