# FINAL insurance check — low-excitation linecut at the highest reachable |D|.
# Closes the one open hedge in the not-SC call: a very fragile SC could be
# suppressed by the 1 nA sense current. Drop to 0.2 nA (amp 0.02 V), tc=1 s for
# SNR, scan the hole-side metallic region where any SC would live. If Rxx still
# shows no dip toward 0, the not-SC call is firm at low drive too.
import numpy as np, time
import scipy.constants as cst

T=temperature(); B=magnet.field()
print(f"T={T*1e3:.1f} mK  B={B*1e3:.3f} mT  amp(before)={sr830_1.amplitude()} V")
assert T<0.08; assert abs(B)<0.01

sr830_1.amplitude(0.02)             # 0.02 V / 100 MOhm -> 0.2 nA
for sr in (sr830_1,sr830_2,sr830_3): sr.time_constant(1.0)   # 1 s for low-drive SNR
sr830_1.sensitivity(1e-3)           # current 0.2 nA*1e6=0.2 mV
sr830_3.sensitivity(2e-5)           # 4T: metallic ~4 nV*100=0.4uV; caps Rxx ~1 kOhm at 0.2 nA
print("amp:",sr830_1.amplitude()," tc:",sr830_3.time_constant()," sr3 sens:",sr830_3.sensitivity())

c_tg=cst.epsilon_0*3/23.6e-9; c_bg=cst.epsilon_0*3/20e-9; n_offset=-c_bg*0.0259/cst.e
def gates_for(n_cm,D_vnm):
    n=np.asarray(n_cm)*1e4; D=D_vnm*1e9
    a=(n-n_offset)*cst.e; bb=D*2*cst.epsilon_0
    return (a+bb)/(2*c_tg),(a-bb)/(2*c_bg)

D=-0.60; n_req=np.linspace(-2e11,-8e11,150)
vtg,vbg=gates_for(n_req,D); vtg2,vbg2=sanitize_tg_bg(vtg,vbg,tg_lims,bg_lims)
print(f"D={D} V/nm low-I: {len(vtg2)}/150 pts, ~{len(vtg2)*3.2/60:.1f} min")
mc=dict(meas_config); mc["bias_voltage_1"]=sr830_1.amplitude()
mc["comment"]=f"low-I insurance linecut D={D} V/nm, n=-2..-8e11, 0.2nA tc1s, 4T=sr3(30-31)"
s=sweep.AsyncStation(mc)
s.add_comment('nD-map'); s.add_comment('cnp-and-dline-calibration')
s.add_comment(f'low-excitation (0.2nA) linecut D={D} — fragile-SC suppression check')
s.ramp(dc205_1.volt,0)
s.ramp(k_tg.volt,vtg2[0]); s.ramp(k_bg.volt,vbg2[0]); time.sleep(8)
s.fp(temperature).fp(fridge_temperature).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr830_1.X).fp(sr830_1.P).fp(sr830_3.X).fp(sr830_3.P)
s.plot(k_tg.volt, sr830_3.X); s.plot('time', k_bg.curr)
s.multisweep([k_tg.volt,k_bg.volt],[vtg2,vbg2],delay=3.0)
# restore standard drive + park
sr830_1.amplitude(0.1)
s.ramp(k_tg.volt,0.0); s.ramp(k_bg.volt,0.0)
