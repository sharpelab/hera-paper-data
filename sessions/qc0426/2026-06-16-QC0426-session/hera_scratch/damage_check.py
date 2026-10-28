# === Damage check — 0 T TG/BG gatemap at Si=0, vs baseline file_id 1 ===
# Post-incident (GPIB jam / Si excursion / range change): confirm the device
# is unchanged. Compare CNP-line slope/position (file 1: slope -1.30, CNP at
# TG~0/BG=0), Rxx scale, channel liveness, and leakage.

# --- Preconditions (assumed, not set) ---
assert abs(magnet.mag()) < 0.05, f"field not ~0 T: {magnet.mag()}"
assert heater.sample_temperature() < 2.0, f"T not at base: {heater.sample_temperature()}"
assert abs(k_2410.volt()) < 0.2, f"Si not ~0 V: {k_2410.volt()}"  # baseline is Si=0
print("pre: B =", magnet.mag(), "T ; T =", heater.sample_temperature(),
      "K ; Si =", k_2410.volt(), "V")

# Re-assert provided contact routing (relays persist; cheap safety).
mux.select({"source": "T2", "drain": "T7", "sr1+": "T3", "sr1-": "T4",
            "sr2+": "B4", "sr2-": "B5", "sr3+": "T5", "sr3-": "B6"})

mc = dict(meas_config)
mc["sr0"]="drain current on T7"; mc["sr1"]="Rxx T3-T4"; mc["sr2"]="Rxx B4-B5"; mc["sr3"]="Rxy T5-B6"
mc["comments"]="Damage-check gatemap: TG[-5,5]x41 fast x BG[-4,4]x15 slow, Si=0, B=0 (vs file 1)"

s = async_station(mc)
s.add_comment('gatemap')
s.add_comment('post-incident damage check, Si=0, B=0; compare CNP line to file_id 1')
s.add_comment('fast DC_bias/TG [-5,5]x41; slow BG [-4,4]x15; slow_delay3 fast_delay1')

s.ramp(k_2410.volt, 0)     # Si stays 0
s.ramp(k_bg.volt, -4)      # slow-axis start

s.fp(k_bg.curr).fp(k_2410.curr)
for sr in [sr0, sr1, sr2, sr3]:
    s.fp(sr.X).fp(sr.P)
s.plot(k_bg.volt, k_bg.curr)   # live leakage
s.plot(dc205_volt, sr0.X)      # live current

try:
    s.megasweep(k_bg.volt, np.linspace(-4, 4, 15),
                dc205_volt, np.linspace(-5, 5, 41),
                slow_delay=3, fast_delay=1)
finally:
    s.ramp(dc205_volt, 0)
    s.ramp(k_bg.volt, 0)
print("done; gates parked at 0")
