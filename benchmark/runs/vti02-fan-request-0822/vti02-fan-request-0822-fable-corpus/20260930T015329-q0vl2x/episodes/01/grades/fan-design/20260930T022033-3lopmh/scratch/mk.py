import numpy as np, json
B = np.unique(np.round(np.hstack((np.arange(0.3, 0.6, 0.005), np.arange(0.6, 1.3001, 0.01))), 4))
out = {
    "status": "extracted", "landed": "field_probe", "form": "probe_only",
    "B_values": [float(x) for x in B],
    "B_min_T": 0.3, "B_max_T": 1.3, "n_B": int(len(B)), "spacing": "other",
    "n_cm2": [3.2e12], "declared_columns_cm2": [], "ladder_stated_h_per_column": None,
    "D": 0.0, "slow_axis": "B", "slow_delay_s": 0.0, "fast_delay_s": 0.0,
    "lockins": [
        {"name": "sr0", "sensitivity_V": 0.02, "sensitivity_set_in_answer": False,
         "time_constant_s": 0.3, "time_constant_set_in_answer": False},
        {"name": "sr1", "sensitivity_V": 5e-6, "sensitivity_set_in_answer": True,
         "time_constant_s": 0.3, "time_constant_set_in_answer": False}],
    "gate_current_reads": [
        {"name": "k_2400_tg_curr", "nplc": 1.0, "nplc_set_in_answer": False},
        {"name": "k_2400_bg_curr", "nplc": 1.0, "nplc_set_in_answer": False}],
    "excitation_V": 1.0, "bias_resistor_ohm": 100e6,
    "n_fans": 1, "stated_wall_clock_h": 0.42,
    "flags": [],
    "notes": (
        "Trailing cells 47-48: a 1D sdh-spot-check field sweep s.sweep(magnet.field, B_vec, delay=0) at "
        "n = +3.2e12 cm^-2, D = 0 (run-5 cal constants committed in the cell: c_tg=2.796e-3, c_bg=2.161e-3, "
        "n_offset=-0.0894, D_offset=-0.013 via calc_gate_voltages -> Vtg +0.984, Vbg +1.166); no fan is issued. "
        "B_vec is piecewise: 5 mT from 0.3 to 0.6 T, 10 mT from 0.6 to 1.3 T, 131 pts. The cell is framed as "
        "pinning the coming landau-fan's B_lo but names no further density columns, so probe_only. sr1 "
        "sensitivity 5e-6 set in the cell; sr0 sens 0.02, both taus 0.3 s and both Keithley nplci 1.0 are "
        "inherited from the close_out(restore=state0) readback in cell 44; drive 1.0 V through 100 MOhm from "
        "that same readback and meas_config (cell 23). Stated time: markdown banner ETA ~25 min (used); the "
        "body's own price line says ~18 min. The appended cells issue no fan sweep at all; n_fans is given "
        "as 1 only because the schema requires >= 1, and refers to the single landau-fan this probe is a "
        "precondition to."
    ),
}
json.dump(out, open("/grade-run/output.json", "w"), indent=1)
print("ok")
