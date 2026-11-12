# === Gate C — cheap liveness on the provided contact configuration ===
# E1 auto: ContactMux routing + a small in-validator TG trace at B=0, BG=Si=0.
# Confirms (1) current passes, (2) Rxx channels live and modulate with gate,
# (3) channels independent (no grounded-device short), (4) BG/Si leakage at floor.
# NOT range-finding (blocklisted): TG stays well inside the provided [-6,+7] V
# validator (sweep -3..+3 V). Current-bias (5 nA) -> modulation is in the Rxx
# voltage channels; sr0 (drain current) should stay ~constant.

# --- preconditions (state this cell assumes but does not set) ---
B0 = magnet.mag(); T0 = heater.sample_temperature()
assert abs(B0) < 0.01, f'field not ~0: {B0} T'
assert T0 < 1.5,       f'T not at base: {T0} K'
assert abs(k_bg.volt()) < 1e-6 and abs(k_2410.volt()) < 1e-6, 'BG/Si not parked at 0'
print(f'preconditions OK: B={B0:.4f} T, T={T0:.3f} K, BG={k_bg.volt()} V, Si={k_2410.volt()} V')

# --- route the provided contacts (Si 16/11 standing closures are unmanaged/untouched) ---
mux.select({"source": "T2", "drain": "B7",
            "sr1+": "T3", "sr1-": "T4",
            "sr2+": "B4", "sr2-": "B5",
            "sr3+": "T5", "sr3-": "B6"})
print('routed:', mux.mc_fragment())

# --- lock-in sensitivity: 5 mV headroom on the Rxx/Rxy channels so a CNP peak
#     (R up to ~1 MOhm at 5 nA bias) does not overload. Config choice, reversible.
for s_ in (sr1, sr2, sr3):
    s_.sensitivity(0.005)

# --- per-run measurement config (structured, current; no inherited text) ---
meas_config["sr0"] = "drain current on B7 (Ithaco x-1e6)"
meas_config["sr1"] = "Rxx T3-T4"
meas_config["sr2"] = "Rxx B4-B5"
meas_config["sr3"] = "Rxy T5-B6"
meas_config["bias_voltage"] = sr1.amplitude()
meas_config["lockin_freq"] = sr1.frequency()
meas_config["sr0_sens"] = sr0.sensitivity()
meas_config["sr1_sens"] = sr1.sensitivity()
meas_config["sr2_sens"] = sr2.sensitivity()
meas_config["sr3_sens"] = sr3.sensitivity()
meas_config["sample_temperature:"] = heater.sample_temperature()
meas_config["Si (V)"] = k_2410.volt()
meas_config["comments"] = ("Gate C liveness: TG -3..+3 V, BG=Si=0, B=0, "
                           "provided config src T2/drain B7; sr1/2/3 sens 5 mV")

# --- build station fresh (comments are station-lifetime; rebuild per intent) ---
s = async_station(meas_config)
s.add_comment('gate-current-sanity-check')
s.add_comment('Gate C liveness - provided contact config; TG trace BG=Si=0 B=0')

s.ramp(k_bg.volt, 0.0)   # BG already 0; never s.ramp(dc205_volt) -> it has no get

s.fp(heater.sample_temperature)
s.fp(k_bg.curr)
s.fp(k_2410.curr)
for lia in (sr0, sr1, sr2, sr3):
    s.fp(lia.X).fp(lia.P)

s.plot(dc205_volt, sr1.X)
s.plot(dc205_volt, sr2.X)
s.plot(dc205_volt, sr0.X)

# TG sweep -3 -> +3 V (well inside validator), 61 pts, 2.0 s dwell (~settling floor)
try:
    s.sweep(dc205_volt, spoints(-3.0, 3.0, 61), delay=2.0)
finally:
    dc205_volt(0.0)   # park TG via direct set (s.ramp would call the missing get)
print('Gate C liveness sweep done; TG parked at 0.')
