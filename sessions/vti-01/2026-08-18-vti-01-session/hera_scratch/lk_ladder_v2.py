# === LK mass ladder (temperature-dependence-vti, Flavor B) — branch A mass ===
# n = -1.74e12 at true D=0; per rung: field sweep 2<->5 T (alternating, from the
# live field), 151 pts @ 20 mT, delay 1 s. Rungs [1.2(base), 2.5, 4, 6, 8, 11, 15] K.
# Guards: hover acceptance, freshness (>=2-3 write periods), direction-aware
# runaway on T_vap, set_both(T, ratio=0.95) only. One file per rung.

import time as _time

# --- preconditions ---
_B, _T = magnet.field(), T_sample()
print(f"preconditions: B={_B:+.3f} T (expect ~5, run-12 end), T={_T:.3f} K, "
      f"Vtg={k_tg.volt():+.4f}, Vbg={k_bg.volt():+.4f} (n=-1.74 point), "
      f"drive={sr1.amplitude()*1e3:.0f} mV, heater ranges={heater.sample_range()},{heater.vaporizer_range()}")
assert _T < 2.2, "T not near base band — stop"  # recovering from the v1 fault at 1.94 K
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0, "heaters not off at start — stop"
try:
    _ami = qcodes.Instrument.find_instrument("ami_he")
    print(f"He level: {_ami.He_level():.2f} in")
except Exception as e:
    print(f"He read unavailable: {e!r}")

n_t = -1.74
Vtg_t, Vbg_t = calc_gate_voltages(n_t, -0.009, c_tg_cal, c_bg_cal, n_offset=n_off_e12)
k_tg.volt(Vtg_t); k_bg.volt(Vbg_t)   # re-assert the point (already there)

RUNGS = [2.5, 4.0, 6.0, 8.0, 11.0, 15.0]   # K; base rung done (run 12); ascend
N_PTS, DWELL = 151, 1
prev_T = 1.2   # run-12 base rung

def _fresh():
    assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
    assert_thermometry_live("T_vaporizer", VTI.temp_logfile_candidates["T_vaporizer"], max_age=15, max_period=12)

def wait_rung(target, prev_T, t_max=2400):
    """Hover acceptance v2 (ladder v1 fault: loop equilibrated 0.06 K below the
    absolute band and timed out). Accept STABILITY at the achieved equilibrium:
    spread < 0.1 K over 90 s, T >= prev_T + 0.3 (monotonic ladder), minimum
    240 s on the rung. The fp'd T is the fit axis; nominal rungs are labels.
    Warn (never fault) outside [target-0.8, target+3]; sanity fence +/-5 K."""
    t0 = _time.time(); _fresh()
    Tv0 = T_vaporizer()
    hist = []
    while True:
        _fresh()
        T, Tv = T_sample(), T_vaporizer()
        now = _time.time()
        hist.append((now, T)); hist = [(t, x) for t, x in hist if now - t <= 90]
        if Tv > max(Tv0, target) + 2.0:                    # true runaway only
            heater.off('both')
            raise RuntimeError(f"runaway: T_vap={Tv:.2f} K > start {Tv0:.2f} & target {target} + 2")
        w = [x for _, x in hist]
        if (now - t0 > 240 and len(w) >= 8 and (max(w) - min(w)) < 0.1
                and T >= prev_T + 0.3 and abs(T - target) < 5.0):
            if not (target - 0.8) <= T <= (target + 3):
                print(f"  note: rung {target} K accepted off-nominal at {T:.3f} K (stable equilibrium)")
            return T
        if now - t0 > t_max:
            heater.off('both')
            raise RuntimeError(f"rung {target} K settle timeout ({t_max}s), T={T:.3f}")
        interruptible_sleep(10)

for rung in RUNGS:
    heater.set_both(rung, ratio=0.95)     # sanctioned call, ratio fixed (consent-gated otherwise)
    T_acc = wait_rung(rung, prev_T)
    prev_T = T_acc
    print(f"rung {rung} K accepted at T={T_acc:.3f} K (ranges {heater.sample_range()},{heater.vaporizer_range()})")

    B_now = magnet.field()                    # alternate direction from the LIVE field
    B_vec = (np.linspace(2.0, 5.0, N_PTS) if abs(B_now - 2.0) < abs(B_now - 5.0)
             else np.linspace(5.0, 2.0, N_PTS))
    mc = {**meas_config,
          "sample_temperature:": T_sample(),
          "Si (V)": 0.0,
          "comments": (f"temperature-dependence-vti Flavor B (LK mass, branch A): rung "
                       f"{rung} K (accepted {T_acc:.3f} K), n={n_t}e12 true D=0 "
                       f"(Vtg={Vtg_t:+.4f}, Vbg={Vbg_t:+.4f}), B {B_vec[0]:.1f}->{B_vec[-1]:.1f} T "
                       f"151 pts @ 20 mT, delay 1 s, drive 100 mV, sens sr1/sr3 200uV.")}
    s = sweep.AsyncStation(mc)
    s.add_comment('temperature-dependence-vti')
    s.add_comment(f'LK rung {rung} K: n = {n_t}e12, D = 0 true, B {B_vec[0]:.1f} -> {B_vec[-1]:.1f} T')
    xp = magnet.field
    s.fp(k_tg.curr).fp(k_bg.curr)
    s.fp(T_sample); s.fp(T_vaporizer)
    s.plot(xp, k_tg.curr); s.plot(xp, k_bg.curr)
    s.plot(xp, T_sample); s.plot(xp, T_vaporizer)
    for lia in [sr0, sr1, sr2, sr3]:
        s.fp(lia.X).fp(lia.P)
        s.plot(xp, lia.X); s.plot(xp, lia.P)
    s.ramp(magnet.field, B_vec[0])
    s.sweep(magnet.field, B_vec, delay=DWELL)
    print(f"rung {rung} K sweep done; B at {magnet.field():+.2f} T")

heater.off('both')
print(f"ladder complete; heaters off, cooling passively toward base. "
      f"B at {magnet.field():+.2f} T, gates at n={n_t}. T={T_sample():.2f} K")
