# Session closeout — park to safe base state. Si paced (5 mV step consent-gated + 0.05).
import numpy as np, time
print("before: B", magnet.mag(), "T ; Si", k_2410.volt(), "V ; TG", k_tg.voltage(), "; BG(set) 0")
# gates to 0
s = async_station(meas_config); s.ramp(dc205_volt, 0); s.ramp(k_bg.volt, 0)
# Si -> 0 (paced; do NOT change k_2410.volt.step)
assert k_2410.volt.step <= 0.005+1e-9, "k_2410.volt.step coarse (consent-gated)"
k_2410.volt.inter_delay = 0.05
for v in [40.,30.,20.,10.,0.]:
    k_2410.volt(v); time.sleep(0.5)
    print(f"  Si {v:.0f} V  leak {float(np.median([k_2410.curr() for _ in range(3)])):.1e} A")
# magnet -> 0
magnet.mag(0)
print("AFTER: B", magnet.mag(), "T ; Si", k_2410.volt(), "V ; sample T", heater.sample_temperature(), "K")
print("parked: magnet 0, gates 0, Si 0 — safe base state")
