# === Step 5 Verify — LK mass ladder: n=6.0e12 D=0 electron point, B 2.8-6.0 T, T {base,10,13,16,20,25} K ===
# recipes: temperature-dependence (Flavor B) + temperature-dependence-vti guard set (mandatory)
import os

# --- preconditions ---
_Ts, _B = T_sample(), magnet.field()
print(f"preconditions: T_sample={_Ts:.3f} K (expect base), B={_B:+.4f} T (expect ~1.2 after fan), "
      f"heater ranges={heater.sample_range()}/{heater.vaporizer_range()} (expect 0/0)")
assert 1.0 <= _Ts <= 1.5, f"not at base T: {_Ts:.3f} K"
assert 1.0 < _B < 3.0, f"unexpected field: {_B:+.4f} T"
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0, "heaters not off at ladder start"

vtg_pt, vbg_pt = d0_point(6.0)
k_tg.volt(vtg_pt); k_bg.volt(vbg_pt)
interruptible_sleep(10)
print(f"gates at ({k_tg.volt():+.3f}, {k_bg.volt():+.3f}) (n=6.0e12, D=0)")

B_LO, B_HI, DB = 2.8, 6.0, 0.036
B_up = np.arange(B_LO, B_HI + 1e-9, DB)
RUNGS = [None, 10.0, 13.0, 16.0, 20.0, 25.0]   # None = base rung, no heating

_lf = [p for p in VTI.temp_logfile_candidates["T_sample"] if os.path.exists(p)][0]

def _fresh():
    age = time.time() - os.path.getmtime(_lf)
    assert age < 15, f"T logfile stale ({age:.0f} s) — worker dead? aborting ladder"

def wait_hover(target, tv_start, timeout_s=2400):
    """VTI hover acceptance: stable (spread<0.1 K over 90 s) within [target-0.5, target+3]."""
    t0 = time.time()
    hist = []
    while time.time() - t0 < timeout_s:
        _fresh()
        T_now, Tv_now = T_sample(), T_vaporizer()
        hist.append((time.time(), T_now))
        # direction-aware runaway guard: fault only on true runaway heating
        if Tv_now > max(tv_start, target) + 2.0:
            heater.off('both')
            raise RuntimeError(f"runaway: T_vap={Tv_now:.2f} K > start/target + 2; heaters off")
        recent = [h for h in hist if h[0] > time.time() - 90]
        if len(recent) >= 7:
            Ts = [h[1] for h in recent]
            if (max(Ts) - min(Ts) < 0.1) and (target - 0.5 <= T_now <= target + 3.0):
                return T_now
        interruptible_sleep(10)
    heater.off('both')
    raise RuntimeError(f"hover timeout at target {target} K; heaters off")

for i, rung in enumerate(RUNGS):
    tv_start = T_vaporizer()
    if rung is not None:
        heater.set_both(rung, ratio=0.95)          # sanctioned method; ratio fixed per card
        interruptible_sleep(5)
        r_s, r_v = heater.sample_range(), heater.vaporizer_range()
        print(f"rung {rung} K: ranges {r_s}/{r_v} (expect nonzero)")
        assert r_s > 0 and r_v > 0, "set_both did not enable heater ranges"
        T_acc = wait_hover(rung, tv_start)
        print(f"rung {rung} K accepted at T={T_acc:.3f} K (hover)")
    else:
        print(f"rung base: T={T_sample():.3f} K, no heating")

    # alternate sweep direction from the live field (never re-traverse)
    _Bnow = magnet.field()
    vec = B_up if abs(_Bnow - B_LO) < abs(_Bnow - B_HI) else B_up[::-1]
    if abs(magnet.field() - vec[0]) > 0.05:
        magnet.field(vec[0])                       # blocking pre-position

    lab = f"{rung:.0f}K" if rung is not None else "base"
    meas_config["comments"] = (f"temperature-dependence-vti Flavor B (LK): rung {lab}, n=6.0e12 D=0 electron, "
                               f"B {vec[0]:.1f}->{vec[-1]:.1f} T x{len(vec)} (dB=36 mT), I_bias=20 nA")
    s = sweep.AsyncStation(meas_config)
    s.add_comment('temperature-dependence-vti')
    s.add_comment(f'LK mass ladder rung {lab} (nominal; per-point T is the fit axis), '
                  f'fixed point Vtg={vtg_pt:+.3f} Vbg={vbg_pt:+.3f}, alternating sweep dir')
    s.fp(T_sample).fp(T_vaporizer)
    s.fp(magnet.field)
    s.fp(k_tg.volt).fp(k_tg.curr)
    s.fp(k_bg.volt).fp(k_bg.curr)
    for _l in (sr0, sr1, sr2, sr3):
        s.fp(_l.X).fp(_l.P)
    s.plot(magnet.field, sr1.X)
    s.plot(magnet.field, sr2.X)
    s.plot(magnet.field, sr3.X)
    s.plot(magnet.field, sr0.X)
    s.plot('time', T_sample)
    s.plot('time', T_vaporizer)
    s.sweep(magnet.field, vec, delay=0)
    print(f"rung {lab} sweep done (run dir written); B at {magnet.field():+.2f} T")

heater.off('both')
print("ladder complete; heaters off, passive return to base; field holds at last sweep end")
