import numpy as np

# Per-run meas_config refresh (no inherited comment text)
meas_config['comments'] = ("reentry-baseline / Gate C liveness: 1D BG sweep "
                           "[-4.5,4.5] @ TG=0, Si=0, B=0. Contacts T2(src)/B7(drain), "
                           "sr1=T3-T4, sr2=B4-B5, sr3=T5-B6(Hall). Confirm contacts "
                           "alive + Rxx responds to gating; bound gate leakage.")
meas_config['sr0_sens'] = sr0.sensitivity()
meas_config['sr1_sens'] = sr1.sensitivity()
meas_config['sr2_sens'] = sr2.sensitivity()
meas_config['sr3_sens'] = sr3.sensitivity()
meas_config['bias_voltage'] = sr1.amplitude()
meas_config['lockin_freq'] = sr1.frequency()
meas_config['sample_temperature:'] = heater.sample_temperature()
meas_config['Si (V)'] = k_si.volt()

# Preflight (silent preconditions + lock-in front-panel settings)
print("T:", heater.sample_temperature(), "K  B:", magnet.field(), "T")
print("drive:", sr1.amplitude(), "V  f:", sr1.frequency(), "Hz")
for nm, sr in [("sr0", sr0), ("sr1", sr1), ("sr2", sr2), ("sr3", sr3)]:
    print(f"  {nm}: tau={sr.time_constant()}s  slope={sr.filter_slope()}  sens={sr.sensitivity()}")

# Start point
dc205_volt(0.0)     # TG -> 0
k_bg.volt(-4.5)     # BG -> sweep start

# Build fresh station, fp channels, sweep
s = async_station(meas_config)
s.add_comment('reentry-baseline')
s.add_comment('GateC liveness: BG[-4.5,4.5] TG=0 Si=0 B=0')
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P).fp(sr2.X).fp(sr2.P).fp(sr3.X).fp(sr3.P)
s.fp(k_bg.curr).fp(k_si.curr)
s.plot(k_bg.volt, sr1.X)
s.sweep(k_bg.volt, spoints(-4.5, 4.5, 91), delay=1.2)
print("sweep complete")
