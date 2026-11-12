# === Gate C — liveness + gross gate safety: gate-current-sanity-check (first-session branch) ===
# Four legs, each gate 0 -> each card limit with the other parked at 0, 101 pts, delay 1 s,
# nplci=10 on the gate-current channels (pA floor). Lock-in X on sr1 (B_1-B_2) + sr0 (drain)
# answer "is the device alive on the provided contacts"; gate currents answer "is it safe".
# Automatic abort: |I_gate| > 1 nA on either Keithley trips the sweep (no operator eyes in E1).
from sharpelab_nb.autorange import autorange_sr830s

# --- preconditions (state this cell assumes but does not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0 = T_sample(); _B0 = magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (expect 1.0-1.5), B = {_B0:+.4f} T (expect |B|<0.02), "
      f"V_tg = {k_tg.volt():+.3f}, V_bg = {k_bg.volt():+.3f}, V_si = {k_si():+.3f} V (expect 0)")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} K off base"
assert abs(_B0) < 0.02, f"magnet not at zero: {_B0} T"
assert abs(k_si()) < 0.01, "Si gate not at 0"

legs = [(k_tg, TG_MAX), (k_tg, TG_MIN), (k_bg, BG_MAX), (k_bg, BG_MIN)]
n_pts, delay = 101, 1.0
I_TRIP = 1e-9   # A — hard abort threshold on either gate current

# pA-floor readback on the gate-current channels (reset at the end if no leg tripped)
k_tg.nplci(10); k_bg.nplci(10)

# sr1 sensitivity sized for an unknown Rxx: 500 uV = 50 kOhm full scale at I_bias = 10 nA
# (drive 1 V / 100 MOhm, as the operator set it); autorange hook tracks from there.
sr1.sensitivity(500e-6)
print(f"drive {sr1.amplitude()} V @ {sr1.frequency()} Hz -> I_bias ~ {sr1.amplitude()/100e6*1e9:.1f} nA; "
      f"sr0 sens {sr0.sensitivity()} V, sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s")

tripped = []
for gate, v_end in legs:
    other = k_bg if gate is k_tg else k_tg
    mc = dict(meas_config); mc["comments"] = f"gate-current-sanity-check: {gate.name} 0 -> {v_end:+g} V, other gate 0, Si 0, B 0"
    s = sweep.AsyncStation(mc)
    s.add_comment('gate-current-sanity-check')
    s.add_comment(f'gate: {gate.name}; leg: 0 -> {v_end:+g} V (card limit); {other.name} parked 0; Vsi = 0; B = 0')
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    xp = gate.volt
    # row layout: [time, setpoint, other.volt, gate.curr, other.curr, T_sample, sr0.X, sr0.P, sr1.X, sr1.P]
    s.fp(other.volt).fp(gate.curr).fp(other.curr).fp(T_sample)
    s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
    s.plot(xp, k_tg.curr); s.plot(xp, k_bg.curr)
    s.plot(xp, sr1.X); s.plot(xp, sr0.X)
    s.register_run_before(autorange_sr830s, (sr0, [sr1]))

    def leak_guard(station, data, _gate=gate):
        i_g, i_o = abs(float(data[3])), abs(float(data[4]))
        if i_g > I_TRIP or i_o > I_TRIP:
            print(f"LEAK TRIP on {_gate.name} leg at V = {float(data[1]):+.3f} V: |I_swept| = {i_g:.3e}, |I_other| = {i_o:.3e} A")
            tripped.append((_gate.name, float(data[1]), i_g, i_o))
            station.interrupt_requested = True
    s.register_run_after(leak_guard, ())

    try:
        s.sweep(gate.volt, np.linspace(0, v_end, n_pts), delay=delay)
    finally:
        s.ramp(gate.volt, 0)
    if tripped:
        break

if tripped:
    print("STOP — a leg tripped the leakage guard; nplci left at 10, gates parked at 0:", tripped)
else:
    k_tg.nplci(1); k_bg.nplci(1)
    print("all four legs ran without a leakage trip; nplci reset to 1")
    print("k_tg.volt validator:", k_tg.volt.vals, "| k_bg.volt validator:", k_bg.volt.vals)
