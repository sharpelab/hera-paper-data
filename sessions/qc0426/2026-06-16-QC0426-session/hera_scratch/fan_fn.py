# === F(n) Landau fan, D=0, electron side, 12.5 mT, ride down 4->1.2 T ===
# 31 density pts n=2..8e12; per-column SdH FFT -> F(n) Onsager overlay (ABA vs ABC).
# drain B7, Si=+50V, 200uV. Magnet at 4 T (file 38 end) -> descend (no re-traverse).
import numpy as np, scipy.constants as cst
C_TG=cst.epsilon_0*3.0/15.6e-9; C_BG=1.298*C_TG; N_OFF=-7.095e14
def gates_for(n_cm2,D=0.0):
    n=n_cm2*1e4; a=(n-N_OFF)*cst.e; b=2*D*cst.epsilon_0
    return (a+b)/(2*C_TG),(a-b)/(2*C_BG)
n_vec=np.linspace(2.0e12,8.0e12,31)          # 31 density pts, Dn=0.2e12
Vtgs,Vbgs=gates_for(n_vec,0.0)
assert Vtgs.min()>-6 and Vtgs.max()<7 and Vbgs.min()>-4.5 and Vbgs.max()<4.5, "n-line out of validators"
B_vec=np.linspace(4.0,1.2,225)               # descend, 12.5 mT
print(f"fan: B {B_vec[0]}->{B_vec[-1]} T x {len(B_vec)} rows (dB={abs(B_vec[1]-B_vec[0])*1000:.1f} mT) ; n {n_vec[0]:.1e}..{n_vec[-1]:.1e} x {len(n_vec)} = {len(B_vec)*len(n_vec)} pts")
# Preconditions
assert abs(magnet.mag()-4.0)<0.25, f"magnet not ~4 T: {magnet.mag()}"
assert heater.sample_temperature()<2.0, f"T not base: {heater.sample_temperature()}"
assert abs(k_2410.volt()-50.0)<1.0, f"Si not +50 V: {k_2410.volt()}"
for nm,sr in [("sr1",sr1),("sr2",sr2),("sr3",sr3)]:
    assert abs(sr.sensitivity()-2e-4)<1e-9, f"{nm} sens not 200uV"
print("pre OK: B",magnet.mag(),"Si",k_2410.volt(),"sens",sr1.sensitivity())
mux.select({"source":"T2","drain":"B7","sr1+":"T3","sr1-":"T4","sr2+":"B4","sr2-":"B5","sr3+":"T5","sr3-":"B6"})
mc=dict(meas_config); mc["sr0"]="drain current on B7"; mc["sr1"]="Rxx T3-T4"; mc["sr2"]="Rxx B4-B5"; mc["sr3"]="Rxy T5-B6"
mc["comments"]="F(n) fan D=0 electron: n=2..8e12 (31pts) x B 4->1.2 T 12.5mT, drain B7, Si=+50V, 200uV"
s=async_station(mc)
s.add_comment('landau-fan-vti')
s.add_comment('F(n) Onsager fan; D=0 electron n=2..8e12 x B 4->1.2T 12.5mT; drain B7 Si=+50V; cal file_id 1')
s.ramp(dc205_volt,Vtgs[0]); s.ramp(k_bg.volt,Vbgs[0])   # magnet already at 4 T
s.fp(k_bg.curr).fp(k_2410.curr)
for sr in [sr0,sr1,sr2,sr3]: s.fp(sr.X).fp(sr.P)
s.plot(magnet.mag, sr0.X)
try:
    s.multimegasweep([magnet.mag],[B_vec],[dc205_volt,k_bg.volt],[Vtgs,Vbgs],slow_delay=1,fast_delay=0.8)
finally:
    s.ramp(dc205_volt,0); s.ramp(k_bg.volt,0)
print("fan done; gates parked 0, Si held +50 V, magnet at", magnet.mag())
