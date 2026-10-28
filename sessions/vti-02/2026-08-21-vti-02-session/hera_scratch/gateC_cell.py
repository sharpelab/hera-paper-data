# === Gate C — gate-current-sanity-check: every gate 0 -> each card limit ===
# Precondition reads (state this cell assumes but does not set): stop on mismatch.
_Ts, _B, _Vsi = T_sample(), magnet.field(), dc205.voltage()
_rs, _rv = heater.sample_range(), heater.vaporizer_range()
print(f"pre: T_sample={_Ts:.3f} K (want 1.05-1.45) | B={_B:+.4f} T (want |B|<0.02) | Si={_Vsi:+.3f} V (want 0) | heater ranges={_rs},{_rv} (want 0,0)")
assert 1.05 <= _Ts <= 1.45, "T_sample out of base band"
assert abs(_B) < 0.02, "magnet not at zero"
assert abs(_Vsi) < 0.01, "Si gate not at 0"
assert _rs == 0 and _rv == 0, "a heater range is on"
# Keithley state, read-first (no writes): mode VOLT, rangev 21, rangei 1 uA, nplci 1, averaging off, 0 V.
# The 2400 reports its 1 uA range as 1.05e-6 (cell [18]); pass that so the 0.1 % compare holds.
assert_keithley_state(k_2400_tg, rangei=1.05e-6)
assert_keithley_state(k_2400_bg, rangei=1.05e-6)
print(f"compliance: tg {k_2400_tg.compliancei()} A, bg {k_2400_bg.compliancei()} A | output: tg {k_2400_tg.output()}, bg {k_2400_bg.output()}")

# Lock-in scale for the liveness read: sr1 was railed at sens 2 uV (X = 2.02 uV at (0,0)).
# 10 nA bias -> 1 mV full scale = 100 kOhm; tau 0.3 -> 0.1 s so a 1 s dwell is 10*tau at 24 dB/oct
# (2f = 27.6 Hz still rejected by ~100 dB at tau = 0.1 s). Recorded here; state0 holds the bring-up values.
sr1.sensitivity(1e-3)
sr0.time_constant(0.1); sr1.time_constant(0.1)
print(f"sr0 sens={sr0.sensitivity()} tau={sr0.time_constant()} | sr1 sens={sr1.sensitivity()} tau={sr1.time_constant()} | drive {sr1.amplitude()} V -> I_bias {sr1.amplitude()/meas_config['bias_resistor']*1e9:.1f} nA")

# one leg per gate per polarity, (gate, endpoint) — endpoints are the committed card limits
legs = [(k_tg, TG_MAX), (k_tg, TG_MIN), (k_bg, BG_MAX), (k_bg, BG_MIN)]
n_pts, delay = 251, 1.0

# pA-floor gate-current readback for this check; reset to 1 in the finally block.
k_tg.nplci(10); k_bg.nplci(10)
try:
    for gate, v_endpoint in legs:
        other = k_bg if gate is k_tg else k_tg
        mc = dict(meas_config)
        mc["comments"] = f"gate-current-sanity-check; {gate.name} 0 -> {v_endpoint:+g} V, {other.name} at 0, Si 0, B 0, 10 nA"
        s = sweep.AsyncStation(mc)
        s.add_comment('gate-current-sanity-check')
        s.add_comment(f'gate: {gate.name}')
        s.add_comment(f'leg: 0 -> {v_endpoint:+g} V (card limit); {other.name} parked at 0; Si = 0 V; B = 0 T')
        s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
        xp = gate.volt
        s.fp(T_sample)
        s.fp(other.volt)
        s.fp(gate.curr).fp(other.curr)
        s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
        s.plot(xp, k_tg.curr); s.plot(xp, k_bg.curr)
        s.plot(xp, sr0.X); s.plot(xp, sr1.X)
        try:
            s.sweep(gate.volt, np.linspace(0, v_endpoint, n_pts), delay=delay)
        finally:
            s.ramp(gate.volt, 0)
finally:
    k_tg.nplci(1); k_bg.nplci(1)
    print(f"nplci reset: tg {k_tg.nplci()}, bg {k_bg.nplci()} | gates: tg {k_tg.volt():+.4f} V, bg {k_bg.volt():+.4f} V")
