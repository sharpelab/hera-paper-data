# === Gate C — gate-current-sanity-check: every active metal gate, 0 -> each card limit ===
# recipe: device-init/gate-current-sanity-check.md (Si parked: no readback, screened, survey blocklisted)

# --- preconditions (state this cell assumes but does not set) ---
_Ts, _B, _Vsi = T_sample(), magnet.field(), dc205.voltage()
print(f"preconditions: T_sample={_Ts:.3f} K (expect 1.0-1.5), B={_B:+.4f} T (expect ~0), V_si={_Vsi:+.3f} V (expect 0)")
assert 1.0 <= _Ts <= 1.5, f"not at base T: {_Ts:.3f} K"
assert abs(_B) <= 0.02, f"field not at zero: {_B:+.4f} T"
assert abs(_Vsi) <= 0.05, f"Si gate not parked: {_Vsi:+.3f} V"

# --- bring-up record: operator-set lock-in settling state (metadata stores None for these) ---
for _lia in (sr0, sr1, sr2, sr3):
    print(f"{_lia.name}: tau={_lia.time_constant()} s, slope={_lia.filter_slope()} dB/oct, sens(pre)={_lia.sensitivity()}")

# --- drive + sensitivities: device-card starting points (CNP / gate-map scale) ---
sr1.amplitude(0.5)       # 0.5 V / 100 MOhm bias resistor = 5 nA (card)
sr1.sensitivity(2e-5)
sr2.sensitivity(2e-5)
sr3.sensitivity(2e-5)
sr0.sensitivity(1e-2)    # drain: 5 nA x 1e6 V/A = 5 mV

# pA-floor gate-current readback for the legs; the reset cell restores nplci=1
k_2400_tg.nplci(10)
k_2400_bg.nplci(10)

legs = [
    (k_tg, TG_MAX), (k_tg, TG_MIN),   # runs 0, 1
    (k_bg, BG_MAX), (k_bg, BG_MIN),   # runs 2, 3
]
n_pts, leg_delay = 251, 1.0

for gate, v_end in legs:
    meas_config["comments"] = f"gate-current-sanity-check: {gate.name}.volt 0 -> {v_end:+g} V, other metal gate + Si parked at 0"
    s = sweep.AsyncStation(meas_config)
    s.add_comment('gate-current-sanity-check')
    s.add_comment(f'gate: {gate.name}, leg: 0 -> {v_end:+g} V (card limit), n_pts={n_pts}, delay={leg_delay} s, nplci=10, I_bias=5 nA, T=base')
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)
    xp = gate.volt
    s.fp(T_sample).fp(T_vaporizer)
    s.fp(k_tg.volt).fp(k_tg.curr)
    s.fp(k_bg.volt).fp(k_bg.curr)
    for _l in (sr0, sr1, sr2, sr3):
        s.fp(_l.X).fp(_l.P)
    s.plot(xp, k_tg.curr)
    s.plot(xp, k_bg.curr)
    for _l in (sr0, sr1, sr2, sr3):
        s.plot(xp, _l.X)
        s.plot(xp, _l.P)
    s.plot('time', T_sample)
    s.plot('time', T_vaporizer)
    try:
        s.sweep(xp, np.linspace(0, v_end, n_pts), delay=leg_delay)
    finally:
        s.ramp(gate.volt, 0)
    print(f"leg done: {gate.name} 0 -> {v_end:+g} V")

print("gate-current-sanity-check: all 4 legs complete; TG/BG parked at 0")
