import numpy as np
import time

# Per-run meas_config (fresh comment, no inherited text)
meas_config['comments'] = ("gatemap B=0 (n,D) cal: fast=DC_bias(TG)[-6,7]x81, "
                           "slow=BG[-4.5,4.5]x41, Si=0, B=0. CNP-line / cap-ratio "
                           "calibration. Contacts T2(src)/B7(drain) sr1=T3-T4 "
                           "sr2=B4-B5 sr3=T5-B6(Hall).")
meas_config['sr0_sens'] = sr0.sensitivity()
meas_config['sr1_sens'] = sr1.sensitivity()
meas_config['sr2_sens'] = sr2.sensitivity()
meas_config['sr3_sens'] = sr3.sensitivity()
meas_config['bias_voltage'] = sr1.amplitude()
meas_config['lockin_freq'] = sr1.frequency()
meas_config['sample_temperature:'] = heater.sample_temperature()
meas_config['Si (V)'] = k_si.volt()

# Preflight (silent preconditions)
print("T:", heater.sample_temperature(), "K  B:", magnet.field(), "T  Si:", k_si.volt(), "V")
print("drive:", sr1.amplitude(), "V  f:", sr1.frequency(), "Hz")

# Ramp gates to start
k_bg.volt(-4.5)
dc205_volt(-6.0)
time.sleep(3)

# Build station + megasweep (TG fast, BG slow)
s = async_station(meas_config)
s.add_comment('gatemap')
s.add_comment('B=0 nD cal: TGfast[-6,7]x81 BGslow[-4.5,4.5]x41 Si=0')
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P).fp(sr2.X).fp(sr2.P).fp(sr3.X).fp(sr3.P)
s.fp(k_bg.curr).fp(k_si.curr)
s.plot(k_bg.volt, k_bg.curr)
s.plot(k_bg.volt, sr1.X)
s.megasweep(k_bg.volt, spoints(-4.5, 4.5, 41),
            dc205_volt, spoints(-6, 7, 81),
            slow_delay=2.0, fast_delay=1.0)
print("megasweep complete")
