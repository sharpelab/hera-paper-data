# === Figure 5 — dV/dI vs (I_dc, T) at the optimum, B=B_eff0 ===
# 2D supercurrent-vs-temperature map: heater the 1-tau-settled slow axis, DC bias
# the fast axis. Shows Ic(T) collapsing to 0 at Tc. Verify (run 11) confirmed a
# clean Ic~36 nA at base. Field already at B_eff0 (from the verify).
import scipy.constants as cst, time

B_EFF0 = -0.366e-3
N_OFF=-0.362e11*1e4
cal_r4=GateCalibration.from_thicknesses(t_tg,t_bg,t_bgSiO2,n_offset=N_OFF)
c_tg,c_bg=cal_r4.c_tg,cal_r4.c_bg; e,eps0=cst.e,cst.epsilon_0
def nD_to_V(n_cm2,D):
    n=np.asarray(n_cm2)*1e4; D=np.asarray(D)*1e9
    A=(n-cal_r4.n_offset)*e; B=(D-cal_r4.D_offset)*2*eps0
    return (A+B)/(2*c_tg),(A-B)/(2*c_bg)
vt_opt,vb_opt=[float(x) for x in nD_to_V(-5.0e11,-0.64)]

# --- preconditions: gates at optimum, heater off, field at B_eff0 ---
Vtg=k_tg.volt(); Vbg=k_bg.volt(); Hv=heater.volt(); B_now=magnet.field()
print(f"V_tg={Vtg:.3f} V_bg={Vbg:.3f} heater={Hv:.3f} V; B={B_now*1e3:.4f} mT (expect B_eff0 {B_EFF0*1e3:.3f})")
assert abs(Vtg-(-5.365))<0.010 and abs(Vbg-(+3.987))<0.010, "gates off optimum"
assert Hv<0.01, "heater not off"
assert abs(B_now-B_EFF0)<0.3e-3, f"B off B_eff0: {B_now*1e3:.3f} mT (re-run the verify to re-zero)"

# --- AC 0.5 nA, 4T sens 0.1 mV, DC bias 0 ---
sr830_1.amplitude(0.05); sr830_2.sensitivity(0.005); sr830_3.sensitivity(1e-4); dc205_1.volt(0.0)
def Ropt(): return (sr830_3.X()/100)/(0.05/1e8)

# --- wait for base + R-settle + 1-hour base dwell (full thermalization) ---
print("base wait + R-settle...")
t0=time.monotonic()
while temperature()>0.045 and time.monotonic()-t0<30*60: interruptable_sleep(30)
Rp=Ropt(); tp=time.monotonic(); ok=0
while True:
    interruptable_sleep(30); Rn=Ropt(); tn=time.monotonic(); dRdt=(Rn-Rp)/((tn-tp)/60); Rp,tp=Rn,tn
    ok = ok+1 if abs(dRdt)<0.4 else 0
    if ok>=2 or tn-t0>15*60: break
print("1-hour base dwell for full thermalization...")
interruptable_sleep(60*60)
print(f"base: T={temperature()*1e3:.1f} mK, zero-bias dV/dI={Ropt():.2f} ohm")

# --- axes: heater slow (1-tau, cap 350 mK), DC bias fast (+/-80 nA, one-way) ---
Vh_cal=np.array([0,1,2,3,4,4.5,5,5.5,6,6.5]); T_cal=np.array([34,48.6,100.3,157.7,228.9,262.4,316.6,363.8,428.4,480.3])
T_targets=np.linspace(34.0,350.0,80); V_ladder=np.interp(T_targets,T_cal,Vh_cal); DWELL=210
Vdc=np.linspace(-8.0,8.0,161)                                   # +/-80 nA, ~1 nA step (one-way; verify showed non-hysteretic)
print(f"heater {len(V_ladder)} steps (34->350 mK, slow_delay {DWELL}s ~1 tau); bias {len(Vdc)} pts +/-80 nA")

meas_config["comment"]=(f"Fig5 dV/dI(I_dc,T); optimum n=-5.0,D=-0.64; B=B_eff0={B_now*1e3:.3f} mT; heater slow "
                        f"{len(V_ladder)}-step uniform-T 34->350 mK (~1 tau); bias fast {len(Vdc)} pts +/-80 nA; "
                        f"AC 0.5 nA; 4T 0.1 mV; R-settled + 1h base dwell")
s=sweep.AsyncStation(meas_config)
s.add_comment('bias-spectroscopy'); s.add_comment('Figure 5: dV/dI vs (I_dc, T) at optimum, B_eff0; 1-tau settled heater axis')
s.add_comment(meas_config["comment"])
xp=dc205_1.volt
s.fp(k_tg.volt).fp(k_bg.volt).fp(temperature).fp(fridge_temperature).fp(heater.volt).fp(heater.curr).fp(magnet.field).fp(dc205_1.volt)
for lia in (sr830_1,sr830_2,sr830_3): s.fp(lia.X).fp(lia.P)
s.plot('time', heater.curr); s.plot('time', temperature); s.plot(xp, sr830_3.X)
try:
    s.multimegasweep([heater.volt],[V_ladder],[dc205_1.volt],[Vdc],
                     slow_delay=DWELL, fast_delay=1, init_delay=False)
finally:
    dc205_1.volt(0.0); heater.volt(0.0)
print(f"done; dc205=0, heater {heater.volt():.2f} V, T={temperature()*1e3:.1f} mK, B={magnet.field()*1e3:.4f} mT")
