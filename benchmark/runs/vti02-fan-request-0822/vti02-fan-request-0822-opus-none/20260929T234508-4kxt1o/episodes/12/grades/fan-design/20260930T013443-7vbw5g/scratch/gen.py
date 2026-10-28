import json, numpy as np
from hera.analysis import field_invB
B = np.unique(np.round(np.concatenate([np.array([0.30, 0.45, 0.60, 0.80, 0.95, 1.10]),
                                       field_invB(1.2, 10.0, 71)]), 4))
out = {
    "status": "extracted",
    "landed": "fan",
    "form": "2d_megasweep",
    "field_mode": "stitched",
    "B_values": [float(x) for x in B],
    "n_min_cm2": -1.2e12,
    "n_max_cm2": 3.2e12,
    "n_columns": 89,
    "D": 0.0,
    "slow_axis": "B",
    "slow_delay_s": 3.0,
    "fast_delay_s": 1.0,
    "lockins": [
        {"name": "sr0", "sensitivity_V": 0.02, "sensitivity_set_in_answer": False,
         "time_constant_s": 0.3, "time_constant_set_in_answer": False},
        {"name": "sr1", "sensitivity_V": 100e-6, "sensitivity_set_in_answer": True,
         "time_constant_s": 0.3, "time_constant_set_in_answer": False},
    ],
    "gate_current_reads": [
        {"name": "k_2400_tg_curr", "nplc": 1.0, "nplc_set_in_answer": False},
        {"name": "k_2400_bg_curr", "nplc": 1.0, "nplc_set_in_answer": False},
    ],
    "excitation_V": 1.0,
    "bias_resistor_ohm": 1e8,
    "n_fans": 1,
    "stated_wall_clock_h": 3.83,
    "flags": [],
    "notes": (
        "Answer = measure cells 47-48 (cell 48 not yet executed). Cell 48 slow axis is a stitched B vector: "
        "np.unique(round(concat([0.30,0.45,0.60,0.80,0.95,1.10], field_invB(1.2,10.0,71)),4)) = 77 rows, 0.30 -> 10.0 T; "
        "fast axis is (k_tg.volt, k_bg.volt) co-swept via calc_gate_voltages over n = np.arange(-1.20, 3.2001, 0.05) "
        "(89 columns, units 1e12 cm^-2) at D = 0, using the run-5 CAL committed in-cell (c_tg 2.796e-3 from the 9.5 nm "
        "geometry prior, c_bg/c_tg ratio data-calibrated, n_offset -0.0894e12, D_offset -0.013 V/nm). "
        "multimegasweep(slow_delay=3.0, fast_delay=1.0). sr1 sensitivity 100 uV is set in cell 48; sr0 sens 0.02 V, both "
        "tau 0.3 s and both Keithley nplci 1.0 are inherited from the close_out(restore=state0) readback in cell 44, which "
        "supersedes the run 6/7 metadata snapshots. Drive 1.0 V / 13.777 Hz through the device card's 100 MOhm bias "
        "resistor (same readback). Stated run time from the cell-47 markdown header: ETA ~09:18, approx 3h50m."
    ),
}
json.dump(out, open("/grade-run/output.json", "w"), indent=1)
print("written", len(B))
