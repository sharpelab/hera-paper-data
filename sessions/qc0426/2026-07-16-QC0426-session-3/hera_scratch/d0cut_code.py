# --- D=0 line cut: n -6e12 -> +6e12 (241 pts), B=0 --- slug: cnp-and-dline-calibration
import scipy.constants as cst

# preconditions
B, Ts = magnet.field(), T_sample()
print(f"pre: B={B:+.4f} T (expect ~0) | T={Ts:.3f} K")
assert abs(B) < 0.02 and 1.0 < Ts < 1.5
assert abs(k_si()) < 0.01, "Si gate not at 0"
print(f"drive: sr1 amp {sr1.amplitude()} V @ {sr1.frequency():.2f} Hz; sens sr1 {sr1.sensitivity()}, sr2 {sr2.sensitivity()}")

# run-4 calibration (device card contract): ratio data-calibrated, scale geometry prior
C_TG = cst.epsilon_0 * 3.0 / 15.6e-9
RATIO = 1.2839
N_OFFSET = -2.407e14  # m^-2
ns = np.linspace(-6e16, 6e16, 241)          # m^-2
Vbgs = (ns - N_OFFSET) * cst.e / (2 * C_TG * RATIO)
Vtgs = RATIO * Vbgs
Vtgs, Vbgs = sanitize_tg_bg(Vtgs, Vbgs, tg_lims, bg_lims)
print(f"line: {len(Vtgs)} pts, V_tg [{Vtgs.min():+.3f},{Vtgs.max():+.3f}], V_bg [{Vbgs.min():+.3f},{Vbgs.max():+.3f}]")

mc = dict(meas_config)
mc["comments"] = "D=0 designed-line cut, n -6e12->+6e12 (241 pts), B=0, T~1.17K; run-4 calibration confirmation"
s = sweep.AsyncStation(mc)
s.add_comment('cnp-and-dline-calibration')
s.add_comment('D=0 line cut; c_bg/c_tg=1.2839, n_offset=-2.407e14 m^-2 (run 4)')
s.ramp(k_tg.volt, Vtgs[0]); s.ramp(k_bg.volt, Vbgs[0])
interruptible_sleep(10)
s.fp(T_sample)
s.fp(k_tg.curr).fp(k_bg.curr)
for lia in (sr0, sr1, sr2, sr3):
    s.fp(lia.X).fp(lia.P)
    s.plot(k_tg.volt, lia.X)
s.plot(k_tg.volt, k_tg.curr)
s.plot('time', k_bg.curr)
try:
    s.multisweep([k_tg.volt, k_bg.volt], [Vtgs, Vbgs], delay=1.2)
finally:
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)
