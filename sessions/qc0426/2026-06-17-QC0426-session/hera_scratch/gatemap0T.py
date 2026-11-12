# === 0 T TG-BG gate map (gatemap.md) — substrate for CNP/(n,D) calibration ===
# B=0, Si=0. Axis-aligned RAW-gate-voltage megasweep (cap ratios not yet trusted).
# Geometry prior: CNP slope dVtg/dVbg = -c_bg/c_tg ~ -1.3, intercept ~0 (CNP near
# origin, confirmed by Gate C liveness). TG fast [-6,+6] catches the CNP line at
# every BG row in [-4.5,+4.5]. Stays inside validators (TG [-6,7], BG [-4.5,4.5]).

# --- preconditions (state assumed, not set by this cell) ---
B0 = magnet.mag(); T0 = heater.sample_temperature()
assert abs(B0) < 0.01, f'field not ~0: {B0} T'
assert T0 < 1.5,       f'T not base: {T0} K'
assert abs(k_2410.volt()) < 1e-6, f'Si not at 0: {k_2410.volt()} V'
print(f'pre: B={B0:.4f}T T={T0:.3f}K Si={k_2410.volt()}V TG(k_tg)={k_tg.voltage()}V BG={k_bg.volt()}V')

# re-assert provided routing (idempotent; Si 16/11 unmanaged/untouched)
mux.select({"source":"T2","drain":"B7","sr1+":"T3","sr1-":"T4",
            "sr2+":"B4","sr2-":"B5","sr3+":"T5","sr3-":"B6"})

# sens 0.5 mV: headroom over the ~1.4k oblique-cut CNP peak at 5 nA, resolves a
# kOhm ridge, safe against overload at the symmetric 2D CNP. (Config choice.)
for s_ in (sr1, sr2, sr3): s_.sensitivity(5e-4)

meas_config["sr0"]="drain current B7 (Ithaco x-1e6)"; meas_config["sr1"]="Rxx T3-T4"
meas_config["sr2"]="Rxx B4-B5"; meas_config["sr3"]="Rxy T5-B6"
meas_config["bias_voltage"]=sr1.amplitude(); meas_config["lockin_freq"]=sr1.frequency()
meas_config["sr0_sens"]=sr0.sensitivity(); meas_config["sr1_sens"]=sr1.sensitivity()
meas_config["sr2_sens"]=sr2.sensitivity(); meas_config["sr3_sens"]=sr3.sensitivity()
meas_config["sample_temperature:"]=heater.sample_temperature(); meas_config["Si (V)"]=k_2410.volt()
meas_config["comments"]=("0T gatemap: BG[-4.5,4.5]x25 (slow) x TG[-6,6]x61 (fast), "
                         "Si=0, src T2/drain B7, sens 0.5mV")

s = async_station(meas_config)
s.add_comment('gatemap')
s.add_comment('0T TG-BG map; Si=0; provided contacts; CNP/(n,D) calibration substrate')

s.ramp(k_bg.volt, -4.5)   # slow-axis start (k_bg has a get -> s.ramp ok)
# TG fast axis starts at -6 via the sweep's first set; never s.ramp(dc205_volt).

s.fp(k_bg.curr); s.fp(k_2410.curr)              # NO LS335 poll (contention)
for lia in (sr0, sr1, sr2, sr3): s.fp(lia.X).fp(lia.P)

s.plot(k_bg.volt, sr1.X)
s.plot(dc205_volt, sr1.X)
s.plot(dc205_volt, sr2.X)

# slow = BG (25 rows), fast = TG (61 pts). fast_delay 1.2 s (~4 tau; CNP is a
# strong feature, not a weak tone), slow_delay 2.0 s.
try:
    s.megasweep(k_bg.volt,    spoints(-4.5, 4.5, 25),
                dc205_volt,    spoints(-6.0, 6.0, 61),
                slow_delay=2.0, fast_delay=1.2)
finally:
    dc205_volt(0.0); k_bg.volt(0.0)
print('gatemap done; TG & BG parked at 0.')
