import numpy as np, json
B_lo = 1.0309096913954
B_hi = 7.1
u1 = np.linspace(1/B_lo, 1/3.5, int(np.ceil((1/B_lo - 1/3.5)/(.01/1.01))) + 1)
u2 = np.linspace(1/3.5, 1/B_hi, int(np.ceil((1/3.5 - 1/B_hi)/(.5/143))) + 1)
B_fan = [round(float(x), 6) for x in 1/np.r_[u1, u2[1:]]]

out = {
    "status": "extracted",
    "landed": "fan",
    "form": "2d_megasweep",
    "field_mode": "stitched",
    "B_values": B_fan,
    "n_min_cm2": 2.8e12,
    "n_max_cm2": 3.2e12,
    "n_columns": 10,
    "D": 0.0,
    "slow_axis": "B",
    "slow_delay_s": 1.0,
    "fast_delay_s": 3.0,
    "lockins": [
        {"name": "sr0", "sensitivity_V": 0.02, "sensitivity_set_in_answer": False,
         "time_constant_s": 0.3, "time_constant_set_in_answer": False},
        {"name": "sr1", "sensitivity_V": 5e-05, "sensitivity_set_in_answer": True,
         "time_constant_s": 0.3, "time_constant_set_in_answer": False},
    ],
    "gate_current_reads": [
        {"name": "k_2400_tg_curr", "nplc": 1.0, "nplc_set_in_answer": False},
        {"name": "k_2400_bg_curr", "nplc": 1.0, "nplc_set_in_answer": False},
    ],
    "excitation_V": 1.0,
    "bias_resistor_ohm": 1e8,
    "n_fans": 1,
    "stated_wall_clock_h": 2.333,
    "flags": [],
    "notes": (
        "Cell 48 (appended with md cell 47): s.multimegasweep([magnet.field],[B_fan],"
        "[k_tg.volt,k_bg.volt],[Vtgs,Vbgs],slow_delay=1,fast_delay=3). B_fan is two legs "
        "uniform in 1/B joined at 3.5 T (71 + 42 pts = 113 rows, 1.03090969 -> 7.1 T ascending), "
        "recomputed in a scratch script. Densities np.linspace(2.8,3.2,10) in 1e12 cm^-2 at D = 0 "
        "via calc_gate_voltages with the run-5 calibration CAL_FAN committed in the cell (absolute "
        "scale is the geometry prior, ~10-15% uncertainty per the markdown). sr1 sensitivity set to "
        "50 uV in cell 48; sr0 sens 0.02 V, both tau = 0.3 s and both nplci = 1 are inherited from "
        "the close_out(restore=state0) readback in cell 44 (which had reset sr1 to 2 uV). Drive 1 V / "
        "13.777 Hz through the 100 MOhm bias resistor (meas_config, asserted in cell 48). ETA "
        "'2h20m' from the cell-47 header."
    ),
}
with open("/grade-run/output.json", "w") as f:
    json.dump(out, f, indent=1)
print("written")
