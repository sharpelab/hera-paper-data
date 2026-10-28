# === LK ladder v2 — CONDITIONAL extension rung 50 K (X_ML ~ 3.7); run only on HERA's re-fit decision ===
_Ts = T_sample()
print(f"preconditions: T={_Ts:.2f} K (expect ~41, still hot), ranges {heater.sample_range()}/{heater.vaporizer_range()} (expect on)")
assert _Ts > 35.0, f"not holding hot ({_Ts:.1f} K) — extend-while-hot window missed; do not re-heat, run shutdown"
assert heater.sample_range() > 0, "heaters not on"

tv_start = T_vaporizer()
heater.set_both(50.0, ratio=0.95)
T_acc = wait_hover(50.0, tv_start)          # helper from the ladder cell (same kernel)
print(f"rung 50 K accepted at T={T_acc:.3f} K")

_Bnow = magnet.field()
vec = np.arange(2.8, 6.0 + 1e-9, 0.036)
vec = vec if abs(_Bnow - 2.8) < abs(_Bnow - 6.0) else vec[::-1]
meas_config["comments"] = ("temperature-dependence-vti Flavor B (LK v2 extension): rung 50K, n=6.0e12 D=0, "
                           f"B {vec[0]:.1f}->{vec[-1]:.1f} T x{len(vec)}, I_bias=20 nA")
s = sweep.AsyncStation(meas_config)
s.add_comment('temperature-dependence-vti')
s.add_comment('LK ladder v2 extension rung 50K (X_ML~3.7), extend-while-hot')
s.fp(T_sample).fp(T_vaporizer)
s.fp(magnet.field)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
for _l in (sr0, sr1, sr2, sr3):
    s.fp(_l.X).fp(_l.P)
s.plot(magnet.field, sr1.X)
s.plot(magnet.field, sr2.X)
s.plot('time', T_sample)
s.sweep(magnet.field, vec, delay=0)
print("extension rung done; run shutdown cell next")
