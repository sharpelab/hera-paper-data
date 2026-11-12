# Precondition reads (silent preconditions) — read-only
print("sample T :", heater.sample_temperature(), "K   (expect ~base 1.2-1.3 K)")
print("B before :", magnet.field(), "T (measured readback)")
print("PS heater:", magnet.persistent_switch_on(), "| output:", magnet.output_enabled())

# Ramp to 0 T for the B=0 (n,D) gate map / VERIFY. ~0.30 T / 0.137 T/min ~= 2.2 min, blocks.
magnet.field(0.0)

print("B after  :", magnet.field(), "T (measured readback)")
