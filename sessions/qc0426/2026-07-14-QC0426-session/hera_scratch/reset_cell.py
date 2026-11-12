# === Reset acquisition state to session-start expectations (handoff) ===
# nplci back to 1 (held Cell B), lock-ins to card values, drive at card default.

k_tg.nplci(1)
k_bg.nplci(1)

for lia in (sr0, sr1, sr2, sr3):
    lia.time_constant(0.3)
    lia.filter_slope(24)
sr0.sensitivity(1e-2)   # card table (metallic-regime drain); note: clips >= ~11 nA
sr1.sensitivity(2e-5)   # CNP / gate-map scale (card)
sr2.sensitivity(2e-5)
sr3.sensitivity(2e-5)
sr1.amplitude(0.5)      # card default drive (0.5 V through bias resistor)

print("--- state readback ---")
print(f"nplci    : tg={k_tg.nplci()}, bg={k_bg.nplci()}")
for lia in (sr0, sr1, sr2, sr3):
    print(f"{lia.name}: tau={lia.time_constant()} s, slope={lia.filter_slope()} dB/oct, "
          f"sens={lia.sensitivity():.1e}, ")
print(f"drive    : {sr1.amplitude()} V @ {sr1.frequency():.3f} Hz")
print(f"gates    : V_tg={k_tg.volt():+.3f} V, V_bg={k_bg.volt():+.3f} V (expect 0/0)")
print(f"Si       : {dc205.voltage():+.3f} V (expect 0), range={dc205.voltage_range()} (RNGE 2), output={dc205.output()}")
print(f"field    : {magnet.field():+.4f} T (expect ~0)")
print(f"T_sample : {T_sample():.3f} K")
print(f"validators: TG {k_2400_tg.volt.vals}, BG {k_2400_bg.volt.vals}, Si {dc205.smart_voltage.vals}, B {magnet.field.vals}")
