# === Step 3b — SdH spot check, HOLE side: n = -6e12 cm^-2, D = 0, B 8 -> 0.5 T (return traverse) ===
# recipe: measurements/sdh-spot-check.md; run AFTER the electron-side read.

# --- preconditions ---
_Ts, _B, _Vsi = T_sample(), magnet.field(), dc205.voltage()
print(f"preconditions: T_sample={_Ts:.3f} K (expect 1.0-1.5), B={_B:+.4f} T (expect ~8, sweeping down), "
      f"V_si={_Vsi:+.3f} V (expect 0)")
assert 1.0 <= _Ts <= 1.5, f"not at base T: {_Ts:.3f} K"
assert _B > 7.5, f"field not at the top of the window: {_B:+.4f} T (this cell sweeps down)"
assert abs(_Vsi) <= 0.05, f"Si gate not parked: {_Vsi:+.3f} V"

# sensitivities unchanged from 3a (same |n|, symmetric R); drive stays 20 nA
B_vec_dn = np.concatenate([np.arange(0.5, 1.0, 0.002),
                           np.arange(1.0, 8.0 + 1e-9, 0.0054)])[::-1]
vtg_pt, vbg_pt = d0_point(-6.0)
print(f"target: (Vtg, Vbg) = ({vtg_pt:+.3f}, {vbg_pt:+.3f}); {len(B_vec_dn)} field points")

meas_config["comments"] = (f"sdh-spot-check: hole n=-6e12 cm^-2 D=0 (Vtg={vtg_pt:+.3f}, Vbg={vbg_pt:+.3f}), "
                           "B 8->0.5 T uniform-B (5.4 mT to 1 T, 2.0 mT below), I_bias=20 nA, F_L=62 T")
s = sweep.AsyncStation(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment('hole side; descending traverse (never re-traverse); grid/dwell as electron cell; '
              'cal: run-4 CNP calibration')

s.ramp(k_tg.volt, vtg_pt)   # gate move at 8 T along validated ranges
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
s.plot('time', T_vaporizer)

s.sweep(magnet.field, B_vec_dn, delay=0)
print("hole spot check done; field holds at 0.5 T, gates at the hole point")
