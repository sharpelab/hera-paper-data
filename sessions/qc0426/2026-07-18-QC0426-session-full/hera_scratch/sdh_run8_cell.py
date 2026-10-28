# === Step 3 redo, run 8 — hole main record: n = -6e12, D = 0, B 0.5 -> 8 T ===
_Ts, _B = T_sample(), magnet.field()
print(f"preconditions: T_sample={_Ts:.3f} K, B={_B:+.4f} T (expect ~0.5), "
      f"gates ({k_tg.volt():+.3f}, {k_bg.volt():+.3f}) (expect hole point -2.797/-2.176)")
assert 1.0 <= _Ts <= 1.5, f"not at base T: {_Ts:.3f} K"
assert 0.4 < _B < 0.7, f"field not at 0.5 T: {_B:+.4f}"
assert abs(k_tg.volt() + 2.7972) < 0.01 and abs(k_bg.volt() + 2.1765) < 0.01, "gates not at the hole point"

sr1.sensitivity(1e-5)   # ceiling 500 Ohm (as run 6)
sr2.sensitivity(5e-6)   # ceiling 250 Ohm

B_up = np.arange(1.0, 8.0 + 1e-9, 0.0054)
meas_config["comments"] = ("sdh-spot-check: hole n=-6e12 D=0 main record, B 1->8 T uniform-B 5.4 mT "
                           "(onset segment = run 7), sens sr1=1e-5 sr2=5e-6, I_bias=20 nA")
s = sweep.AsyncStation(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment('hole side main record; bare ramp 0.5->1.0 T then points; ends at 8 T (fan-ready)')

s.ramp(magnet.field, B_up[0])

xp = magnet.field
s.fp(T_sample).fp(T_vaporizer)
s.fp(magnet.field)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
for _l in (sr0, sr1, sr2, sr3):
    s.fp(_l.X).fp(_l.P)
s.plot(xp, k_tg.curr)
s.plot(xp, k_bg.curr)
for _l in (sr0, sr1, sr2, sr3):
    s.plot(xp, _l.X)
    s.plot(xp, _l.P)
s.plot('time', T_sample)

s.sweep(magnet.field, B_up, delay=0)
print("run 8 done; field at 8 T, gates at hole point")
