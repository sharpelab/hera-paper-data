# Electron side at 2x field density (25 mT) — resolve the undersampled oscillations.
# n=+8e12, D=0, B 0->4 T, 161 pts, drain B7, Si=+50V, 200uV.
import numpy as np, scipy.constants as cst
C_TG=cst.epsilon_0*3.0/15.6e-9; C_BG=1.298*C_TG; N_OFF=-7.095e14
def gates_for(n_cm2,D=0.0):
    n=n_cm2*1e4; a=(n-N_OFF)*cst.e; b=2*D*cst.epsilon_0
    return (a+b)/(2*C_TG),(a-b)/(2*C_BG)
n_t=8.0e12; Vtg,Vbg=gates_for(n_t,0.0)
assert -6<Vtg<7 and -4.5<Vbg<4.5
assert abs(magnet.mag())<0.05, f"B not ~0: {magnet.mag()}"
assert heater.sample_temperature()<2.0, f"T not base: {heater.sample_temperature()}"
assert abs(k_2410.volt()-50.0)<1.0, f"Si not +50 V: {k_2410.volt()}"
for nm,sr in [("sr1",sr1),("sr2",sr2),("sr3",sr3)]:
    assert abs(sr.sensitivity()-2e-4)<1e-9, f"{nm} sens not 200uV"
print("pre OK: B",magnet.mag(),"Si",k_2410.volt(),f"-> n=+8e12 Vtg={Vtg:.3f} Vbg={Vbg:.3f}")
B_vec=np.linspace(0.0,4.0,161)   # 25 mT
print(f"B: 0->4 T, {len(B_vec)} pts, dB={B_vec[1]-B_vec[0]*1:.4f} T")
mux.select({"source":"T2","drain":"B7","sr1+":"T3","sr1-":"T4","sr2+":"B4","sr2-":"B5","sr3+":"T5","sr3-":"B6"})
mc=dict(meas_config); mc["sr0"]="drain current on B7"; mc["sr1"]="Rxx T3-T4"; mc["sr2"]="Rxx B4-B5"; mc["sr3"]="Rxy T5-B6"
mc["comments"]="Electron side 2x density: n=+8e12 D=0, B 0->4 T 25 mT, drain B7, Si=+50V, 200uV"
s=async_station(mc); s.add_comment('field-sweep-1d')
s.add_comment('electron side n=+8e12 D=0, B 0->4 T 25mT (2x density), drain B7, Si=+50V; 2-FS resolution')
s.ramp(k_bg.volt,Vbg); s.ramp(dc205_volt,Vtg)
s.fp(k_bg.curr).fp(k_2410.curr)
for sr in [sr0,sr1,sr2,sr3]: s.fp(sr.X).fp(sr.P)
s.plot(magnet.mag, sr0.X)
try:
    s.sweep(magnet.mag, B_vec, delay=0.2)
finally:
    s.ramp(dc205_volt,0); s.ramp(k_bg.volt,0)
print("done; gates parked 0, Si held +50 V, magnet at", magnet.mag())
