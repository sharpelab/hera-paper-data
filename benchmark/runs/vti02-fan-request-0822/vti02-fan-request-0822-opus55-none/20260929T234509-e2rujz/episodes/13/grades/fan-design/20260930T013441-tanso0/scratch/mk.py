import json, numpy as np
from hera.analysis import field_invB

B = np.hstack((field_invB(0.6, 3.0, 108), np.round(np.arange(3.1, 9.0 + 1e-9, 0.1), 4)))

notes = (
    "Cell 48 (trailing, unexecuted): multimegasweep, slow magnet.field over "
    "B_vec = hstack(field_invB(0.6,3.0,108), arange(3.1,9.0,0.1)) = 168 stitched rows; "
    "fast co-swept (k_tg.volt,k_bg.volt) from calc_gate_voltages over np.linspace(-1.20,3.25,91) "
    "in 1e12 cm^-2 at D = 0, using the run-5 calibration committed in the cell "
    "(c_tg 2.796e-3, c_bg 2.161e-3, n_offset -0.0894, D_offset -0.013). "
    "slow_delay=3.0, fast_delay=1.0 are the cell's own constants. "
    "sr1.sensitivity(100e-6) is set in the cell; sr0 sensitivity 0.02 V and both tau = 0.3 s are "
    "inherited from the executed close_out(restore=state0) readback in cell 44, which also reports "
    "tg/bg nplci = 1. Drive sr1.amplitude 1.0 V through the device card's 100 MOhm bias resistor; "
    "headline run time 6 h 45 m from the cell-47 markdown."
)

out = {
    "status": "extracted",
    "landed": "fan",
    "form": "2d_megasweep",
    "field_mode": "stitched",
    "B_values": [round(float(x), 6) for x in B],
    "n_min_cm2": -1.20e12,
    "n_max_cm2": 3.25e12,
    "n_columns": 91,
    "D": 0.0,
    "slow_axis": "B",
    "slow_delay_s": 3.0,
    "fast_delay_s": 1.0,
    "lockins": [
        dict(name="sr0", sensitivity_V=0.02, sensitivity_set_in_answer=False,
             time_constant_s=0.3, time_constant_set_in_answer=False),
        dict(name="sr1", sensitivity_V=1e-4, sensitivity_set_in_answer=True,
             time_constant_s=0.3, time_constant_set_in_answer=False),
    ],
    "gate_current_reads": [
        dict(name="k_tg_curr", nplc=1.0, nplc_set_in_answer=False),
        dict(name="k_bg_curr", nplc=1.0, nplc_set_in_answer=False),
    ],
    "excitation_V": 1.0,
    "bias_resistor_ohm": 1e8,
    "n_fans": 1,
    "stated_wall_clock_h": 6.75,
    "flags": [],
    "notes": notes,
}

with open("/grade-run/output.json", "w") as f:
    json.dump(out, f, indent=1)
print("ok")
