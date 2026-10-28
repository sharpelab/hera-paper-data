# === Damage-check LINE CUT — D=0 n-line through CNP, Si=+50V, B=0, 200uV ===
# Health check (line-cut form of the gatemap). Sweep, not held -> no high-|n|
# trapping. Leave Si at +50 V (current). Compare CNP/Rxx to file 1 / file 4.
import numpy as np, scipy.constants as cst
C_TG=cst.epsilon_0*3.0/15.6e-9; C_BG=1.298*C_TG; N_OFF=-7.095e14   # file-1 cal
def gates_for(n_cm2, D=0.0):
    n_m2=n_cm2*1e4; a=(n_m2-N_OFF)*cst.e; b=2.0*D*cst.epsilon_0
    return (a+b)/(2*C_TG), (a-b)/(2*C_BG)

n_line = np.linspace(-8.0e12, 8.0e12, 161)   # D=0, hole -> electron through CNP
Vtgs, Vbgs = gates_for(n_line, 0.0)
assert Vtgs.min()>-6 and Vtgs.max()<7 and Vbgs.min()>-4.5 and Vbgs.max()<4.5, "line out of validators"

# --- Preconditions (do NOT change Si) ---
assert abs(magnet.mag()) < 0.05, f"field not ~0 T: {magnet.mag()}"
assert heater.sample_temperature() < 2.0, f"T not at base: {heater.sample_temperature()}"
assert abs(k_2410.volt() - 50.0) < 1.0, f"Si not ~+50 V: {k_2410.volt()}"
for nm,sr in [("sr1",sr1),("sr2",sr2),("sr3",sr3)]:
    assert abs(sr.sensitivity()-2e-4)<1e-9, f"{nm} sens not 200uV: {sr.sensitivity()}"
print("pre OK: B",magnet.mag(),"Si",k_2410.volt(),"sens",sr1.sensitivity())
print(f"D=0 line: n {n_line[0]:.1e}->{n_line[-1]:.1e} ({len(n_line)} pts); Vtg {Vtgs[0]:.2f}..{Vtgs[-1]:.2f}, Vbg {Vbgs[0]:.2f}..{Vbgs[-1]:.2f}")

mc = dict(meas_config)
mc["sr0"]="drain current on T7"; mc["sr1"]="Rxx T3-T4"; mc["sr2"]="Rxx B4-B5"; mc["sr3"]="Rxy T5-B6"
mc["comments"]="Damage-check line cut: D=0 n-line -8..+8e12 through CNP, Si=+50V, B=0, sens 200uV"

s = async_station(mc)
s.add_comment('reentry-baseline')
s.add_comment('damage-check line cut (D=0 n-line), Si=+50V, B=0; cal file_id 1')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(dc205_volt, Vtgs[0])
s.fp(k_bg.curr).fp(k_2410.curr)
for sr in [sr0, sr1, sr2, sr3]: s.fp(sr.X).fp(sr.P)
s.plot(dc205_volt, sr0.X)
try:
    s.multisweep([dc205_volt, k_bg.volt], [Vtgs, Vbgs], delay=0.5)
finally:
    s.ramp(dc205_volt, 0); s.ramp(k_bg.volt, 0)
print("done; gates parked 0, Si held +50 V")
