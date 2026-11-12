# === Gate C — liveness pass (gate-current-sanity-check), Cell A ===
# Four legs: TG 0->+3, TG 0->-3, BG 0->+4.5, BG 0->-4.5 (card limits from the
# SAFETIES slot; nothing hand-substituted). Other gate parked at 0, Si at 0.
# Per leg: watch swept-gate curr (pA, charging slope = safe), parked-gate curr
# (floor = no cross-gate path), lock-in X (nonzero, smooth = alive).

# -- preconditions (state this cell assumes but does not set)
B = magnet.field()
Ts = T_sample()
print(f"precheck: B={B:+.4f} T (expect ~0), T_sample={Ts:.3f} K (expect ~1.2)")
assert abs(B) < 0.05, f"STOP: field not at zero: {B} T"
assert Ts < 1.5, f"STOP: sample not at base: {Ts} K"

# -- bring-up record: lock-in settling + drive state (run-metadata snapshots
#    store tau/slope as None — this printout is where tau lives on disk)
for lia in (sr0, sr1, sr2, sr3):
    print(f"{lia.name}: tau={lia.time_constant()} s, slope={lia.filter_slope()} dB/oct, "
          f"sens={lia.sensitivity()} V")
print(f"sr1 drive: amplitude={sr1.amplitude()} V, freq={sr1.frequency():.2f} Hz")
print(f"rangei: k_tg={k_2400_tg.rangei()}, k_bg={k_2400_bg.rangei()}")

# liveness drive ~1 nA: 0.1 V into the 100 MOhm bias resistor (device card
# drive->current relation); don't inherit the residual amplitude
sr1.amplitude(0.1)

# pA-floor gate-current readback; the follow-up cell resets to 1
k_2400_tg.nplci(10)
k_2400_bg.nplci(10)

legs = [
    (k_2400_tg, TG_MAX), (k_2400_tg, TG_MIN),
    (k_2400_bg, BG_MAX), (k_2400_bg, BG_MIN),
]
n_pts = 251
delay = 1  # s >= 4*tau = 1.2 s effective with read time (device-card dwell floor)

for gate, v_end in legs:
    meas_config["comments"] = (
        f"gate-current-sanity-check: {gate.name} 0 -> {v_end:+g} V (card limit), "
        f"other gate parked 0, Si 0; drive 0.1 V / 100 MOhm ~1 nA, 13 Hz"
    )
    s = sweep.AsyncStation(meas_config)
    s.add_comment('gate-current-sanity-check')
    s.add_comment(f'gate: {gate.name}')
    s.add_comment(f'leg: 0 -> {v_end:+g} V (card limit)')

    # park both gates at 0 (swept one starts from 0)
    s.ramp(k_2400_tg.volt, 0)
    s.ramp(k_2400_bg.volt, 0)

    xp = gate.volt
    s.fp(k_2400_tg.volt).fp(k_2400_tg.curr)
    s.fp(k_2400_bg.volt).fp(k_2400_bg.curr)
    s.fp(T_sample)
    s.plot(xp, k_2400_tg.curr)
    s.plot(xp, k_2400_bg.curr)
    s.plot(xp, T_sample)
    for lia in (sr0, sr1, sr2, sr3):
        s.fp(lia.X).fp(lia.P)
        s.plot(xp, lia.X)

    try:
        s.sweep(gate.volt, np.linspace(0, v_end, n_pts), delay=delay)
    finally:
        s.ramp(gate.volt, 0)

print("gate-current-sanity-check: all legs complete; gates parked at 0")
