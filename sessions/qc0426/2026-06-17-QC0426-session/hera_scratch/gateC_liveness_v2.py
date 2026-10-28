# === Gate C — cheap liveness on the provided contacts (v2, LS335 fix) ===
# Re-run of cell 30 (errored: per-point heater.sample_temperature poll hit the
# LS335/Grafana VISA-contention quirk). Fix: NO Lakeshore poll inside the loop.
# T is snapshotted once in meas_config; the Grafana logger keeps the time series.
# Otherwise identical: provided contacts, TG -3..+3 V trace, BG=Si=0, B=0.
# Current-bias (5 nA) -> modulation lives in Rxx (sr1/sr2); sr0 (I) ~constant.

# --- preconditions (state this cell assumes but does not set) ---
B0 = magnet.mag(); T0 = heater.sample_temperature()   # single reads OK; not per-point
assert abs(B0) < 0.01, f'field not ~0: {B0} T'
assert T0 < 1.5,       f'T not at base: {T0} K'
assert abs(k_bg.volt()) < 1e-6 and abs(k_2410.volt()) < 1e-6, 'BG/Si not parked at 0'
print(f'preconditions OK: B={B0:.4f} T, T={T0:.3f} K, TG(k_tg)={k_tg.voltage()} V, '
      f'BG={k_bg.volt()} V, Si={k_2410.volt()} V')

# --- route the provided contacts (Si 16/11 standing closures unmanaged/untouched) ---
mux.select({"source": "T2", "drain": "B7",
            "sr1+": "T3", "sr1-": "T4",
            "sr2+": "B4", "sr2-": "B5",
            "sr3+": "T5", "sr3-": "B6"})
print('routed:', mux.mc_fragment())

# --- 5 mV headroom on Rxx/Rxy channels so a CNP peak does not overload ---
for s_ in (sr1, sr2, sr3):
    s_.sensitivity(0.005)

# --- per-run measurement config ---
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
meas_config["comments"] = ("Gate C liveness v2 (LS335 fix): TG -3..+3 V, BG=Si=0, B=0, "
                           "provided config src T2/drain B7; sr1/2/3 sens 5 mV")

# --- build station fresh ---
s = async_station(meas_config)
s.add_comment('gate-current-sanity-check')
s.add_comment('Gate C liveness v2 - no LS335 per-point poll')

s.ramp(k_bg.volt, 0.0)   # BG already 0; never s.ramp(dc205_volt) -> no get

# Followed params: NO heater.sample_temperature (LS335 contention).
s.fp(k_bg.curr)
s.fp(k_2410.curr)
for lia in (sr0, sr1, sr2, sr3):
    s.fp(lia.X).fp(lia.P)

s.plot(dc205_volt, sr1.X)
s.plot(dc205_volt, sr2.X)
s.plot(dc205_volt, sr0.X)

try:
    s.sweep(dc205_volt, spoints(-3.0, 3.0, 61), delay=2.0)
finally:
    dc205_volt(0.0)   # park TG via direct set
print('Gate C liveness v2 done; TG parked at 0.')
