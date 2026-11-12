import json, numpy as np
B = np.hstack(([0.0, 0.5], 1 / np.arange(1.0, 1 / 1.5, -0.03), 1 / np.arange(1 / 1.5, 1 / 4.5, -0.012), np.arange(4.5, 10.0001, 0.25)))
B = np.unique(np.round(B, 3))
B = B[np.hstack((np.diff(B) > 0.015, True))]
out = {
    "status": "extracted",
    "landed": "fan",
    "form": "2d_megasweep",
    "field_mode": "stitched",
    "B_values": [float(x) for x in B],
    "n_min_cm2": -1.24e12,
    "n_max_cm2": 3.24e12,
    "n_columns": 150,
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
    "stated_wall_clock_h": 5.25,
    "flags": [],
    "notes": (
        "Cell 48 (trailing, unexecuted) issues s.multimegasweep([magnet.field],[B_vec],[k_tg.volt,k_bg.volt],"
        "[Vtg_vec,Vbg_vec], slow_delay=3.0, fast_delay=1.0). Fast axis np.linspace(-1.24,3.24,150) in 1e12 cm^-2 "
        "at D=0 via calc_gate_voltages with the cell's run-5 CAL (c_tg 2.796e-3, c_bg 2.161e-3, n_offset -0.0894, "
        "D_offset -0.013), giving Vtg -0.288..+0.995 V and Vbg -0.480..+1.181 V, inside the validators; the markdown "
        "notes the spot checks imply an n-scale ~0.90x this geometry prior, so values are left unscaled. Slow axis is "
        "a stitched 73-row B vector (0, 0.5; d(1/B)=0.03 on 1-1.5 T; 0.012 on 1.5-4.5 T; 0.25 T on 4.5-10 T), "
        "reproduced in a scratch script. sr1 sensitivity set to 100 uV in cell 48; sr0 sensitivity 0.02 V, both taus "
        "0.3 s, drive 1.0 V and nplci 1/1 inherited from the cell-44 close_out(restore=state0) readback (cell 46 is a "
        "read-only probe). Bias resistor 100 MOhm from device_card.md. Stated ETA ~5 h 15 m in cell 47."
    ),
}
json.dump(out, open("/grade-run/output.json", "w"), indent=1)
print("ok")
