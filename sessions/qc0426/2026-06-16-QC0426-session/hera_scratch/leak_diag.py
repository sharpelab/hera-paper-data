# Diagnose the 64 nA reading: config + leakage at 5 V vs 0 V (offset vs real).
print("rangev:", k_2410.rangev(), " rangei:", k_2410.rangei())
for p in ("compliancei","compliance","curr_compliance"):
    try: print(p, "=", getattr(k_2410, p)()); break
    except Exception: pass
print("-- Si = 5 V --")
for _ in range(4): print("  curr:", k_2410.curr())
print("-- ramp Si -> 0 V --")
k_2410.volt.step = 1.0; k_2410.volt.inter_delay = 0.05
k_2410.volt(0.0)
print("Si volt:", k_2410.volt())
for _ in range(4): print("  curr:", k_2410.curr())
