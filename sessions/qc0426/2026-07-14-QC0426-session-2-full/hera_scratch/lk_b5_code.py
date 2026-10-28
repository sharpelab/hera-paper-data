# === Cell B v5 (hover acceptance; rungs 2-8): LK ladder 25 -> base (logfile guard 90 s; directional vap guard) ===
def logfile_fresh(max_age_s=90):
    paths = [p for p in _VTI.temp_logfile_candidates["T_sample"] if os.path.exists(p)]
    age = time.time() - max(os.path.getmtime(p) for p in paths)
    assert age < max_age_s, f"T_sample logfile stale ({age:.0f} s) — lakeshore worker dead?"

# (v3 ladder body — identical to v2 below)
from sharpelab_nb.gates import calc_gate_voltages

def hover_at(target, band=(-0.5, 3.0), spread=0.10, window_s=90, timeout_s=1200, poll_s=15):
    """set_both already/now engaged; accept quasi-stationary T near nominal.
    Returns (elapsed, T_at_accept). Directional vaporizer guard retained."""
    Tv_start = T_vaporizer()
    heater.set_both(target, ratio=0.99)
    print(f"--> set_both({target}, 0.99) + hover accept: band [{target+band[0]:.1f},{target+band[1]:.1f}] K, spread<{spread} K/{window_s}s")
    t0, hist = time.time(), []
    while True:
        interruptible_sleep(poll_s)
        logfile_fresh()
        el, T, Tv = time.time() - t0, T_sample(), T_vaporizer()
        hist.append((time.time(), T))
        hist = [h for h in hist if h[0] > time.time() - window_s]
        if int(el) % 60 < poll_s:
            print(f"    {el:5.0f} s  T={T:7.3f}  T_vap={Tv:7.3f}")
        assert not (Tv > Tv_start + 2 and Tv > target + 2), f"vaporizer RUNAWAY: T_vap={Tv:.2f}"
        Ts = [h[1] for h in hist]
        if (len(hist) >= 4 and max(Ts) - min(Ts) < spread
                and target + band[0] <= T <= target + band[1]):
            print(f"    HOVER-ACCEPTED at T={T:.3f} K (nominal {target}) in {el:.0f} s")
            return el, T
        if el > timeout_s:
            raise RuntimeError(f"hover at {target} K not reached in {timeout_s} s (T={T:.3f})")

def set_T_verified(target, hold_s=60, timeout_s=None, poll_s=10):
    """set_both + settle-verify (logfile). Vaporizer guard is directional:
    fault only on runaway heating (Tv > start+2 AND Tv > target+2)."""
    tol = max(0.05, 0.005 * target)
    timeout_s = timeout_s or (900 if target < 20 else 1800)
    Tv_start = T_vaporizer()
    heater.set_both(target, ratio=0.99)
    print(f"--> set_both({target}, 0.99): ranges=({heater.sample_range()},{heater.vaporizer_range()}), "
          f"tol={tol*1e3:.0f} mK, Tv_start={Tv_start:.2f}")
    t0, ok_since = time.time(), None
    while True:
        interruptible_sleep(poll_s)
        logfile_fresh()
        el, T, Tv = time.time() - t0, T_sample(), T_vaporizer()
        if int(el) % 60 < poll_s:
            print(f"    {el:5.0f} s  T={T:7.3f}  T_vap={Tv:7.3f}")
        assert not (Tv > Tv_start + 2 and Tv > target + 2), \
            f"vaporizer RUNAWAY: T_vap={Tv:.2f} K (start {Tv_start:.2f}, target {target})"
        if abs(T - target) <= tol:
            ok_since = ok_since or time.time()
            if time.time() - ok_since >= hold_s:
                print(f"    SETTLED {target} K in {el:.0f} s (T_vap={Tv:.3f})")
                return el
        else:
            ok_since = None
        if el > timeout_s:
            raise RuntimeError(f"timeout: {target} K not settled in {timeout_s} s (T={T:.3f})")

_B0 = magnet.field()
print(f"precheck: T={T_sample():.3f} K (drifting down from 50), B={_B0:+.3f} T, Vsi={dc205.voltage():+.3f}")
assert abs(dc205.voltage()) < 1e-3
logfile_fresh()

C_TG, C_BG, N_OFF = 1.7027e-3, 2.1751e-3, -0.0365
vtg_t, vbg_t = calc_gate_voltages(+6.0, 0.0, C_TG, C_BG, n_offset=N_OFF)
sr1.sensitivity(2e-5); sr2.sensitivity(2e-5); sr3.sensitivity(5e-5); sr0.sensitivity(5e-2)
k_tg.volt(vtg_t); k_bg.volt(vbg_t)
print(f"electron point set: Vtg {vtg_t:+.3f}, Vbg {vbg_t:+.3f}")

RUNGS = [18.0, 14.0, 10.0, 7.0, 5.0, 3.0, None]   # rung 1 (25 K) = run 10, done
N_PTS = 421

try:
    for i, rung in enumerate(RUNGS):
        if rung is not None:
            # descend with heaters OFF (fast), catch 0.2 K below, lift + hold
            if T_sample() > rung + 0.3:
                heater.off('both')
                print(f"--> descending to {rung} K (heaters off)")
                t0d = time.time()
                while T_sample() > rung - 0.2:
                    interruptible_sleep(10)
                    logfile_fresh()
                    if int(time.time() - t0d) % 120 < 10:
                        print(f"    descend {time.time()-t0d:5.0f} s  T={T_sample():7.3f}")
                    if time.time() - t0d > 3600:
                        raise RuntimeError(f"descent to {rung} K timed out (T={T_sample():.3f})")
                print(f"    passed {rung} K after {time.time()-t0d:.0f} s — catching")
            settle, T_accept = hover_at(rung)
        else:
            heater.off('both')
            print("--> heaters OFF, settling to base (<=1.6 K)")
            t0 = time.time()
            while T_sample() > 1.6:
                interruptible_sleep(30)
                logfile_fresh()
                if time.time() - t0 > 3600:
                    raise RuntimeError(f"base not reached in 60 min (T={T_sample():.3f})")
            settle = time.time() - t0
        T_now = T_sample()

        down = magnet.field() > 6.0   # start at the nearer endpoint (restart-robust)
        B_vec = np.linspace(8.0, 4.0, N_PTS) if down else np.linspace(4.0, 8.0, N_PTS)

        s = sweep.AsyncStation(meas_config)
        s.add_comment('temperature-dependence')
        s.add_comment(f'LK ladder rung {i+1}/{len(RUNGS)}: T = {T_now:.3f} K '
                      f'({"base" if rung is None else str(rung)+" K set"}), electron n = +6e12, D = 0 '
                      f'({vtg_t:.3f}, {vbg_t:.3f}); B {B_vec[0]:.0f}->{B_vec[-1]:.0f} T uniform 9.5 mT; '
                      f'I_bias=20 nA, sens fixed across ladder, settle {settle:.0f} s, cal run 4')
        s.fp(T_sample)
        s.fp(k_tg.volt).fp(k_tg.curr)
        s.fp(k_bg.volt).fp(k_bg.curr)
        s.plot('time', k_tg.curr)
        s.plot('time', k_bg.curr)
        for lia in (sr0, sr1, sr2, sr3):
            s.fp(lia.X).fp(lia.P)
            s.plot(magnet.field, lia.X)
        s.sweep(magnet.field, B_vec, delay=1.2)
        print(f"    rung {i+1} done: T was {T_now:.3f} K (now {T_sample():.3f} K)")
finally:
    heater.off('both')
    k_tg.volt(0); k_bg.volt(0)
    print(f"ladder exit: heaters off, gates parked, T={T_sample():.3f} K, B={magnet.field():+.3f} T")
