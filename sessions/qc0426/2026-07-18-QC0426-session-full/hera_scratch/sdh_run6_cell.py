# === Step 3 redo, run 6 — electron re-acquire: n = +6e12, D = 0, B 8 -> 2 T, unclipped sens ===
_Ts, _B = T_sample(), magnet.field()
print(f"preconditions: T_sample={_Ts:.3f} K (expect 1.0-1.5), B={_B:+.4f} T (expect ~8), "
      f"gates ({k_tg.volt():+.3f}, {k_bg.volt():+.3f}) (expect electron point +2.848/+2.216)")
assert 1.0 <= _Ts <= 1.5, f"not at base T: {_Ts:.3f} K"
assert _B > 7.5, f"field not at 8 T: {_B:+.4f}"
assert abs(k_tg.volt() - 2.8485) < 0.01 and abs(k_bg.volt() - 2.2164) < 0.01, "gates not at the electron point"

sr1.sensitivity(1e-5)   # ceiling 500 Ohm (extrapolated R(8T) ~ 360)
sr2.sensitivity(5e-6)   # ceiling 250 Ohm (extrapolated ~ 180)
# sr3 5e-5, sr0 5e-2 unchanged (unclipped in run 5)

B_dn = np.arange(8.0, 2.0 - 1e-9, -0.0054)
meas_config["comments"] = ("sdh-spot-check: electron n=+6e12 D=0 REDO, B 8->2 T uniform-B 5.4 mT, "
                           "sens sr1=1e-5 sr2=5e-6 (run 5 clipped >2.4 T), I_bias=20 nA")
s = sweep.AsyncStation(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment('electron redo, down-traverse; overlap 2.0-2.4 T with run 5 usable window for stitch/grid-change check')

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
s.plot('time', T_vaporizer)

s.sweep(magnet.field, B_dn, delay=0)
print("run 6 done; field at 2 T, gates at electron point")
