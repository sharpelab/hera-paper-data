# === Gate C: gate-current sanity check — Cell A (4 legs, one file each) ===
# Preconditions (state this cell assumes but does not set)
_T = T_sample(); _B = magnet.field()
print(f"precheck: T_sample = {_T:.3f} K (expect < 2), B = {_B:+.4f} T (expect ~0), "
      f"Vtg = {k_tg.volt():+.3f}, Vbg = {k_bg.volt():+.3f}, Vsi = {dc205.voltage():+.3f}")
assert _T < 2.0, "not at base T"
assert abs(_B) < 0.05, "magnet not at zero"
assert abs(k_tg.volt()) < 1e-3 and abs(k_bg.volt()) < 1e-3, "gates not parked at 0"

legs = [
    (k_tg, TG_MAX), (k_tg, TG_MIN),   # +3 / -3 V (SAFETIES limits)
    (k_bg, BG_MAX), (k_bg, BG_MIN),   # +4.5 / -4.5 V
]
n_pts = 251
delay = 1  # s; > 4*tau settling floor (tau = 0.3 s, 24 dB/oct)
lockins = [sr0, sr1, sr2, sr3]

# pA-floor gate-current readback; reset cell restores nplci=1
k_tg.nplci(10)
k_bg.nplci(10)

for gate, v_endpoint in legs:
    s = sweep.AsyncStation(meas_config)
    s.add_comment('gate-current-sanity-check')
    s.add_comment(f'gate: {gate.name}, leg: 0 -> {v_endpoint:+g} V (card limit); '
                  f'other gate 0, Vsi = 0, B = 0, T = {_T:.2f} K, I_bias = 5 nA')

    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)

    xp = gate.volt
    s.fp(T_sample)
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

print("all legs done; gates parked at 0")
