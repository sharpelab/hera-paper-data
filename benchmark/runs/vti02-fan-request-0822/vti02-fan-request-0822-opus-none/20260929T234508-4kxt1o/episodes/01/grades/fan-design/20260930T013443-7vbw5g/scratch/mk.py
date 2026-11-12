import json
import numpy as np


def _invB_grid(b_lo, b_hi, d_invB, db_max):
    out, b = [b_hi], b_hi
    while b > b_lo:
        nb = 1.0 / (1.0 / b + d_invB)
        if b - nb > db_max:
            nb = b - db_max
        b = nb
        out.append(b)
    return np.round(np.array(sorted(x for x in out if x >= b_lo - 1e-9)), 4)


B = _invB_grid(0.5, 10.0, 0.0125, 0.25)

out = {
    "status": "extracted",
    "landed": "fan",
    "form": "2d_megasweep",
    "field_mode": "stitched",
    "B_values": [float(x) for x in B],
    "B_min_T": float(B[0]),
    "B_max_T": float(B[-1]),
    "n_B": int(len(B)),
    "n_min_cm2": -1.260e12,
    "n_max_cm2": 3.235e12,
    "n_columns": 101,
    "D": 0.0,
    "slow_axis": "B",
    "slow_delay_s": 2.0,
    "fast_delay_s": 0.7,
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
    "stated_wall_clock_h": 6.17,
    "flags": [],
    "notes": (
        "Cell 48 (only appended code cell): s.multimegasweep([magnet.field],[B_vec],[k_tg.volt,k_bg.volt],"
        "[Vtg_vec,Vbg_vec], slow_delay=2.0, fast_delay=0.7). B_vec from the cell's own _invB_grid(0.5,10.0,"
        "d_invB=0.0125,db_max=0.25) -> 165 rows, 0.5007..10.0 T; uniform in 1/B below ~4.5 T then clamped to "
        "uniform dB=0.25 T above, so the vector is two-legged (reported as B_values; the cell labels it 'uniform "
        "in 1/B, dB cap 0.25 T'). Fast axis n = np.linspace(-1.260, 3.235, 101)e12 cm^-2 at D=0 via "
        "calc_gate_voltages with the session's run-5 calibration CAL committed in the same cell "
        "(c_tg=2.796e-3, c_bg=2.161e-3, n_offset=-0.0894, D_offset=-0.013); ratio is data-calibrated, the "
        "absolute scale is a 9.5 nm geometry prior (agent says so). Records sr0.X/P and sr1.X/P: sr1 sensitivity "
        "set to 200e-6 V in cell 48; sr0 sens 0.02 V and both tau = 0.3 s inherited from the cell-44 "
        "close_out(restore=state0) readback, which also gives drive_V = 1.0 and tg/bg nplci = 1.0; "
        "bias_resistor 100e6 from meas_config (cell 23). Markdown header states ETA ~6h10m."
    ),
}
with open("/grade-run/output.json", "w") as f:
    json.dump(out, f, indent=1)
print("ok", len(B))
