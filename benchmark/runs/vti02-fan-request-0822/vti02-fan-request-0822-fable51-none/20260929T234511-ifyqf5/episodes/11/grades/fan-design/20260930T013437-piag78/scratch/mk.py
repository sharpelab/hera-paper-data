import json, numpy as np
from hera.analysis import field_invB
B = np.unique(np.round(np.hstack(([0.0, 0.5, 0.75], field_invB(1.0, 5.0, 68), np.arange(5.25, 10.0001, 0.25))), 4))
out = {
    "status": "extracted", "landed": "fan", "form": "2d_megasweep", "field_mode": "stitched",
    "B_values": [float(x) for x in B],
    "n_min_cm2": -1.25e12, "n_max_cm2": 3.25e12, "n_columns": 151, "D": 0.0,
    "slow_axis": "B", "slow_delay_s": 3.0, "fast_delay_s": 0.5,
    "lockins": [
        {"name": "sr0", "sensitivity_V": 0.02, "sensitivity_set_in_answer": False,
         "time_constant_s": 0.1, "time_constant_set_in_answer": True},
        {"name": "sr1", "sensitivity_V": 1e-4, "sensitivity_set_in_answer": True,
         "time_constant_s": 0.1, "time_constant_set_in_answer": True}],
    "gate_current_reads": [
        {"name": "k_2400_tg_curr", "nplc": 1.0, "nplc_set_in_answer": False},
        {"name": "k_2400_bg_curr", "nplc": 1.0, "nplc_set_in_answer": False}],
    "excitation_V": 1.0, "bias_resistor_ohm": 1e8, "n_fans": 1, "stated_wall_clock_h": 4.75,
    "flags": [],
    "notes": (
        "Cell 48 (trailing, unexecuted) is a multimegasweep: slow magnet.field over a stitched 91-row vector "
        "B_rows = unique(round(hstack([0, 0.5, 0.75], field_invB(1.0, 5.0, 68), arange(5.25, 10.0001, 0.25)), 4)), 0 -> 10 T; "
        "fast (k_tg.volt, k_bg.volt) co-swept along the run-5 D = 0 line via calc_gate_voltages over "
        "n = arange(-1.25, 3.25001, 0.03) x151 in 1e12 cm^-2 (CAL c_tg = 2.796e-3 geometry prior, c_bg = 2.161e-3, "
        "n_offset = -0.0894, D_offset = -0.013); slow_delay = 3.0, fast_delay = 0.5. "
        "Cell 48 sets sr1 sensitivity 100 uV and sr0/sr1 tau 0.1 s (restored in finally); sr0 sensitivity 0.02 V and "
        "nplci 1/1 are inherited from the cell-44 close_out(restore=state0) readback, which also gives drive 1.0 V into "
        "the 100 MOhm bias resistor (10 nA). Markdown cell 47 states ETA ~4h45m; its pricing paragraph says ~4.4 h nominal."
    ),
}
json.dump(out, open("/grade-run/output.json", "w"), indent=1)
print("ok")
