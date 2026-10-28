# Session calibration commit — cnp-and-dline-calibration output (run 4).
# ratio DATA-CALIBRATED (CNP slope, sr1+sr2 mean); absolute scale GEOMETRY PRIOR
# (c_tg anchored, 15.6 nm hBN κ=3) pending SdH/QH lever-arm upgrade.
import scipy.constants as cst

C_TG = cst.epsilon_0 * 3.0 / 15.6e-9        # 1.7027e-3 F/m^2 — anchor
RATIO = 1.2839                               # c_bg/c_tg, run 4 CNP slope
C_BG = RATIO * C_TG                          # 2.1861e-3 F/m^2
N_OFFSET = -2.407e14                         # m^-2, from +22.6 mV intercept
cal = GateCalibration(C_TG, C_BG, n_offset=N_OFFSET, D_offset=0.0)

def d0_gates(n12):
    """(V_tg, V_bg) on the D=0 line at density n12 [1e12 cm^-2]."""
    n_t = n12 * 1e16 - N_OFFSET
    vbg = n_t * cst.e / (2 * C_TG * RATIO)
    return RATIO * vbg, vbg

for n12 in (-6, -3, 3, 6):
    vt, vb = d0_gates(n12)
    n_chk, D_chk = cal.n_D(vt, vb)
    print(f"n={n12:+d}e12 @ D=0: V_tg={vt:+.4f}, V_bg={vb:+.4f}  "
          f"(roundtrip n={n_chk*1e-16:+.3f}e12, D={D_chk:.2e} V/m)")
