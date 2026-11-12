# === Gate C — provided-contact liveness scout (first-session branch) ===
# Route the provided contact config, confirm contacts alive + device passes
# current, and scout the CNP along a 1D TG sweep at B=0, BG=Si=0. No
# references this session -> qualitative liveness (reentry-baseline
# first-session branch), not a quantitative reentry comparison.

# --- Preconditions (state this cell assumes but does not set) ---
assert abs(magnet.mag()) < 0.01, f"field not ~0 T: {magnet.mag()}"
assert heater.sample_temperature() < 2.0, f"T not at base: {heater.sample_temperature()}"
print("pre: B =", magnet.mag(), "T ;  T =", heater.sample_temperature(), "K")
print("pre: BG =", k_bg.volt(), "V ;  Si =", k_2410.volt(), "V ;  TG =", k_tg.voltage(), "V")

# --- Route the provided contact configuration ---
mux.select({"source": "T2", "drain": "T7",
            "sr1+": "T3", "sr1-": "T4",
            "sr2+": "B4", "sr2-": "B5",
            "sr3+": "T5", "sr3-": "B6"})
print("mux: source T2, drain T7 | sr1 T3-T4 | sr2 B4-B5 | sr3 T5-B6")

# --- Per-run measurement config (real contact labels + comment) ---
mc = dict(meas_config)
mc["sr0"] = "drain current on T7"
mc["sr1"] = "Rxx T3-T4"
mc["sr2"] = "Rxx B4-B5"
mc["sr3"] = "Rxy T5-B6"
mc["comments"] = "Gate C liveness scout: 1D TG sweep -5.9->+6.9 V, BG=Si=0, B=0"

s = async_station(mc)
s.add_comment('reentry-baseline')
s.add_comment('gate-C liveness scout, first-session branch (no references)')
s.add_comment('TG sweep -5.9 -> +6.9 V, BG=0, Si=0, B=0')

# Park BG/Si at 0; start TG at the hole end (smooth DC205 ramp from current V).
s.ramp(k_bg.volt, 0)
s.ramp(k_2410.volt, 0)

# Monitor: Keithley gate-leakage currents + all lock-in X/P.
s.fp(k_bg.curr).fp(k_2410.curr)
for sr in [sr0, sr1, sr2, sr3]:
    s.fp(sr.X).fp(sr.P)

s.plot(dc205_volt, sr0.X)  # live drain current

try:
    s.sweep(dc205_volt, np.linspace(-5.9, 6.9, 79), delay=1.0)
finally:
    s.ramp(dc205_volt, 0)
print("done; TG parked at 0 V")
