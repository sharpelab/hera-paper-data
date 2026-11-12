import numpy as np
from hera.analysis import fan_grids, resistance_grids, GateCalibration
from scipy.interpolate import griddata

fan = fan_grids("data/1")
ci = {c: i for i, c in enumerate(fan.cols)}
G = fan.data.reshape(fan.nrows, fan.nfast, len(fan.cols))
VTG = G[:, :, ci["DC_bias"]].ravel()
VBG = G[:, :, ci["k_2400_volt"]].ravel()
rg = resistance_grids(fan)

# session calibration
t_tg = 15.6e-9; ratio = 1.3091; t_bg_eff = t_tg / ratio; intc = 0.1740
_c0 = GateCalibration.from_thicknesses(t_tg, t_bg_eff, 0.0)
_n0, _ = _c0.n_D(intc, 0.0)
cal = GateCalibration.from_thicknesses(t_tg, t_bg_eff, 0.0, n_offset=-_n0)
base = np.array(cal.n_D(0.0, 0.0))
M = np.column_stack([np.array(cal.n_D(1.0, 0.0)) - base, np.array(cal.n_D(0.0, 1.0)) - base])
Minv = np.linalg.inv(M)
def gates_for(n, D): return Minv @ (np.array([n, D]) - base)

pts = np.column_stack([VTG, VBG])
print(" n[e12]  Vtg    Vbg   | R_sr1   R_sr2   R_sr3(Hall)  [ohm, nearest map pt]")
for n12 in (-5, -4, -3, -2, -1, 1, 2, 3, 4, 5):
    vtg, vbg = gates_for(n12 * 1e16, 0.0)
    row = f"{n12:+5d}  {vtg:+5.2f}  {vbg:+5.2f}  |"
    for ch in ("sr1", "sr2", "sr3"):
        R = np.abs(rg.R[ch]).ravel()
        val = griddata(pts, R, (vtg, vbg), method="nearest")
        row += f" {float(val):7.1f}"
    print(row)
print("\n(metallic = tens of ohms; insulating arm = ramps to kOhms+ away from CNP)")
