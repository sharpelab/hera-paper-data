import json, numpy as np
B_tail = np.round(np.arange(0.2, 0.951, 0.075), 4)
B_main = np.round(1.0/np.linspace(1.0, 0.1, 73), 4)
B = [float(x) for x in np.unique(np.hstack((B_tail, B_main)))]
out = {
 "status": "extracted",
 "landed": "fan",
 "form": "2d_megasweep",
 "field_mode": "stitched",
 "B_values": B,
 "n_min_cm2": -1.25e12,
 "n_max_cm2": 3.25e12,
 "n_columns": 181,
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
 "stated_wall_clock_h": 7.0,
 "flags": [],
 "notes": "Cell 48 (last code cell) issues s.multimegasweep with magnet.field slow over a stitched B_vec and co-swept k_tg/k_bg fast, slow_delay=3.0, fast_delay=1.0. B_vec = np.arange(0.2,0.951,0.075) (11 apex rows) unioned with 1/np.linspace(1.0,0.1,73) (uniform-1/B, 1 to 10 T) = 84 rows, recomputed in a scratch script. Fast axis n = np.linspace(-1.25,3.25,181)e12 cm^-2 at D = 0 via calc_gate_voltages with the run-5 calibration committed in the cell (c_tg 2.796e-3, c_bg 2.161e-3, n_offset -0.0894, D_offset -0.013). sr1 sensitivity 100 uV is set in the cell; sr0 sens 0.02 V, both tau 0.3 s, nplci 1/1 and drive 1.0 V are inherited from the cell-44 close_out(restore=state0) readback; 100 MOhm bias resistor from device_card.md:64. The 7 h figure is stated in the cell-47 markdown."
}
json.dump(out, open("/grade-run/output.json", "w"), indent=1)
print("ok")
