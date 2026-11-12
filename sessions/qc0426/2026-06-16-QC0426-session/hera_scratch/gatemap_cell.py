# === Step 1 — 0 T (n,D) gate map (gatemap.md) ===
# Gate-C scout put the CNP at (TG,BG) ~ (0,0), Si=0. Map the full CNP line
# across the gate window to fit the cap ratio (cnp-and-dline-calibration:
# c_bg/c_tg = -slope) and pick clean hole/electron regions + the D=0 line.
# Geometry-prior slope ~-1.3 -> CNP reaches TG ~ +/-5.2 over BG +/-4, so the
# TG[-5.95,5.95] x BG[-4,4] box brackets it with margin.

# --- Preconditions (assumed, not set here) ---
assert abs(magnet.mag()) < 0.01, f"field not ~0 T: {magnet.mag()}"
assert heater.sample_temperature() < 2.0, f"T not at base: {heater.sample_temperature()}"
print("pre: B =", magnet.mag(), "T ;  T =", heater.sample_temperature(),
      "K ;  Si =", k_2410.volt(), "V")

# --- Per-run config (fresh station -> no stale scout comments) ---
mc = dict(meas_config)
mc["sr0"] = "drain current on T7"
mc["sr1"] = "Rxx T3-T4"
mc["sr2"] = "Rxx B4-B5"
mc["sr3"] = "Rxy T5-B6"
mc["comments"] = "Step1 gatemap: TG[-5.95,5.95]x101 fast x BG[-4,4]x41 slow, Si=0, B=0"

s = async_station(mc)
s.add_comment('gatemap')
s.add_comment('Step1 0T (n,D) map; Si=0; Gate-C scout (file 0) put CNP ~(0,0)')
s.add_comment('fast DC_bias/TG [-5.95,5.95]x101; slow BG [-4,4]x41; slow_delay3 fast_delay1')

# Position slow axis + Si; fast axis (DC205) is positioned by the megasweep.
s.ramp(k_2410.volt, 0)
s.ramp(k_bg.volt, -4)

# Monitor: gate leakage + all lock-in X/P.
s.fp(k_bg.curr).fp(k_2410.curr)
for sr in [sr0, sr1, sr2, sr3]:
    s.fp(sr.X).fp(sr.P)

s.plot(k_bg.volt, k_bg.curr)   # live leakage
s.plot(dc205_volt, sr0.X)      # live current

try:
    s.megasweep(k_bg.volt, np.linspace(-4, 4, 41),
                dc205_volt, np.linspace(-5.95, 5.95, 101),
                slow_delay=3, fast_delay=1)
finally:
    s.ramp(dc205_volt, 0)
    s.ramp(k_bg.volt, 0)
print("done; gates parked at 0")
