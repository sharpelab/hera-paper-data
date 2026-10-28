import json
B = json.load(open('/grade-run/scratch/bvec.json'))
out = {
    "status": "extracted", "landed": "fan", "form": "2d_megasweep", "field_mode": "stitched",
    "B_values": B,
    "n_min_cm2": -1.25e12, "n_max_cm2": 3.25e12, "n_columns": 151, "D": 0.0,
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
    "excitation_V": 1.0, "bias_resistor_ohm": 1e8, "n_fans": 1, "stated_wall_clock_h": 7.5,
    "flags": [],
    "notes": (
        "Cell 48 (appended, unexecuted): s.multimegasweep([magnet.field],[B_vec],[k_tg.volt,k_bg.volt],"
        "[Vtg_vec,Vbg_vec], slow_delay=3.0, fast_delay=1.0). B_vec is stitched - uniform in 1/B "
        "(d(1/B)=0.007) from 1.25 to 5 T, then np.arange(5.0,10.0001,0.2) to 10 T, 112 rows, reproduced "
        "in a scratch script. Fast axis n = np.linspace(-1.25,3.25,151)e12 cm^-2 at D = 0 via "
        "calc_gate_voltages with the session's run-5 calibration committed in the cell (c_tg 2.796e-3, "
        "c_bg 2.161e-3, n_offset -0.0894, D_offset -0.013); V_tg -0.2914..+0.9979, V_bg -0.4835..+1.1847. "
        "sr1 sensitivity set to 100 uV in the cell; sr0 sensitivity 0.02 and both tau 0.3 s inherited from "
        "cell 44's close_out(restore=state0) readback, which also restored tg/bg nplci = 1. Drive 1.0 V "
        "through the device card's 100 MOhm bias resistor; 7 h 30 m stated in cell 47's markdown."
    ),
}
json.dump(out, open('/grade-run/output.json', 'w'), indent=1)
print("ok")
