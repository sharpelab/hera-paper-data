import numpy as np
import time

# --- preconditions ---
T = temperature(); B = magnet.field()
print(f"precond: T = {T*1e3:.1f} mK ; B = {B*1e3:.4f} mT (pristine) ; "
      f"k_tg={k_tg.volt():+.3f} k_bg={k_bg.volt():+.3f} V")
assert T < 0.1, f"T not at base: {T} K"
assert abs(B) < 0.005, f"field not pristine: {B} T"

# drive at validated 0.5 nA
sr830_1.amplitude(0.05)
meas_config["bias_voltage_1"] = sr830_1.amplitude()
assert abs(sr830_1.amplitude() - 0.05) < 1e-4, "drive not at 0.5 nA"
print(f"drive 0.5 nA OK (I_bias {meas_config['bias_voltage_1']/meas_config['bias_resistor']*1e9:.3f} nA)")

k_tg.nplci(1); k_bg.nplci(1)

# remainder rows of the same 61-pt BG grid; TG fast axis identical to run 2
bg_full = np.linspace(-4.0, 4.2, 61)
bg_slow = bg_full[44:]                  # +2.013 .. +4.2, 17 rows
tg_fast = np.linspace(-7.0, 6.0, 101)

meas_config["comment"] = (
    "Step-1 gatemap REMAINDER (stitches onto run 2 rows 0-43): BG slow [2.013,4.2] (17) "
    "x TG fast [-7,6] (101), B~0 pristine, drive 0.5 nA; sr4 dropped (unusable)"
)
s = sweep.AsyncStation(meas_config)
s.add_comment('gatemap')
s.add_comment('zf1 Step-1 remainder; BG slow [2.013,4.2] (17), TG fast [-7,6] (101); stitch onto run 2; B~0; 0.5 nA')

s.ramp(k_bg.volt, bg_slow[0])
s.ramp(k_tg.volt, tg_fast[0])
time.sleep(10)

s.fp(temperature)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
for lia in (sr830_1, sr830_2, sr830_3):   # sr4 dropped (unusable + fewer SNAP reads)
    s.fp(lia.X).fp(lia.P)

s.plot(k_bg.volt, k_bg.curr)
s.plot('time', k_tg.curr)
s.plot(k_tg.volt, sr830_3.X)

try:
    s.megasweep(k_bg.volt, bg_slow, k_tg.volt, tg_fast, slow_delay=3, fast_delay=1)
finally:
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)
