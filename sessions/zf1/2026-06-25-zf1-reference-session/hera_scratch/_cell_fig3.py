# === Figure 3 — R(T, n) map at the widest-D line (D=-0.64), B=B_eff0 ===
# Flavor A: heater the dense slow axis stepping DOWN (measure-while-cooling),
# n-line fast at fixed D. Uniform-T ladder (~100 pts, 480->34 mK) built from the
# warm-up's measured heater->T. Ends heater OFF at base, positioned for Fig 4a.
import scipy.constants as cst, time

B_EFF0 = -0.366e-3

# --- preconditions: heated (~480 mK), B_eff0, heater drawing ---
T_now = temperature(); B_now = magnet.field(); Hv = heater.volt(); Ih = heater.curr()
print(f"T = {T_now*1e3:.1f} mK     (expect ~480, warmed)")
print(f"B = {B_now*1e3:.4f} mT    (expect B_eff0 {B_EFF0*1e3:.3f})")
print(f"heater = {Hv:.3f} V, I = {Ih:.3e} A   (expect ~6.5 V, drawing)")
assert abs(B_now - B_EFF0) < 0.0015, f"B off B_eff0: {B_now*1e3:.3f} mT"
assert Hv > 6.0 and abs(Ih) > 1e-9, "heater not at ceiling / not drawing — run warm-up (cell 40) first"

# --- AC sense (re-assert): 1 nA, 4T 0.1 mV, DC 0 ---
dc205_1.volt(0.0); sr830_1.amplitude(0.1); sr830_2.sensitivity(0.005); sr830_3.sensitivity(1e-4)

# --- (n,D) calibration ---
N_OFF=-0.362e11*1e4
cal_r4=GateCalibration.from_thicknesses(t_tg,t_bg,t_bgSiO2,n_offset=N_OFF)
c_tg,c_bg=cal_r4.c_tg,cal_r4.c_bg; e,eps0=cst.e,cst.epsilon_0
def nD_to_V(n_cm2,D_Vnm):
    n=np.asarray(n_cm2)*1e4; D=np.asarray(D_Vnm)*1e9
    A=(n-cal_r4.n_offset)*e; B=(D-cal_r4.D_offset)*2*eps0
    return (A+B)/(2*c_tg),(A-B)/(2*c_bg)

# --- fast axis: n-line at D=-0.64 ---
n_line=np.round(np.arange(-4.0,-6.501,-0.02),3)         # 126 pts, into normal both sides (1e11 cm^-2 units)
vt_line,vb_line=nD_to_V(n_line*1e11,-0.64)              # *1e11: nD_to_V takes cm^-2
assert (vt_line>=-7).all() and (vt_line<=6).all() and (vb_line>=-4).all() and (vb_line<=4.2).all(), "n-line breaches validators"

# --- slow axis: uniform-T descending ladder from the warm-up's heater->T (this cooldown) ---
Vh_cal=np.array([0,1,2,3,4,4.5,5,5.5,6,6.5]); T_cal=np.array([34,48.6,100.3,157.7,228.9,262.4,316.6,363.8,428.4,480.3])
T_targets=np.linspace(480.0,34.0,100)                   # mK, descending
V_ladder=np.interp(T_targets,T_cal,Vh_cal)              # -> heater V (ends at 0 = base)
print(f"ladder: {len(V_ladder)} steps, heater {V_ladder[0]:.3f}->{V_ladder[-1]:.3f} V "
      f"(T {T_targets[0]:.0f}->{T_targets[-1]:.0f} mK, ~{T_targets[0]-T_targets[1]:.1f} mK/step)")
print(f"n-line: {len(n_line)} pts, D=-0.64, n[-4.0,-6.5]")

meas_config["comment"]=(f"Fig3 R(T,n) Flavor-A map; D=-0.64 widest-D line; B=B_eff0={B_EFF0*1e3:.3f} mT; "
                        f"heater slow {len(V_ladder)}-step uniform-T 480->34 mK (descending, measure-while-cooling); "
                        f"n fast {len(n_line)} pts [-4.0,-6.5]e11 0.02 step; AC 1 nA; 4T 0.1 mV; slow_delay 90 fast_delay 1")
s=sweep.AsyncStation(meas_config)
s.add_comment('temperature-dependence')
s.add_comment('Figure 3: R(T,n) at widest-D line D=-0.64, B=B_eff0 (Flavor A, heater slow axis)')
s.add_comment(meas_config["comment"])
xp=k_tg.volt
s.fp(k_tg.volt).fp(k_tg.curr); s.fp(k_bg.volt).fp(k_bg.curr)
s.fp(temperature).fp(fridge_temperature).fp(heater.volt).fp(heater.curr).fp(magnet.field)
for lia in (sr830_1,sr830_2,sr830_3): s.fp(lia.X).fp(lia.P)
s.plot('time', heater.curr)      # confirm heater drawing through the run
s.plot('time', temperature)      # T descending ladder
s.plot(xp, sr830_3.X)            # 4T Rxx vs n (live)
try:
    s.multimegasweep([heater.volt],[V_ladder],[k_tg.volt,k_bg.volt],[vt_line,vb_line],
                     slow_delay=90, fast_delay=1, init_delay=False)
finally:
    heater.volt(0.0)             # ensure heater off at base
    # leave gates at optimum for the verify/next steps
    vt_opt,vb_opt=nD_to_V(-5.0e11,-0.64); s.ramp(k_tg.volt,float(vt_opt)); s.ramp(k_bg.volt,float(vb_opt))
print(f"done; heater {heater.volt():.2f} V, T={temperature()*1e3:.1f} mK, B={magnet.field()*1e3:.3f} mT")
