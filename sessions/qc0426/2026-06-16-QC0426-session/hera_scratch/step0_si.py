# === Step 0 — energize Si to +50 V (contact doping) + CNP safety cut ===
# Graphite bottom gate screens Si from the channel (operator): expect CNP
# unshifted; Si dopes the contacts. Mandatory leakage watch on the 50 V gate.
import numpy as np, time

# --- Preconditions ---
assert abs(magnet.mag()) < 0.05, f"field not ~0 T: {magnet.mag()}"
assert heater.sample_temperature() < 2.0, f"T not at base: {heater.sample_temperature()}"
print("pre: B =", magnet.mag(), "T ; T =", heater.sample_temperature(), "K ; Si =", k_2410.volt(), "V")

# Re-assert provided contact routing (relays persist, cheap safety).
mux.select({"source": "T2", "drain": "T7", "sr1+": "T3", "sr1-": "T4",
            "sr2+": "B4", "sr2-": "B5", "sr3+": "T5", "sr3-": "B6"})

# --- Ramp Si 0 -> +50 V in 5 V steps, leakage-monitored (abort > 2 nA) ---
for v in np.linspace(5, 50, 10):
    k_2410.volt(float(v))
    il = k_2410.curr()
    print(f"Si {v:4.0f} V   I_leak = {il:.2e} A")
    assert abs(il) < 2e-9, f"Si leakage {il:.2e} A at {v} V — ABORT"
print("Si energized:", k_2410.volt(), "V ; leak", k_2410.curr(), "A")
time.sleep(10)  # settle contacts/gate

# --- CNP safety cut: 1D TG at BG=0, B=0 (confirm CNP unshifted, contacts ok) ---
mc = dict(meas_config)
mc["sr0"]="drain current on T7"; mc["sr1"]="Rxx T3-T4"; mc["sr2"]="Rxx B4-B5"; mc["sr3"]="Rxy T5-B6"
mc["comments"]="Si=+50V CNP safety cut: 1D TG -3..+3 V, BG=0, B=0"

s = async_station(mc)
s.add_comment('reentry-baseline')
s.add_comment('Si=+50V contact-doping CNP safety check (graphite screens channel)')
s.add_comment('TG -3..+3 V, BG=0, B=0')
s.ramp(k_bg.volt, 0)
s.fp(k_bg.curr).fp(k_2410.curr)
for sr in [sr0, sr1, sr2, sr3]:
    s.fp(sr.X).fp(sr.P)
s.plot(dc205_volt, sr0.X)
try:
    s.sweep(dc205_volt, np.linspace(-3.0, 3.0, 61), delay=1.0)
finally:
    s.ramp(dc205_volt, 0)
print("done; Si held +50 V, TG parked 0")
