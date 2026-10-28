# === Thermal-machinery validation: 3 K / 10 K / 50 K plateaus, then off -> base-ish ===
import os, time
from sharpelab_nb.constants import VTI as _VTI

# park gates for the thermal excursion
k_tg.volt(0); k_bg.volt(0)
print(f"gates parked: Vtg={k_tg.volt():+.3f}, Vbg={k_bg.volt():+.3f}; B={magnet.field():+.3f} T (stays)")

def _logfile_fresh(max_age_s=30):
    paths = [p for p in _VTI.temp_logfile_candidates["T_sample"] if os.path.exists(p)]
    age = time.time() - max(os.path.getmtime(p) for p in paths)
    assert age < max_age_s, f"T_sample logfile stale ({age:.0f} s) — lakeshore worker dead?"
    return age

_logfile_fresh()
print(f"start: T_sample={T_sample():.3f} K, T_vap={T_vaporizer():.3f} K, "
      f"ranges (smp/vap)=({heater.sample_range()},{heater.vaporizer_range()})")

def set_T_verified(target, hold_s=60, timeout_s=None, poll_s=10):
    """set_both + settle-verify off the worker logfile. Returns settle time [s]."""
    tol = max(0.05, 0.005 * target)
    timeout_s = timeout_s or (900 if target < 20 else 1500)
    heater.set_both(target, ratio=0.99)
    print(f"--> set_both({target}, 0.99): ranges (smp/vap)=({heater.sample_range()},{heater.vaporizer_range()}), tol={tol*1e3:.0f} mK")
    t0, ok_since = time.time(), None
    while True:
        interruptible_sleep(poll_s)
        _logfile_fresh()
        el, T, Tv = time.time() - t0, T_sample(), T_vaporizer()
        if int(el) % 60 < poll_s:
            print(f"    {el:5.0f} s  T={T:7.3f}  T_vap={Tv:7.3f}")
        assert Tv < target * 1.3 + 2, f"vaporizer overshoot: T_vap={Tv:.2f} K at target {target} K"
        if abs(T - target) <= tol:
            ok_since = ok_since or time.time()
            if time.time() - ok_since >= hold_s:
                print(f"    SETTLED {target} K in {el:.0f} s (held {hold_s} s within {tol*1e3:.0f} mK; T_vap={Tv:.3f})")
                return el
        else:
            ok_since = None
        if el > timeout_s:
            raise RuntimeError(f"timeout: {target} K not settled in {timeout_s} s (T={T:.3f})")

summary = {}
try:
    for target in (3.0, 10.0, 50.0):
        summary[target] = set_T_verified(target)
finally:
    heater.off('both')
    print("heaters OFF (both) — drifting to base")

# monitored cooldown to <= 1.5 K
t0 = time.time()
while True:
    interruptible_sleep(30)
    _logfile_fresh()
    el, T = time.time() - t0, T_sample()
    if int(el) % 300 < 30:
        print(f"    cooldown {el/60:4.1f} min  T={T:.3f} K")
    if T <= 1.5:
        summary["cooldown_50K_to_1.5K"] = el
        print(f"    BASE-ISH reached: {T:.3f} K in {el/60:.1f} min")
        break
    if el > 5400:
        raise RuntimeError(f"cooldown timeout: T={T:.3f} K after 90 min")

print("\n=== machinery validation summary ===")
for k, v in summary.items():
    print(f"  {k}: {v:.0f} s ({v/60:.1f} min)")
print(f"end state: T={T_sample():.3f} K, T_vap={T_vaporizer():.3f} K, heaters off, gates 0, B={magnet.field():+.3f} T")
