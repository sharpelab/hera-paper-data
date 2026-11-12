import json, numpy as np
from hera.analysis import field_invB
fan_B = np.r_[0.0, 0.5, 0.75, 1.0, field_invB(1.5, 10.0, 86)]
out = {
    "status": "extracted", "landed": "fan", "form": "2d_megasweep", "field_mode": "stitched",
    "B_values": [round(float(x), 6) for x in fan_B],
    "n_min_cm2": -1.20e12, "n_max_cm2": 3.20e12, "n_columns": 111, "D": 0.0,
    "slow_axis": "B", "slow_delay_s": 3.0, "fast_delay_s": 3.0,
    "lockins": [
        {"name": "sr0", "sensitivity_V": 0.02, "sensitivity_set_in_answer": False,
         "time_constant_s": 0.3, "time_constant_set_in_answer": False},
        {"name": "sr1", "sensitivity_V": 1e-4, "sensitivity_set_in_answer": True,
         "time_constant_s": 0.3, "time_constant_set_in_answer": False}],
    "gate_current_reads": [
        {"name": "k_2400_tg_curr", "nplc": 1.0, "nplc_set_in_answer": False},
        {"name": "k_2400_bg_curr", "nplc": 1.0, "nplc_set_in_answer": False}],
    "excitation_V": 1.0, "bias_resistor_ohm": 1e8, "n_fans": 1, "stated_wall_clock_h": 11.0,
    "flags": [],
    "notes": (
        "Cell 48: s.multimegasweep([magnet.field],[fan_B],[k_tg.volt,k_bg.volt],[fan_tg,fan_bg],"
        "slow_delay=3.0,fast_delay=3.0); fan_B = np.r_[0.0,0.5,0.75,1.0,field_invB(1.5,10.0,86)] "
        "(90 pts, stitched: 4 coarse preview points then uniform 1/B from 1.5 to 10 T). Density "
        "fan_n = np.linspace(-1.20,3.20,111) in 1e12 cm^-2 at D = 0 V/nm via calc_gate_voltages with "
        "the cell's explicit run-5 fit (c_tg=2.796e-3, c_bg=2.1607e-3 F/m^2, n_offset=-0.0894, "
        "D_offset=-0.013). sr1 sensitivity 100 uV is set in cell 48; sr0 sensitivity 0.02 and both "
        "taus 0.3 s are inherited from the cell-44 close_out(restore=state0) readback, which also "
        "prints tg/bg nplci = 1.0 (cell 48 only asserts them). Drive 1 V through the 100 MOhm bias "
        "resistor (meas_config). Markdown cell 47 header states ETA ~11 h (body prices ~10.4 h with "
        "margin); a denser 0.75-1.5 T extension (~100 rows, ~10 h) is explicitly deferred, not issued."),
}
json.dump(out, open("/grade-run/output.json", "w"), indent=1)
print("ok")
