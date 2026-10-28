# HERA — plan step 2: coarse full-box gate map at B = 0 (CNP line, D-dependence, offsets)
_T, _B, _Vsi = T_sample(), magnet.field(), dc205.voltage()
print(f"precheck: T_sample={_T:.3f} K (want 1.0-1.4) | B={_B:.4f} T (want |B|<0.02) | V_si={_Vsi:.3f} V (want 0) | "
      f"gates now V_tg={k_tg.volt():.3f} V_bg={k_bg.volt():.3f}")
assert 1.0 <= _T <= 1.4, "T_sample out of base window"
assert abs(_B) < 0.02, "magnet not at zero"
assert abs(_Vsi) < 0.01, "Si not at 0 V"
for _s in (sr0, sr1):
    _s.time_constant(0.1)
print(f"sr0 sens={sr0.sensitivity()} V, sr1 sens={sr1.sensitivity()} V, tau={sr1.time_constant()} s")

meas_config["sample_temperature:"] = T_sample()
meas_config["Si (V)"] = dc205.voltage()
meas_config["comments"] = "gatemap-coarse: TG fast -0.3->1.0 @20 mV (66), BG slow 2.0->-1.3 @100 mV (34), Si=0, B=0, base T"
s = sweep.AsyncStation(meas_config)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.Y).fp(k_tg.curr).fp(k_bg.curr).fp(T_sample)
s.add_comment("gatemap-coarse")
s.add_comment("megasweep BG slow 2.0->-1.3 V @100mV (34 rows) x TG fast -0.3->1.0 V @20mV (66 pts); "
              "slow_delay 1 s, fast_delay 0.5 s, tau 100 ms; V_si=0, B=0; I_bias 10 nA")
# megasweep row = [time, slow, fast, *followed] -> sr1_X idx 5, sr1_Y idx 6
ar1 = SrAutoRange(sr1, cols=(5, 6), gain=1.0, lo=1e-6, hi=0.5)
s.register_run_after(ar1, args=())
# live monitor: 1D lines vs V_tg (the 2D-mesh plotter path killed its subprocess at point 3 in run 2 — BrokenPipe)
for _p in (sr1.X, sr0.X, sr1.Y, sr0.P, k_tg.curr, k_bg.curr, T_sample):
    s.plot(k_tg.volt, _p)

_vt = spoints(-0.3, 1.0, 66)
_vb = spoints(2.0, -1.3, 34)
print(f"grid: {len(_vb)} rows x {len(_vt)} pts = {len(_vb)*len(_vt)} pts; est {len(_vb)*(len(_vt)*0.68+3)/60:.0f} min")
_t0 = time.time()
res = s.megasweep(k_bg.volt, _vb, k_tg.volt, _vt, slow_delay=1.0, fast_delay=0.5)
_dt = time.time() - _t0
print(f"run {res.id}: {_dt/60:.1f} min, {_dt/(len(_vb)*len(_vt)):.3f} s/pt incl. turnaround; sr1 autorange log: {ar1.log[-10:]} ({len(ar1.log)} steps)")
print(f"end state: V_tg={k_tg.volt():.4f} V, V_bg={k_bg.volt():.4f} V, T_sample={T_sample():.3f} K, sr1 sens={sr1.sensitivity()} V")
