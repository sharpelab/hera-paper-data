# === Session park: field to zero, gates to zero, heaters confirmed off ===
_Ts = T_sample()
print(f"pre-park: T={_Ts:.2f} K (passive descent from ladder), B={magnet.field():+.3f} T, "
      f"gates ({k_tg.volt():+.3f}, {k_bg.volt():+.3f}), ranges {heater.sample_range()}/{heater.vaporizer_range()}")
k_tg.volt(0)
k_bg.volt(0)
magnet.field(0.0)   # blocking ramp ~20 min from 2.8 T
print(f"parked: B={magnet.field():+.4f} T, gates ({k_tg.volt():+.3f}, {k_bg.volt():+.3f}), "
      f"T={T_sample():.2f} K, DC205 {dc205.voltage():+.3f} V")
