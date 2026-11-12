# HERA E1 kernel-binding probe — read-only, no instrument writes
print("bound instruments:", type(magnet).__name__, type(dc205).__name__,
      type(k_2400_tg).__name__, type(sr0).__name__)
print("B        :", magnet.field(), "T")
print("T_sample :", T_sample(), "K")
print("V_si     :", dc205.voltage(), "V (expect 0)")
print("V_tg/V_bg:", k_tg.volt(), "/", k_bg.volt(), "V")
print("validators:", k_2400_tg.volt.vals, k_2400_bg.volt.vals,
      dc205.smart_voltage.vals, magnet.field.vals)
