# === Figure 1 (REVISED, supersedes cell 31) — wide high-res (n,D) dome map at B=B_eff0 ===
# Per operator: ~10 h figure-grade budget, wide range, finer than 0.02/0.005.
# n[-7,-1] step 0.015 (fast, 401) x D[-0.69,-0.40] step 0.004 (slow, 73 rows),
# D ordered extremal -> -0.40 so the dome core lands in the first ~2 h.
import scipy.constants as cst

B_EFF0 = -0.366e-3   # T (Step 0)

# --- silent-precondition reads ---
T_now = temperature(); B_now = magnet.field()
Vtg_now = k_tg.volt(); Vbg_now = k_bg.volt(); Hv = heater.volt()
print(f"T = {T_now*1e3:.1f} mK     (expect ~34)")
print(f"B = {B_now*1e3:.4f} mT    (expect ~0; will ramp to B_eff0)")
print(f"V_tg = {Vtg_now:.3f} V     (expect -5.365, optimum)")
print(f"V_bg = {Vbg_now:.3f} V     (expect +3.987, optimum)")
print(f"heater = {Hv:.3f} V       (expect 0)")
assert T_now < 0.060, f"T high: {T_now*1e3:.1f} mK"
assert abs(B_now) < 0.005, f"B off-zero at start: {B_now*1e3:.3f} mT"
assert Hv < 0.01, f"heater on: {Hv:.3f} V"

# --- (n,D) calibration: USE EXACTLY ---
N_OFF = -0.362e11 * 1e4
cal_r4 = GateCalibration.from_thicknesses(t_tg, t_bg, t_bgSiO2, n_offset=N_OFF)
c_tg, c_bg = cal_r4.c_tg, cal_r4.c_bg
e, eps0 = cst.e, cst.epsilon_0
def nD_to_V(n_cm2, D_Vnm):
    n = np.asarray(n_cm2)*1e4; D = np.asarray(D_Vnm)*1e9
    A = (n - cal_r4.n_offset)*e; B = (D - cal_r4.D_offset)*2*eps0
    return (A+B)/(2*c_tg), (A-B)/(2*c_bg)

# --- AC sense config: 1 nA, 4T sens 1 mV, DC bias 0 ---
dc205_1.volt(0.0)
sr830_1.amplitude(0.1)
sr830_2.sensitivity(0.005)
sr830_3.sensitivity(0.001)
k_tg.nplci(1); k_bg.nplci(1)

# --- grid: n fast 0.015 step, D slow 0.004 step (extremal -> -0.40), boustrophedon ---
n_fast = np.round(np.arange(-1.0, -7.0001, -0.015), 5)          # 401 pts
D_desc = np.round(np.arange(-0.40, -0.69001, -0.004), 4)
D_slow = D_desc[::-1]                                            # ascending: -0.688 .. -0.40
vtg_l = []; vbg_l = []; rowlen = []
for i, D0 in enumerate(D_slow):
    nn = n_fast if i % 2 == 0 else n_fast[::-1]
    vt, vb = nD_to_V(nn*1e11, D0)
    vt, vb = sanitize_tg_bg(vt, vb, tg_lims, bg_lims)            # clips the extremal-D edge at BG cap
    vtg_l.append(vt); vbg_l.append(vb); rowlen.append(len(vt))
vtg = np.concatenate(vtg_l); vbg = np.concatenate(vbg_l)
print(f"grid: {len(D_slow)} D-rows x up to {len(n_fast)} n = {len(vtg)} pts kept "
      f"(row len {min(rowlen)}-{max(rowlen)}; short rows = extremal-D clip at BG cap)")
print(f"V_tg[{vtg.min():.3f},{vtg.max():.3f}]  V_bg[{vbg.min():.3f},{vbg.max():.3f}] (<=4.2)")
assert vbg.max() <= 4.2 and vtg.min() >= -7.0, "validator breach in path!"

meas_config["comment"] = (f"Fig1 REVISED wide dome map (nD-map); n[-7,-1]e11 fast 0.015 step x "
                          f"D[-0.69,-0.40] slow 0.004 step (extremal->-0.40); {len(vtg)} pts "
                          f"boustrophedon; delay 1.3; AC 1 nA; 4T sens 1 mV; B=B_eff0={B_EFF0*1e3:.3f} mT")
s = sweep.AsyncStation(meas_config)
s.add_comment('nD-map')
s.add_comment('Figure 1 (revised, ~10h figure-grade): wide high-res SC dome map at B_eff0')
s.add_comment(meas_config["comment"])
# position field + gates to the first grid point
s.ramp(magnet.field, B_EFF0)
s.ramp(k_tg.volt, vtg[0]); s.ramp(k_bg.volt, vbg[0]); interruptable_sleep(15)
print(f"positioned: B={magnet.field()*1e3:.3f} mT, V_tg={k_tg.volt():.3f}, V_bg={k_bg.volt():.3f}")
xp = k_tg.volt
s.fp(k_tg.volt).fp(k_tg.curr); s.fp(k_bg.volt).fp(k_bg.curr)
s.fp(temperature).fp(magnet.field)
for lia in (sr830_1, sr830_2, sr830_3): s.fp(lia.X).fp(lia.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot(xp, sr830_1.X)       # current monitor
s.plot(xp, sr830_2.X)       # 2T
s.plot(xp, sr830_3.X)       # 4T Rxx (30-31) -- the dome
try:
    s.multisweep([k_tg.volt, k_bg.volt], [vtg, vbg], delay=1.3)
finally:
    vt_opt, vb_opt = nD_to_V(-5.0e11, -0.64)
    s.ramp(k_tg.volt, float(vt_opt)); s.ramp(k_bg.volt, float(vb_opt))
print(f"done; gates at optimum, B={magnet.field()*1e3:.3f} mT")
