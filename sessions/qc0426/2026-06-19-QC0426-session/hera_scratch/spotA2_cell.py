import numpy as np, time
# --- preconditions: gates still at hole density, magnet at ~2 T (sweep ramps it to 0) ---
T0 = heater.sample_temperature()
print('pre: B=%.3f T  TG=%.3f BG=%.3f Si=%.3f  T=%.3f K' % (magnet.mag(), dc205.voltage(), k_2400.volt(), k_2410.volt(), T0))
assert abs(dc205.voltage()-(-4.666)) < 0.05 and abs(k_2400.volt()-(-3.616)) < 0.05, 'gates not at hole n=-10e12'
assert abs(k_2410.volt()) < 1e-6, 'Si not 0'
# --- lock-in config for high-n metallic SdH (Rxx ~tens of Ohm) ---
sr1.time_constant(0.3)              # was 0.03 (too noisy); match sr2/sr3
sr1.sensitivity(2e-6)               # |R|~128 Ohm -> ~30% FS
sr2.sensitivity(5e-7)               # |R|~26 Ohm  -> ~24% FS  (cleanest channel)
# sr3=5e-6 (Hall, grows to ~250 Ohm @4T), sr0=1e-2 already set
time.sleep(3)
for k,sr in [('sr0_sens',sr0),('sr1_sens',sr1),('sr2_sens',sr2),('sr3_sens',sr3)]:
    meas_config[k]=sr.sensitivity()
meas_config['comments'] = ('SdH spot-check HOLE n=-10e12 D=0 (re-run, proper sens; sr1 tau 0.3); '
                           'B 0->4T dB=10mT; fp X/Y/R, Rxx=|R| (phase offset cosmetic); T_start=%.3f K' % T0)
s = async_station(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment(meas_config['comments'])
s.fp(magnet.mag); s.fp(k_2400.curr); s.fp(k_2410.curr); s.fp(sr0.X)
for sr in (sr1, sr2, sr3):
    s.fp(sr.X); s.fp(sr.Y); s.fp(sr.R)
s.plot(magnet.mag, sr2.R)          # live: clean-channel magnitude
field = np.arange(0.0, 4.0 + 1e-9, 0.010)   # first point ramps 2->0, then up to 4 T
s.sweep(magnet.mag, field, delay=0.5)
print('spot A v2 done; B=%.3f T  T_end=%.3f K' % (magnet.mag(), heater.sample_temperature()))
