# === Session calibration commit v2 (run 4) — fixes the missing sharpelab_nb.gates imports ===
from sharpelab_nb.gates import stack_capacitance, calc_nD, calc_gate_voltages as _cgv

CAL_SLOPE = -1.2852          # combined sr1/sr2 CNP slope, run 4
CAL_B = +0.0513              # V_tg intercept at V_bg = 0
c_tg_cal = stack_capacitance([(15.6, 3)])       # F/m^2, geometry-prior anchor
c_bg_cal = -CAL_SLOPE * c_tg_cal                 # ratio-calibrated
n_off_disp = -calc_nD(CAL_B, 0, c_tg_cal, c_bg_cal)[0]   # 1e12 cm^-2 (sharpelab display units)
cal = GateCalibration(c_tg=c_tg_cal, c_bg=c_bg_cal, n_offset=n_off_disp * 1e16, D_offset=0.0)  # SI

def d0_point(n_e12):
    """(V_tg, V_bg) on the calibrated D=0 line at n [1e12 cm^-2]."""
    return _cgv(n_e12, 0.0, c_tg_cal, c_bg_cal, n_offset=n_off_disp)

print(f"cal committed: c_bg/c_tg = {c_bg_cal/c_tg_cal:.4f}, n_offset = {n_off_disp:+.4f} e12 cm^-2")
print(f"D=0 points: n=+6 -> {d0_point(6.0)}, n=-6 -> {d0_point(-6.0)}")
