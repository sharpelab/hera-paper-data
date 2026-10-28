# Cell 2 — Aaron's snake: n=-8e12 B 0->4 (up), n=+8e12 B 4->0 (down), 50 mT.
# NEW config (drain B7), Si=+50 V. (B7-death risk flagged; Aaron approved.)
import numpy as np, scipy.constants as cst
C_TG=cst.epsilon_0*3.0/15.6e-9; C_BG=1.298*C_TG; N_OFF=-7.095e14
def gates_for(n_cm2,D=0.0):
    n=n_cm2*1e4; a=(n-N_OFF)*cst.e; b=2*D*cst.epsilon_0
    return (a+b)/(2*C_TG),(a-b)/(2*C_BG)
assert abs(magnet.mag())<0.05, f"B not ~0: {magnet.mag()}"
assert heater.sample_temperature()<2.0, f"T not base: {heater.sample_temperature()}"
assert abs(k_2410.volt()-50.0)<1.0, f"Si not +50 V: {k_2410.volt()}"
for nm,sr in [("sr1",sr1),("sr2",sr2),("sr3",sr3)]:
    assert abs(sr.sensitivity()-2e-4)<1e-9, f"{nm} sens not 200uV"
print("pre OK: B",magnet.mag(),"Si",k_2410.volt(),"sens",sr1.sensitivity())
B_up=np.linspace(0.0,4.0,81); B_down=np.linspace(4.0,0.0,81)
def run(n_t,B_vec,tag):
    Vtg,Vbg=gates_for(n_t,0.0)
    assert -6<Vtg<7 and -4.5<Vbg<4.5
    mux.select({"source":"T2","drain":"B7","sr1+":"T3","sr1-":"T4","sr2+":"B4","sr2-":"B5","sr3+":"T5","sr3-":"B6"})
    mc=dict(meas_config); mc["sr0"]="drain current on B7"; mc["sr1"]="Rxx T3-T4"; mc["sr2"]="Rxx B4-B5"; mc["sr3"]="Rxy T5-B6"
    mc["comments"]=f"Aaron snake {tag}: n={n_t:.1e} D=0, B {B_vec[0]}->{B_vec[-1]} T 50mT, drain B7, Si=+50V, 200uV"
    s=async_station(mc); s.add_comment('field-sweep-1d')
    s.add_comment(f"Aaron snake {tag} n={n_t:.2e} drain B7 Si=+50V; 2-FS check @ 200uV")
    s.ramp(k_bg.volt,Vbg); s.ramp(dc205_volt,Vtg)
    s.fp(k_bg.curr).fp(k_2410.curr)
    for sr in [sr0,sr1,sr2,sr3]: s.fp(sr.X).fp(sr.P)
    s.plot(magnet.mag, sr0.X)   # live drain current (B7 survival watch)
    s.sweep(magnet.mag,B_vec,delay=0.2)
    print(f"  done {tag}")
try:
    run(-8.0e12,B_up,"hole up")        # 0 -> 4 T
    run(+8.0e12,B_down,"electron dn")  # 4 -> 0 T (snake)
finally:
    s.ramp(dc205_volt,0); s.ramp(k_bg.volt,0)
print("snake done; gates parked 0, Si held +50 V, magnet at", magnet.mag())
