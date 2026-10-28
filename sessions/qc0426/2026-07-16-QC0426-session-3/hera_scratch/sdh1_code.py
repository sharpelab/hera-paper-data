# --- SdH spot check 1/2: hole side n=-6e12, D=0, B 1->8 T uniform-B --- slug: sdh-spot-check
B0, Ts = magnet.field(), T_sample()
print(f"pre: B={B0:+.4f} T (expect ~0) | T={Ts:.3f} K")
assert abs(B0) < 0.05 and 1.0 < Ts < 1.5, "precondition mismatch"
assert abs(k_si()) < 0.01, "Si gate not at 0"

# drive: card high-|n| standard 2 V -> 20 nA; sens with MR headroom (see markdown)
sr1.amplitude(2.0)
sr1.sensitivity(5e-5); sr2.sensitivity(5e-5); sr3.sensitivity(5e-5)
print(f"drive {sr1.amplitude()} V @ {sr1.frequency():.2f} Hz -> I_bias 20 nA; "
      f"sens sr1 {sr1.sensitivity()}, sr2 {sr2.sensitivity()}, sr3 {sr3.sensitivity()}, sr0 {sr0.sensitivity()}")

VTG, VBG = -2.8115, -2.1898   # n=-6e12, D=0 (run-4 calibration)
B_vec = np.linspace(1.0, 8.0, 1303)   # dB = 5.38 mT = (1/3F_L)*B_lo^2, F_L=62 T

settle_saved = magnet.settle_s
magnet.settle_s = 1.2   # = 4*tau dwell per point (lock-in tracks through the ramp)
print(f"magnet.settle_s: {settle_saved} -> {magnet.settle_s}")

mc = dict(meas_config)
mc["comments"] = ("SdH spot check hole side: n=-6e12 cm^-2, D=0 (Vtg -2.8115, Vbg -2.1898), "
                  "B 1->8 T, 1303 pts dB=5.38mT, 20nA@13Hz, T~1.17K")
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment('hole side; F_L=62.0 T; d(1/B)=5.38e-3/T (1/3 Nyquist); ends at 8 T for SC2 ride-down')
s.ramp(k_tg.volt, VTG); s.ramp(k_bg.volt, VBG)
interruptible_sleep(10)
s.fp(T_sample)
s.fp(k_tg.curr).fp(k_bg.curr)
for lia in (sr0, sr1, sr2, sr3):
    s.fp(lia.X).fp(lia.P)
    s.plot(magnet.field, lia.X)
s.plot(magnet.field, k_tg.curr)
s.plot('time', T_sample)

try:
    s.ramp(magnet.field, 1.0)   # blocking position ramp, ~7 min
    s.sweep(magnet.field, B_vec, delay=0)   # dwell = settle_s per point
finally:
    magnet.settle_s = settle_saved
    k_tg.volt(0); k_bg.volt(0)
    print(f"end: B={magnet.field():+.3f} T (left for SC2 ride-down), gates parked, settle_s={magnet.settle_s}")
