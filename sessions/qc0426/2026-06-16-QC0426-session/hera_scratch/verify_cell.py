# === Session-start VERIFY (read-only) — QC0426 / VTI, 2026-06-16 ===
# Run AFTER the Setup section (cells 2-16) and SAFETIES (cell 18).
# No hardware moves here — reads only.

# (1) Magnet: measured field (set-vs-read) + PS heater / output status
print("magnet.mag() [measured T]:", magnet.mag())
_st = magnet._status()
print("magnet._status():", _st)

# (2) Temperature: sample base + vaporizer
print("sample_temperature (K) :", heater.sample_temperature())
print("vaporizer_temperature (K):", heater.vaporizer_temperature())

# (3) SAFETIES committed — echo the validators actually on the params
print("dc205_volt.vals  :", dc205_volt.vals)
print("k_tg.voltage.vals:", k_tg.voltage.vals)
print("k_bg.volt.vals   :", k_bg.volt.vals)
print("k_2410.volt.vals :", k_2410.volt.vals)
print("magnet.mag.vals  :", magnet.mag.vals)
print("Si k_2410.volt() :", k_2410.volt())  # standing screening-gate setpoint

# (4) Lock-in settling (rig card: record tau/slope at bring-up; metadata stores None)
for nm, sr in [("sr0", sr0), ("sr1", sr1), ("sr2", sr2), ("sr3", sr3)]:
    print(f"{nm}: f={sr.frequency()} Hz  tau={sr.time_constant()} s  "
          f"slope={sr.filter_slope()}  sens={sr.sensitivity()}  amp={sr.amplitude()}")
