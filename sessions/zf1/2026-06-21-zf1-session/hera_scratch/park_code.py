# Session close — park to a safe resting state (optional: skip if you want to
# stay at SC1 for follow-ups like reproducing on pair 7-31 or a re-run Tc once
# the temperature worker is restarted).
import time
s=sweep.AsyncStation(meas_config)
s.ramp(dc205_1.volt, 0.0)        # device-card: zero DC bias
s.ramp(k_tg.volt, 0.0)
s.ramp(k_bg.volt, 0.0)
print("magnet:", magnet.field(), "T (nominal 0, carries remanence)")
print("heater:", heater.volt(), "V ; gates parked to 0 ; DC bias 0")
print("AC drive left at", sr830_1.amplitude(), "V")
