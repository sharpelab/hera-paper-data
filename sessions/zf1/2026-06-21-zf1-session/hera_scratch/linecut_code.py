# n-linecuts at fixed D (investigation Step 1 heuristic-zoom: locate the arc).
# Cap ratio confirmed 1.189 (CNP-slope fit, run 2); (n,D) now calibrated.
# Fine n-scan at high SNR on the hole side, high |D|, to RESOLVE or rule out a
# narrow SC arc that the coarse survey (Dn~6e10) could have averaged over.
# D=-0.60 is the highest |D| with a full n-window inside the gate validators
# (D=-0.75 would need TG<-7). 4T sr3 (30-31) is the Rxx channel.
# Recipe: cnp-and-dline-calibration (D-line design) + nD-map (co-swept line).
import numpy as np, time
import scipy.constants as cst

# ---- preconditions ----
T=temperature(); B=magnet.field()
print(f"T={T*1e3:.1f} mK  B={B*1e3:.3f} mT  TG={k_tg.volt():.3f} BG={k_bg.volt():.3f}  amp={sr830_1.amplitude()} V")
assert T<0.08, f"T not base {T*1e3:.1f} mK"
assert abs(B)<0.01, f"B too large {B*1e3:.3f} mT"

# ---- high-SNR settings ----
for sr in (sr830_1,sr830_2,sr830_3): sr.time_constant(0.3)
sr830_1.sensitivity(2e-3); sr830_2.sensitivity(2e-3); sr830_3.sensitivity(5e-6)
print("tc:",sr830_3.time_constant()," sens:",sr830_1.sensitivity(),sr830_2.sensitivity(),sr830_3.sensitivity())

# ---- calibrated (n,D) inverse (ratio 1.189; n_offset from CNP intercept b=+0.0259 V) ----
c_tg=cst.epsilon_0*3/23.6e-9; c_bg=cst.epsilon_0*3/20e-9
n_offset=-c_bg*0.0259/cst.e
def gates_for(n_cm,D_vnm):
    n=np.asarray(n_cm)*1e4; D=D_vnm*1e9
    a=(n-n_offset)*cst.e; bb=D*2*cst.epsilon_0
    return (a+bb)/(2*c_tg),(a-bb)/(2*c_bg)
def n_of(vtg,vbg):
    return ((c_tg*np.asarray(vtg)+c_bg*np.asarray(vbg))/cst.e + n_offset)*1e-4  # cm^-2

delay=1.0; N=200
for D in (-0.60,-0.45):
    n_req=np.linspace(1e11,-8e11,N)
    vtg,vbg=gates_for(n_req,D)
    vtg2,vbg2=sanitize_tg_bg(vtg,vbg,tg_lims,bg_lims)
    nr=n_of(vtg2,vbg2)
    print(f"D={D:+.2f} V/nm: {len(vtg2)}/{N} pts, n=[{nr.max()/1e11:+.2f},{nr.min()/1e11:+.2f}]e11, "
          f"~{len(vtg2)*(delay+0.2)/60:.1f} min")
    mc=dict(meas_config); mc["bias_voltage_1"]=sr830_1.amplitude()
    mc["comment"]=f"n-linecut fixed D={D} V/nm, n=+1..-8e11, 1nA tc300ms, 4T=sr3(30-31)"
    s=sweep.AsyncStation(mc)
    s.add_comment('nD-map'); s.add_comment('cnp-and-dline-calibration')
    s.add_comment(f'n-linecut D={D} V/nm hole-side candidate scan (cap ratio 1.189)')
    s.ramp(dc205_1.volt,0)
    s.ramp(k_tg.volt,vtg2[0]); s.ramp(k_bg.volt,vbg2[0]); time.sleep(8)
    s.fp(temperature).fp(fridge_temperature)
    s.fp(k_tg.curr).fp(k_bg.curr)
    s.fp(sr830_1.X).fp(sr830_1.P).fp(sr830_2.X).fp(sr830_2.P).fp(sr830_3.X).fp(sr830_3.P)
    s.plot(k_tg.volt, sr830_3.X)    # 4T vs TG (proxy for n along the line)
    s.plot('time', k_bg.curr)       # live leakage
    s.multisweep([k_tg.volt,k_bg.volt],[vtg2,vbg2],delay=delay)

s.ramp(k_tg.volt,0.0); s.ramp(k_bg.volt,0.0)
