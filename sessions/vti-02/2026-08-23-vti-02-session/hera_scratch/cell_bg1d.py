# HERA — plan step 1: BG sweep at V_tg = 0 (CNP hunt on the back gate)
_T, _B, _Vtg, _Vsi = T_sample(), magnet.field(), k_tg.volt(), dc205.voltage()
print(f"precheck: T_sample={_T:.3f} K (want 1.0-1.4) | B={_B:.4f} T (want |B|<0.02) | "
      f"V_tg={_Vtg:.4f} V (want 0) | V_si={_Vsi:.3f} V (want 0) | V_bg now {k_bg.volt():.4f} V")
assert 1.0 <= _T <= 1.4, "T_sample out of base window"
assert abs(_B) < 0.02, "magnet not at zero"
assert abs(_Vtg) < 1e-3 and abs(_Vsi) < 0.01, "TG/Si not at 0 V"

# ranging: tau 100 ms (run 0 showed interference through 30 ms), delay 0.5 s
for _s in (sr0, sr1):
    _s.time_constant(0.1)
    _s.filter_slope(24)
print(f"sr0 sens={sr0.sensitivity()} V, sr1 sens={sr1.sensitivity()} V (autorange hook active on sr1)")
time.sleep(0.5)

# station — lock-in X stored RAW (gain 1); mc['sr0_gain'] carries the Ithaco gain for analysis/hera-watch
meas_config["sample_temperature:"] = T_sample()
meas_config["Si (V)"] = dc205.voltage()
meas_config["comments"] = "bg-sweep-1d: BG 0->2.0->-1.3->0 V @10 mV, TG=0, Si=0, B=0, base T"
s = sweep.AsyncStation(meas_config)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.Y).fp(k_tg.curr).fp(k_bg.curr).fp(T_sample)
s.add_comment("bg-sweep-1d")
s.add_comment("BG 0->2.0->-1.3->0 V @10mV (661 pts), delay 0.5 s, tau 100 ms; V_tg=0, V_si=0, B=0; I_bias 10 nA")
ar1 = SrAutoRange(sr1, cols=(4, 5), gain=1.0, lo=1e-6, hi=0.5)
s.register_run_after(ar1, args=())
for _p in (sr1.X, sr0.X, sr1.Y, sr0.P, k_tg.curr, k_bg.curr, T_sample):
    s.plot(k_bg.volt, _p)

_vb = np.concatenate([spoints(0.0, 2.0, 201), spoints(2.0, -1.3, 331)[1:], spoints(-1.3, 0.0, 131)[1:]])
print(f"sweep: {len(_vb)} pts, V_bg in [{_vb.min():.2f}, {_vb.max():.2f}] V, ends at {_vb[-1]:.2f} V")
_t0 = time.time()
res = s.sweep(k_bg.volt, _vb, delay=0.5)
_dt = time.time() - _t0
print(f"run {res.id}: {_dt/60:.1f} min, {_dt/len(_vb):.3f} s/pt; sr1 autorange log: {ar1.log}")
print(f"end state: V_tg={k_tg.volt():.4f} V, V_bg={k_bg.volt():.4f} V, T_sample={T_sample():.3f} K, sr1 sens={sr1.sensitivity()} V")
