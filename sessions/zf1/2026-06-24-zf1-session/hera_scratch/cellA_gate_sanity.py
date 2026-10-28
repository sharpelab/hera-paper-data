# === Gate C liveness / gross-safety: gate-current-sanity-check ===
# Sweep each active gate 0 -> each device-card limit, the other parked at 0,
# watching gate current at pA resolution (nplci=10). Read the live plots per leg:
#   sr830_3.X  (4T Rxx, contacts 30-31): nonzero, smoothly varying -> device alive
#   sr830_1.X  (current ch, 5-4) and sr830_2.X (2T, 5-4): sensible, not flat
#   swept gate *.curr : pA, riding the capacitive charging slope -> safe
#   parked gate *.curr: at the readback floor -> no cross-gate path
# A gross turn-up off the charging slope = LEAK -> Kernel Interrupt (the finally
# parks the swept gate); stop and report, do NOT run Cell B.

# --- preconditions (this cell assumes these, does not set them) ---
print("T probe MC  :", temperature(), "K   (expect base, ~0.03)")
print("B field     :", magnet.field(), "T   (expect ~0)")
print("k_tg.volt   :", k_tg.volt(), "V")
print("k_bg.volt   :", k_bg.volt(), "V")
print("TG validator:", k_tg.volt.vals, "  BG validator:", k_bg.volt.vals)
assert temperature() < 0.060, "probe MC not at base T"
assert abs(magnet.field()) < 0.005, "field not near zero"

# one leg per gate per polarity, (gate, endpoint = card limit from the SAFETIES slot)
legs = [
    (k_tg, TG_MAX), (k_tg, TG_MIN),
    (k_bg, BG_MAX), (k_bg, BG_MIN),
]
n_pts   = 251
delay   = 1            # s
lockins = [sr830_1, sr830_2, sr830_3]   # mc: sr1(I,5-4), sr2(2T,5-4), sr3(4T,30-31)

# pA-floor readback on the gate-current channels; Cell B resets to 1.
k_tg.nplci(10)
k_bg.nplci(10)

# AC sense drive ~1 nA: 0.1 V across the 100 MOhm bias resistor (device card).
# Set explicitly so we don't inherit a residual amplitude that starves the X read.
sr830_1.amplitude(0.1)

for gate, v_endpoint in legs:
    s = sweep.AsyncStation(meas_config)
    s.add_comment('gate-current-sanity-check')
    s.add_comment(f'gate: {gate.name}')
    s.add_comment(f'leg: 0 -> {v_endpoint:+g} V (card limit)')

    # park both gates at 0 (the swept one starts from 0)
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)

    xp = gate.volt
    s.fp(temperature)
    s.fp(k_tg.volt).fp(k_tg.curr)
    s.fp(k_bg.volt).fp(k_bg.curr)
    s.plot(xp, k_tg.curr)
    s.plot(xp, k_bg.curr)
    for lia in lockins:
        s.fp(lia.X).fp(lia.P)
        s.plot(xp, lia.X)

    try:
        s.sweep(gate.volt, np.linspace(0, v_endpoint, n_pts), delay=delay)
    finally:
        s.ramp(gate.volt, 0)
