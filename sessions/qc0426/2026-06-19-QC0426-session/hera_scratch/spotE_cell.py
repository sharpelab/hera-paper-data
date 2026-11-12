import numpy as np, time
# --- electron-side both-signs check (Step 3): n=+5e12, D=0; reuse 8 T on the descent ---
T0 = heater.sample_temperature()
assert magnet.mag() > 7.9, 'expected ~8 T for descending electron sweep'
assert abs(sr1.amplitude()-2.0) < 0.01 and abs(k_2410.volt()) < 1e-6
VTG, VBG = +2.337, +1.811           # n=+5e12 at D=0 (mirror of the hole point)
dc205_volt(VTG); k_2400.volt(VBG)
for w in range(25):
    if abs(k_2400.volt()-VBG) < 0.005 and abs(dc205.voltage()-VTG) < 0.005: break
    time.sleep(1)
sr1.sensitivity(2e-5); sr2.sensitivity(2e-5); sr3.sensitivity(1e-4); time.sleep(2)
Ib = sr1.amplitude()/100e6
print('gates settled %ds: TG=%.3f BG=%.3f | n=+5e12 @ %.2fT  I=%.2fnA  sr1=%.0f sr2=%.0f Hall=%.0f Ohm' % (
    w, dc205.voltage(), k_2400.volt(), magnet.mag(), sr0.X()/(-1e6)*1e9, sr1.R()/Ib, sr2.R()/Ib, sr3.R()/Ib))
for k,sr in [('sr0_sens',sr0),('sr1_sens',sr1),('sr2_sens',sr2),('sr3_sens',sr3)]:
    meas_config[k]=sr.sensitivity()
meas_config['comments'] = ('SdH spot-check ELECTRON n=+5e12 D=0 (both-signs check, Step 3); '
                           'B 8->0T dB=20mT descending; 20nA; T_start=%.3f K' % T0)
s = async_station(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment(meas_config['comments'])
s.fp(magnet.mag); s.fp(k_2400.curr); s.fp(k_2410.curr); s.fp(sr0.X)
for sr in (sr1, sr2, sr3):
    s.fp(sr.X); s.fp(sr.Y); s.fp(sr.R)
s.plot(magnet.mag, sr2.R)
field = np.arange(7.98, -0.001, -0.020)   # 8 -> 0 descending, parks at 0
s.sweep(magnet.mag, field, delay=0.5)
print('electron spot done; B=%.3f T  T_end=%.3f K' % (magnet.mag(), heater.sample_temperature()))
