# --- Landau fan hole side: B 1.6->8 T uniform-1/B x101, n -1.5->-6e12 x87, D=0 --- slug: landau-fan-vti
import scipy.constants as cst

B0, Ts = magnet.field(), T_sample()
print(f"pre: B={B0:+.3f} T (expect ~1, SC2 endpoint) | T={Ts:.3f} K")
assert 0.9 < B0 < 1.7 and 1.0 < Ts < 1.5, "precondition mismatch"
assert abs(k_si()) < 0.01 and abs(k_tg.volt()) < 0.01 and abs(k_bg.volt()) < 0.01
assert abs(sr1.amplitude() - 2.0) < 1e-2, "drive not at 2 V (20 nA)"

# split sensitivities (see markdown): sr1 no-clip, sr2 fine-digitization, sr3 Hall range
sr1.sensitivity(2e-4); sr2.sensitivity(5e-5); sr3.sensitivity(2e-4)
print(f"sens: sr1 {sr1.sensitivity()}, sr2 {sr2.sensitivity()}, sr3 {sr3.sensitivity()}, sr0 {sr0.sensitivity()}")

# fast axis: D=0 paired n-line, run-4 calibration
C_TG = cst.epsilon_0 * 3.0 / 15.6e-9
RATIO, N_OFF = 1.2839, -2.407e14
ns = np.linspace(-1.5e16, -6.0e16, 87)              # m^-2
Vbgs = (ns - N_OFF) * cst.e / (2 * C_TG * RATIO)
Vtgs = RATIO * Vbgs
Vtgs, Vbgs = sanitize_tg_bg(Vtgs, Vbgs, tg_lims, bg_lims)
print(f"n-line: {len(Vtgs)} pts, Vtg [{Vtgs.min():+.3f},{Vtgs.max():+.3f}], Vbg [{Vbgs.min():+.3f},{Vbgs.max():+.3f}]")

# slow axis: uniform in 1/B, 1.6 -> 8 T ascending
B_vec = field_invB(1.6, 8.0, 101)
print(f"B rows: {len(B_vec)}, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T; dB {B_vec[1]-B_vec[0]:.4f} .. {B_vec[-1]-B_vec[-2]:.4f} T")

settle_saved = magnet.settle_s
magnet.settle_s = 1.2

mc = dict(meas_config)
mc["comments"] = ("Landau fan hole side: n -1.5->-6e12 (87 pts, D=0, run-4 cal), "
                  "B 1.6->8 T uniform-1/B (101 rows, d(1/B)=5.0e-3), 20nA@13Hz, "
                  "sens sr1 2e-4/sr2 5e-5/sr3 2e-4, fast_delay 1.8 (6tau), T~1.17K")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('D = 0, n = -1.5 to -6.0e12 cm^-2, B = 1.6 to 8 T; per-column-FFT fan; ends 8 T for ride-down grid-change cut')
s.fp(T_sample)
s.fp(k_tg.curr).fp(k_bg.curr)
for lia in (sr0, sr1, sr2, sr3):
    s.fp(lia.X).fp(lia.P)
    s.plot(k_tg.volt, lia.X)
s.plot(k_tg.volt, k_tg.curr)
s.plot('time', k_bg.curr)
s.plot('time', T_sample)

try:
    s.ramp(k_tg.volt, Vtgs[0]); s.ramp(k_bg.volt, Vbgs[0])
    interruptible_sleep(10)
    s.multimegasweep([magnet.field], [B_vec],
                     [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=1, fast_delay=1.8)
finally:
    magnet.settle_s = settle_saved
    k_tg.volt(0); k_bg.volt(0)
    print(f"end: B={magnet.field():+.3f} T, gates parked, settle_s={magnet.settle_s}")
