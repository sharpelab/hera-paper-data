# === Gate-C re-entry baseline — constant-D n-linecut at D = -0.64 V/nm ===
# Reproduce the SC dome arc on this fresh kernel/session before committing
# to the high-res campaign. Expect Rxx(4T, 30-31) -> ~0 near n = -5.0e11,
# normal/metallic on both flanks. Compare to prior runs 5-8 (20260624-4-zf1).
import scipy.constants as cst

# --- silent-precondition reads (expected vs actual; STOP on mismatch) ---
T_now = temperature(); B_now = magnet.field()
Vtg_now = k_tg.volt(); Vbg_now = k_bg.volt(); Hv = heater.volt()
print(f"T = {T_now*1e3:.1f} mK        (expect ~34 base)")
print(f"B = {B_now*1e3:.4f} mT       (expect ~0)")
print(f"V_tg = {Vtg_now:.3f} V        (expect ~-5.365, held at dome from handoff)")
print(f"V_bg = {Vbg_now:.3f} V        (expect ~+3.987, held at dome from handoff)")
print(f"heater = {Hv:.3f} V          (expect 0)")
assert T_now < 0.060, f"T high: {T_now*1e3:.1f} mK"
assert abs(B_now) < 0.005, f"B off-zero: {B_now*1e3:.3f} mT"
assert Hv < 0.01, f"heater on: {Hv:.3f} V"

# --- (n,D) calibration: USE EXACTLY (handoff §1; ratio data-pinned, n_off from CNP) ---
N_OFF = -0.362e11 * 1e4   # m^-2
cal_r4 = GateCalibration.from_thicknesses(t_tg, t_bg, t_bgSiO2, n_offset=N_OFF)
c_tg, c_bg = cal_r4.c_tg, cal_r4.c_bg
e, eps0 = cst.e, cst.epsilon_0
def nD_to_V(n_cm2, D_Vnm):
    n = np.asarray(n_cm2)*1e4; D = np.asarray(D_Vnm)*1e9
    A = (n - cal_r4.n_offset)*e; B = (D - cal_r4.D_offset)*2*eps0
    return (A+B)/(2*c_tg), (A-B)/(2*c_bg)

# --- AC sense config: 1 nA drive; 4T (sr830_3) at 1 mV for low-R SC region ---
dc205_1.volt(0.0)            # zero DC bias for AC sense
sr830_1.amplitude(0.1)       # 0.1 V -> 1 nA through 100 MOhm
sr830_2.sensitivity(0.005)   # 2T (5-4): 50 kOhm ceiling
sr830_3.sensitivity(0.001)   # 4T (30-31): resolves tens of Ohm; SC channel
k_tg.nplci(1); k_bg.nplci(1)

# --- D = -0.64 cut, n -4.0 -> -6.0e11 (0.05 step, 41 pts): brackets dome into normal both flanks ---
D0 = -0.64
n_scan = np.arange(-4.0, -6.01, -0.05) * 1e11
vtg, vbg = nD_to_V(n_scan, D0)
vtg, vbg = sanitize_tg_bg(vtg, vbg, tg_lims, bg_lims)
print(f"cut: {len(vtg)} pts; V_tg in [{vtg.min():.3f},{vtg.max():.3f}], V_bg in [{vbg.min():.3f},{vbg.max():.3f}]")

meas_config["comment"] = (f"re-entry baseline; constant-D n-cut D={D0:+.2f} V/nm; "
                          f"n -4.0->-6.0e11 (0.05 step), {len(vtg)} pts; AC 1 nA; 4T sens 1 mV; B~0, base T")
s = sweep.AsyncStation(meas_config)
s.add_comment('re-entry-baseline')
s.add_comment('constant-D n-linecut (gate-C re-entry); reproduce SC dome arc vs prior runs 5-8')
s.add_comment(meas_config["comment"])
s.ramp(k_tg.volt, vtg[0]); s.ramp(k_bg.volt, vbg[0]); interruptable_sleep(10)
xp = k_tg.volt
s.fp(k_tg.volt).fp(k_tg.curr); s.fp(k_bg.volt).fp(k_bg.curr); s.fp(temperature)
for lia in (sr830_1, sr830_2, sr830_3): s.fp(lia.X).fp(lia.P)
s.plot('time', k_tg.curr)   # TG leakage
s.plot('time', k_bg.curr)   # BG leakage
s.plot(xp, sr830_1.X)       # current monitor
s.plot(xp, sr830_2.X)       # 2T (5-4)
s.plot(xp, sr830_3.X)       # 4T Rxx (30-31) -- the SC channel
try:
    s.multisweep([k_tg.volt, k_bg.volt], [vtg, vbg], delay=1.2)
finally:
    # leave gates at the dome optimum (n=-5.0, D=-0.64) -> positioned for Step 0
    vt_opt, vb_opt = nD_to_V(-5.0e11, D0)
    s.ramp(k_tg.volt, float(vt_opt)); s.ramp(k_bg.volt, float(vb_opt))
print("done; gates parked at optimum n=-5.0e11, D=-0.64 (V_tg=-5.365, V_bg=+3.987)")
