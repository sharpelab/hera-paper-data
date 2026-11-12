# Figure 1 — analysis: widest-D line + optimal n (with the BG-cap constraint on the T-map)
import scipy.constants as cst
c_tg, c_bg = cal.c_tg, cal.c_bg; e, eps0 = cst.e, cst.epsilon_0
def nD_to_V(n_cm2, D_Vnm):
    n = np.asarray(n_cm2)*1e4*1e11; D = np.asarray(D_Vnm)*1e9
    A = (n - cal.n_offset)*e; B = (D - cal.D_offset)*2*eps0
    return float((A+B)/(2*c_tg)), float((A-B)/(2*c_bg))

# core (<2 ohm) n-width per D row
def core_width(D0, thr=2.0):
    sel = np.abs(D_Vnm - D0) < 0.0015
    if sel.sum() < 5: return np.nan, np.nan, np.nan
    o = np.argsort(n11[sel]); nl = n11[sel][o]; Rl = R[sel][o]; c = Rl < thr
    if c.sum() == 0: return 0.0, np.nan, np.nan
    return nl[c].max()-nl[c].min(), 0.5*(nl[c].min()+nl[c].max()), Rl.min()

for D0 in [-0.64, -0.65, -0.655, -0.66, -0.665, -0.67]:
    w, cen, rmin = core_width(D0)
    vt, vb = nD_to_V(-4.0, D0)
    print(f"D={D0:+.3f}: core width={w:.2f}e11 center n={cen:+.3f}  | T-map n=-4.0 -> V_bg={vb:.3f} "
          f"{'OK' if vb<=4.2 else 'CLIPS'}")

# SELECTION
D_SEL = -0.64
w, n_opt, _ = core_width(D_SEL)
Vtg_opt, Vbg_opt = nD_to_V(-5.0, D_SEL)
print(f"\nSELECTED widest-D line: D = {D_SEL:+.3f} V/nm (flat-max width among cap-accessible D; best margin)")
print(f"OPTIMAL doping: n = -5.0e11 (core center {n_opt:+.3f}) -> V_tg={Vtg_opt:.3f}, V_bg={Vbg_opt:.3f}")
print(f"True peak width ~0.60e11 at D~-0.665 to -0.67 but BG-cap-limited for the T-map (high-|D| flank).")
