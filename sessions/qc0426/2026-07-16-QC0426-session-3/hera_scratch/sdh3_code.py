# --- ride-down SdH: electron n=+3.0e12, D=0, B 8->1.3 T --- slug: sdh-spot-check
import scipy.constants as cst
B0, Ts = magnet.field(), T_sample()
print(f"pre: B={B0:+.3f} T (expect ~8, fan endpoint) | T={Ts:.3f} K")
assert 7.9 < B0 < 8.05 and 1.0 < Ts < 1.5
assert abs(k_si()) < 0.01 and abs(k_tg.volt()) < 0.01 and abs(k_bg.volt()) < 0.01
assert abs(sr1.amplitude() - 2.0) < 1e-2
print(f"sens: sr1 {sr1.sensitivity()}, sr2 {sr2.sensitivity()}, sr3 {sr3.sensitivity()}")

C_TG = cst.epsilon_0*3.0/15.6e-9; RATIO, N_OFF = 1.2839, -2.407e14
n_t = 3.0e16 - N_OFF
VBG = n_t*cst.e/(2*C_TG*RATIO); VTG = RATIO*VBG
print(f"gates: VTG={VTG:+.4f}, VBG={VBG:+.4f} (n=+3.0e12, D=0)")
B_vec = np.linspace(8.0, 1.3, 369)

settle_saved = magnet.settle_s
magnet.settle_s = 1.2
mc = dict(meas_config)
mc["comments"] = ("ride-down SdH spot check: n=+3.0e12, D=0, B 8->1.3 T, 369 pts dB=18.2mT, "
                  "20nA@13Hz; model-overlay point (electron, inside 3.5e12 clamp)")
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment('electron n=+3.0e12; F_L=31.0 T nominal; fan ride-down 8->1.3 T')
s.ramp(k_tg.volt, VTG); s.ramp(k_bg.volt, VBG)
interruptible_sleep(10)
s.fp(T_sample)
s.fp(k_tg.curr).fp(k_bg.curr)
for lia in (sr0, sr1, sr2, sr3):
    s.fp(lia.X).fp(lia.P)
    s.plot(magnet.field, lia.X)
s.plot(magnet.field, k_tg.curr)
try:
    s.sweep(magnet.field, B_vec, delay=0)
finally:
    magnet.settle_s = settle_saved
    k_tg.volt(0); k_bg.volt(0)
    print(f"end: B={magnet.field():+.3f} T, gates parked, settle_s={magnet.settle_s}")
