# --- Gate C leg 3/4: k_bg 0 -> +4.5 V (card limit) --- slug: gate-current-sanity-check
# preconditions (state this cell assumes but does not set)
B, Ts = magnet.field(), T_sample()
print(f"pre: B={B:+.4f} T (expect ~0) | T={Ts:.3f} K (expect 1.0-1.5)")
assert abs(B) < 0.02 and 1.0 < Ts < 1.5, "precondition mismatch — stop"
print(f"pre: TG={k_tg.volt():+.4f} BG={k_bg.volt():+.4f} Si={k_si():+.4f} V (expect all ~0)")
assert abs(k_tg.volt()) < 0.01 and abs(k_bg.volt()) < 0.01 and abs(k_si()) < 0.01

# drive per device card: 0.5 V / 100 MOhm = 5 nA at ~13 Hz (sr1 = drive lock-in)
if abs(sr1.amplitude() - 0.5) > 1e-3:
    sr1.amplitude(0.5)
if not (11 < sr1.frequency() < 15):
    sr1.frequency(13)
print(f"drive: sr1 amp {sr1.amplitude()} V, freq {sr1.frequency():.3f} Hz")

k_tg.nplci(10); k_bg.nplci(10)  # pA-floor gate-current readback; reset cell restores 1

mc = dict(meas_config)
mc["comments"] = "gate C liveness leg 3/4: k_bg 0 -> +4.5 V, other gates 0, B=0, T~1.17 K"
s = sweep.AsyncStation(mc)
s.add_comment('gate-current-sanity-check')
s.add_comment('gate: k_bg; leg: 0 -> +4.5 V (card limit); drive 5 nA @ 13 Hz')
s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
s.fp(T_sample)
s.fp(k_tg.volt).fp(k_tg.curr).fp(k_bg.volt).fp(k_bg.curr)
s.plot(k_bg.volt, k_tg.curr)
s.plot(k_bg.volt, k_bg.curr)
for lia in (sr0, sr1, sr2, sr3):
    s.fp(lia.X).fp(lia.P)
    s.plot(k_bg.volt, lia.X)
try:
    s.sweep(k_bg.volt, np.linspace(0, BG_MAX, 251), delay=1)
finally:
    s.ramp(k_bg.volt, 0)
