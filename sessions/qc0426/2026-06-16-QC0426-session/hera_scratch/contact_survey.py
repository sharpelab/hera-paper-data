# === Two-terminal contact survey (contact-survey-2t) ===
# Current-bias rig -> alive pair pins at ~5 nA, dead ~0. Spanning set: each
# in-use contact in >=2 pairs (localizes a bad contact). Si=0, D=0, low |n|
# (-1..-4e12: de-trapped, conducting, no high-|n| start-hold). Drain current
# = aliveness; voltage channels parked on spares (ignored).
import numpy as np, scipy.constants as cst
C_TG=cst.epsilon_0*3.0/15.6e-9; C_BG=1.298*C_TG; N_OFF=-7.095e14
def gates_for(n_cm2,D=0.0):
    n=n_cm2*1e4; a=(n-N_OFF)*cst.e; b=2*D*cst.epsilon_0
    return (a+b)/(2*C_TG),(a-b)/(2*C_BG)
n_line=np.linspace(-1.0e12,-4.0e12,21); Vtgs,Vbgs=gates_for(n_line,0.0)

# Preconditions
assert abs(magnet.mag())<0.05, f"B not ~0: {magnet.mag()}"
assert heater.sample_temperature()<2.0, f"T not base: {heater.sample_temperature()}"
assert abs(k_2410.volt())<0.5, f"Si not ~0: {k_2410.volt()}"
print("pre: B",magnet.mag(),"Si",k_2410.volt(),"sens",sr1.sensitivity())

# Spanning set (each in-use contact >=2x); voltage channels -> spares (disjoint)
pairs=[("T2","T7"),("T2","T3"),("T7","T4"),("T3","T4"),
       ("T5","B4"),("B4","B5"),("B5","B6"),("T5","B6")]
SPARES={"sr1+":"T1","sr1-":"T6","sr2+":"B1","sr2-":"B2","sr3+":"B3","sr3-":"B7"}
I_bias=5e-9
print(f"{len(pairs)} pairs; n=-1..-4e12 D=0; alive ~5 nA, dead ~0")
for src,dst in pairs:
    sel={"source":src,"drain":dst}; sel.update(SPARES)
    mux.select(sel)
    mc=dict(meas_config); mc["sr0"]=f"drain current on {dst}"
    mc["comments"]=f"contact-survey-2t: source={src} drain={dst}, D=0 n=-1..-4e12, Si=0, 200uV"
    try: mc.update(mux.mc_fragment())
    except Exception: pass
    s=async_station(mc); s.add_comment('contact-survey-2t'); s.add_comment(f'pair source={src} drain={dst}')
    s.ramp(k_bg.volt,Vbgs[0]); s.ramp(dc205_volt,Vtgs[0])
    s.fp(k_bg.curr).fp(k_2410.curr)
    for sr in [sr0,sr1,sr2,sr3]: s.fp(sr.X).fp(sr.P)
    s.multisweep([dc205_volt,k_bg.volt],[Vtgs,Vbgs],delay=0.5)
    print(f"  done pair source={src} drain={dst}")
s.ramp(dc205_volt,0); s.ramp(k_bg.volt,0)
print("survey done; gates parked 0, Si=0")
