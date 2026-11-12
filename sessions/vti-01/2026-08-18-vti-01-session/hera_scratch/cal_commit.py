# === cnp-and-dline-calibration commit (run 7) — session (n, D) conversion ===
# Two-tier provenance: ratio DATA-CALIBRATED (c_bg/c_tg = 0.7222, run 7 CNP fit,
# sr1/sr3 spread 0.4%); absolute scale GEOMETRY PRIOR (c_tg anchored, 14.9 nm hBN)
# pending the quantum-Hall lever-arm upgrade. Full contract: device card +
# ana cells 17-20.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

c_tg_cal = 1.7827e-3        # F/m^2 — ANCHOR (geometry prior)
c_bg_cal = 1.2874e-3        # F/m^2 — ratio-calibrated (0.7222 x c_tg)
n_off_e12 = -0.0593         # 1e12 cm^-2 (display units for calc_gate_voltages)
cal = GateCalibration(c_tg_cal, c_bg_cal, n_offset=-5.934e14, D_offset=0.0)  # SI

def d0_line(ns_e12, tg_lim=0.8, bg_lim=5.0):
    """Paired (Vtg, Vbg, n) vectors along D=0, clipped by DROPPING (never clamp).
    ns_e12 in 1e12 cm^-2. Realized window: n in [-1.837, +1.720]e12."""
    ns_e12 = np.asarray(ns_e12, float)
    Vt, Vb = calc_gate_voltages(ns_e12, np.zeros_like(ns_e12),
                                c_tg_cal, c_bg_cal, n_offset=n_off_e12)
    Vt, Vb = np.asarray(Vt), np.asarray(Vb)
    keep = (np.abs(Vt) <= tg_lim) & (np.abs(Vb) <= bg_lim)
    return Vt[keep], Vb[keep], ns_e12[keep]

# sanity: roundtrip + window print
_vt, _vb, _nk = d0_line(np.linspace(-2.0, 2.0, 801))
_n, _D = calc_nD(_vt, _vb, c_tg_cal, c_bg_cal, n_offset=n_off_e12)
print(f"D=0 designer live: n {_nk.min():+.3f}..{_nk.max():+.3f} e12, "
      f"max|D| roundtrip {np.abs(np.asarray(_D)).max():.2e} V/nm, "
      f"Vtg {_vt.min():+.3f}..{_vt.max():+.3f}, Vbg {_vb.min():+.3f}..{_vb.max():+.3f}")
