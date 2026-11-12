# === Device health re-check: reduced-extent legs (reentry-baseline) ===
# References: this session's runs 0-3 (in-range portions). Identical acquisition:
# drive 0.5 V / 13 Hz, delay 1.2 s, nplci 10 (offsets match runs 0-3; Cell B still held).

# --- preconditions (state this cell assumes but does not set) ---
T_now = T_sample()
B_now = magnet.field()
V_si = dc205.voltage()
print(f"T_sample = {T_now:.3f} K   (expect ~1.1-1.3 K)")
print(f"B        = {B_now:+.4f} T  (expect ~0)")
print(f"V_si     = {V_si:+.3f} V   (expect 0)")
print(f"V_tg/V_bg = {k_tg.volt():+.3f} / {k_bg.volt():+.3f} V (expect 0/0)")
assert T_now < 2.0 and abs(B_now) < 0.02 and abs(V_si) < 1e-2

sr1.amplitude(0.5)
k_tg.nplci(10)
k_bg.nplci(10)

meas_config['bias_voltage'] = sr1.amplitude()   # refresh stale key (was frozen at bring-up residual)
meas_config['comments'] = 'reentry-baseline: post-excursion health check, TG/BG legs at design extents, Si 0 V, B=0'

legs = [
    (k_tg, +4.0), (k_tg, -4.0),
    (k_bg, +4.5), (k_bg, -4.5),
]
n_pts, delay = 151, 1.2

for gate, v_end in legs:
    s = sweep.AsyncStation(meas_config)
    s.add_comment('reentry-baseline')
    s.add_comment(f'gate: {gate.name}; leg: 0 -> {v_end:+g} V (design extent)')
    s.add_comment('references: runs 0-3 in-range portions (same acquisition)')

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

print("health-check legs complete; TG/BG parked at 0")
