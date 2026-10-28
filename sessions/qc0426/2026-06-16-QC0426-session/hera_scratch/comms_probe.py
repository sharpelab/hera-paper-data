# READ-ONLY comms probe — no gate writes. Find if k_2410 is wedged or the bus.
import time
def tryread(name, fn):
    t=time.time()
    try:
        v=fn(); print(f"OK   {name}: {v}   ({time.time()-t:.1f}s)")
    except Exception as e:
        print(f"FAIL {name}: {type(e).__name__}: {str(e)[:70]}   ({time.time()-t:.1f}s)")
tryread("magnet.mag", magnet.mag)
tryread("sample_T", heater.sample_temperature)
tryread("sr0.X", sr0.X)
tryread("sr1.X", sr1.X)
tryread("k_bg.curr (other Keithley)", k_bg.curr)
tryread("k_2410.curr (Si)", k_2410.curr)
tryread("k_2410.volt get (Si)", k_2410.volt)
