# Fine high-SNR zoom on the candidate low-Rxx spot found at the extremal-D edge
# (corner map run 9): n~-5e11, D~-0.67 V/nm, Rxx 4-7 Ohm (2 adjacent pixels,
# 4x below local baseline, sane phase, in the s41586 proximity-SC prior).
# Goal: confirm it is real/contiguous, locate its minimum, characterize extent.
# If real -> bias spectroscopy for a critical current next. 4T=sr3(30-31).
import numpy as np, time

T=temperature(); B=magnet.field()
print(f"T={T*1e3:.1f} mK  B={B*1e3:.3f} mT  amp={sr830_1.amplitude()} V")
assert T<0.08; assert abs(B)<0.01

for sr in (sr830_1,sr830_2,sr830_3): sr.time_constant(0.3)   # high SNR
sr830_1.amplitude(0.1)
sr830_1.sensitivity(2e-3); sr830_2.sensitivity(2e-3)
sr830_3.sensitivity(5e-5)      # caps ~500 Ohm; fine low-R resolution (spot ~4 Ohm)
print("tc:",sr830_3.time_constant()," sr3 sens:",sr830_3.sensitivity())

N_tg,N_bg=41,26
tg_vec=np.linspace(-6.0,-5.2,N_tg)     # SLOW; brackets spot TG~-5.6
bg_vec=np.linspace(3.95,4.20,N_bg)     # FAST; up to BG cap (spot BG~4.18)
fast_delay,slow_delay=0.9,1.5
print(f"zoom {N_tg}x{N_bg}, est ~{N_tg*(slow_delay+N_bg*(fast_delay+0.2))/60:.0f} min")

mc=dict(meas_config); mc["bias_voltage_1"]=sr830_1.amplitude()
mc["comment"]="candidate zoom: TG[-6,-5.2] x BG[3.95,4.2] around n~-5e11 D~-0.67, tc300ms sr3 5e-5, 4T=sr3(30-31)"
s=sweep.AsyncStation(mc)
s.add_comment('gatemap'); s.add_comment('cnp-and-dline-calibration')
s.add_comment('fine zoom on candidate low-Rxx spot n~-5e11 D~-0.67 (extremal-D)')
s.ramp(dc205_1.volt,0); s.ramp(k_tg.volt,-6.0); s.ramp(k_bg.volt,3.95); time.sleep(10)
s.fp(temperature).fp(fridge_temperature).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr830_1.X).fp(sr830_1.P).fp(sr830_2.X).fp(sr830_2.P).fp(sr830_3.X).fp(sr830_3.P)
s.plot(k_bg.volt, sr830_3.X); s.plot('time', k_bg.curr); s.plot('time', k_tg.curr)
s.megasweep(k_tg.volt, tg_vec, k_bg.volt, bg_vec, slow_delay=slow_delay, fast_delay=fast_delay)
s.ramp(k_tg.volt,0.0); s.ramp(k_bg.volt,0.0)
