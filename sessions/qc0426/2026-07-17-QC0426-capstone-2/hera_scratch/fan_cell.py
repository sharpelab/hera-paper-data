# === Landau fan (landau-fan-vti): hole side, D = 0, per-column SdH-FFT design ===
# n: -0.5 -> -3.5e12 cm^-2 (101 columns; clamp 3.5e12 = model overlay validity)
# B: 0.77 -> 8 T uniform in 1/B (field_invB), 141 rows
#   D(1/B) = 8.33e-3 1/T = 1/(3*40 T) — 1/3-Nyquist on the lambda-scaled
#   supra tone at n_max (F_L*1.07 at 3.5e12 ~ 38.7 T). Harmonics >60 T alias
#   to >43 T — outside the 0-40 T claim band (noted).
# n-axis: dn = 0.03e12 >= 2 pts/ray for B >= 0.86 T (ray Nyquist).
# delta_F = 1/(1/0.77 - 1/8) = 0.85 T — separates 27 vs 33 (>> 2*delta_F).

# -- preconditions (assumed, not set)
B = magnet.field()
Ts = T_sample()
print(f"precheck: B={B:+.3f} T (expect ~0.7), T={Ts:.3f} K")
assert abs(B - 0.7) < 0.15, f"STOP: field not at ~0.7 T: {B} T"
assert Ts < 1.5, f"STOP: not at base T: {Ts} K"

# -- sensitivities sized at the global worst corner (n=-0.5e12 x 8 T):
#    sr1 R(worst) ~ 16-20 kOhm -> 5e-4 (25 kOhm ceiling @ 20 nA)
#    sr2 ~ 2.5x lower R -> 2e-4 (10 kOhm); sr3 |Rxy|max = 8/(0.5e16 e) = 10 kOhm -> 5e-4
sr1.sensitivity(5e-4)
sr2.sensitivity(2e-4)
sr3.sensitivity(5e-4)
print(f"sens: sr1 {sr1.sensitivity()}, sr2 {sr2.sensitivity()}, sr3 {sr3.sensitivity()}; "
      f"drive {sr1.amplitude()} V (20 nA)")

# -- axes
ns = np.linspace(-0.5, -3.5, 101)          # e12 cm^-2
Vtgs, Vbgs = gates_for(ns, 0.0)
assert np.all(np.abs(Vtgs) <= 3.0) and np.all(np.abs(Vbgs) <= 4.5), "n-line exits validators"
print(f"n-line: Vtg {Vtgs[0]:+.3f}..{Vtgs[-1]:+.3f}, Vbg {Vbgs[0]:+.3f}..{Vbgs[-1]:+.3f}")

B_vec = field_invB(0.77, 8.0, 141)         # uniform in 1/B, ascending
print(f"B rows: {len(B_vec)} from {B_vec[0]:.3f} to {B_vec[-1]:.3f} T")

meas_config["comments"] = (
    "landau-fan-vti: hole side, D=0, n -0.5..-3.5e12 (101 cols) x B 0.77..8 T "
    "(141 rows, uniform 1/B, D(1/B)=8.33e-3); 20 nA @ 13 Hz; sens sr1 5e-4 "
    "sr2 2e-4 sr3 5e-4; settle_s=1.2; inherits run-5/6 spot-check design"
)
s = sweep.AsyncStation(meas_config)
s.add_comment('landau-fan-vti')
s.add_comment('D = 0 V/nm, n = -0.5 to -3.5 e12 cm^-2, B = 0.77 to 8 T')

s.ramp(k_2400_tg.volt, Vtgs[0])
s.ramp(k_2400_bg.volt, Vbgs[0])
interruptible_sleep(10)

s.fp(magnet.field)
s.fp(k_2400_tg.volt).fp(k_2400_tg.curr)
s.fp(k_2400_bg.volt).fp(k_2400_bg.curr)
s.fp(T_sample)
s.plot(k_2400_tg.volt, k_2400_tg.curr)
s.plot(k_2400_tg.volt, k_2400_bg.curr)
s.plot(k_2400_tg.volt, T_sample)
for lia in (sr0, sr1, sr2, sr3):
    s.fp(lia.X).fp(lia.P)
    s.plot(k_2400_tg.volt, lia.X)

try:
    s.multimegasweep([magnet.field], [B_vec],
                     [k_2400_tg.volt, k_2400_bg.volt], [Vtgs, Vbgs],
                     slow_delay=1, fast_delay=1)
finally:
    s.ramp(k_2400_tg.volt, 0)
    s.ramp(k_2400_bg.volt, 0)

print(f"fan complete; B at {magnet.field():+.3f} T; gates parked at 0")
