import numpy as np
from hera.analysis import GateCalibration

# Calibration from cnp_fit.py (sr1 fit, geometry-prior absolute scale)
t_tg = 15.6e-9
ratio = 1.3091
t_bg_eff = t_tg / ratio
intc = 0.1740   # Vtg @ Vbg=0 on CNP line
slope = -1.3091

cal0 = GateCalibration.from_thicknesses(t_tg, t_bg_eff, 0.0)
n0, _ = cal0.n_D(intc, 0.0)
cal = GateCalibration.from_thicknesses(t_tg, t_bg_eff, 0.0, n_offset=-n0)
print("c_tg =", cal.c_tg, "F/m^2 ; c_bg =", cal.c_bg, "F/m^2 ; ratio", cal.c_bg/cal.c_tg)

# Linearize n_D to invert: [n,D] = M @ [Vtg,Vbg] + k
base = np.array(cal.n_D(0.0, 0.0))
cx = np.array(cal.n_D(1.0, 0.0)) - base   # d/dVtg
cy = np.array(cal.n_D(0.0, 1.0)) - base   # d/dVbg
M = np.column_stack([cx, cy])             # 2x2: rows (n,D), cols (Vtg,Vbg)
Minv = np.linalg.inv(M)

def gates_for(n, D):
    rhs = np.array([n, D]) - base
    return Minv @ rhs   # [Vtg, Vbg]

# (n=0, D=0) operating point
vtg0, vbg0 = gates_for(0.0, 0.0)
print(f"\n(n=0, D=0) point: V_tg={vtg0:+.3f} V, V_bg={vbg0:+.3f} V")
# cross-check vs Gate C (CNP at TG=0 -> Vbg) and map fit
print(f"  map CNP at TG=0: Vbg = {-intc/slope:+.3f} V ; Gate C measured Vbg=+0.40 V (settling-lagged)")

# D-axis sanity: D in V/m. Convert to V/nm for intuition
print(f"  |D| at CNP corners (Vbg=+/-4.5 on CNP line): ", end="")
for vbg in (-4.5, 4.5):
    vtg = slope*vbg + intc
    _, D = cal.n_D(vtg, vbg)
    print(f"Vbg={vbg:+.1f}->D={D/1e9:+.3f} V/nm ", end="")
print()

# Design the D=0 line: n sweep, clip to validators
TG_MIN, TG_MAX = -6.0, 7.0
BG_MIN, BG_MAX = -4.5, 4.5
n_grid = np.linspace(-6e16, 6e16, 601)   # +/-6e12 cm^-2
rows = np.array([gates_for(n, 0.0) for n in n_grid])  # (601,2) Vtg,Vbg
vtg, vbg = rows[:, 0], rows[:, 1]
inwin = (vtg >= TG_MIN) & (vtg <= TG_MAX) & (vbg >= BG_MIN) & (vbg <= BG_MAX)
print(f"\nD=0 line realized n-window within validators:")
print(f"  n from {n_grid[inwin].min()/1e16:+.2f} to {n_grid[inwin].max()/1e16:+.2f} e12 cm^-2")
print(f"  binding gate: Vtg range [{vtg[inwin].min():.2f},{vtg[inwin].max():.2f}], "
      f"Vbg range [{vbg[inwin].min():.2f},{vbg[inwin].max():.2f}]")
# which gate clips first on each side
for side, sel in [("hole (n<0)", n_grid < 0), ("electron (n>0)", n_grid > 0)]:
    s = sel & inwin
    print(f"  {side}: |n|max = {np.abs(n_grid[s]).max()/1e16:.2f} e12 cm^-2")

# Slope of D=0 line in gate space
dvtg_dvbg_D0 = np.polyfit(vbg[inwin], vtg[inwin], 1)[0]
print(f"\nD=0 line slope dVtg/dVbg = {dvtg_dvbg_D0:+.4f} (CNP line slope was {slope:+.4f})")
