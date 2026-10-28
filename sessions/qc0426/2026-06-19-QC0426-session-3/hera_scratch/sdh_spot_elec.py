# Step 3b — SdH spot check, ELECTRON side. Fixed (n=+5e12, D=0), B swept 4->0 T
# (descend, ride the magnet home from the hole spot check; onset read at the low end).
# CLEAN acquisition: FIXED high-field-sized sensitivities so nothing clips over 0-4 T
# (hole-side lesson: sr1/sr2 clipped at 2e-6/109Ω, sr3 clipped on the classical Hall).
# bias 2V/20nA; dwell 2.2 s (7*tau). NO LS335 fp. FFT window will be [1,4] T (alias-free:
# 8 mT Nyquist at 1 T ~ 62 T > F_L 52 T; below 1 T the step under-samples F_L).
import numpy as np, time

c_tg, c_bg, n_off = 1.7027e-3, 2.2004e-3, -1.581e15
E, EPS0 = 1.602176634e-19, 8.8541878128e-12
def gates_for(n, D=0.0):
    return ((n-n_off)*E/2 + EPS0*D)/c_tg, ((n-n_off)*E/2 - EPS0*D)/c_bg
n_target = +5e16
Vtg, Vbg = gates_for(n_target, 0.0)
assert -6.0 <= Vtg <= 7.0 and -4.5 <= Vbg <= 4.5, f"gate OOR {Vtg},{Vbg}"

B0 = magnet.mag()
print(f"[precond] B={B0:+.4f} T (expect ~4)  target n=+5e12 D=0 -> Vtg={Vtg:.3f} Vbg={Vbg:.3f}")
assert abs(B0-4.0) < 0.2, "magnet not at ~4 T (hole spot check should have left it there)"
try: T0 = heater.sample_temperature()
except Exception as e: T0 = None; print("[warn] T:", e)

sr1.amplitude(2.0); meas_config["bias_voltage"] = sr1.amplitude()
meas_config["comments"] = f"sdh-spot-check ELECTRON n=+5e12 D=0 (Vtg={Vtg:.3f},Vbg={Vbg:.3f}); B 4->0T 8mT; bias 2V/20nA; fixed sens sr1/2=1e-5 sr3=2e-5; T_start={T0}"
s = async_station(meas_config)
s.add_comment('sdh-spot-check'); s.add_comment(meas_config["comments"])
s.fp(k_2400.curr).fp(k_2410.curr)
for sx in (sr0, sr1, sr2, sr3): s.fp(sx.X).fp(sx.P)
s.plot(magnet.mag, sr1.X); s.plot(magnet.mag, sr2.X); s.plot('time', k_2410.curr)

# position gates (at 4 T — fine), settle, set FIXED high-field sensitivities
s.ramp(k_si.volt, 0.0); s.ramp(k_bg.volt, Vbg); s.ramp(dc205_volt, Vtg); time.sleep(5)
sr1.sensitivity(1e-5); sr2.sensitivity(1e-5); sr3.sensitivity(2e-5)
meas_config["sr1_sens"]=sr1.sensitivity(); meas_config["sr2_sens"]=sr2.sensitivity(); meas_config["sr3_sens"]=sr3.sensitivity()
Im = sr0.X()/abs(meas_config["sr0_gain"])
print(f"[settle@4T] I={Im*1e9:.2f} nA  R_sr1={abs(sr1.X()/Im):.0f} R_sr2={abs(sr2.X()/Im):.0f} Rxy_sr3={abs(sr3.X()/Im):.0f} Ω")
time.sleep(2)

field_vec = np.linspace(4.0, 0.0, 501)   # descend
s.sweep(magnet.mag, field_vec, delay=2.2)
print("[done] SdH spot check ELECTRON complete; magnet home at 0 T")
