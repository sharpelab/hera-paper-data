# === SdH spot check 2/2: ELECTRON side, n = +6e12 cm^-2, D = 0, B 8 -> 0.25 T (uniform 1/B) ===
from sharpelab_nb.gates import calc_gate_voltages
from hera.analysis import field_invB

_T = T_sample(); _B = magnet.field()
print(f"precheck: T={_T:.3f} K (<2), B={_B:+.3f} T (expect ~8), Vsi={dc205.voltage():+.3f} (0)")
assert _T < 2.0 and _B > 7.5 and abs(dc205.voltage()) < 1e-3

C_TG, C_BG, N_OFF = 1.7027e-3, 2.1751e-3, -0.0365
n_target, D_target = +6.0, 0.0
vtg_t, vbg_t = calc_gate_voltages(n_target, D_target, C_TG, C_BG, n_offset=N_OFF)
print(f"target ({n_target:+.1f}e12, D=0) -> Vtg {vtg_t:+.3f} V, Vbg {vbg_t:+.3f} V")

B_vec = field_invB(8.0, 0.25, 721)

s = sweep.AsyncStation(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment(f'electron side: n = +{n_target}e12 cm^-2, D = 0 -> (Vtg, Vbg) = ({vtg_t:.3f}, {vbg_t:.3f}); '
              f'B 8->0.25 T uniform 1/B, N=721, d(1/B)=5.4e-3; I_bias=20 nA, '
              f'sens sr1/sr2 2e-5 sr3 5e-5, T={_T:.2f} K, cal run 4')

s.ramp(k_tg.volt, vtg_t)
s.ramp(k_bg.volt, vbg_t)
interruptible_sleep(10)              # settle after crossing CNP at 8 T

s.fp(T_sample)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
s.plot('time', k_tg.curr)
s.plot('time', k_bg.curr)
for lia in (sr0, sr1, sr2, sr3):
    s.fp(lia.X).fp(lia.P)
    s.plot(magnet.field, lia.X)

s.sweep(magnet.field, B_vec, delay=1.2)
print("electron-side spot check done; magnet at 0.25 T; parking gates at 0")
k_tg.volt(0); k_bg.volt(0)
