"""Design constant-D n-linecuts; invert (n,D)->(V_tg,V_bg), check validators."""
import numpy as np
import scipy.constants as cst
from hera.analysis import GateCalibration

# calibration from run 4 (ratio data-pinned; n_offset from CNP)
n_off = -0.362e11 * 1e4   # m^-2
cal = GateCalibration.from_thicknesses(23.6e-9, 20e-9, 0, n_offset=n_off)
c_tg, c_bg = cal.c_tg, cal.c_bg
e, eps0 = cst.e, cst.epsilon_0
print(f"c_tg={c_tg:.4e}  c_bg={c_bg:.4e}  ratio={c_tg/c_bg:.4f}  n_off={cal.n_offset:.3e}")

def nD_to_V(n_cm2, D_Vnm):
    n = np.asarray(n_cm2)*1e4; D = np.asarray(D_Vnm)*1e9
    A = (n - cal.n_offset)*e          # c_tg Vtg + c_bg Vbg
    B = (D - cal.D_offset)*2*eps0     # c_tg Vtg - c_bg Vbg
    return (A+B)/(2*c_tg), (A-B)/(2*c_bg)

TG=(-7.0,6.0); BG=(-4.0,4.2)
n_scan = np.arange(1.0, -8.01, -0.05)   # 1e11 cm^-2 units
for D0 in (-0.45,-0.55,-0.65):
    vtg,vbg = nD_to_V(n_scan*1e11, D0)
    ok = (vtg>=TG[0])&(vtg<=TG[1])&(vbg>=BG[0])&(vbg<=BG[1])
    # roundtrip check
    nn,DD = cal.n_D(vtg[ok],vbg[ok])
    rt = np.allclose(DD/1e9, D0, atol=1e-6)
    nlo,nhi = n_scan[ok].min(), n_scan[ok].max()
    print(f"D={D0:+.2f} V/nm: realized n∈[{nlo:+.2f},{nhi:+.2f}]e11 ({ok.sum()}/{len(n_scan)} pts), "
          f"V_tg∈[{vtg[ok].min():+.2f},{vtg[ok].max():+.2f}] V_bg∈[{vbg[ok].min():+.2f},{vbg[ok].max():+.2f}] roundtrip={rt}")
    # how much of the target band [-6,-4] is covered?
    band = (n_scan>=-6)&(n_scan<=-4)&ok
    print(f"    target band n∈[-6,-4] covered: {band.sum()} pts")
