# === Figure 2 — Fraunhofer: dV/dI vs (I_dc, B_perp) at the optimum, base T ===
# 2D bias-vs-field map. Single CROSS-ZERO field pass B_eff0 +/- 5 mT (AUTHORIZED,
# the one sanctioned exception to the one-sided rule), 0.1 mT step. Central lobe
# (max Ic) at B_eff0 self-checks the effective zero. Run AFTER the recovery verify.
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

# --- preconditions: gates at optimum, heater off, base T ---
Vtg=k_tg.volt(); Vbg=k_bg.volt(); Hv=heater.volt(); T0=temperature()
print(f"V_tg={Vtg:.3f} V_bg={Vbg:.3f} heater={Hv:.3f} V; T={T0*1e3:.1f} mK; B now {magnet.field()*1e3:.4f} mT")
assert abs(Vtg-(-5.365))<0.010 and abs(Vbg-(+3.987))<0.010, "gates off optimum"
assert Hv<0.01, "heater not off"
assert T0<0.060, f"not at base: {T0*1e3:.1f} mK"

sr830_1.amplitude(0.05); sr830_2.sensitivity(0.005); sr830_3.sensitivity(1e-4); dc205_1.volt(0.0)

# --- field axis: single cross-zero pass B_eff0 +/- 5 mT (authorized); bias fast +/-80 nA ---
B_vec=np.round(np.arange(B_EFF0-5e-3, B_EFF0+5e-3+0.05e-3, 0.1e-3), 6)   # ~101 steps, low->high (one cross-zero)
Vdc=np.linspace(-8.0,8.0,161)                                            # +/-80 nA
print(f"field {len(B_vec)} steps {B_vec[0]*1e3:.3f}->{B_vec[-1]*1e3:.3f} mT (centered on B_eff0={B_EFF0*1e3:.3f}); bias {len(Vdc)} pts +/-80 nA")
assert abs(B_vec).max() < 0.1, "field exceeds session cap"

# position at the negative extreme, settle (single continuous pass from here)
print(f"ramping to start {B_vec[0]*1e3:.3f} mT ...")
magnet.field(float(B_vec[0])); interruptable_sleep(30)
print(f"at {magnet.field()*1e3:.4f} mT; sweeping up through B_eff0 (cross-zero, authorized)")

meas_config["comment"]=(f"Fig2 Fraunhofer dV/dI(I_dc,B_perp); optimum n=-5.0,D=-0.64; base T; B_eff0={B_EFF0*1e3:.3f} mT; "
                        f"field slow {len(B_vec)} pts {B_vec[0]*1e3:.2f}->{B_vec[-1]*1e3:.2f} mT (cross-zero, 0.1 mT); "
                        f"bias fast {len(Vdc)} pts +/-80 nA; AC 0.5 nA; 4T 0.1 mV")
s=sweep.AsyncStation(meas_config)
s.add_comment('fraunhofer'); s.add_comment('Figure 2: Fraunhofer dV/dI(I_dc, B_perp) at optimum, base T; cross-zero centered on B_eff0')
s.add_comment(meas_config["comment"])
xp=dc205_1.volt
s.fp(k_tg.volt).fp(k_bg.volt).fp(temperature).fp(magnet.field).fp(dc205_1.volt)
for lia in (sr830_1,sr830_2,sr830_3): s.fp(lia.X).fp(lia.P)
s.plot(xp, sr830_3.X)            # dV/dI vs bias at each field
s.plot('time', temperature)      # watch for ramp/flux heating near 0
try:
    s.multimegasweep([magnet.field],[B_vec],[dc205_1.volt],[Vdc],
                     slow_delay=3, fast_delay=1, init_delay=False)
finally:
    dc205_1.volt(0.0); magnet.field(B_EFF0)   # return to B_eff0
print(f"done; dc205=0, B={magnet.field()*1e3:.4f} mT (B_eff0), T={temperature()*1e3:.1f} mK")
