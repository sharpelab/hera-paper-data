# === 4T re-verify on the new config (drain T7 -> B7) ===
# D=0 line cut through CNP, MODERATE n=-4..+4e12 (protect new drain; high |n|
# likely killed T7). Si=0, B=0, 200 uV. Confirms: B7 drain conducts, CNP,
# Rxx (sr1/sr2) + Rxy (sr3) sane at the corrected sensitivity, leakage.
import numpy as np, scipy.constants as cst
C_TG=cst.epsilon_0*3.0/15.6e-9; C_BG=1.298*C_TG; N_OFF=-7.095e14
def gates_for(n_cm2,D=0.0):
    n=n_cm2*1e4; a=(n-N_OFF)*cst.e; b=2*D*cst.epsilon_0
    return (a+b)/(2*C_TG),(a-b)/(2*C_BG)
n_line=np.linspace(-4.0e12, 4.0e12, 81); Vtgs,Vbgs=gates_for(n_line,0.0)
assert Vtgs.min()>-6 and Vtgs.max()<7 and Vbgs.min()>-4.5 and Vbgs.max()<4.5

assert abs(magnet.mag())<0.05, f"B not ~0: {magnet.mag()}"
assert heater.sample_temperature()<2.0, f"T not base: {heater.sample_temperature()}"
assert abs(k_2410.volt())<0.5, f"Si not ~0: {k_2410.volt()}"
for nm,sr in [("sr1",sr1),("sr2",sr2),("sr3",sr3)]:
    assert abs(sr.sensitivity()-2e-4)<1e-9, f"{nm} sens not 200uV"
print("pre OK: B",magnet.mag(),"Si",k_2410.volt(),"sens",sr1.sensitivity())

# NEW config: only drain changed T7 -> B7
mux.select({"source":"T2","drain":"B7","sr1+":"T3","sr1-":"T4",
            "sr2+":"B4","sr2-":"B5","sr3+":"T5","sr3-":"B6"})
print("mux: source T2, drain B7 | sr1 T3-T4 | sr2 B4-B5 | sr3 T5-B6")

mc=dict(meas_config)
mc["sr0"]="drain current on B7"; mc["sr1"]="Rxx T3-T4"; mc["sr2"]="Rxx B4-B5"; mc["sr3"]="Rxy T5-B6"
mc["comments"]="4T re-verify NEW config (drain B7): D=0 n-line -4..+4e12 through CNP, Si=0, B=0, 200uV"
s=async_station(mc)
s.add_comment('reentry-baseline')
s.add_comment('4T re-verify new config source T2 drain B7; D=0 -4..+4e12, Si=0, B=0; cal file_id 1')
s.ramp(k_bg.volt,Vbgs[0]); s.ramp(dc205_volt,Vtgs[0])
s.fp(k_bg.curr).fp(k_2410.curr)
for sr in [sr0,sr1,sr2,sr3]: s.fp(sr.X).fp(sr.P)
s.plot(dc205_volt, sr0.X)
try:
    s.multisweep([dc205_volt,k_bg.volt],[Vtgs,Vbgs],delay=0.5)
finally:
    s.ramp(dc205_volt,0); s.ramp(k_bg.volt,0)
print("done; gates parked 0, Si=0, new config drain B7")
