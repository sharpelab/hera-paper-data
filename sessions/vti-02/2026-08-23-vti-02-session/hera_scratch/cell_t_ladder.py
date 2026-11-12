# HERA — plan step 5: temperature ladder of R_CNP at five D values (B = 0), one run per T point
_T, _B, _Vsi = T_sample(), magnet.field(), dc205.voltage()
print(f"precheck: T_sample={_T:.3f} K (want base 1.0-1.5) | B={_B:.4f} T (want |B|<0.02, not ramping: {not magnet.is_ramping()}) | "
      f"V_si={_Vsi:.3f} V (want 0) | heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (want 0/0) | T_vap={T_vaporizer():.3f} K")
assert 1.0 <= _T <= 1.5, "not at base"
assert abs(_B) < 0.02 and not magnet.is_ramping(), "magnet not at zero"
assert abs(_Vsi) < 0.01, "Si not at 0 V"
for _s in (sr0, sr1):
    _s.time_constant(0.1)

# five CNP points from run 4 (V_bg, V_tg*): D-D0 ~ -0.11, 0, +0.10, +0.19, +0.28 V/nm; +/-75 mV TG window @5 mV each
_PTS = [(+0.40, -0.271), (0.00, +0.110), (-0.45, +0.371), (-0.80, +0.618), (-1.15, +0.890)]
_dv = np.round(np.arange(-0.075, 0.075 + 1e-9, 0.005), 4)
_vt_list, _vb_list = [], []
for _vb0, _vt0 in _PTS:
    _vt, _vb = sanitize_tg_bg(_vt0 + _dv, np.full_like(_dv, _vb0), tg_lims, bg_lims)
    _vt_list.append(_vt); _vb_list.append(_vb)
_vt_all = np.concatenate(_vt_list); _vb_all = np.concatenate(_vb_list)
assert _vt_all.min() >= TG_MIN and _vt_all.max() <= TG_MAX and _vb_all.min() >= BG_MIN and _vb_all.max() <= BG_MAX
T_LADDER = [None, 2.0, 3.0, 4.5, 6.5, 9.0, 13.0, 18.0, 25.0, 35.0, 50.0]   # None = base, heaters off
RATIO = 0.95
assert max(t for t in T_LADDER if t) <= T_SESSION_CAP
print(f"ladder: {len(T_LADDER)} T points, {len(_vt_all)} pts per run (~{len(_vt_all)*0.68/60:.1f} min each)")


def settle_T(target, max_wait=600, window=60, tol_frac=0.03, tol_abs=0.05):
    """Hover acceptance (rig card): accept when T_sample has been stable over `window` s, not on proximity."""
    t0 = time.time(); hist = []
    interruptible_sleep(90)
    while time.time() - t0 < max_wait:
        hist.append((time.time(), T_sample()))
        recent = [T for (tt, T) in hist if tt > time.time() - window]
        if len(recent) >= 6 and (max(recent) - min(recent)) < max(tol_frac * target, tol_abs):
            return np.mean(recent), True
        interruptible_sleep(10)
    return T_sample(), False


ladder_runs = []
for _Tset in T_LADDER:
    if _Tset is None:
        _Tnow, _ok = T_sample(), True
    else:
        heater.set_both(_Tset, ratio=RATIO)
        _Tnow, _ok = settle_T(_Tset)
    print(f"[{time.strftime('%H:%M:%S')}] T set {_Tset} -> T_sample {_Tnow:.3f} K (stable={_ok}); T_vap {T_vaporizer():.3f} K; "
          f"ranges {heater.sample_range()}/{heater.vaporizer_range()}")
    meas_config["sample_temperature:"] = T_sample()
    meas_config["Si (V)"] = dc205.voltage()
    meas_config["comments"] = f"cnp-t-ladder: T_set={_Tset} K (T_sample {_Tnow:.3f} K), 5 CNP windows (D-D0 -0.11,0,+0.10,+0.19,+0.28), B=0"
    s = sweep.AsyncStation(meas_config)
    s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.Y).fp(k_tg.curr).fp(k_bg.curr).fp(T_sample).fp(T_vaporizer)
    s.add_comment("cnp-t-ladder")
    s.add_comment(f"T_set={_Tset} K ratio {RATIO}, T_sample at start {_Tnow:.3f} K stable={_ok}; multisweep [k_bg.volt,k_tg.volt] over 5 windows "
                  f"V_bg in {[p[0] for p in _PTS]} x TG +/-75 mV @5mV about {[p[1] for p in _PTS]}; delay 0.5 s, tau 100 ms; B=0, V_si=0; I_bias 10 nA")
    ar1 = SrAutoRange(sr1, cols=(5, 6), gain=1.0, lo=1e-6, hi=0.5)
    s.register_run_after(ar1, args=())
    for _p in (sr1.X, sr0.X, sr1.Y, sr0.P, T_sample, k_tg.curr, k_bg.curr, T_vaporizer):
        s.plot(k_tg.volt, _p)
    res = s.multisweep([k_bg.volt, k_tg.volt], [_vb_all, _vt_all], delay=0.5)
    ladder_runs.append((_Tset, _Tnow, res.id))
    print(f"   run {res.id} done; T_sample now {T_sample():.3f} K")
    if s.interrupt_requested or getattr(s, "_interrupted", False):
        print("interrupted — stopping ladder"); break

heater.off()
print(f"heaters off: ranges {heater.sample_range()}/{heater.vaporizer_range()}; T_sample {T_sample():.3f} K")
print("ladder runs:", ladder_runs)
