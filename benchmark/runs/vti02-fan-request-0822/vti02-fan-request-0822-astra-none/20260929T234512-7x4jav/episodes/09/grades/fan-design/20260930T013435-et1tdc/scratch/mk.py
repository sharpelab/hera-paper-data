import numpy as np, json
from hera.analysis import field_invB
fan_B = np.r_[0.0, np.round(np.arange(.5, 1.41, .1), 8), field_invB(1.5, 10., 85)]
out = {
    "status": "extracted", "landed": "fan", "form": "2d_megasweep", "field_mode": "stitched",
    "B_values": [round(float(x), 6) for x in fan_B],
    "n_min_cm2": -1.2e12, "n_max_cm2": 3.2e12, "n_columns": 111, "D": 0.0,
    "slow_axis": "B", "slow_delay_s": 3.0, "fast_delay_s": 0.0,
    "lockins": [
        {"name": "sr0", "sensitivity_V": 0.02, "sensitivity_set_in_answer": False,
         "time_constant_s": 0.3, "time_constant_set_in_answer": False},
        {"name": "sr1", "sensitivity_V": 1e-4, "sensitivity_set_in_answer": True,
         "time_constant_s": 0.3, "time_constant_set_in_answer": False}],
    "gate_current_reads": [
        {"name": "k_2400_tg_curr", "nplc": 1.0, "nplc_set_in_answer": False},
        {"name": "k_2400_bg_curr", "nplc": 1.0, "nplc_set_in_answer": False}],
    "excitation_V": 1.0, "bias_resistor_ohm": 1e8, "n_fans": 1, "stated_wall_clock_h": 12.5,
    "flags": [],
    "notes": (
        "cell 48: multimegasweep([magnet.field],[fan_B],[k_tg.volt,k_bg.volt],[fan_vtg,fan_vbg], "
        "slow_delay=3.0, fast_delay=0.0); fan_B = np.r_[0.0, arange(0.5,1.41,0.1), field_invB(1.5,10.,85)] "
        "= 96 stitched setpoints (0 T reference + 10 coarse uniform + 85 inverse-B). Densities are "
        "np.linspace(-1.2,3.2,111) in 1e12 cm^-2, converted to gates in-cell with the run-5 fit "
        "(c_tg=2.7961e-3, c_bg=2.1607e-3 F/m^2, n_offset=-0.0894e12, D_offset=-0.013 V/nm) at D=0 V/nm; "
        "markdown cell 47 states ~12h30m. The 3 s effective per-point dwell lives in the register_run_before "
        "hook, not fast_delay. sr1 sensitivity set to 100 uV in the answer; sr0 0.02 V and both taus 0.3 s "
        "inherited from the cell-44 close_out(restore=state0) readback (that restore had put sr1 back at 2 uV); "
        "gate NPLC 1 from the same readback and re-asserted in cell 48."),
}
json.dump(out, open('/grade-run/output.json', 'w'), indent=1)
print('ok')
