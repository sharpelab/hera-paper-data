# Re-energize Si to +50 V — COARSE step (lesson: fine 5 mV step flooded GPIB).
import time
try: k_2410.visa_handle.timeout = 10000
except Exception as e: print("vt skip:", e)
k_2410.volt.step = 1.0          # coarse: ~50 writes total, not 10k
k_2410.volt.inter_delay = 0.05  # pace the bus
print("range:", k_2410.rangev(), "V ; start Si:", k_2410.volt(), "V")
for v in range(5, 51, 5):
    k_2410.volt(float(v))
    il = k_2410.curr()
    print(f"Si {v:3d} V   I_leak = {il:.2e} A")
    assert abs(il) < 2e-9, f"Si leak {il:.2e} at {v} V — ABORT"
    time.sleep(0.3)
print("Si energized:", k_2410.volt(), "V ; leak", k_2410.curr(), "A")
