# Clean re-run of the n-linecuts with CORRECTED sr3 sensitivity.
# Bug (logged): voltage channels have a x100 preamp, so the lock-in sees
# V_4T x100; sr3=5uV capped Rxx at ~50 Ohm (runs 2-4 clipped above that).
# Fix: sr3=2e-4 -> caps at V_4T=2uV -> Rxx ~2 kOhm. Goal: true Rxx(n) on the
# hole side at the accessible D, to (a) confirm NO low-Rxx (SC) dip with clean
# data, (b) characterize the resistive plateau (gap vs anomalous metal), (c)
# +D asymmetry control. Recipe: cnp-and-dline-calibration + nD-map. 4T=sr3(30-31).
import numpy as np, time
import scipy.constants as cst

# ---- preconditions ----
T=temperature(); B=magnet.field()
print(f"T={T*1e3:.1f} mK  B={B*1e3:.3f} mT  TG={k_tg.volt():.3f} BG={k_bg.volt():.3f}  amp={sr830_1.amplitude()} V")
assert T<0.08, f"T not base {T*1e3:.1f} mK"
assert abs(B)<0.01, f"B too large {B*1e3:.3f} mT"

# ---- settings: corrected sr3 range ----
for sr in (sr830_1,sr830_2,sr830_3): sr.time_constant(0.3)
sr830_1.sensitivity(2e-3); sr830_2.sensitivity(2e-3)
sr830_3.sensitivity(2e-4)      # x100 preamp aware: caps Rxx ~2 kOhm at 1 nA
print("tc:",sr830_3.time_constant()," sr3 sens:",sr830_3.sensitivity())

# ---- calibrated (n,D) inverse (ratio 1.189; n_off from CNP intercept +0.0259 V) ----
c_tg=cst.epsilon_0*3/23.6e-9; c_bg=cst.epsilon_0*3/20e-9
n_offset=-c_bg*0.0259/cst.e
def gates_for(n_cm,D_vnm):
    n=np.asarray(n_cm)*1e4; D=D_vnm*1e9
    a=(n-n_offset)*cst.e; bb=D*2*cst.epsilon_0
    return (a+bb)/(2*c_tg),(a-bb)/(2*c_bg)
def n_of(vtg,vbg):
    return ((c_tg*np.asarray(vtg)+c_bg*np.asarray(vbg))/cst.e+n_offset)*1e-4

delay=1.0; N=200
for D in (-0.60,-0.45,+0.45):          # hole-side candidate D's + +D asymmetry control
    n_req=np.linspace(1e11,-8e11,N)
    vtg,vbg=gates_for(n_req,D)
    vtg2,vbg2=sanitize_tg_bg(vtg,vbg,tg_lims,bg_lims)
    nr=n_of(vtg2,vbg2)
    print(f"D={D:+.2f} V/nm: {len(vtg2)}/{N} pts, n=[{nr.max()/1e11:+.2f},{nr.min()/1e11:+.2f}]e11, ~{len(vtg2)*1.2/60:.1f} min")
    mc=dict(meas_config); mc["bias_voltage_1"]=sr830_1.amplitude()
    mc["comment"]=f"CLEAN n-linecut D={D} V/nm, n=+1..-8e11, 1nA tc300ms, sr3 sens 2e-4, 4T=sr3(30-31)"
    s=sweep.AsyncStation(mc)
    s.add_comment('nD-map'); s.add_comment('cnp-and-dline-calibration')
    s.add_comment(f'CLEAN n-linecut D={D} V/nm (sr3 range fixed); SC candidate check')
    s.ramp(dc205_1.volt,0)
    s.ramp(k_tg.volt,vtg2[0]); s.ramp(k_bg.volt,vbg2[0]); time.sleep(8)
    s.fp(temperature).fp(fridge_temperature)
    s.fp(k_tg.curr).fp(k_bg.curr)
    s.fp(sr830_1.X).fp(sr830_1.P).fp(sr830_2.X).fp(sr830_2.P).fp(sr830_3.X).fp(sr830_3.P)
    s.plot(k_tg.volt, sr830_3.X); s.plot('time', k_bg.curr)
    s.multisweep([k_tg.volt,k_bg.volt],[vtg2,vbg2],delay=delay)

s.ramp(k_tg.volt,0.0); s.ramp(k_bg.volt,0.0)
