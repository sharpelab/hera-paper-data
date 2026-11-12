# Aaron's suggestion: VISA device clear on k_2410 to unwedge the GPIB bus.
import time
try:
    k_2410.visa_handle.clear()
    print("device clear sent to k_2410")
except Exception as e:
    print("clear raised:", type(e).__name__, str(e)[:120])

def tryread(name, fn):
    t=time.time()
    try: print(f"OK   {name}: {fn()}   ({time.time()-t:.1f}s)")
    except Exception as e: print(f"FAIL {name}: {type(e).__name__}: {str(e)[:60]}   ({time.time()-t:.1f}s)")

# k_2410 comms test (reads only; do NOT re-set rangev — QC raised it for +50 V)
tryread("k_2410 IDN", k_2410.IDN)
tryread("k_2410.rangev", k_2410.rangev)
tryread("k_2410.volt get", k_2410.volt)
tryread("k_2410.curr", k_2410.curr)
# did the clear free the rest of the GPIB bus?
tryread("k_bg.curr", k_bg.curr)
tryread("sr0.X", sr0.X)
tryread("sample_T (LS335)", heater.sample_temperature)
