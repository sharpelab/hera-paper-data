import numpy as np, json
from hera.analysis import field_invB
FL_MAX = 33.1
segs = [(0.6, 1.0, 1/(3*16.0)), (1.0, 3.5, 1/(3*FL_MAX)), (3.5, 10.0, 0.005)]
B_parts = [field_invB(a, b, int(np.ceil((1/a - 1/b)/d)) + 1) for a, b, d in segs]
B_vec = np.unique(np.round(np.hstack(B_parts), 5))
out = {
    "status": "extracted",
    "landed": "fan",
    "form": "2d_megasweep",
    "field_mode": "stitched",
    "B_values": [float(x) for x in B_vec],
    "n_min_cm2": 1.2e12,
    "n_max_cm2": 3.2e12,
    "n_columns": 76,
    "D": 0.0,
    "slow_axis": "B",
    "slow_delay_s": 3.0,
    "fast_delay_s": 1.0,
    "lockins": [
        {"name": "sr0", "sensitivity_V": 0.02, "sensitivity_set_in_answer": False,
         "time_constant_s": 0.3, "time_constant_set_in_answer": False},
        {"name": "sr1", "sensitivity_V": 1e-4, "sensitivity_set_in_answer": True,
         "time_constant_s": 0.3, "time_constant_set_in_answer": False},
    ],
    "gate_current_reads": [
        {"name": "k_2400_tg_curr", "nplc": 1.0, "nplc_set_in_answer": False},
        {"name": "k_2400_bg_curr", "nplc": 1.0, "nplc_set_in_answer": False},
    ],
    "excitation_V": 1.0,
    "bias_resistor_ohm": 1e8,
    "n_fans": 1,
    "stated_wall_clock_h": 5.25,
    "flags": [],
    "notes": (
        "Cell 48 (last code cell, unexecuted) issues s.multimegasweep([magnet.field],[B_vec],"
        "[k_tg.volt,k_bg.volt],[Vtgs,Vbgs], slow_delay=3.0, fast_delay=1.0). Slow axis is a stitched "
        "1/B-uniform vector: field_invB over three segments (0.6-1.0 T at d(1/B)=1/48, 1.0-3.5 T at "
        "1/(3*33.1), 3.5-10 T at 0.005) hstacked and np.unique'd -> 143 rows, 0.6 to 10.0 T (reproduced "
        "in a scratch script). Fast axis np.linspace(1.2,3.2,76)e12 cm^-2 at D=0 V/nm via "
        "calc_gate_voltages with the cell's run-5 CAL (Vtg +0.411..+0.984, Vbg +0.425..+1.166 V, inside "
        "the cell-18 validators). sr1 sensitivity set to 100 uV in the answer; sr1/sr0 tau 0.3 s and sr0 "
        "sens 20 mV inherited from the cell-44 close_out(restore=state0) readback, which also gives "
        "drive 1.0 V and tg/bg nplci = 1.0 (the answer only asserts nplci, does not set it). Bias "
        "resistor 100 MOhm from meas_config (cell 23) and the device card. ETA '~5h15m' stated in the "
        "cell-47 markdown. The markdown also declines a hole-side fan; no probe is issued."
    ),
}
json.dump(out, open("/grade-run/output.json", "w"), indent=1)
print(len(B_vec), B_vec[0], B_vec[-1])
