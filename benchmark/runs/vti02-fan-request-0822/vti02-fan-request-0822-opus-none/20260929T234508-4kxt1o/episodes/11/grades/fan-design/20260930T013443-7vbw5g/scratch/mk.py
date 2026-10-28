import json, numpy as np
B_apex = np.array([0.25, 0.50, 0.75, 1.00])
B_core = 1.0 / np.linspace(1/1.2, 1/5.0, 55)
B_high = np.arange(5.25, 10.0 + 1e-9, 0.25)
B = [float(x) for x in np.round(np.concatenate([B_apex, B_core, B_high]), 4)]

notes = (
    "Cell 48 (trailing code cell): s.multimegasweep([magnet.field],[B_vec],[k_tg.volt,k_bg.volt],"
    "[Vtg_vec,Vbg_vec], slow_delay=2.0, fast_delay=1.0). B_vec is stitched: 4 apex rows 0.25-1.0 T + "
    "55 rows uniform in 1/B (1.2-5.0 T) + 20 rows uniform in B (5.25-10.0 T, 0.25 T) = 79 rows. "
    "Fast axis n = np.round(np.arange(-33,88)*0.037,6) e12 cm^-2 (-1.221..+3.219e12, 121 pts) at D=0 via "
    "calc_gate_voltages with the session's run-5 calibration committed in the cell (c_tg=2.796e-3, "
    "c_bg=2.161e-3, n_offset=-0.0894, D_offset=-0.013); absolute scale is still the 9.5 nm geometry prior. "
    "sr1 sensitivity 200 uV is set in the cell; sr0 sensitivity 0.02 V and both tau = 0.3 s are inherited "
    "from the close_out(restore=state0) readback in cell 44, which supersedes the run 6/7 snapshots; "
    "nplci 1/1 comes from that same readback and is asserted in cell 48. Drive 1.0 V through the 100 MOhm "
    "bias resistor (10 nA) from the same readback. Cell 47's header states ETA ~5 h 15 m."
)

out = {
    "status": "extracted",
    "landed": "fan",
    "form": "2d_megasweep",
    "field_mode": "stitched",
    "B_values": B,
    "n_min_cm2": -1.221e12,
    "n_max_cm2": 3.219e12,
    "n_columns": 121,
    "D": 0.0,
    "slow_axis": "B",
    "slow_delay_s": 2.0,
    "fast_delay_s": 1.0,
    "lockins": [
        {"name": "sr0", "sensitivity_V": 0.02, "sensitivity_set_in_answer": False,
         "time_constant_s": 0.3, "time_constant_set_in_answer": False},
        {"name": "sr1", "sensitivity_V": 200e-6, "sensitivity_set_in_answer": True,
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
    "notes": notes,
}
json.dump(out, open("/grade-run/output.json", "w"), indent=1)
print("ok")
