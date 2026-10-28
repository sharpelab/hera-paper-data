import json, numpy as np
B = np.unique(np.round(np.hstack((1/np.arange(1/0.6, 0.8-1e-9, -0.03),
 1/np.arange(0.8, 0.35355-1e-9, -0.0125),
 np.arange(2.8, 10.0+1e-9, 0.1))), 4))
out = {
 "status": "extracted",
 "landed": "fan",
 "form": "2d_megasweep",
 "field_mode": "stitched",
 "B_values": [float(x) for x in B],
 "n_min_cm2": -1.25e12,
 "n_max_cm2": 3.20e12,
 "n_columns": 90,
 "D": 0.0,
 "slow_axis": "B",
 "slow_delay_s": 3.0,
 "fast_delay_s": 1.0,
 "lockins": [
   {"name": "sr0", "sensitivity_V": 0.02, "sensitivity_set_in_answer": False,
    "time_constant_s": 0.3, "time_constant_set_in_answer": False},
   {"name": "sr1", "sensitivity_V": 1e-4, "sensitivity_set_in_answer": True,
    "time_constant_s": 0.3, "time_constant_set_in_answer": False}
 ],
 "gate_current_reads": [
   {"name": "k_2400_tg_curr", "nplc": 1.0, "nplc_set_in_answer": False},
   {"name": "k_2400_bg_curr", "nplc": 1.0, "nplc_set_in_answer": False}
 ],
 "excitation_V": 1.0,
 "bias_resistor_ohm": 1e8,
 "n_fans": 1,
 "stated_wall_clock_h": 6.0,
 "flags": [],
 "notes": "cell 48: multimegasweep, slow [magnet.field] = stitched B_vec (138 rows, 0.6 -> 10 T: d(1/B)=0.03 to 1.25 T, 0.0125 to 2.76 T, then 0.1 T uniform in B), fast [k_tg.volt, k_bg.volt] co-swept from calc_gate_voltages(n_vec, D=0, run-5 CAL c_tg=2.796e-3, c_bg=2.161e-3, n_offset=-0.0894, D_offset=-0.013) with n_vec = np.arange(-1.25, 3.2001, 0.05) in 1e12 cm^-2 (90 pts); slow_delay 3.0 / fast_delay 1.0 passed explicitly. sr1 sensitivity 100 uV set in the answer cell; sr1 tau 0.3 s and sr0 sens 0.02 / tau 0.3 s inherited from the cell-44 close_out(restore=state0) printed readback (cell 46 is a read-only namespace probe). Gate nplci (1,1) from that same readback, re-asserted in the precondition block. Drive 1.0 V / 13.777 Hz asserted; bias_resistor 100e6 from meas_config (cell 23). Wall clock from cell 47: '~6 h realistic' (5.5 h floor), ETA ~11:26."
}
json.dump(out, open("/grade-run/output.json", "w"), indent=1)
print("ok")
