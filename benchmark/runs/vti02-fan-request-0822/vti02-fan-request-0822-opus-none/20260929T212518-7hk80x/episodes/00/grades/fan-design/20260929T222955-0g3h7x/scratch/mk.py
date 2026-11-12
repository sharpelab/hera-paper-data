import json, numpy as np
B = np.round(np.concatenate(([0.0, 0.2, 0.4, 0.6, 0.8], 1.0 / np.linspace(1.0, 0.1, 145))), 5)
notes = (
 "Answer is cells 47 (markdown) + 48 (unexecuted code, landau-fan). Cell 48: "
 "multimegasweep([magnet.field],[B_vec],[k_tg.volt,k_bg.volt],[Vtg_vec,Vbg_vec], slow_delay=2.0, fast_delay=0.5); "
 "B_vec = round(concatenate(([0,0.2,0.4,0.6,0.8], 1.0/linspace(1.0,0.1,145))),5) -> 150 rows, a 5-row uniform-in-B "
 "low-field leg joined to a 145-row uniform-in-1/B leg from 1 to 10 T, hence field_mode stitched and B_values. "
 "Fast axis n_vec = round(arange(-1.20,3.2001,0.040),4) = 111 pts from -1.20 to +3.20 (units 1e12 cm^-2 per the "
 "calc_gate_voltages docstring) at D = 0, using the in-cell run-5 calibration CAL (c_tg=2.796e-3, c_bg=2.161e-3, "
 "n_offset=-0.0894, D_offset=-0.013). Cell 48 sets sr1.sensitivity(100e-6); sr0 sensitivity 0.02 V and both tau = 0.3 s "
 "are inherited from the executed close_out(restore=state0) readback in cell 44 (drive_V 1.0, sr0_sens 0.02, sr0_tau 0.3, "
 "sr1_sens 2e-6, sr1_tau 0.3, tg/bg_nplci 1.0). Excitation 1.0 V through bias_resistor 100e6 from meas_config (cell 23). "
 "nplci is asserted == 1, not set. Stated run time ~5h10m (4.4 h nominal) in the cell-47 header."
)
out = {
 "status": "extracted", "landed": "fan", "form": "2d_megasweep", "field_mode": "stitched",
 "B_values": [float(x) for x in B],
 "n_min_cm2": -1.20e12, "n_max_cm2": 3.20e12, "n_columns": 111, "D": 0.0,
 "slow_axis": "B", "slow_delay_s": 2.0, "fast_delay_s": 0.5,
 "lockins": [
  {"name": "sr0", "sensitivity_V": 0.02, "sensitivity_set_in_answer": False,
   "time_constant_s": 0.3, "time_constant_set_in_answer": False},
  {"name": "sr1", "sensitivity_V": 1e-4, "sensitivity_set_in_answer": True,
   "time_constant_s": 0.3, "time_constant_set_in_answer": False}],
 "gate_current_reads": [
  {"name": "k_2400_tg_curr", "nplc": 1.0, "nplc_set_in_answer": False},
  {"name": "k_2400_bg_curr", "nplc": 1.0, "nplc_set_in_answer": False}],
 "excitation_V": 1.0, "bias_resistor_ohm": 1e8, "n_fans": 1,
 "stated_wall_clock_h": 5.17,
 "flags": [],
 "notes": notes,
}
with open("/grade-run/output.json", "w") as f:
    json.dump(out, f, indent=1)
print("written")
