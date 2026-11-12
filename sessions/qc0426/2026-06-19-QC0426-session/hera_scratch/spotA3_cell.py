import numpy as np, time
# --- preconditions: gates at hole density, magnet at 4 T ---
T0 = heater.sample_temperature()
print('pre: B=%.3f T  TG=%.3f BG=%.3f Si=%.3f  T=%.3f K' % (magnet.mag(), dc205.voltage(), k_2400.volt(), k_2410.volt(), T0))
assert abs(dc205.voltage()-(-4.666)) < 0.05 and abs(k_2400.volt()-(-3.616)) < 0.05, 'gates not at hole'
assert abs(k_2410.volt()) < 1e-6, 'Si not 0'
assert magnet.mag() > 3.9, 'expected magnet near 4 T for descending sweep'
# --- raise bias for SNR (tested: 4x current -> SNR 14-60, linear, no heating); rescale sens ---
sr1.amplitude(2.0); time.sleep(3)
sr0.sensitivity(5e-2); sr1.sensitivity(2e-6); sr2.sensitivity(2e-6); sr3.sensitivity(1e-5)
time.sleep(2)
meas_config['bias_voltage'] = sr1.amplitude()
for k,sr in [('sr0_sens',sr0),('sr1_sens',sr1),('sr2_sens',sr2),('sr3_sens',sr3)]:
    meas_config[k]=sr.sensitivity()
meas_config['comments'] = ('SdH spot-check HOLE n=-10e12 D=0 (2V bias=20nA, SNR-fixed); '
                           'B 4->0T dB=10mT; fp X/Y/R; T_start=%.3f K' % T0)
s = async_station(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment(meas_config['comments'])
s.fp(magnet.mag); s.fp(k_2400.curr); s.fp(k_2410.curr); s.fp(sr0.X)
for sr in (sr1, sr2, sr3):
    s.fp(sr.X); s.fp(sr.Y); s.fp(sr.R)
s.plot(magnet.mag, sr2.R)
field = np.arange(4.0, 0.0 - 1e-9, -0.010)   # descending 4 -> 0 (reuse 4 T position)
s.sweep(magnet.mag, field, delay=0.5)
print('spot A v3 done; B=%.3f T  T_end=%.3f K' % (magnet.mag(), heater.sample_temperature()))
