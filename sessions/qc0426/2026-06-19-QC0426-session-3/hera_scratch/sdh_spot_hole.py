# Step 3 — SdH spot check, HOLE side. Fixed (n=-5e12, D=0), B swept 0->4T from zero
# (reads the onset). High-|n| bias 2V/20nA; adaptive lock-in sensitivity (~2x headroom);
# dwell at the 7*tau settling floor (tau=0.3, 24 dB/oct). NO LS335 fp (rig-card quirk).
# Gate point from the device-card (n,D) calibration (GateCalibration / SI convention).
import numpy as np, time

# --- calibration (device card, run 1) ---
c_tg, c_bg, n_off = 1.7027e-3, 2.2004e-3, -1.581e15
E, EPS0 = 1.602176634e-19, 8.8541878128e-12
def gates_for(n, D=0.0):
    vtg = ((n-n_off)*E/2 + EPS0*D)/c_tg
    vbg = ((n-n_off)*E/2 - EPS0*D)/c_bg
    return vtg, vbg
n_target = -5e16                       # -5e12 cm^-2
Vtg, Vbg = gates_for(n_target, 0.0)
assert -6.0 <= Vtg <= 7.0 and -4.5 <= Vbg <= 4.5, f"gate point OOR: {Vtg},{Vbg}"

# --- preconditions ---
B0 = magnet.mag()
print(f"[precond] B={B0:+.4f} T (expect ~0)  target n=-5e12 D=0 -> Vtg={Vtg:.3f} Vbg={Vbg:.3f}")
assert abs(B0) < 0.05, "magnet not at ~0"
try: T0 = heater.sample_temperature()
except Exception as e: T0 = None; print("[warn] T read:", e)

# --- high-|n| bias 2V/20nA (sr1 is the AC source) ---
sr1.amplitude(2.0); meas_config["bias_voltage"] = sr1.amplitude()
print(f"[bias] V_ac={sr1.amplitude()} V -> ~{sr1.amplitude()/100e6*1e9:.0f} nA")

# --- station + fp (no LS335) ---
meas_config["comments"] = f"sdh-spot-check HOLE n=-5e12 D=0 (Vtg={Vtg:.3f},Vbg={Vbg:.3f}); B 0->4T 8mT; bias 2V/20nA; T_start={T0}"
s = async_station(meas_config)
s.add_comment('sdh-spot-check'); s.add_comment(meas_config["comments"])
s.fp(k_2400.curr).fp(k_2410.curr)
for sx in (sr0, sr1, sr2, sr3): s.fp(sx.X).fp(sx.P)
s.plot(magnet.mag, sr1.X); s.plot(magnet.mag, sr2.X); s.plot('time', k_2410.curr)

# --- position gates, settle, set sensitivity ---
s.ramp(k_si.volt, 0.0); s.ramp(k_bg.volt, Vbg); s.ramp(dc205_volt, Vtg); time.sleep(5)
SENS=[2e-9,5e-9,1e-8,2e-8,5e-8,1e-7,2e-7,5e-7,1e-6,2e-6,5e-6,1e-5,2e-5,5e-5,1e-4,2e-4,5e-4,1e-3,2e-3,5e-3,1e-2,2e-2,5e-2,1e-1,2e-1,5e-1,1.0]
Im = sr0.X()/abs(meas_config["sr0_gain"])
print(f"[settle] I_meas={Im*1e9:.2f} nA  R_sr1={abs(sr1.X()/Im):.0f} R_sr2={abs(sr2.X()/Im):.0f} ohm")
for sx in (sr1, sr2, sr3):
    x = abs(sx.X()); pick = next((v for v in SENS if v >= 2.2*max(x,1e-9)), 1.0)
    sx.sensitivity(pick); print(f"   {sx.name}: |X|={x:.2e} -> sens {pick:.0e}")
meas_config["sr1_sens"]=sr1.sensitivity(); meas_config["sr2_sens"]=sr2.sensitivity(); meas_config["sr3_sens"]=sr3.sensitivity()
time.sleep(2)

# --- field sweep 0 -> 4 T, 8 mT step, dwell 2.2 s (7*tau floor) ---
field_vec = np.linspace(0.0, 4.0, 501)
s.sweep(magnet.mag, field_vec, delay=2.2)
print("[done] SdH spot check HOLE complete; B left at 4 T for the electron-side descent")
