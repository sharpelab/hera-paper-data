# === SESSION SHUTDOWN — safe park ===
print("before:  k_tg=%.4f  k_bg=%.4f  dc205=%.4f  B=%.6f T  T=%.4f K" % (
    k_tg.volt(), k_bg.volt(), dc205_1.volt(), magnet.field(), temperature()))

dc205_1.volt(0)            # DC bias to 0 first (device-card rule)
sr830_1.amplitude(0.004)   # AC excitation to SR830 minimum (un-drive the device)
k_tg.volt(0)               # gates to 0 (rate-limited by volt.step)
k_bg.volt(0)
magnet.field(0)            # magnet to 0 (blocks until holding)

tg, bg, dc, Bf = k_tg.volt(), k_bg.volt(), dc205_1.volt(), magnet.field()
print("AFTER:   k_tg=%.4f V  k_bg=%.4f V  dc205=%.4f V  B=%.6f T  T=%.4f K" % (
    tg, bg, dc, Bf, temperature()))
assert abs(tg) < 1e-3 and abs(bg) < 1e-3, "gates NOT at 0"
assert abs(Bf) < 2e-3, "magnet NOT at ~0"
print(">>> safe park complete: gates 0 V, magnet 0 T, DC bias 0, drive at minimum")
