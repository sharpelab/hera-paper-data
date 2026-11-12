# Extremal-D corner map — explore the high-|D| wedge out to the -0.76 V/nm cap,
# which the constant-D=-0.60 linecuts and the (clipped) survey did NOT cleanly
# cover. Bounded by BG=+4.2 (the validator that caps -D); max |D| rises 0.66->0.76
# as n deepens. sr3 PROPERLY RANGED (2e-4, no clip). Recipe: gatemap + nD region.
import numpy as np, time

T=temperature(); B=magnet.field()
print(f"T={T*1e3:.1f} mK  B={B*1e3:.3f} mT  TG={k_tg.volt():.3f} BG={k_bg.volt():.3f}  amp={sr830_1.amplitude()} V")
assert T<0.08, f"T not base {T*1e3:.1f} mK"
assert abs(B)<0.01, f"B too large {B*1e3:.3f} mT"

# settings (sr3 fixed for the full Rxx range; current-bias 1 nA)
for sr in (sr830_1,sr830_2,sr830_3): sr.time_constant(0.1)
sr830_1.amplitude(0.1)
sr830_1.sensitivity(2e-3); sr830_2.sensitivity(2e-3); sr830_3.sensitivity(2e-4)
print("tc:",sr830_3.time_constant()," amp:",sr830_1.amplitude()," sr3 sens:",sr830_3.sensitivity())

N_tg,N_bg=51,49
tg_vec=np.linspace(-7.0,-4.5,N_tg)     # SLOW; -7 corner first (highest |D|/leakage -> early checkpoint)
bg_vec=np.linspace(3.0,4.2,N_bg)       # FAST; BG=4.2 is the -D cap edge
fast_delay,slow_delay=0.3,1.0
print(f"corner map {N_tg}x{N_bg}, D up to -0.76 V/nm cap, est ~{N_tg*(slow_delay+N_bg*(fast_delay+0.2))/60:.0f} min")

mc=dict(meas_config); mc["bias_voltage_1"]=sr830_1.amplitude()
mc["comment"]="extremal-D corner map: TG[-7,-4.5] x BG[3.0,4.2], D->-0.76 cap, sr3 2e-4 (no clip), 4T=sr3(30-31)"
s=sweep.AsyncStation(mc)
s.add_comment('gatemap'); s.add_comment('cnp-and-dline-calibration')
s.add_comment('extremal-|D| corner map to the -0.76 V/nm cap (SC re-check)')
s.ramp(dc205_1.volt,0); s.ramp(k_tg.volt,-7.0); s.ramp(k_bg.volt,3.0); time.sleep(10)
s.fp(temperature).fp(fridge_temperature).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr830_1.X).fp(sr830_1.P).fp(sr830_2.X).fp(sr830_2.P).fp(sr830_3.X).fp(sr830_3.P)
s.plot(k_bg.volt, sr830_3.X); s.plot('time', k_bg.curr); s.plot('time', k_tg.curr)
s.megasweep(k_tg.volt, tg_vec, k_bg.volt, bg_vec, slow_delay=slow_delay, fast_delay=fast_delay)
s.ramp(k_tg.volt,0.0); s.ramp(k_bg.volt,0.0)
