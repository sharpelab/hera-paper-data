import numpy as np, time
# --- preconditions ---
T0 = heater.sample_temperature(); B0 = magnet.mag()
print('precond: T=%.3f K  B=%.4f T  BG=%.3f  Si=%.3f' % (T0, B0, k_2400.volt(), k_2410.volt()))
assert T0 < 2.0, 'T high'
assert abs(B0) < 0.05, 'B not ~0 (spot check must start near 0 for onset)'
assert abs(k_2410.volt()) < 1e-6, 'Si not 0'
# --- target: hole n=-10e12 cm^-2 at D=0 ---
VTG, VBG = -4.666, -3.616
meas_config['comments'] = ('SdH spot-check HOLE n=-10e12 cm^-2 D=0 (V_tg=%.3f V_bg=%.3f); '
                           'B 0->4T dB=10mT; onset + tone content; T_start=%.3f K' % (VTG, VBG, T0))
s = async_station(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment(meas_config['comments'])
s.fp(magnet.mag)                 # measured field per point (for 1/B FFT)
s.fp(k_2400.curr); s.fp(k_2410.curr)
for sr in (sr0, sr1, sr2, sr3):
    s.fp(sr.X); s.fp(sr.P)
s.plot(magnet.mag, sr1.X)
# ramp gates to (n=-10e12, D=0) at B=0
s.ramp(k_2400.volt, VBG)
s.ramp(dc205_volt, VTG)
time.sleep(2)
print('at target: TG=%.3f BG=%.3f  I_drain=%.3f nA' % (dc205.voltage(), k_2400.volt(), sr0.X()/(-1e6)*1e9))
field = np.arange(0.0, 4.0 + 1e-9, 0.010)   # 0..4 T, 10 mT step (401 pts)
s.sweep(magnet.mag, field, delay=0.5)
print('spot A done; B=%.3f T  T_end=%.3f K' % (magnet.mag(), heater.sample_temperature()))
