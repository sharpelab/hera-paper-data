# === LK ladder v2 — X-designed rungs {base,10,15,21,29,41} K; ends HOLDING at 41 K (extend-while-hot) ===
# recipes: temperature-dependence Flavor B + temperature-dependence-vti guard set; new X-design rule
import os

# --- preconditions ---
_Ts, _B = T_sample(), magnet.field()
print(f"preconditions: T_sample={_Ts:.3f} K (expect base after park), B={_B:+.4f} T (expect ~0), "
      f"heater ranges={heater.sample_range()}/{heater.vaporizer_range()} (expect 0/0)")
assert 1.0 <= _Ts <= 1.6, f"not at base T: {_Ts:.3f} K"
assert abs(_B) <= 0.05, f"field not parked at 0: {_B:+.4f} T"
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0, "heaters not off at ladder start"

vtg_pt, vbg_pt = d0_point(6.0)
k_tg.volt(vtg_pt); k_bg.volt(vbg_pt)
interruptible_sleep(10)
print(f"gates at ({k_tg.volt():+.3f}, {k_bg.volt():+.3f}) (n=6.0e12, D=0 electron point)")

# sensitivities as v1 (comparability)
sr1.sensitivity(1e-5); sr2.sensitivity(5e-6); sr3.sensitivity(1e-4); sr0.sensitivity(5e-2)

B_LO, B_HI, DB = 2.8, 6.0, 0.036
B_up = np.arange(B_LO, B_HI + 1e-9, DB)
RUNGS = [None, 10.0, 15.0, 21.0, 29.0, 41.0]   # None = base; X_ML ~ 0.73,1.10,1.54,2.12,3.00

_lf = [p for p in VTI.temp_logfile_candidates["T_sample"] if os.path.exists(p)][0]

def _fresh():
    age = time.time() - os.path.getmtime(_lf)
    assert age < 15, f"T logfile stale ({age:.0f} s) — worker dead? aborting ladder"

def wait_hover(target, tv_start, timeout_s=2400):
    t0 = time.time()
    hist = []
    while time.time() - t0 < timeout_s:
        _fresh()
        T_now, Tv_now = T_sample(), T_vaporizer()
        hist.append((time.time(), T_now))
        if Tv_now > max(tv_start, target) + 2.0:
            heater.off('both')
            raise RuntimeError(f"runaway: T_vap={Tv_now:.2f} K; heaters off")
        recent = [h for h in hist if h[0] > time.time() - 90]
        if len(recent) >= 7:
            Ts_r = [h[1] for h in recent]
            if (max(Ts_r) - min(Ts_r) < 0.1) and (target - 0.5 <= T_now <= target + 3.0):
                return T_now
        interruptible_sleep(10)
    heater.off('both')
    raise RuntimeError(f"hover timeout at {target} K; heaters off")

magnet.field(B_LO)   # blocking ramp 0 -> 2.8 T (~20 min)

for rung in RUNGS:
    tv_start = T_vaporizer()
    if rung is not None:
        heater.set_both(rung, ratio=0.95)
        interruptible_sleep(5)
        assert heater.sample_range() > 0 and heater.vaporizer_range() > 0, "set_both did not enable ranges"
        T_acc = wait_hover(rung, tv_start)
        print(f"rung {rung} K accepted at T={T_acc:.3f} K (hover)")
    else:
        print(f"rung base: T={T_sample():.3f} K")

    _Bnow = magnet.field()
    vec = B_up if abs(_Bnow - B_LO) < abs(_Bnow - B_HI) else B_up[::-1]
    if abs(magnet.field() - vec[0]) > 0.05:
        magnet.field(vec[0])

    lab = f"{rung:.0f}K" if rung is not None else "base2"
    meas_config["comments"] = (f"temperature-dependence-vti Flavor B (LK v2, X-designed): rung {lab}, "
                               f"n=6.0e12 D=0 electron, B {vec[0]:.1f}->{vec[-1]:.1f} T x{len(vec)}, I_bias=20 nA")
    s = sweep.AsyncStation(meas_config)
    s.add_comment('temperature-dependence-vti')
    s.add_comment(f'LK ladder v2 rung {lab}: top X>=3 for m_ML=0.019 at B_eff=3.82 (new X-design rule); '
                  f'fixed point Vtg={vtg_pt:+.3f} Vbg={vbg_pt:+.3f}; base2 doubles as repro check vs run 10')
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
    print(f"rung {lab} sweep done; B at {magnet.field():+.2f} T")

print("LADDER v2 TOP RUNG DONE — HOLDING at 41 K, heaters ON.")
print("HERA: re-fit ML amplitude now; execute EXACTLY ONE of the next two cells (extend 50 K | shutdown).")
