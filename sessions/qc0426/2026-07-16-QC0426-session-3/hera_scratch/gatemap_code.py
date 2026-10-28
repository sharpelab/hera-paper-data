# --- 0 T coarse-BG gate map: TG fast [-3,+3]x151, BG slow [-2.4,+2.4]x25 --- slug: gatemap
# preconditions (assumed, not set): B~0, base T, gates parked, NPLC reset to 1
B, Ts = magnet.field(), T_sample()
print(f"pre: B={B:+.4f} T (expect ~0) | T={Ts:.3f} K (expect 1.0-1.5)")
assert abs(B) < 0.02 and 1.0 < Ts < 1.5, "precondition mismatch — stop"
print(f"pre: TG={k_tg.volt():+.4f} BG={k_bg.volt():+.4f} Si={k_si():+.4f} V (expect ~0)")
assert abs(k_si()) < 0.01, "Si gate not at 0"
npl_tg, npl_bg = k_tg.nplci(), k_bg.nplci()
print(f"pre: nplci TG={npl_tg} BG={npl_bg} (expect 1 — reset cell ran)")
assert npl_tg == 1 and npl_bg == 1, "nplci not reset — run the gate C reset cell first"
print(f"drive: sr1 amp {sr1.amplitude()} V, freq {sr1.frequency():.3f} Hz (expect 0.5 V / ~13 Hz)")
assert abs(sr1.amplitude() - 0.5) < 1e-3

# sensitivity for kΩ-scale ridge at finite D (see markdown): 40 kΩ ceiling at 5 nA
sr1.sensitivity(2e-4)
sr2.sensitivity(2e-4)
print(f"sens: sr1 {sr1.sensitivity()}, sr2 {sr2.sensitivity()}, sr3 {sr3.sensitivity()}, sr0 {sr0.sensitivity()}")

mc = dict(meas_config)
mc["comments"] = ("0T coarse-BG gatemap for CNP-line calibration: TG fast -3->+3 (151), "
                  "BG slow -2.4->+2.4 (25), Si=0, B=0, T~1.17K, 5nA@13Hz, sr1/sr2 sens 2e-4")
s = sweep.AsyncStation(mc)
s.add_comment('gatemap')
s.add_comment('coarse-BG CNP-calibration map; feeds cnp-and-dline-calibration')
s.ramp(k_tg.volt, -3.0)
s.ramp(k_bg.volt, -2.4)
interruptible_sleep(10)

s.fp(T_sample)
s.fp(k_tg.volt).fp(k_tg.curr).fp(k_bg.volt).fp(k_bg.curr)
for lia in (sr0, sr1, sr2, sr3):
    s.fp(lia.X).fp(lia.P)
    s.plot(k_tg.volt, lia.X)
s.plot(k_tg.volt, k_tg.curr)
s.plot('time', k_bg.curr)
s.plot('time', T_sample)

try:
    # megasweep(slow, slow_v, fast, fast_v) — BG slow (25 rows), TG fast (151 pts)
    s.megasweep(k_bg.volt, spoints(-2.4, 2.4, 25),
                k_tg.volt, spoints(-3.0, 3.0, 151),
                slow_delay=3, fast_delay=1.2)
finally:
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)
