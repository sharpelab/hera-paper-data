# HERA E1 kernel-bind + VERIFY-completion probe — READ-ONLY (no hardware writes).
# Confirms this kernel carries the operator's instruments, finishes the session-start
# VERIFY field/T reads, echoes the committed SAFETIES validators, and records the
# lock-in tau/slope (rig card: operator-set, not in run metadata).
_g = globals()
print("=== namespace bind ===")
for _n in ("magnet", "heater", "sr0", "sr1", "sr2", "sr3", "k_2400", "k_2410",
           "dc205", "qsw", "mux", "dc205_volt", "k_tg", "k_bg", "k_si"):
    print(f"  {_n:11s} {type(_g[_n]).__name__ if _n in _g else 'MISSING'}")

print("=== magnet  (VERIFY: 0 T) ===")
print("  mag() =", magnet.mag(), " status field =", magnet._status()['field'])
print("  PS_on =", magnet.persistent_switch_on(), " output_enabled =", magnet.output_enabled())

print("=== thermometry  (VERIFY: base 1.2-1.3 K) ===")
print("  sample_T =", heater.sample_temperature(), " vaporizer_T =", heater.vaporizer_temperature())

print("=== SAFETIES validators  (echo committed ranges) ===")
print("  dc205_volt.vals =", dc205_volt.vals)
print("  k_2400.volt.vals =", k_2400.volt.vals, " (k_bg)")
print("  k_2410.volt.vals =", k_2410.volt.vals, " (k_si)")
print("  magnet.mag.vals  =", magnet.mag.vals)

print("=== lock-in settling  (tau / slope / sens) ===")
for _s in (sr0, sr1, sr2, sr3):
    print(f"  {_s.name}: tau={_s.time_constant()}  slope={_s.filter_slope()}  sens={_s.sensitivity()}")
