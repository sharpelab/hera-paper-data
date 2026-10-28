# Anchor retest: resolve T1,T2,T5 against proven-alive anchor T3.
# Current-bias: T3-X = 5 nA -> X alive; ~0 -> X dead. (T3 proven alive: T3-T4=5nA)
import numpy as np, scipy.constants as cst
C_TG=cst.epsilon_0*3.0/15.6e-9; C_BG=1.298*C_TG; N_OFF=-7.095e14
def gates_for(n_cm2,D=0.0):
    n=n_cm2*1e4; a=(n-N_OFF)*cst.e; b=2*D*cst.epsilon_0
    return (a+b)/(2*C_TG),(a-b)/(2*C_BG)
n_line=np.linspace(-2.0e12,-4.0e12,11); Vtgs,Vbgs=gates_for(n_line,0.0)
assert abs(magnet.mag())<0.05 and heater.sample_temperature()<2.0 and abs(k_2410.volt())<0.5
print("pre OK: B",magnet.mag(),"Si",k_2410.volt())
tests=["T1","T2","T5"]; anchor="T3"
sparesV=["B5","B6","B7","B3","B4","T4"]   # proven-alive, ignored voltage routing
for x in tests:
    sel={"source":anchor,"drain":x,
         "sr1+":sparesV[0],"sr1-":sparesV[1],"sr2+":sparesV[2],"sr2-":sparesV[3],
         "sr3+":sparesV[4],"sr3-":sparesV[5]}
    mux.select(sel)
    mc=dict(meas_config); mc["sr0"]=f"drain current on {x}"
    mc["comments"]=f"anchor-retest-2t: source={anchor} drain={x}, D=0 n=-2..-4e12, Si=0, 200uV"
    try: mc.update(mux.mc_fragment())
    except Exception: pass
    s=async_station(mc); s.add_comment('contact-survey-2t'); s.add_comment(f'anchor retest source={anchor} drain={x}')
    s.ramp(k_bg.volt,Vbgs[0]); s.ramp(dc205_volt,Vtgs[0])
    s.fp(k_bg.curr).fp(k_2410.curr)
    for sr in [sr0,sr1,sr2,sr3]: s.fp(sr.X).fp(sr.P)
    s.multisweep([dc205_volt,k_bg.volt],[Vtgs,Vbgs],delay=0.5)
    print(f"  done {anchor}-{x}")
s.ramp(dc205_volt,0); s.ramp(k_bg.volt,0)
print("anchor retest done")
