import numpy as np, json
B = np.r_[0.0, 1/np.linspace(1/1.5, 1/4.0, 51), np.round(np.arange(4.1, 10.0001, 0.1), 4)]
out = {
 "status": "extracted", "landed": "fan", "form": "2d_megasweep", "field_mode": "stitched",
 "B_values": [round(float(x), 6) for x in B],
 "n_min_cm2": -1.2e12, "n_max_cm2": 3.2e12, "n_columns": 111, "D": 0.0,
 "slow_axis": "B", "slow_delay_s": 3.0, "fast_delay_s": 3.0,
 "lockins": [
   {"name": "sr0", "sensitivity_V": 0.02, "sensitivity_set_in_answer": True,
    "time_constant_s": 0.3, "time_constant_set_in_answer": False},
   {"name": "sr1", "sensitivity_V": 1e-4, "sensitivity_set_in_answer": True,
    "time_constant_s": 0.3, "time_constant_set_in_answer": False}],
 "gate_current_reads": [
   {"name": "k_2400_tg_curr", "nplc": 1.0, "nplc_set_in_answer": False},
   {"name": "k_2400_bg_curr", "nplc": 1.0, "nplc_set_in_answer": False}],
 "excitation_V": 1.0, "bias_resistor_ohm": 1e8, "n_fans": 1, "stated_wall_clock_h": 14.0,
 "flags": [],
 "notes": ("Cell 48 (trailing, unexecuted) is the landau-fan: s.multimegasweep([magnet.field],[B_fan],"
   "[k_tg.volt,k_bg.volt],[Vtg_fan,Vbg_fan], slow_delay=3.0, fast_delay=3.0). "
   "B_fan = np.r_[0.0, 1/np.linspace(1/1.5,1/4.0,51), np.arange(4.1,10.0001,0.1)]: 112 stitched points "
   "(B=0 baseline, 51 inverse-B rows 1.5-4 T, 60 uniform 0.1 T rows 4.1-10 T). Densities are the cell's own "
   "n_nominal = np.linspace(-1.2,3.2,111)*1e16 m^-2 at nominal D=0, converted to TG -0.277033..+0.983594 V / "
   "BG -0.465040..+1.166281 V via the session's run-5 GateCalibration (ratio/offsets session-fitted, absolute "
   "scale anchored to geometry). sr0/sr1 sensitivities set in the cell (0.02 V, 100 uV); tau 0.3 s and gate "
   "NPLC 1.0 inherited from the cell-44 close_out(restore=state0) readback. Drive 1 V through the 100 MOhm "
   "bias resistor (meas_config, asserted in the cell). Headline 14 h stated in the markdown cell 47 and plan.md step 4.")
}
json.dump(out, open('/grade-run/output.json', 'w'), indent=1)
print('ok')
