# --- session park: field to zero ---
print(f"pre: B={magnet.field():+.3f} T, TG={k_tg.volt():+.3f}, BG={k_bg.volt():+.3f}, Si={k_si():+.3f}")
magnet.field(0.0)   # blocking ramp
print(f"parked: B={magnet.field():+.4f} T | PS {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
print(f"T_sample {T_sample():.3f} K")
