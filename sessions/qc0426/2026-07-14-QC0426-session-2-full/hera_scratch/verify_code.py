# HERA — session-start VERIFY (read-only; no instrument writes)
print("--- magnet ---")
print(f"field (measured):     {magnet.field():+.4f} T   (expect ~0)")
print(f"persistent switch on: {magnet.persistent_switch_on()}   (expect True)")
print(f"output enabled:       {magnet.output_enabled()}   (expect True)")

print("--- thermometry (worker logfiles) ---")
print(f"T_sample:    {T_sample():.3f} K   (expect ~1.2-1.3 K)")
print(f"T_vaporizer: {T_vaporizer():.3f} K")

print("--- gates (all should be parked at 0) ---")
print(f"k_tg.volt:     {k_tg.volt():+.4f} V")
print(f"k_bg.volt:     {k_bg.volt():+.4f} V")
print(f"dc205.voltage: {dc205.voltage():+.4f} V   range code {dc205.voltage_range()} (need 2)   output {dc205.output()}")

print("--- committed validators (SAFETIES) ---")
print(f"k_tg.volt.vals:           {k_2400_tg.volt.vals}")
print(f"k_bg.volt.vals:           {k_2400_bg.volt.vals}")
print(f"dc205.smart_voltage.vals: {dc205.smart_voltage.vals}")
print(f"dc205.voltage.vals:       {dc205.voltage.vals}")
print(f"magnet.field.vals:        {magnet.field.vals}")

print("--- lock-in bring-up record (tau / slope / sens / amp / freq) ---")
for name, lia in [("sr0", sr0), ("sr1", sr1), ("sr2", sr2), ("sr3", sr3)]:
    print(f"{name}: tau={lia.time_constant()} s  slope={lia.filter_slope()} dB/oct  "
          f"sens={lia.sensitivity()}  amp={lia.amplitude()} V  "
          f"freq={lia.frequency():.3f} Hz  X={lia.X():+.3e}")
