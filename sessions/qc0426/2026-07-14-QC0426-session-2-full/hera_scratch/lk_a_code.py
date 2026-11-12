# === Cell A: thermal proof base -> 3 -> 10 -> 50 K, END HOLDING AT 50 K ===
import os, time
from sharpelab_nb.constants import VTI as _VTI

k_tg.volt(0); k_bg.volt(0)
print(f"gates parked; B={magnet.field():+.3f} T (stays)")

def logfile_fresh(max_age_s=30):
    paths = [p for p in _VTI.temp_logfile_candidates["T_sample"] if os.path.exists(p)]
    age = time.time() - max(os.path.getmtime(p) for p in paths)
    assert age < max_age_s, f"T_sample logfile stale ({age:.0f} s) — lakeshore worker dead?"

logfile_fresh()
print(f"start: T={T_sample():.3f} K, T_vap={T_vaporizer():.3f} K")

def set_T_verified(target, hold_s=60, timeout_s=None, poll_s=10):
    """set_both(target, 0.99) + settle-verify off the worker logfile. Returns settle time [s]."""
    tol = max(0.05, 0.005 * target)
    timeout_s = timeout_s or (900 if target < 20 else 1800)
    heater.set_both(target, ratio=0.99)
    print(f"--> set_both({target}, 0.99): ranges=({heater.sample_range()},{heater.vaporizer_range()}), tol={tol*1e3:.0f} mK")
    t0, ok_since = time.time(), None
    while True:
        interruptible_sleep(poll_s)
        logfile_fresh()
        el, T, Tv = time.time() - t0, T_sample(), T_vaporizer()
        if int(el) % 60 < poll_s:
            print(f"    {el:5.0f} s  T={T:7.3f}  T_vap={Tv:7.3f}")
        assert Tv < target * 1.3 + 2, f"vaporizer overshoot: T_vap={Tv:.2f} K"
        if abs(T - target) <= tol:
            ok_since = ok_since or time.time()
            if time.time() - ok_since >= hold_s:
                print(f"    SETTLED {target} K in {el:.0f} s (T_vap={Tv:.3f})")
                return el
        else:
            ok_since = None
        if el > timeout_s:
            raise RuntimeError(f"timeout: {target} K not settled in {timeout_s} s (T={T:.3f})")

settle_log = {}
try:
    for target in (3.0, 10.0, 50.0):
        settle_log[target] = set_T_verified(target)
except BaseException:
    heater.off('both')
    print("EXCEPTION/interrupt -> heaters OFF (safe drift)")
    raise

print("\n=== up-leg summary (feeds ladder pricing) ===")
for k, v in settle_log.items():
    print(f"  {k} K: settled in {v:.0f} s ({v/60:.1f} min)")
print(f"HOLDING at 50 K (heaters ON). T={T_sample():.3f} K. Run the ladder cell next.")
