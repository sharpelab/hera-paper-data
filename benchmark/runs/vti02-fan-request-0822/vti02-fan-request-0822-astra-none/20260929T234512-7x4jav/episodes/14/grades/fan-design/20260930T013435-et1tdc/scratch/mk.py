import json, numpy as np, sys
sys.path.insert(0, '/episode')
from hera.analysis import field_invB

B = np.r_[0., 0.5, 0.75, 1., 1.25, 1.5, 1.75, field_invB(2., 10., 81)]
notes = (
    "Cell 48 (appended code cell, after md cell 47): "
    "s.multimegasweep([magnet.field],[fan_B],[k_tg.volt,k_bg.volt],[fan_tg,fan_bg],slow_delay=3.0,fast_delay=3.0). "
    "fan_B = np.r_[0,0.5,0.75,1,1.25,1.5,1.75, field_invB(2.,10.,81)] = 88 stitched rows (7 sparse uniform-B points then 81 uniform in 1/B over 2-10 T). "
    "Density axis fan_n = np.linspace(-1.2e16, 3.2e16, 111) m^-2 at nominal D = 0, converted in-cell to gate voltages with the run-5 calibration "
    "c_tg=2.7961e-3, c_bg=2.1607e-3 F/m^2, n_offset=-0.0894e16 m^-2, D_offset=-0.013e9 V/m; absolute scale is geometry-anchored and D=0 is a CNP resistance-minimum proxy. "
    "sr1 sensitivity is set to 100 uV in cell 48; sr0 sensitivity 0.02 V and both time constants 0.3 s / 24 dB are inherited from the close_out(restore=state0) readback in cell 44, "
    "which also prints tg_nplci/bg_nplci = 1.0 (re-asserted in cell 48). Drive sr1.amplitude 1.0 V through meas_config['bias_resistor'] = 100e6 ohm. "
    "Stated time: md cell 47 header line 'ETA ~16:23 (approx 11h)'; the body prices ~10.3 h before margin."
)
out = {
    "status": "extracted",
    "landed": "fan",
    "form": "2d_megasweep",
    "field_mode": "stitched",
    "B_values": [round(float(x), 9) for x in B],
    "n_min_cm2": -1.2e12,
    "n_max_cm2": 3.2e12,
    "n_columns": 111,
    "D": 0.0,
    "slow_axis": "B",
    "slow_delay_s": 3.0,
    "fast_delay_s": 3.0,
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
    "excitation_V": 1.0,
    "bias_resistor_ohm": 1e8,
    "n_fans": 1,
    "stated_wall_clock_h": 11.0,
    "flags": [],
    "notes": notes,
}
with open('/grade-run/output.json', 'w') as f:
    json.dump(out, f, indent=1)
print("written")
