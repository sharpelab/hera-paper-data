# === Fig 5 verify (cheap) — 1D dV/dI vs I_dc at base, optimum, B=B_eff0 ===
# Confirms the supercurrent is clean (Ic ~28 nA, switching ~+/-36 nA) before the
# 2D dV/dI(I_dc, T). Ramps field back to B_eff0 from the Fig-4 field. AC 0.5 nA.
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

# --- preconditions: gates at optimum, heater off ---
Vtg=k_tg.volt(); Vbg=k_bg.volt(); Hv=heater.volt()
print(f"V_tg={Vtg:.3f} V_bg={Vbg:.3f} heater={Hv:.3f} V; B now {magnet.field()*1e3:.4f} mT")
assert abs(Vtg-(-5.365))<0.010 and abs(Vbg-(+3.987))<0.010, "gates off optimum"
assert Hv<0.01, "heater not off"

# --- ramp field back to B_eff0 (from the +0.75 mT Fig-4 field; crosses controller 0) ---
print(f"ramping magnet to B_eff0 = {B_EFF0*1e3:.3f} mT ...")
magnet.field(B_EFF0); interruptable_sleep(20)
B_read=magnet.field(); print(f"magnet at {B_read*1e3:.4f} mT (target B_eff0; true sample field ~0)")
assert abs(B_read-B_EFF0)<0.3e-3, f"field off B_eff0: {B_read*1e3:.3f} mT"

# --- AC 0.5 nA, 4T sens 0.1 mV, zero DC bias to start ---
sr830_1.amplitude(0.05)          # 0.05 V -> 0.5 nA
sr830_2.sensitivity(0.005)
sr830_3.sensitivity(1e-4)        # 0.1 mV (resolves dV/dI 0..2 kOhm at 0.5 nA)
dc205_1.volt(0.0)
I_bias_ac = 0.05/1e8             # 0.5 nA

# --- wait for base + R-settle (field ramp deposited some heat) ---
print("waiting for base (T<45 mK) + R-settle...")
t0=time.monotonic()
while temperature()>0.045 and time.monotonic()-t0<30*60: interruptable_sleep(30)
def Ropt(): return (sr830_3.X()/100)/I_bias_ac
Rp=Ropt(); tp=time.monotonic(); ok=0
while True:
    interruptable_sleep(30); Rn=Ropt(); tn=time.monotonic(); dRdt=(Rn-Rp)/((tn-tp)/60); Rp,tp=Rn,tn
    ok = ok+1 if abs(dRdt)<0.4 else 0
    if ok>=2 or tn-t0>15*60: break
print(f"base: T={temperature()*1e3:.1f} mK, B={magnet.field()*1e3:.4f} mT, zero-bias dV/dI={Ropt():.2f} ohm")

# --- bias sweep: round-trip +/-80 nA = +/-8 V (I_dc = V_dc/1e8) ---
Vdc=np.hstack((np.linspace(-8,8,151), np.linspace(8,-8,151)))   # round-trip, hysteresis check
print(f"dV/dI vs I_dc round-trip +/-80 nA ({len(Vdc)} pts, delay 1) at base, B_eff0, optimum")
meas_config["comment"]=(f"Fig5-verify 1D dV/dI vs I_dc at base; optimum n=-5.0,D=-0.64; B=B_eff0={B_read*1e3:.3f} mT; "
                        f"round-trip +/-80 nA ({len(Vdc)} pts); AC 0.5 nA; 4T 0.1 mV; confirm Ic before 2D")
s=sweep.AsyncStation(meas_config)
s.add_comment('bias-spectroscopy'); s.add_comment('Fig 5 verify: 1D dV/dI(I_dc) at base, B_eff0, optimum (Ic check)')
s.add_comment(meas_config["comment"])
xp=dc205_1.volt
s.fp(k_tg.volt).fp(k_bg.volt).fp(temperature).fp(magnet.field).fp(dc205_1.volt)
for lia in (sr830_1,sr830_2,sr830_3): s.fp(lia.X).fp(lia.P)
s.plot(xp, sr830_3.X)    # dV/dI vs bias -- the supercurrent dip + switching
s.plot(xp, sr830_1.X)    # AC current monitor
try:
    s.sweep(dc205_1.volt, Vdc, delay=1)
finally:
    dc205_1.volt(0.0)
print(f"done; dc205=0, T={temperature()*1e3:.1f} mK, B={magnet.field()*1e3:.4f} mT")
