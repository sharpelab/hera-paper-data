# === Step 3 redo, run 7 — hole onset segment: n = -6e12, D = 0, B 2 -> 0.5 T fine ===
_Ts, _B = T_sample(), magnet.field()
print(f"preconditions: T_sample={_Ts:.3f} K, B={_B:+.4f} T (expect ~2)")
assert 1.0 <= _Ts <= 1.5, f"not at base T: {_Ts:.3f} K"
assert 1.8 < _B < 2.3, f"field not at 2 T: {_B:+.4f}"

vtg_pt, vbg_pt = d0_point(-6.0)
sr1.sensitivity(5e-6)   # ceiling 250 Ohm; hole R(2T) ~ 100 by electron analogy
sr2.sensitivity(2e-6)   # ceiling 100 Ohm

B_dn = np.arange(2.0, 0.5 - 1e-9, -0.002)
meas_config["comments"] = (f"sdh-spot-check: hole n=-6e12 D=0 onset segment (Vtg={vtg_pt:+.3f}, Vbg={vbg_pt:+.3f}), "
                           "B 2->0.5 T uniform-B 2.0 mT (Nyquist at 0.5 T), sens sr1=5e-6 sr2=2e-6, I_bias=20 nA")
s = sweep.AsyncStation(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment('hole side onset segment; gates moved at 2 T; main record follows as run 8 (0.5->8 T)')

s.ramp(k_tg.volt, vtg_pt)
s.ramp(k_bg.volt, vbg_pt)
interruptible_sleep(10)

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

s.sweep(magnet.field, B_dn, delay=0)
print("run 7 done; field at 0.5 T, gates at hole point")
