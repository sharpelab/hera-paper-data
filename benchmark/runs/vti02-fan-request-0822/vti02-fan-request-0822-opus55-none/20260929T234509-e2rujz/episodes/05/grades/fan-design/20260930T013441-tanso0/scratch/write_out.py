import json, numpy as np
from hera.analysis import field_invB
B = np.round(np.hstack((field_invB(1.0, 3.1, 68), np.arange(3.2, 10.0001, 0.1))), 4)
out = {
 "status": "extracted",
 "landed": "fan",
 "form": "2d_megasweep",
 "field_mode": "stitched",
 "B_values": [float(x) for x in B],
 "n_min_cm2": -1.25e12,
 "n_max_cm2": 3.24e12,
 "n_columns": 150,
 "D": 0.0,
 "slow_axis": "B",
 "slow_delay_s": 3.0,
 "fast_delay_s": 1.0,
 "lockins": [
  {"name": "sr0", "sensitivity_V": 0.02, "sensitivity_set_in_answer": False,
   "time_constant_s": 0.3, "time_constant_set_in_answer": False},
  {"name": "sr1", "sensitivity_V": 1e-4, "sensitivity_set_in_answer": True,
   "time_constant_s": 0.3, "time_constant_set_in_answer": False}],
 "gate_current_reads": [
  {"name": "k_2400_tg_curr", "nplc": 1.0, "nplc_set_in_answer": False},
  {"name": "k_2400_bg_curr", "nplc": 1.0, "nplc_set_in_answer": False}],
 "excitation_V": 1.0,
 "bias_resistor_ohm": 1e8,
 "n_fans": 1,
 "stated_wall_clock_h": 9.0,
 "flags": [],
 "notes": "Cell 48 (trailing, unexecuted) issues s.multimegasweep([magnet.field],[B_vec],[k_tg.volt,k_bg.volt],[Vtg_vec,Vbg_vec], slow_delay=3.0, fast_delay=1.0); B_vec = hstack(field_invB(1.0,3.1,68), arange(3.2,10.0001,0.1)) = 137 stitched rows (uniform 1/B to 3.1 T, then 0.1 T to 10 T). Fast axis n = np.linspace(-1.25,3.24,150)e12 cm^-2 at D=0 via calc_gate_voltages with the run-5 CAL committed in the same cell (Vtg -0.291..+0.995 V, Vbg -0.484..+1.181 V, inside the cell-18 validators); the cell states the absolute density scale is the geometry prior and reads ~11% high, values left unscaled. sr1 sensitivity set to 100 uV in the answer; sr0 sensitivity 0.02 V and both tau = 0.3 s inherited from the cell-44 close_out(restore=state0) readback, which also gives drive 1.0 V and tg/bg nplci = 1.0; bias resistor 1e8 from the device card and run metadata. Stated run time: headline ~9 h in cell 47.",
}
json.dump(out, open("/grade-run/output.json", "w"), indent=1)
print("ok")
