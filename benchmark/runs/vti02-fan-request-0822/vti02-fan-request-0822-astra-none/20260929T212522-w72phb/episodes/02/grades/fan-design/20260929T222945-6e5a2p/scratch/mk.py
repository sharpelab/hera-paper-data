import json, numpy as np
from hera.analysis import field_invB
B = np.r_[0., .5, .75, 1., field_invB(1.25, 6., 103)]
out = {
 "status": "extracted", "landed": "fan", "form": "2d_megasweep", "field_mode": "stitched",
 "B_values": [round(float(x), 6) for x in B],
 "n_min_cm2": -1.2e12, "n_max_cm2": 3.2e12, "n_columns": 89, "D": 0.0,
 "slow_axis": "B", "slow_delay_s": 3.0, "fast_delay_s": 3.0,
 "lockins": [
   {"name": "sr0", "sensitivity_V": 0.02, "sensitivity_set_in_answer": False,
    "time_constant_s": 0.3, "time_constant_set_in_answer": False},
   {"name": "sr1", "sensitivity_V": 1e-4, "sensitivity_set_in_answer": True,
    "time_constant_s": 0.3, "time_constant_set_in_answer": False}],
 "gate_current_reads": [
   {"name": "k_2400_tg_curr", "nplc": 1.0, "nplc_set_in_answer": False},
   {"name": "k_2400_bg_curr", "nplc": 1.0, "nplc_set_in_answer": False}],
 "excitation_V": 1.0, "bias_resistor_ohm": 1e8, "n_fans": 1, "stated_wall_clock_h": 10.5,
 "flags": [],
 "notes": (
   "Cell 48 (appended code, with markdown cell 47): s.multimegasweep([magnet.field],[B_fan],"
   "[k_tg.volt,k_bg.volt],[Vtg_fan,Vbg_fan],slow_delay=3.,fast_delay=3.). "
   "B_fan = np.r_[0,0.5,0.75,1.0, field_invB(1.25,6.,103)] = 107 rows: four low-field context "
   "points stitched onto a 103-point inverse-B leg 1.25-6 T. Density n_fan = np.linspace(-1.2,3.2,89) "
   "in 1e12 cm^-2 at D = 0, converted with calc_gate_voltages and the cell's own FAN_CAL (run-5 "
   "calibration c_tg=2.7961e-3, c_bg=2.1607e-3, n_offset=-0.08938, D_offset=-0.013), giving "
   "TG -0.277033..+0.983594 V and BG -0.465040..+1.166281 V, reproduced in a scratch script; the "
   "markdown calls the absolute density scale geometry-anchored and provisional. Followed channels "
   "include sr0.X/P, sr1.X/P and k_tg.curr/k_bg.curr. sr1 sensitivity is set to 100 uV inside the "
   "answer cell; sr0 sensitivity 0.02 V and both tau = 0.3 s are inherited from the "
   "close_out(restore=state0) readback in cell 44, which also prints tg/bg nplci = 1.0. Drive 1.0 V "
   "through the 1e8 ohm bias resistor (meas_config, asserted in the cell). Stated ETA 10h30m in the "
   "cell-47 header; the markdown separately budgets ~8.5 h of point time for 9,523 points."
 )
}
json.dump(out, open("/grade-run/output.json", "w"), indent=1)
print("ok", len(B))
