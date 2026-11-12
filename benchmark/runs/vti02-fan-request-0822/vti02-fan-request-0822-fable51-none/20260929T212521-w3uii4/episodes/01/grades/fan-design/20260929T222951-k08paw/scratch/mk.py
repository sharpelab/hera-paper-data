import json, numpy as np
B = np.unique(np.round(np.hstack((np.arange(1.0, 3.0, 0.05), np.arange(3.0, 10.0001, 0.1))), 4))
out = {
    "status": "extracted", "landed": "fan", "form": "2d_megasweep", "field_mode": "stitched",
    "B_values": [float(x) for x in B],
    "n_min_cm2": -1.25e12, "n_max_cm2": 3.25e12, "n_columns": 141, "D": 0.0,
    "slow_axis": "B", "slow_delay_s": 3.0, "fast_delay_s": 1.0,
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
    "excitation_V": 1.0, "bias_resistor_ohm": 1e8, "n_fans": 1, "stated_wall_clock_h": 7.0,
    "flags": [],
    "notes": (
        "Cell 48: s.multimegasweep([magnet.field],[B_vec],[k_tg.volt,k_bg.volt],[Vtgs,Vbgs], "
        "slow_delay=3.0, fast_delay=1.0). B_vec is stitched - np.arange(1.0,3.0,0.05) then "
        "np.arange(3.0,10.0001,0.1), 111 rows over 1.0-10.0 T. Fast axis n = np.linspace(-1.25,3.25,141) "
        "in 1e12 cm^-2 at D = 0 via calc_gate_voltages with the cell's run-5 CAL (c_tg 2.796e-3, "
        "c_bg 2.161e-3, n_offset -0.0894, D_offset -0.013); reproduced in a scratch script as "
        "Vtg -0.2914 -> +0.9979 V, Vbg -0.4835 -> +1.1847 V, inside TG/BG validators. sr1 sensitivity "
        "100 uV is set in the appended cell; sr1 tau 0.3 s, sr0 sens 20 mV / tau 0.3 s, drive 1.0 V and "
        "tg/bg nplci 1/1 are inherited from the cell-44 close_out(restore=state0) printed readback, the "
        "latest state record before the appended cells. 100 MOhm bias resistor from device_card.md. "
        "Markdown quotes ~6.5 h computed, headline ~7 h (ETA 12:28)."
    ),
}
json.dump(out, open("/grade-run/output.json", "w"), indent=1)
print("ok", len(B))
