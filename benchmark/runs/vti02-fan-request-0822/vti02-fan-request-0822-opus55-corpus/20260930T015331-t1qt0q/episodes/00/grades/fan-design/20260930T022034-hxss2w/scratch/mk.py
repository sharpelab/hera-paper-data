import numpy as np, json
B_LO, B_HI, DINV_LO, R_STEP = 1.0, 10.0, 0.0099, 0.016
B_X = R_STEP / DINV_LO
s1 = 1.0 / np.arange(1 / B_LO, 1 / B_X, -DINV_LO)
s2 = np.geomspace(B_X, B_HI, int(np.ceil(np.log(B_HI / B_X) / np.log(1 + R_STEP))) + 1)
B = [float(x) for x in np.round(np.concatenate([s1, s2]), 4)]

notes = (
    "Cell 48 (appended, with markdown cell 47): s.multimegasweep([magnet.field],[B_vec],"
    "[k_tg.volt,k_bg.volt],[Vtgs,Vbgs], slow_delay=3.0, fast_delay=2.1). B_vec is stitched: "
    "1/B-uniform at d(1/B)=0.0099 from 1.0 T to 1.6162 T (39 pts), then geometric dB/B=1.6% to "
    "10.0 T (116 pts) = 155 rows; reproduced in a scratch script. Density axis "
    "np.linspace(1.80,3.25,32)e12 cm^-2 at D=0 via calc_gate_voltages with the session's run-5 "
    "calibration committed in the cell (c_tg=2.796e-3, c_bg=2.161e-3, n_offset=-0.0894, "
    "D_offset=-0.013); V_tg +0.583->+0.998, V_bg +0.647->+1.185, inside the TG/BG validators. "
    "sr1 sensitivity set to 50 uV in the answer; sr0 sens 0.02 V and both taus 0.3 s inherited "
    "from the close_out(restore=state0) readback in cell 44; nplci 1/1 likewise from that "
    "readback and asserted in the cell's precondition block. Drive 1.0 V through the device "
    "card's 100 MOhm bias resistor. Headline ETA ~4h55m from cell 47; a hole-side fan "
    "(-1.27..-0.6, ~2 h) is named as explicitly excluded/deferred, not issued."
)

out = {
    "status": "extracted",
    "landed": "fan",
    "form": "2d_megasweep",
    "field_mode": "stitched",
    "B_values": B,
    "spacing": "stitched",
    "n_min_cm2": 1.80e12,
    "n_max_cm2": 3.25e12,
    "n_columns": 32,
    "D": 0.0,
    "slow_axis": "B",
    "slow_delay_s": 3.0,
    "fast_delay_s": 2.1,
    "lockins": [
        {"name": "sr0", "sensitivity_V": 0.02, "sensitivity_set_in_answer": False,
         "time_constant_s": 0.3, "time_constant_set_in_answer": False},
        {"name": "sr1", "sensitivity_V": 5e-5, "sensitivity_set_in_answer": True,
         "time_constant_s": 0.3, "time_constant_set_in_answer": False},
    ],
    "gate_current_reads": [
        {"name": "k_2400_tg_curr", "nplc": 1.0, "nplc_set_in_answer": False},
        {"name": "k_2400_bg_curr", "nplc": 1.0, "nplc_set_in_answer": False},
    ],
    "excitation_V": 1.0,
    "bias_resistor_ohm": 1e8,
    "n_fans": 1,
    "stated_wall_clock_h": 4.92,
    "flags": [],
    "notes": notes,
}
json.dump(out, open("/grade-run/output.json", "w"), indent=1)
print("ok", len(B))
