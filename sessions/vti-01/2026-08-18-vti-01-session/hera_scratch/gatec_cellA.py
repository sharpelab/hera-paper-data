# === Gate C — gate-current-sanity-check: Cell A (all 4 legs) ===
# Sweep each gate 0 -> each card limit, other gate parked at 0, Si parked at 0.
# Watch: lock-in X nonzero & varying = alive; gate curr in pA on charging slope = safe.

# --- preconditions (state this cell assumes but does not set) ---
_B = magnet.field()
_T = T_sample()
_vtg, _vbg, _vsi = k_tg.volt(), k_bg.volt(), dc205.voltage()
print(f"preconditions: B={_B:+.4f} T (expect ~0), T_sample={_T:.3f} K (expect ~1.2-1.3), "
      f"Vtg={_vtg:+.4f}, Vbg={_vbg:+.4f}, Vsi={_vsi:+.4f} (expect all ~0)")
assert abs(_B) < 0.02, f"B={_B:+.4f} T not ~0 — stop"
assert _T < 1.5, f"T_sample={_T:.3f} K not at base — stop"
assert abs(_vtg) < 0.01 and abs(_vbg) < 0.01 and abs(_vsi) < 0.01, "gates not parked at 0 — stop"

# pA-floor gate-current readback (Cell B resets nplci to 1; rangei 1e-9 stays —
# the right default for leakage monitoring; 1.05 nA full scale)
print("rangei before:", k_tg.rangei(), k_bg.rangei())
k_tg.nplci(10); k_bg.nplci(10)
k_tg.rangei(1e-9); k_bg.rangei(1e-9)

# liveness drive ~1 nA: 10 mV across the 10 MOhm bias resistor (don't inherit residual amp)
sr1.amplitude(0.010)

legs = [
    (k_tg, TG_MAX), (k_tg, TG_MIN),   # 0 -> +/-0.8 V
    (k_bg, BG_MAX), (k_bg, BG_MIN),   # 0 -> +/-5.0 V
]
n_pts, delay = 251, 1
lockins = [sr0, sr1, sr2, sr3]

for gate, v_endpoint in legs:
    other = k_bg if gate is k_tg else k_tg
    mc = {**meas_config,
          "sample_temperature:": T_sample(),
          "Si (V)": dc205.voltage(),
          "comments": (f"gate-current-sanity-check: {gate.name} 0 -> {v_endpoint:+g} V "
                       f"(card limit), {other.name} parked 0, Vsi=0, B~0, "
                       f"nplci=10 rangei=1e-9, drive 10 mV / 10 MOhm ~ 1 nA @ 13.777 Hz")}
    s = sweep.AsyncStation(mc)
    s.add_comment('gate-current-sanity-check')
    s.add_comment(f'gate: {gate.name}')
    s.add_comment(f'leg: 0 -> {v_endpoint:+g} V (card limit)')

    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)

    xp = gate.volt
    s.fp(other.volt)
    s.fp(gate.curr).fp(other.curr)
    s.fp(T_sample)
    s.plot(xp, k_tg.curr)
    s.plot(xp, k_bg.curr)
    s.plot(xp, other.volt)
    s.plot(xp, T_sample)
    for lia in lockins:
        s.fp(lia.X).fp(lia.P)
        s.plot(xp, lia.X)
        s.plot(xp, lia.P)

    try:
        s.sweep(gate.volt, np.linspace(0, v_endpoint, n_pts), delay=delay)
    finally:
        s.ramp(gate.volt, 0)
    print(f"leg done: {gate.name} 0 -> {v_endpoint:+g} V")

print("Cell A complete — all 4 legs run, gates parked at 0.")
