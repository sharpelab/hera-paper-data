# === FULL two-terminal contact survey — all 15 device contacts ===
# Current-bias: alive ~5 nA, dead ~0. Cycle so each contact is in 2 pairs and
# expected-dead (B1,B2,T6,T7) are separated by alive contacts (so every alive
# contact has >=1 alive pair). Si=0, D=0, n=-2..-4e12 (moderate, safe). One run/pair.
import numpy as np, scipy.constants as cst
C_TG=cst.epsilon_0*3.0/15.6e-9; C_BG=1.298*C_TG; N_OFF=-7.095e14
def gates_for(n_cm2,D=0.0):
    n=n_cm2*1e4; a=(n-N_OFF)*cst.e; b=2*D*cst.epsilon_0
    return (a+b)/(2*C_TG),(a-b)/(2*C_BG)
n_line=np.linspace(-2.0e12,-4.0e12,11); Vtgs,Vbgs=gates_for(n_line,0.0)

assert abs(magnet.mag())<0.05, f"B not ~0: {magnet.mag()}"
assert heater.sample_temperature()<2.0, f"T not base: {heater.sample_temperature()}"
assert abs(k_2410.volt())<0.5, f"Si not ~0: {k_2410.volt()}"
print("pre: B",magnet.mag(),"Si",k_2410.volt(),"sens",sr1.sensitivity())

# cycle over all 15 contacts; dead-expected T6,T7,B1,B2 separated by alive
cycle=["T6","T1","T2","T7","T3","T4","B1","T5","B8","B2","B3","B4","B5","B6","B7"]
pairs=[(cycle[i], cycle[(i+1)%len(cycle)]) for i in range(len(cycle))]
print(f"{len(pairs)} pairs (full cycle); alive ~5 nA, dead ~0")
for src,dst in pairs:
    others=[c for c in cycle if c not in (src,dst)][:6]   # voltage chans -> ignored spares
    sel={"source":src,"drain":dst,
         "sr1+":others[0],"sr1-":others[1],"sr2+":others[2],"sr2-":others[3],
         "sr3+":others[4],"sr3-":others[5]}
    mux.select(sel)
    mc=dict(meas_config); mc["sr0"]=f"drain current on {dst}"
    mc["comments"]=f"full-contact-survey-2t: source={src} drain={dst}, D=0 n=-2..-4e12, Si=0, 200uV"
    try: mc.update(mux.mc_fragment())
    except Exception: pass
    s=async_station(mc); s.add_comment('contact-survey-2t')
    s.add_comment(f'full survey pair source={src} drain={dst}')
    s.ramp(k_bg.volt,Vbgs[0]); s.ramp(dc205_volt,Vtgs[0])
    s.fp(k_bg.curr).fp(k_2410.curr)
    for sr in [sr0,sr1,sr2,sr3]: s.fp(sr.X).fp(sr.P)
    s.multisweep([dc205_volt,k_bg.volt],[Vtgs,Vbgs],delay=0.5)
    print(f"  done {src}-{dst}")
s.ramp(dc205_volt,0); s.ramp(k_bg.volt,0)
print("FULL survey done; gates parked 0, Si=0")
