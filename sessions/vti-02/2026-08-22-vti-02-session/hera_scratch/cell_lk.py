# === LK mass ladder (`temperature-dependence-vti`, Flavor B): same field sweep at n = +3.2e12, D = 0, T rungs ascending ===
# Per rung: heater.set_both(T, ratio=0.95) (authorized method; ratio deviations consent-gated) -> hover acceptance
# (spread < 0.1 K over 90 s, within [T-0.5, T+3] K; freshness-guarded) -> field sweep over [2, 7] T, direction
# alternating from the live field (never re-traverse). Base rung first (no heater). Ends with heaters off.
from sharpelab_nb.gates import calc_gate_voltages
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_spot, D_spot = 3.2, 0.0
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX

RUNGS = [None, 6.0, 10.0, 15.0, 22.0, 30.0]          # K; None = base, no heater. All <= T_SESSION_CAP.
assert all(t is None or t <= T_SESSION_CAP for t in RUNGS)
B_A, B_B, DB = 2.0, 7.0, 0.025                       # LK window: 2-7 T, 25 mT (Nyquist on the 44 T harmonic at 2 T: 0.025/4 = 0.0063 <= 0.0114)
I_TRIP = 1e-9
LOG = VTI.temp_logfile_candidates

def fresh_T():
    assert_thermometry_live("T_sample", LOG["T_sample"], max_age=15, max_period=12)
    assert_thermometry_live("T_vaporizer", LOG["T_vaporizer"], max_age=15, max_period=12)
    return T_sample(), T_vaporizer()

def hover_wait(target, max_wait=40 * 60):
    """Hover acceptance: T_sample stable (ptp < 0.1 K over 90 s) inside [target-0.5, target+3]. Runaway guard:
    T_vap > 2 K above both its rung-start value and the target. Returns the accepted T."""
    t0 = time.time(); hist = []; Tv0 = fresh_T()[1]
    while time.time() - t0 < max_wait:
        Ts, Tv = fresh_T(); hist.append((time.time(), Ts))
        hist = [h for h in hist if time.time() - h[0] <= 90]
        if Tv > Tv0 + 2 and Tv > target + 2:
            heater.off('both'); raise RuntimeError(f"runaway: T_vap {Tv:.2f} K > start {Tv0:.2f} + 2 and > target {target} + 2 — heaters off")
        if len(hist) >= 10 and (time.time() - hist[0][0]) >= 85:
            vals = [h[1] for h in hist]
            if (max(vals) - min(vals)) < 0.1 and (target - 0.5) <= Ts <= (target + 3):
                print(f"  hover accepted: T_sample {Ts:.3f} K (target {target}), spread {max(vals)-min(vals):.3f} K / 90 s, T_vap {Tv:.2f} K, {time.time()-t0:.0f} s")
                return Ts
        interruptible_sleep(10)
    raise RuntimeError(f"hover acceptance timed out at target {target} K (T_sample {Ts:.2f})")

# --- preconditions ---
Ts0, Tv0 = fresh_T(); B0 = magnet.field()
print(f"precondition T_sample {Ts0:.3f} K (base), T_vap {Tv0:.3f}, heaters ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0), B = {B0:+.3f} T, V_si {k_si():+.3f}")
assert 1.0 <= Ts0 <= 1.5 and heater.sample_range() == 0 and heater.vaporizer_range() == 0 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
sr1.sensitivity(50e-6)
print(f"spot (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s; rungs {RUNGS}")

mc = dict(meas_config); mc["Si (V)"] = k_si()
s = sweep.AsyncStation(mc)
s.add_comment('temperature-dependence-vti')
s.add_comment(f'Flavor B LK ladder at n = {n_spot:+.2f}e12, D = {D_spot} (run-5 cal), (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); B window [{B_A}, {B_B}] T {DB*1e3:.0f} mT alternating; rungs {RUNGS} K via set_both(T, ratio=0.95), hover acceptance')
s.ramp(k_bg.volt, Vbg_spot); s.ramp(k_tg.volt, Vtg_spot)
s.fp(T_sample).fp(T_vaporizer).fp(k_tg.curr).fp(k_bg.curr)   # LS335 is never polled per point (worker owns it); heater reads are per-rung control reads only
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(magnet.field, sr1.X); s.plot(magnet.field, sr0.X); s.plot('time', T_sample); s.plot('time', k_tg.curr)
# row layout: [time, B, T_sample, T_vap, i_tg, i_bg, sr0X, sr0P, sr1X, sr1P]
def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[4])), abs(float(data[5]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A"); station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    for k, T_target in enumerate(RUNGS):
        if T_target is None:
            Tacc = fresh_T()[0]; print(f"rung {k}: base, T_sample {Tacc:.3f} K")
        else:
            heater.set_both(T_target, ratio=0.95)
            assert heater.sample_range() > 0 and heater.vaporizer_range() > 0, "heater ranges did not go nonzero"
            print(f"rung {k}: set_both({T_target}, 0.95) -> ranges {heater.sample_range()}/{heater.vaporizer_range()}; waiting for hover acceptance")
            Tacc = hover_wait(T_target)
        Bnow = magnet.field()
        Bvec = np.arange(B_A, B_B + 1e-9, DB) if abs(Bnow - B_A) <= abs(Bnow - B_B) else np.arange(B_B, B_A - 1e-9, -DB)
        Bvec = np.round(Bvec, 4); assert Bvec.max() <= B_SESSION_CAP
        s.add_comment(f'rung {k}: target {T_target} K, accepted T_sample {Tacc:.3f} K, sweep {Bvec[0]} -> {Bvec[-1]} T')
        print(f"  sweep {Bvec[0]} -> {Bvec[-1]} T ({len(Bvec)} pts) from B = {Bnow:+.3f}")
        s.sweep(magnet.field, Bvec, delay=0)
        s._comments = [c for c in s._comments if not str(c).startswith('rung ')]   # station-lifetime comments: keep one rung tag per run
finally:
    heater.off('both')
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"ladder end: heaters off (ranges {heater.sample_range()}/{heater.vaporizer_range()}), gates parked, B = {magnet.field():+.3f} T, T_sample {T_sample():.2f} K")
