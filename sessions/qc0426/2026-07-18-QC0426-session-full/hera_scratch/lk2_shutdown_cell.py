# === LK ladder v2 — shutdown: heaters off, passive return to base; park field + gates ===
heater.off('both')
print(f"heaters off at T={T_sample():.2f} K; passive descent to base")
k_tg.volt(0); k_bg.volt(0)
magnet.field(0.0)   # blocking ~23 min from 6 T / ~0 from 2.8 depending on last leg
print(f"parked: B={magnet.field():+.4f} T, gates (0,0), T={T_sample():.2f} K (descending), DC205 {dc205.voltage():+.3f} V")
