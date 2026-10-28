# Bias spectroscopy (dV/dI vs I_dc) — the decisive SC test at the confirmed
# low-Rxx arc minimum (run 10): n=-5.02e11, D=-0.673 V/nm (TG=-5.64, BG=4.20),
# Rxx->0.6 Ohm. A supercurrent lobe (dV/dI ~0 for |I_dc|<Ic, rising at Ic) is
# the SC tell; flat ohmic dV/dI = good metal. Recipe: bias-spectroscopy.md.
# I_ac dropped to 0.5 nA (<< expected Ic); DC bias via dc205_1 / 100 MOhm.
import numpy as np, time

T=temperature(); B=magnet.field()
print(f"T={T*1e3:.1f} mK  B={B*1e3:.3f} mT  TG={k_tg.volt():.3f} BG={k_bg.volt():.3f}")
assert T<0.08, f"T not base {T*1e3:.1f} mK"
assert abs(B)<0.01, f"B too large {B*1e3:.3f} mT"

# gate to the arc minimum
s_pre=sweep.AsyncStation(meas_config)
s_pre.ramp(dc205_1.volt,0.0)
s_pre.ramp(k_tg.volt,-5.640); s_pre.ramp(k_bg.volt,4.200)

# excitation: 0.5 nA AC (gentle), tc 300 ms; sr3 ranged for 0-400 Ohm dV/dI
sr830_1.amplitude(0.05)          # 0.05 V / 100 MOhm = 0.5 nA AC
for sr in (sr830_1,sr830_2,sr830_3): sr.time_constant(0.3)
sr830_1.sensitivity(1e-3); sr830_3.sensitivity(2e-5)
time.sleep(5)
print(f"gates TG={k_tg.volt():.3f} BG={k_bg.volt():.3f}  I_ac={sr830_1.amplitude()/1e8*1e9:.2f} nA")
# zero-bias differential R right now
r0=(sr830_3.X()/100)/(sr830_1.X()/-1e6)
print(f"zero-bias dV/dI = {r0:.2f} Ohm  (arc Rxx was ~0.6 Ohm)")

# DC bias round-trip: I_dc = V/1e8; +/-2 V = +/-20 nA
fwd=np.linspace(-2.0,2.0,81); bwd=np.linspace(2.0,-2.0,81)
vdc=np.hstack([fwd,bwd])
print(f"DC bias +/-20 nA round-trip, {len(vdc)} pts (~0.5 nA step)")

mc=dict(meas_config); mc["bias_voltage_1"]=sr830_1.amplitude()
mc["comment"]="bias-spec dV/dI vs Idc at arc min n=-5.02e11 D=-0.673 (TG-5.64,BG4.20); Iac=0.5nA, +/-20nA roundtrip, B=0"
s=sweep.AsyncStation(mc)
s.add_comment('bias-spectroscopy')
s.add_comment('dV/dI vs Idc at SC-candidate arc minimum n=-5.02e11 D=-0.673, B=0 base T')
s.ramp(dc205_1.volt,-2.0); time.sleep(8)
s.fp(temperature).fp(fridge_temperature).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr830_1.X).fp(sr830_1.P).fp(sr830_3.X).fp(sr830_3.P)
s.plot(dc205_1.volt, sr830_3.X)     # live dV/dI proxy vs DC bias
s.sweep(dc205_1.volt, vdc, delay=1.0)
s.ramp(dc205_1.volt,0.0)            # device-card: zero DC bias when done
