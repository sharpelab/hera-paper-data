# === Step 4: D=0 Landau fan, electron side — B slow (126 rows, 1.33->8 T uniform 1/B),
# === n fast (51 cols, +2.0 -> +6.3 e12) ===
from sharpelab_nb.gates import calc_gate_voltages
from hera.analysis import field_invB

_T = T_sample(); _B = magnet.field()
print(f"precheck: T={_T:.3f} K (<2), B={_B:+.3f} T (expect ~0.25), Vsi={dc205.voltage():+.3f} (0), "
      f"Vtg={k_tg.volt():+.3f}, Vbg={k_bg.volt():+.3f} (parked 0)")
assert _T < 2.0 and abs(_B) < 0.6 and abs(dc205.voltage()) < 1e-3

C_TG, C_BG, N_OFF = 1.7027e-3, 2.1751e-3, -0.0365   # run-4 calibration
ns = np.linspace(2.0, 6.3, 51)                      # 1e12 cm^-2, electron side
Vtgs, Vbgs = calc_gate_voltages(ns, np.zeros_like(ns), C_TG, C_BG, n_offset=N_OFF)
assert np.abs(Vtgs).max() <= 3.0 and np.abs(Vbgs).max() <= 4.5
print(f"n-line: Vtg {Vtgs[0]:+.3f}..{Vtgs[-1]:+.3f}, Vbg {Vbgs[0]:+.3f}..{Vbgs[-1]:+.3f}")

B_vec = field_invB(1.33, 8.0, 126)                  # d(1/B) = 5.0e-3; B_lo = computed onset (run 6)

# worst-corner sensitivity sizing (n=2e12 @ 8 T, QH regime)
sr1.sensitivity(1e-4); sr2.sensitivity(1e-4); sr3.sensitivity(2e-4); sr0.sensitivity(5e-2)

s = sweep.AsyncStation(meas_config)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = 0, n = +2.0 to +6.3 e12 (51 cols), B = 1.33 to 8 T uniform 1/B '
              f'(126 rows, d(1/B)=5.0e-3, B_lo = run-6 computed onset); I_bias=20 nA, '
              f'sens sr1/sr2 1e-4 sr3 2e-4, fast_delay=1.2 (4 tau), T={_T:.2f} K, cal run 4')

s.ramp(k_tg.volt, Vtgs[0])
s.ramp(k_bg.volt, Vbgs[0])
s.ramp(magnet.field, B_vec[0])       # blocking ramp = the settle (VTI variant step 4)

s.fp(T_sample)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
s.plot('time', k_tg.curr)
s.plot('time', k_bg.curr)
for lia in (sr0, sr1, sr2, sr3):
    s.fp(lia.X).fp(lia.P)
    s.plot(k_tg.volt, lia.X)

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=3, fast_delay=1.2)
finally:
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)
print("fan done; magnet at 8 T, gates parked at 0")
