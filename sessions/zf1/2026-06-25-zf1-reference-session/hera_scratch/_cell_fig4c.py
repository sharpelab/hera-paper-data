# === Figure 4c — R(T,n) at B = B_eff0 + 4 mT, D=-0.64 (2.2x B_c -> fully normal) ===
# Same 1-tau settled ascending method. Field +3.634 mT (no zero-cross from +1.634).
# Trimmed: cap 200 mK, ~25 pts (endpoint: confirm no SC -> flat normal R).
# Post-field-ramp R-settle as in 4b.
import scipy.constants as cst, time

B_EFF0 = -0.366e-3
B_TARGET = B_EFF0 + 4.0e-3        # = +3.634 mT (B_eff0 + 4 mT)
N_OFF=-0.362e11*1e4
cal_r4=GateCalibration.from_thicknesses(t_tg,t_bg,t_bgSiO2,n_offset=N_OFF)
c_tg,c_bg=cal_r4.c_tg,cal_r4.c_bg; e,eps0=cst.e,cst.epsilon_0
def nD_to_V(n_cm2,D):
    n=np.asarray(n_cm2)*1e4; D=np.asarray(D)*1e9
    A=(n-cal_r4.n_offset)*e; B=(D-cal_r4.D_offset)*2*eps0
    return (A+B)/(2*c_tg),(A-B)/(2*c_bg)
n_line=np.round(np.arange(-4.0,-6.501,-0.02),3); vt_line,vb_line=nD_to_V(n_line*1e11,-0.64)
assert (vt_line>=-7).all() and (vt_line<=6).all() and (vb_line>=-4).all() and (vb_line<=4.2).all()
vt_opt,vb_opt=[float(x) for x in nD_to_V(-5.0e11,-0.64)]

Vtg=k_tg.volt(); Vbg=k_bg.volt(); Hv=heater.volt()
assert abs(Vtg-(-5.365))<0.010 and abs(Vbg-(+3.987))<0.010, "gates off optimum"
assert Hv<0.01, "heater not off"
dc205_1.volt(0.0); sr830_1.amplitude(0.1); sr830_2.sensitivity(0.005); sr830_3.sensitivity(1e-4)
I_bias=0.1/1e8
def Ropt(): return (sr830_3.X()/100)/I_bias

# --- position field (one-sided, increasing |B|, no zero-cross), read back ---
print(f"B now {magnet.field()*1e3:.4f} mT; ramping to B_eff0+4mT = {B_TARGET*1e3:.3f} mT ...")
magnet.field(B_TARGET); interruptable_sleep(20)
B_read=magnet.field(); print(f"magnet at {B_read*1e3:.4f} mT (true field {(B_read-B_EFF0)*1e3:.2f} mT)")
assert abs(B_read-B_TARGET)<0.2e-3, f"field off target: {B_read*1e3:.3f} mT"

# --- wait for base, THEN R-settle (sample plateau after the field ramp) ---
print("waiting for base (T<45 mK)...")
t0=time.monotonic()
while temperature()>0.045 and time.monotonic()-t0<60*60: interruptable_sleep(30)
print(f"T={temperature()*1e3:.1f} mK; now waiting for R(optimum) to plateau (sample settle)...")
Rp=Ropt(); tp=time.monotonic(); ok=0
while True:
    interruptable_sleep(30); Rn=Ropt(); tn=time.monotonic(); dRdt=(Rn-Rp)/((tn-tp)/60); Rp,tp=Rn,tn
    ok = ok+1 if abs(dRdt)<0.4 else 0
    if ok>=2 or tn-t0>15*60: print(f"  R settled: {Ropt():.2f} ohm (dR/dt={dRdt:+.2f}/min), T={temperature()*1e3:.1f} mK"); break

# --- ladder: cap 200 mK, ~25 pts (endpoint: confirm flat normal, no SC) ---
Vh_cal=np.array([0,1,2,3,4,4.5,5,5.5,6,6.5]); T_cal=np.array([34,48.6,100.3,157.7,228.9,262.4,316.6,363.8,428.4,480.3])
T_targets=np.linspace(34.0,200.0,25); V_ladder=np.interp(T_targets,T_cal,Vh_cal); DWELL=210
print(f"ladder {len(V_ladder)} steps (34->200 mK, ~{T_targets[1]-T_targets[0]:.1f} mK), slow_delay {DWELL}s; B held {B_read*1e3:.3f} mT")

meas_config["comment"]=(f"Fig4c R(T,n); D=-0.64; B={B_read*1e3:.3f} mT (B_eff0+4mT, true {(B_read-B_EFF0)*1e3:.2f} mT); "
                        f"ascending {len(V_ladder)}-step 34->200 mK; slow_delay {DWELL}s (~1 tau); n {len(n_line)} pts; "
                        f"AC 1 nA; 4T 0.1 mV; B_eff0={B_EFF0*1e3:.3f} mT; post-ramp R-settled")
s=sweep.AsyncStation(meas_config)
s.add_comment('temperature-dependence'); s.add_comment('Figure 4c: R(T,n) at B_eff0+4mT, D=-0.64; 1-tau settled, R-settled start')
s.add_comment(meas_config["comment"])
s.fp(k_tg.volt).fp(k_tg.curr); s.fp(k_bg.volt).fp(k_bg.curr)
s.fp(temperature).fp(fridge_temperature).fp(heater.volt).fp(heater.curr).fp(magnet.field)
for lia in (sr830_1,sr830_2,sr830_3): s.fp(lia.X).fp(lia.P)
s.plot('time', heater.curr); s.plot('time', temperature); s.plot(k_tg.volt, sr830_3.X)
try:
    s.multimegasweep([heater.volt],[V_ladder],[k_tg.volt,k_bg.volt],[vt_line,vb_line],
                     slow_delay=DWELL, fast_delay=1, init_delay=False)
finally:
    heater.volt(0.0); s.ramp(k_tg.volt,vt_opt); s.ramp(k_bg.volt,vb_opt)
print(f"done; heater {heater.volt():.2f} V, T={temperature()*1e3:.1f} mK, B={magnet.field()*1e3:.3f} mT")
