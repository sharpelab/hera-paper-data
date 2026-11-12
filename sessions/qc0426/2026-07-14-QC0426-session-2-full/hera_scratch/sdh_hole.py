# === SdH spot check 1/2: HOLE side, n = -6e12 cm^-2, D = 0, B 0.25 -> 8 T (uniform 1/B) ===
from sharpelab_nb.gates import calc_gate_voltages
from hera.analysis import field_invB

_T = T_sample(); _B = magnet.field()
print(f"precheck: T={_T:.3f} K (<2), B={_B:+.3f} T (expect ~0), Vsi={dc205.voltage():+.3f} (0)")
assert _T < 2.0 and abs(_B) < 0.3 and abs(dc205.voltage()) < 1e-3

# session calibration (run 4): ratio data-calibrated, scale geometry-anchored
C_TG, C_BG, N_OFF = 1.7027e-3, 2.1751e-3, -0.0365   # F/m^2, F/m^2, 1e12 cm^-2
n_target, D_target = -6.0, 0.0
vtg_t, vbg_t = calc_gate_voltages(n_target, D_target, C_TG, C_BG, n_offset=N_OFF)
print(f"target ({n_target:+.1f}e12, D=0) -> Vtg {vtg_t:+.3f} V, Vbg {vbg_t:+.3f} V (validators fence)")

# high-|n| metallic excitation; sens sized for 8 T worst corner (see markdown)
sr1.amplitude(2.0)          # I_bias = 20 nA through 100 MOhm
sr1.sensitivity(2e-5); sr2.sensitivity(2e-5); sr3.sensitivity(5e-5); sr0.sensitivity(5e-2)

B_vec = field_invB(0.25, 8.0, 721)   # d(1/B) = 5.4e-3 = 1/(3*F_L(6e12))

s = sweep.AsyncStation(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment(f'hole side: n = {n_target}e12 cm^-2, D = 0 -> (Vtg, Vbg) = ({vtg_t:.3f}, {vbg_t:.3f}); '
              f'B 0.25->8 T uniform 1/B, N=721, d(1/B)=5.4e-3 (Nyquist x3 on F_L=62 T); '
              f'I_bias=20 nA, sens sr1/sr2 2e-5 sr3 5e-5, T={_T:.2f} K, cal run 4')

s.ramp(k_tg.volt, vtg_t)
s.ramp(k_bg.volt, vbg_t)
s.ramp(magnet.field, B_vec[0])       # blocking ramp; the set call is the settle

s.fp(T_sample)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
s.plot('time', k_tg.curr)
s.plot('time', k_bg.curr)
for lia in (sr0, sr1, sr2, sr3):
    s.fp(lia.X).fp(lia.P)
    s.plot(magnet.field, lia.X)

s.sweep(magnet.field, B_vec, delay=1.2)
print("hole-side spot check done; magnet at 8 T, gates still at hole point")
