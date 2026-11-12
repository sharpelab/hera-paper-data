import numpy as np, time
# --- preconditions: gates at hole density, magnet ~1.85 T, bias 2 V ---
T0 = heater.sample_temperature()
print('pre: B=%.3f T  TG=%.3f BG=%.3f Si=%.3f  bias=%.2f V  T=%.3f K' % (
    magnet.mag(), dc205.voltage(), k_2400.volt(), k_2410.volt(), sr1.amplitude(), T0))
assert abs(dc205.voltage()-(-4.666)) < 0.05 and abs(k_2400.volt()-(-3.616)) < 0.05, 'gates not at hole'
assert abs(k_2410.volt()) < 1e-6, 'Si not 0'
assert abs(sr1.amplitude()-2.0) < 0.01, 'bias not 2 V'
# sens rescaled for high-field MR rise (Rxx grows) + larger Hall at 8 T
sr1.sensitivity(5e-6); sr2.sensitivity(5e-6); sr3.sensitivity(2e-5)
time.sleep(2)
for k,sr in [('sr0_sens',sr0),('sr1_sens',sr1),('sr2_sens',sr2),('sr3_sens',sr3)]:
    meas_config[k]=sr.sensitivity()
meas_config['comments'] = ('SdH spot-check HOLE n=-10e12 D=0 HIGH-FIELD (20nA); B 2->8T dB=15mT; '
                           'SdH marginal <4T (T_e damping) -> push to 8T cap; onset+tones; T_start=%.3f K' % T0)
s = async_station(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment(meas_config['comments'])
s.fp(magnet.mag); s.fp(k_2400.curr); s.fp(k_2410.curr); s.fp(sr0.X)
for sr in (sr1, sr2, sr3):
    s.fp(sr.X); s.fp(sr.Y); s.fp(sr.R)
s.plot(magnet.mag, sr2.R)
field = np.arange(2.0, 8.0 + 1e-9, 0.015)   # 2 -> 8 T ascending, 15 mT (401 pts)
s.sweep(magnet.mag, field, delay=0.5)
print('spot HF done; B=%.3f T  T_end=%.3f K' % (magnet.mag(), heater.sample_temperature()))
