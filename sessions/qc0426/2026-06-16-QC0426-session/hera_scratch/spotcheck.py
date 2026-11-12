# === SdH spot check (fixed sensitivity 200 uV) — snake field at +/-8e12, D=0 ===
# Aaron: with sens fixed, recheck SdH onset + whether TWO Fermi surfaces resolve.
# Snake: n=-8e12 sweep B up (0->4 T), then n=+8e12 sweep B down (4->0 T), 50 mT.
import numpy as np, scipy.constants as cst
C_TG = cst.epsilon_0*3.0/15.6e-9; C_BG = 1.298*C_TG; N_OFF = -7.095e14   # file-1 cal
def gates_for(n_cm2, D=0.0):
    n_m2=n_cm2*1e4; a=(n_m2-N_OFF)*cst.e; b=2.0*D*cst.epsilon_0
    return (a+b)/(2*C_TG), (a-b)/(2*C_BG)

# --- Preconditions ---
assert abs(magnet.mag()) < 0.05, f"field not ~0 T: {magnet.mag()}"
assert heater.sample_temperature() < 2.0, f"T not at base: {heater.sample_temperature()}"
assert abs(k_2410.volt() - 50.0) < 1.0, f"Si not ~+50 V: {k_2410.volt()}"
for nm,sr in [("sr1",sr1),("sr2",sr2),("sr3",sr3)]:
    assert abs(sr.sensitivity()-2e-4) < 1e-9, f"{nm} sens not 200 uV: {sr.sensitivity()}"
print("pre OK: B", magnet.mag(), "Si", k_2410.volt(), "sens", sr1.sensitivity())

# Pace BG positioning moves (large Keithley ramps) — avoid GPIB flood.
k_bg.volt.inter_delay = 0.05   # inter_delay (NOT the consent-gated .step)

B_up   = np.linspace(0.0, 4.0, 81)   # 50 mT
B_down = np.linspace(4.0, 0.0, 81)

def run(n_cm2, B_vec, tag):
    Vtg, Vbg = gates_for(n_cm2, 0.0)
    assert -6 < Vtg < 7 and -4.5 < Vbg < 4.5, "gate target out of validators"
    print(f"{tag}: n={n_cm2:.1e}, Vtg={Vtg:.3f}, Vbg={Vbg:.3f}, B {B_vec[0]}->{B_vec[-1]} T")
    mc = dict(meas_config)
    mc["sr0"]="drain current on T7"; mc["sr1"]="Rxx T3-T4"; mc["sr2"]="Rxx B4-B5"; mc["sr3"]="Rxy T5-B6"
    mc["comments"]=f"SdH spot check (sens 200uV): n={n_cm2:.1e} cm-2 D=0, B {B_vec[0]}->{B_vec[-1]} T 50mT, Si=+50V"
    s = async_station(mc)
    s.add_comment('field-sweep-1d')
    s.add_comment('trilayer-stacking-fs-count Step3 redo @ sens 200uV; 2-FS resolution check')
    s.add_comment(f'n={n_cm2:.2e} cm-2, D=0, B {B_vec[0]}->{B_vec[-1]} T uniform 50 mT; cal file_id 1')
    s.ramp(k_bg.volt, Vbg); s.ramp(dc205_volt, Vtg)
    s.fp(k_bg.curr).fp(k_2410.curr)
    for sr in [sr0, sr1, sr2, sr3]: s.fp(sr.X).fp(sr.P)
    s.plot(magnet.mag, sr1.X)
    s.sweep(magnet.mag, B_vec, delay=1.0)

try:
    run(-8.0e12, B_up,   "A hole up")     # 0 -> 4 T
    run(+8.0e12, B_down, "B electron dn") # 4 -> 0 T (snake)
finally:
    s = async_station(meas_config)
    s.ramp(dc205_volt, 0); s.ramp(k_bg.volt, 0)
print("done; gates parked 0, Si held +50 V, magnet at", magnet.mag(), "T")
