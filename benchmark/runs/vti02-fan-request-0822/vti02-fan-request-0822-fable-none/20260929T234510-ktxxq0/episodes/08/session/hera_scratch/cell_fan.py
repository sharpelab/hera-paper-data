# === Landau fan at D = 0 (`landau-fan`): n fast -1.25..+3.20e12 (131), B slow 0.5 -> 10 T (133 rows, uniform-1/B x2 segments) ===
from sharpelab_nb.gates import calc_gate_voltages

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.02: fan starts at 0.5), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.02 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- fast axis: D = 0 line, n = -1.25 .. +3.20e12 cm^-2, 131 pts (dn = 0.034e12) ---
n_vec = np.linspace(-1.25, 3.20, 131)
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX
print(f"fast axis: n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 (131), Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f}, "
      f"Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V")

# --- slow axis: B ascending 0.5 -> 10 T, uniform in 1/B, two segments ---
invB = np.unique(np.hstack((np.linspace(1/0.5, 1/1.3, 63),    # d(1/B)=0.0199, Nyquist 25 T (B < 1.3 T)
                            np.linspace(1/1.3, 1/10.0, 71)))) # d(1/B)=0.0096, Nyquist 52 T
B_vec = np.round(1.0 / invB[::-1], 5)                          # ascending 0.5 -> 10 T, 133 rows
assert B_vec[0] == 0.5 and B_vec[-1] <= B_SESSION_CAP and len(B_vec) == 133

FAST_DELAY, SLOW_DELAY = 0.7, 3.0   # 0.7 s ~ 2.3 tau (tau 0.3 s / 24 dB) - uniform lag, slopes untouched
I_TRIP = 1e-9

# Fixed sensitivity: 100 uV = 10 kOhm FS at 10 nA; gapped-CNP columns at high B may rail - accepted, stated in md.
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS); tau {sr1.time_constant()} s, "
      f"slope {sr1.filter_slope()} dB/oct")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan D=0: n fast -1.25..+3.20e12 (131), B slow 0.5->10 T uniform-1/B 2-seg (133 rows), "
                  "Vsi = 0, sr1 100 uV, cal run 5")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: n -1.25..+3.20e12 cm^-2 131 pts (dn 0.034e12), co-swept Vtg {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f} / '
              f'Vbg {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f} V; B 0.5->10 T ascending, 133 rows uniform-1/B '
              f'(d(1/B) 0.0199 below 1.3 T / 0.0096 above); cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm; after runs 6/7 spot checks')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, magnet.field, sr1.X)          # the fan, live
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f} V: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
# no park: field stays at 10 T, gates at the n = +3.2e12 end - the next step rides the field down.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, "
      f"T = {T_sample():.3f} K")
