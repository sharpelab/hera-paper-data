# === Figure 3 (SETTLED re-do) — R(T,n) at D=-0.64, B=B_eff0, R+T-gated per-step settling ===
# Flavor-B: ascending V-ladder from base; at each step park gates at the optimum,
# settle until BOTH R (sample proxy) and probe-T plateau, THEN sweep the n-line
# (one file/step). R-gating auto-allocates dwell to the transition. Fixes the
# ~50 mK sample-probe lag that biased the dynamic map (run 4).
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
vt_opt,vb_opt=[float(x) for x in nD_to_V(-5.0e11,-0.64)]    # optimum (settling poll point)
n_line=np.round(np.arange(-4.0,-6.501,-0.02),3)
vt_line,vb_line=nD_to_V(n_line*1e11,-0.64)                   # *1e11: nD_to_V takes cm^-2
assert (vt_line>=-7).all() and (vt_line<=6).all() and (vb_line>=-4).all() and (vb_line<=4.2).all()

# --- AC sense; preconditions ---
dc205_1.volt(0.0); sr830_1.amplitude(0.1); sr830_2.sensitivity(0.005); sr830_3.sensitivity(1e-4)
I_bias=0.1/1e8
def Ropt(): return (sr830_3.X()/100)/I_bias
B_now=magnet.field(); assert abs(B_now-B_EFF0)<0.0015, f"B off B_eff0: {B_now*1e3:.3f} mT"

# --- wait for base (settle test left the fridge warm) ---
print("waiting for base (T<45 mK)...")
t0=time.monotonic()
while temperature()>0.045 and time.monotonic()-t0<40*60:
    interruptable_sleep(30)
print(f"T={temperature()*1e3:.1f} mK at start (base wait {(time.monotonic()-t0)/60:.0f} min)")

# --- V-ladder: ascending, dense in the transition (~3.5-5.5 V) ---
V_ladder=np.array([0,1.5,2.5,3.2,3.5,3.7,3.9,4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,5.0,5.1,5.2,5.3,5.5,5.7,6.0,6.3,6.5])
print(f"{len(V_ladder)} settled T-steps; n-line {len(n_line)} pts at D=-0.64")

# --- settle gate (inline in the loop): R-plateau AND probe-T-plateau,
#     min 4 min, max 18 min, require 2 consecutive passes (poll 20 s) ---
ladder=[]
for i,V in enumerate(V_ladder):
    # build a fresh Station per step so each file's comment carries its own settled T
    heater.volt(V); time.sleep(1.0)
    assert abs(heater.curr())>1e-9, f"heater not drawing at {V} V"
    s0=sweep.AsyncStation(meas_config); s0.ramp(k_tg.volt,vt_opt); s0.ramp(k_bg.volt,vb_opt)
    # settle poll at optimum
    t0=time.monotonic(); Tp=temperature(); Rp=Ropt(); tp=t0; ok=0
    while True:
        interruptable_sleep(20)
        Tn=temperature(); Rn=Ropt(); tn=time.monotonic(); dt=(tn-tp)/60.0
        dTdt=(Tn-Tp)*1e3/dt; dRdt=(Rn-Rp)/dt; el=tn-t0; Tp,Rp,tp=Tn,Rn,tn
        ok = ok+1 if (abs(dRdt)<0.4 and abs(dTdt)<0.3) else 0
        if (el>=240 and ok>=2) or el>1080: break
    Tset=temperature()
    print(f"step {i:2d}: heater {V:4.1f} V -> settled T={Tset*1e3:6.1f} mK, R_opt={Ropt():6.2f} ohm ({el:.0f}s)")
    ladder.append((V,Tset*1e3,Ropt()))
    # n-line sweep at this settled T -> one file
    meas_config["comment"]=(f"Fig3-settled step {i}: D=-0.64, B=B_eff0, heater {V} V, settled T={Tset*1e3:.1f} mK; "
                            f"n {len(n_line)} pts [-4.0,-6.5]e11; AC 1 nA; 4T 0.1 mV; R+T-gated settle")
    s=sweep.AsyncStation(meas_config)
    s.add_comment('temperature-dependence')
    s.add_comment(f'Figure 3 SETTLED step {i}/{len(V_ladder)-1}: R(n) at settled T={Tset*1e3:.0f} mK, D=-0.64, B_eff0')
    s.add_comment(meas_config["comment"])
    s.fp(k_tg.volt).fp(k_tg.curr); s.fp(k_bg.volt).fp(k_bg.curr)
    s.fp(temperature).fp(fridge_temperature).fp(heater.volt).fp(heater.curr).fp(magnet.field)
    for lia in (sr830_1,sr830_2,sr830_3): s.fp(lia.X).fp(lia.P)
    s.plot(k_tg.volt, sr830_3.X)
    s.multisweep([k_tg.volt,k_bg.volt],[vt_line,vb_line],delay=1.0)

heater.volt(0.0)
s_end=sweep.AsyncStation(meas_config); s_end.ramp(k_tg.volt,vt_opt); s_end.ramp(k_bg.volt,vb_opt)
print("\n=== settled ladder (V, T_mK, R_opt) ===")
for V,T,R in ladder: print(f"  {V:4.1f}  {T:6.1f}  {R:6.2f}")
print(f"done; heater off, T={temperature()*1e3:.1f} mK, gates at optimum. {len(ladder)} settled files.")
