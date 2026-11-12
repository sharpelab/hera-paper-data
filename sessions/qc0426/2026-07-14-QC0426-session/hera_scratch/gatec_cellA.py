# === Gate C / Cell A — gate-current-sanity-check: every Keithley gate 0 -> each card limit ===
# Si (DC205) parked at 0 V, no Si leg: no current readback on the DC205; leakage
# watch is the Keithley curr channels. Watch per leg: lock-in X nonzero & smooth
# = alive; swept-gate curr in pA on the charging slope = safe. Gross turn-up ->
# interrupt (finally parks the gate), stop, skip Cell B.

# --- preconditions (state this cell assumes but does not set) ---
T_now = T_sample()
B_now = magnet.field()
V_si = dc205.voltage()
print(f"T_sample = {T_now:.3f} K   (expect ~1.1-1.3 K base)")
print(f"B        = {B_now:+.4f} T  (expect ~0)")
print(f"V_si     = {V_si:+.3f} V   (expect 0)")
for lia in (sr0, sr1, sr2, sr3):
    print(f"{lia.name}: tau={lia.time_constant()} s, slope={lia.filter_slope()} dB/oct, "
          f"sens={lia.sensitivity():.1e}")  # bring-up record: tau/slope live only here (rig card)
assert T_now < 2.0, "sample T out of range"
assert abs(B_now) < 0.02, "field not at zero"
assert abs(V_si) < 1e-2, "Si gate not parked at 0"

sr1.amplitude(0.5)  # card default drive: 0.5 V / 100 MOhm = 5 nA
print(f"drive: {sr1.amplitude()} V @ {sr1.frequency()} Hz through 100 MOhm")

# pA-floor gate-current readback; Cell B resets to 1
k_tg.nplci(10)
k_bg.nplci(10)

meas_config['comments'] = 'gate-current-sanity-check: TG/BG legs 0->card limits, Si parked 0 V, B=0'

# one leg per gate per polarity, (gate, endpoint) -- endpoints are the committed card limits
legs = [
    (k_tg, TG_MAX), (k_tg, TG_MIN),
    (k_bg, BG_MAX), (k_bg, BG_MIN),
]
n_pts, delay = 251, 1.2  # 4*tau = 1.2 s settling floor (device card)

for gate, v_end in legs:
    s = sweep.AsyncStation(meas_config)
    s.add_comment('gate-current-sanity-check')
    s.add_comment(f'gate: {gate.name}')
    s.add_comment(f'leg: 0 -> {v_end:+g} V (card limit)')

    # park both Keithley gates at 0 (the swept one starts from 0)
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)

    xp = gate.volt
    s.fp(T_sample)
    s.fp(k_tg.volt).fp(k_tg.curr)
    s.fp(k_bg.volt).fp(k_bg.curr)
    s.plot(xp, k_tg.curr)
    s.plot(xp, k_bg.curr)
    for lia in (sr0, sr1, sr2, sr3):
        s.fp(lia.X).fp(lia.P)
        s.plot(xp, lia.X)

    try:
        s.sweep(gate.volt, np.linspace(0, v_end, n_pts), delay=delay)
    finally:
        s.ramp(gate.volt, 0)

print("all legs complete; TG/BG parked at 0")
