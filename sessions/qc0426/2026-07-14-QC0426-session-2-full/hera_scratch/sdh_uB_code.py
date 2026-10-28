# === Spot-check redesign validation: uniform-B, electron n = +6e12, D = 0, 1.33 -> 8 T ===
from sharpelab_nb.gates import calc_gate_voltages

_T = T_sample(); _B = magnet.field()
print(f"precheck: T={_T:.3f} K (<2), B={_B:+.3f} T (expect ~0), Vsi={dc205.voltage():+.3f} (0)")
assert _T < 2.0 and abs(_B) < 0.3 and abs(dc205.voltage()) < 1e-3

C_TG, C_BG, N_OFF = 1.7027e-3, 2.1751e-3, -0.0365
vtg_t, vbg_t = calc_gate_voltages(+6.0, 0.0, C_TG, C_BG, n_offset=N_OFF)
print(f"target (+6.0e12, D=0) -> Vtg {vtg_t:+.3f}, Vbg {vbg_t:+.3f}")

sr1.sensitivity(2e-5); sr2.sensitivity(2e-5); sr3.sensitivity(5e-5); sr0.sensitivity(5e-2)

B_vec = np.linspace(1.33, 8.0, 703)   # uniform B, dB = 9.5 mT = d(1/B)_Nyq * B_lo^2

s = sweep.AsyncStation(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment(f'UNIFORM-B collection variant (head-to-head vs run 6): electron n = +6e12, '
              f'D = 0 -> ({vtg_t:.3f}, {vbg_t:.3f}); B 1.33->8 T linear, N=703, dB=9.5 mT; '
              f'I_bias=20 nA, sens sr1/sr2 2e-5 sr3 5e-5, T={_T:.2f} K, cal run 4')

s.ramp(k_tg.volt, vtg_t)
s.ramp(k_bg.volt, vbg_t)
s.ramp(magnet.field, B_vec[0])

s.fp(T_sample)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
s.plot('time', k_tg.curr)
s.plot('time', k_bg.curr)
for lia in (sr0, sr1, sr2, sr3):
    s.fp(lia.X).fp(lia.P)
    s.plot(magnet.field, lia.X)

s.sweep(magnet.field, B_vec, delay=1.2)
print("uniform-B spot check done; magnet at 8 T, gates at electron point")
