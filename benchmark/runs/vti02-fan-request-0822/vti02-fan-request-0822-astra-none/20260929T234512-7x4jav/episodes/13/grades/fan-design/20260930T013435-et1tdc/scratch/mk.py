import json, numpy as np
f = np.concatenate(([0.0, 0.5, 0.75], np.linspace(1, 3, 17), np.linspace(3.25, 10, 28)))
out = {
 "status": "extracted", "landed": "fan", "form": "2d_megasweep", "field_mode": "stitched",
 "B_values": [round(float(x), 4) for x in f],
 "n_min_cm2": -1.2e12, "n_max_cm2": 3.2e12, "n_columns": 177, "D": 0.0,
 "slow_axis": "B", "slow_delay_s": 3.0, "fast_delay_s": 3.0,
 "lockins": [
   {"name": "sr0", "sensitivity_V": 0.02, "sensitivity_set_in_answer": False,
    "time_constant_s": 0.3, "time_constant_set_in_answer": False},
   {"name": "sr1", "sensitivity_V": 1e-4, "sensitivity_set_in_answer": True,
    "time_constant_s": 0.3, "time_constant_set_in_answer": False}],
 "gate_current_reads": [
   {"name": "k_2400_tg_curr", "nplc": 1.0, "nplc_set_in_answer": False},
   {"name": "k_2400_bg_curr", "nplc": 1.0, "nplc_set_in_answer": False}],
 "excitation_V": 1.0, "bias_resistor_ohm": 1e8, "n_fans": 1, "stated_wall_clock_h": 9.75,
 "flags": [],
 "notes": ("Cell 48 (appended, with markdown cell 47): s.multimegasweep([magnet.field],[_fan_fields],"
   "[k_tg.volt,k_bg.volt],[_fan_tg,_fan_bg], slow_delay=3.0, fast_delay=3.0). Field vector is stitched: "
   "[0,0.5,0.75] + linspace(1,3,17) (0.125 T) + linspace(3.25,10,28) (0.25 T) = 48 rows. Fast axis is 177 "
   "co-swept TG/BG points from the run-5 calibration constants committed in the cell (c_tg, c_bg, n_offset, "
   "D_offset) at nominal n = -1.2..+3.2e12 cm^-2 by 0.025e12, D_est = 0 (TG -0.277..+0.984 V, BG -0.465..+1.166 V, "
   "reproduced in a scratch script); the cell notes the absolute density is geometry-anchored and the D zero "
   "provisional. sr0 X/P and sr1 X/P are followed; sr1 sensitivity is set to 100 uV in the answer cell, all other "
   "lock-in and NPLC values are inherited from the cell-44 close_out(restore=state0) readback (sr0 0.02 V, both "
   "tau 0.3 s, tg/bg nplci 1.0). Drive 1.0 V at 13.777 Hz through meas_config['bias_resistor'] = 100e6. "
   "Headline ETA ~9h45m stated in cell 47.")
}
json.dump(out, open('/grade-run/output.json', 'w'), indent=1)
print('ok')
