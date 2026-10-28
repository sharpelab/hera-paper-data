# Finish Si ramp 30 -> +50 V robustly: coarse step, pacing, longer VISA timeout.
import time
try:
    k_2410.visa_handle.timeout = 10000   # ms, was timing out on rapid writes
    print("visa timeout set 10 s")
except Exception as e:
    print("visa timeout set skipped:", e)
k_2410.volt.step = 0.5          # coarse — Si is a contact gate, no fine res needed
k_2410.volt.inter_delay = 0.02  # pace the Keithley
for v in [35.0, 40.0, 45.0, 50.0]:
    k_2410.volt(v)
    il = k_2410.curr()
    print(f"Si {v:.0f} V   I_leak = {il:.2e} A")
    assert abs(il) < 2e-9, f"Si leakage {il:.2e} A at {v} V — ABORT"
    time.sleep(0.5)
print("Si energized to +50 V ; leak", k_2410.curr(), "A")
k_2410.volt.step = 0.005        # restore fine step
k_2410.volt.inter_delay = 0
