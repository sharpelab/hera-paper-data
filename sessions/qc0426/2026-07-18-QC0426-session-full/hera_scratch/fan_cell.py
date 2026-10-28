# === Step 4 — D=0 Landau fan, electron side: B 8 -> 1.2 T (131 rows, 1/B-uniform) x n 2.0 -> 6.2e12 (81 pts) ===
# recipes: landau-fan + landau-fan-vti; per-column SdH-FFT fan; acquisition inherited from spot checks

# --- preconditions ---
_Ts, _B = T_sample(), magnet.field()
print(f"preconditions: T_sample={_Ts:.3f} K (expect 1.0-1.5), B={_B:+.4f} T (expect ~8 after run 8)")
assert 1.0 <= _Ts <= 1.5, f"not at base T: {_Ts:.3f} K"
assert _B > 7.5, f"field not at 8 T: {_B:+.4f} T (fan descends from 8)"

# --- sensitivities: fixed whole-fan, worst-corner (n=2e12 x 8 T) sized ---
sr1.sensitivity(1e-4)
sr2.sensitivity(5e-5)
sr3.sensitivity(1e-4)
sr0.sensitivity(5e-2)
# drive stays 2 V / 20 nA

# --- axes ---
ns_fan = np.linspace(2.0, 6.2, 81)          # 1e12 cm^-2 labels (calibrated scale 1.106x geometry)
Vtgs, Vbgs = d0_point(ns_fan)                # calibrated D=0 line
assert Vtgs.max() < 3.0 and abs(Vbgs).max() < 4.5, "fan line exits validators"
B_vec = field_invB(8.0, 1.2, 131)            # descending, uniform 1/B, d(1/B)=5.4e-3
print(f"fast axis: n {ns_fan[0]}-{ns_fan[-1]}e12, Vtg [{Vtgs.min():+.3f},{Vtgs.max():+.3f}], "
      f"Vbg [{Vbgs.min():+.3f},{Vbgs.max():+.3f}]; slow: B {B_vec[0]:.2f}->{B_vec[-1]:.2f} T x{len(B_vec)}")

meas_config["comments"] = ("landau-fan-vti: D=0, n=2.0->6.2e12 (labels, cal 1.106x) x 81, "
                           "B 8->1.2 T x 131 uniform-1/B (d(1/B)=5.4e-3, spot-check-inherited), "
                           "fast_delay=1.8 (6tau), I_bias=20 nA, sens sr1=1e-4 sr2=5e-5 sr3=1e-4")
s = sweep.AsyncStation(meas_config)
s.add_comment('landau-fan-vti')
s.add_comment('D = 0, n = 2.0 to 6.2e12 cm^-2 (81 pts), B = 8 to 1.2 T (131 rows, 1/B-uniform), electron side; '
              'per-column SdH-FFT fan; onset 1.2 T from run 5; worst corner sized from run-4 R(n) x 16 MR')

# position fast axis at its start (gates are at the hole point after run 8)
s.ramp(k_tg.volt, Vtgs[0])
s.ramp(k_bg.volt, Vbgs[0])
interruptible_sleep(10)

s.fp(T_sample).fp(T_vaporizer)
s.fp(magnet.field)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
for _l in (sr0, sr1, sr2, sr3):
    s.fp(_l.X).fp(_l.P)
s.plot(k_tg.volt, k_tg.curr)
s.plot(k_tg.volt, k_bg.curr)
for _l in (sr0, sr1, sr2, sr3):
    s.plot(k_tg.volt, _l.X)
    s.plot(k_tg.volt, _l.P)
s.plot('time', T_sample)
s.plot('time', T_vaporizer)

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=1, fast_delay=1.8)
print("fan complete; field at 1.2 T, gates at the n=6.2e12 D=0 point")
