# --- LK mass ladder: (n=-6e12, D=0), 6 rungs base..25 K, alternating 3<->8 T sweeps ---
# slug: temperature-dependence-vti  (operator-unbanned this session; see markdown)
import time as _time
from pathlib import Path

B0, Ts0 = magnet.field(), T_sample()
print(f"pre: B={B0:+.3f} T | T={Ts0:.3f} K | TG {k_tg.volt():+.3f} BG {k_bg.volt():+.3f} Si {k_si():+.3f}")
assert abs(k_si()) < 0.01, "Si not at 0"
assert abs(sr1.amplitude() - 2.0) < 1e-2, "drive not 2 V"
assert 1.0 < Ts0 < 1.5, "not starting from base"
print(f"sens: sr1 {sr1.sensitivity()}, sr2 {sr2.sensitivity()}, sr3 {sr3.sensitivity()}")

VTG, VBG = -2.8115, -2.1898          # n=-6e12, D=0 (run-4 calibration)
B_LO, B_HI, NPTS = 3.0, 8.0, 251     # dB 20 mT; see markdown
RUNGS = [None, 6.0, 10.0, 14.0, 19.0, 25.0]

def t_fresh():
    p = next(Path(c) for c in VTI.temp_logfile_candidates["T_sample"] if Path(c).exists())
    age = _time.time() - p.stat().st_mtime
    assert age < 15, f"T logfile stale ({age:.0f} s) — lakeshore worker dead?"
    return T_sample()

def hover_wait(nominal, timeout_s=40 * 60):
    """VTI hover acceptance: stable <0.1 K over 90 s within [nom-0.5, nom+3]."""
    t0 = _time.time()
    Tvap0 = T_vaporizer()
    window = []
    while _time.time() - t0 < timeout_s:
        interruptible_sleep(15)
        T = t_fresh()
        Tv = T_vaporizer()
        now = _time.time()
        window.append((now, T))
        window = [(tt, T_) for tt, T_ in window if now - tt <= 90]
        # runaway guard: fault only on true runaway (rising above rung-start AND target)
        assert not (Tv > Tvap0 + 2 and Tv > nominal + 2), f"runaway heating: T_vap {Tv:.2f} K"
        Ts_ = [T_ for _, T_ in window]
        if (now - t0 > 90 and len(Ts_) >= 4 and max(Ts_) - min(Ts_) < 0.1
                and nominal - 0.5 <= np.mean(Ts_) <= nominal + 3):
            print(f"  rung {nominal} K: hover-accepted at {np.mean(Ts_):.2f} K after {(now-t0)/60:.1f} min")
            return float(np.mean(Ts_))
    raise RuntimeError(f"rung {nominal} K: no hover acceptance within {timeout_s/60:.0f} min")

k_tg.volt(VTG); k_bg.volt(VBG)
interruptible_sleep(10)
try:
    for i, rung in enumerate(RUNGS):
        if rung is None:
            T_acc = t_fresh()
            print(f"rung 0 (base): T = {T_acc:.3f} K (T_e ~ 8 K regime — see markdown)")
        else:
            heater.set_both(rung, ratio=0.95)
            T_acc = hover_wait(rung)
        B_now = magnet.field()
        asc = abs(B_now - B_LO) < abs(B_now - B_HI)
        vec = np.linspace(B_LO, B_HI, NPTS) if asc else np.linspace(B_HI, B_LO, NPTS)
        mc = dict(meas_config)
        mc["comments"] = (f"LK ladder rung {i}/{len(RUNGS)-1}: nominal {rung if rung else 'base'} K, "
                          f"accepted {T_acc:.2f} K, n=-6e12 D=0, B {vec[0]:.0f}->{vec[-1]:.0f} T, 20nA@13Hz")
        s = sweep.AsyncStation(mc)
        s.add_comment('temperature-dependence-vti')
        s.add_comment(f'LK mass ladder (Flavor B); rung {i}; nominal {rung} K; n=-6e12, D=0')
        s.fp(T_sample); s.fp(T_vaporizer)
        s.fp(k_tg.curr).fp(k_bg.curr)
        for lia in (sr0, sr1, sr2, sr3):
            s.fp(lia.X).fp(lia.P)
            s.plot(magnet.field, lia.X)
        s.plot('time', T_sample)
        settle_saved = magnet.settle_s
        magnet.settle_s = 1.2
        try:
            s.sweep(magnet.field, vec, delay=0)
        finally:
            magnet.settle_s = settle_saved
finally:
    heater.off('both')
    k_tg.volt(0); k_bg.volt(0)
    print("ladder finally: heaters off, gates parked; ramping B to 0 …")
    magnet.field(0.0)
    print(f"parked: B={magnet.field():+.4f} T, T_sample {T_sample():.3f} K (passive recovery to base)")
