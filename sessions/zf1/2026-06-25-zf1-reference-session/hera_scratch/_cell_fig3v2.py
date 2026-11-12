# === Figure 3 (re-do) — R(T,n) at D=-0.64, B=B_eff0: 1-tau-dwell, small-step ascending ===
# Fix for run 4's lag: ~1 tau dwell per step + small steps -> sample tracks T well.
# tau ~ 3.5 min (warm-up 1 V settles reached probe dT/dt<1 mK/min in ~510-780 s).
# slow_delay = 210 s (~1 tau); 120 uniform-T steps (~3.7 mK) -> residual lag ~1.4 mK.
# Single ascending traverse from base (no re-warm; dwell lets it reach the top). No averaging.
import scipy.constants as cst, time

B_EFF0 = -0.366e-3
# --- (n,D) calibration ---
N_OFF=-0.362e11*1e4
cal_r4=GateCalibration.from_thicknesses(t_tg,t_bg,t_bgSiO2,n_offset=N_OFF)
c_tg,c_bg=cal_r4.c_tg,cal_r4.c_bg; e,eps0=cst.e,cst.epsilon_0
def nD_to_V(n_cm2,D):
    n=np.asarray(n_cm2)*1e4; D=np.asarray(D)*1e9
    A=(n-cal_r4.n_offset)*e; B=(D-cal_r4.D_offset)*2*eps0
    return (A+B)/(2*c_tg),(A-B)/(2*c_bg)
n_line=np.round(np.arange(-4.0,-6.501,-0.02),3)
vt_line,vb_line=nD_to_V(n_line*1e11,-0.64)               # *1e11: nD_to_V takes cm^-2
assert (vt_line>=-7).all() and (vt_line<=6).all() and (vb_line>=-4).all() and (vb_line<=4.2).all(), "n-line breaches validators"

# --- preconditions: B_eff0, gates at optimum, heater off ---
B_now=magnet.field(); Vtg=k_tg.volt(); Vbg=k_bg.volt(); Hv=heater.volt()
print(f"B={B_now*1e3:.4f} mT V_tg={Vtg:.3f} V_bg={Vbg:.3f} heater={Hv:.3f} V")
assert abs(B_now-B_EFF0)<0.0015, f"B off B_eff0: {B_now*1e3:.3f} mT"
assert abs(Vtg-(-5.365))<0.010 and abs(Vbg-(+3.987))<0.010, "gates off optimum"
assert Hv<0.01, "heater not off"
dc205_1.volt(0.0); sr830_1.amplitude(0.1); sr830_2.sensitivity(0.005); sr830_3.sensitivity(1e-4)

# --- wait for base (settle test left the fridge warm) ---
print("waiting for base (T<45 mK)...")
t0=time.monotonic()
while temperature()>0.045 and time.monotonic()-t0<45*60:
    interruptable_sleep(30)
print(f"T={temperature()*1e3:.1f} mK at start (waited {(time.monotonic()-t0)/60:.0f} min)")

# --- slow axis: uniform-T ascending ladder (small steps), from warm-up heater->T ---
Vh_cal=np.array([0,1,2,3,4,4.5,5,5.5,6,6.5]); T_cal=np.array([34,48.6,100.3,157.7,228.9,262.4,316.6,363.8,428.4,480.3])
T_targets=np.linspace(34.0,480.0,120)                    # mK, ascending
V_ladder=np.interp(T_targets,T_cal,Vh_cal)
DWELL=210                                                # s, ~1 tau (tau~3.5 min)
print(f"ladder: {len(V_ladder)} steps, heater {V_ladder[0]:.3f}->{V_ladder[-1]:.3f} V "
      f"(T {T_targets[0]:.0f}->{T_targets[-1]:.0f} mK, ~{T_targets[1]-T_targets[0]:.1f} mK/step); "
      f"slow_delay={DWELL} s (~1 tau); n-line {len(n_line)} pts")

meas_config["comment"]=(f"Fig3 re-do R(T,n); D=-0.64, B=B_eff0={B_EFF0*1e3:.3f} mT; heater ASCENDING "
                        f"{len(V_ladder)}-step uniform-T 34->480 mK (~3.7 mK steps); slow_delay {DWELL}s (~1 tau); "
                        f"n {len(n_line)} pts [-4.0,-6.5]e11; AC 1 nA; 4T 0.1 mV")
s=sweep.AsyncStation(meas_config)
s.add_comment('temperature-dependence')
s.add_comment('Figure 3 (re-do): R(T,n) at D=-0.64, B_eff0; 1-tau-dwell small-step ascending (no averaging)')
s.add_comment(meas_config["comment"])
xp=k_tg.volt
s.fp(k_tg.volt).fp(k_tg.curr); s.fp(k_bg.volt).fp(k_bg.curr)
s.fp(temperature).fp(fridge_temperature).fp(heater.volt).fp(heater.curr).fp(magnet.field)
for lia in (sr830_1,sr830_2,sr830_3): s.fp(lia.X).fp(lia.P)
s.plot('time', heater.curr); s.plot('time', temperature); s.plot(xp, sr830_3.X)
try:
    s.multimegasweep([heater.volt],[V_ladder],[k_tg.volt,k_bg.volt],[vt_line,vb_line],
                     slow_delay=DWELL, fast_delay=1, init_delay=False)
finally:
    heater.volt(0.0)
    vt_o,vb_o=nD_to_V(-5.0e11,-0.64); s.ramp(k_tg.volt,float(vt_o)); s.ramp(k_bg.volt,float(vb_o))
print(f"done; heater {heater.volt():.2f} V, T={temperature()*1e3:.1f} mK, B={magnet.field()*1e3:.3f} mT")
