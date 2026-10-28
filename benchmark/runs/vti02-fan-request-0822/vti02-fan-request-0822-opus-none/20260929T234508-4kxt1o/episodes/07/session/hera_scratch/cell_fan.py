# === Landau fan at D = 0 (`landau-fan`): B slow 0 -> 10 T x n fast -1.25 .. +3.25e12 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0), "
      f"V_si = {k_si():+.3f} V (0), V_tg/V_bg = {k_tg.volt():+.4f}/{k_bg.volt():+.4f} V, "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), step = {k_2400_tg.volt.step}/{k_2400_bg.volt.step} V, "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert k_2400_tg.volt.step == 0.005 and k_2400_bg.volt.step == 0.005, "Keithley step pacing changed"
assert magnet.persistent_switch_on() and magnet.output_enabled()
_f, _a = sr1.frequency(), sr1.amplitude()
assert abs(_f - 13.777) < 0.01 and abs(_a - 1.0) < 1e-6, f"drive moved: {_f} Hz, {_a} V"

# --- fast axis: density along D = 0, co-swept (V_tg, V_bg) ---
N_FAST = 139
n_vec = np.linspace(-1.25, 3.25, N_FAST)                    # 1e12 cm^-2, dn = 0.0326e12
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec),
                                      CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
_nr, _Dr = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.abs(_Dr).max() < 1e-6, "D = 0 line closure failed"

# --- slow axis: B uniform in B, 50 mT below 3 T (1/B Nyquist -> F_max 40 T), 100 mT above ---
B_vec = np.unique(np.round(np.hstack((np.arange(0.0, 3.0, 0.05), np.arange(3.0, 10.0001, 0.10))), 4))
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() >= 0

# --- lock-ins: tau 300 -> 50 ms (24 dB/oct -> dwell 0.5 s = 10 tau, the 1 % settling floor),
#     sr1 sensitivity 500 uV = 50 kOhm FS at 10 nA. Both restored in `finally`. ---
FAST_DELAY, SLOW_DELAY = 0.5, 3.0
TAU_FAN, SR1_FS = 0.05, 500e-6
_tau0 = {"sr0": sr0.time_constant(), "sr1": sr1.time_constant()}
_sens0 = sr1.sensitivity()
I_TRIP, T_TRIP = 1e-9, 2.0
s = None
_clip = {"n": 0, "worst": 0.0}

try:
    sr0.time_constant(TAU_FAN); sr1.time_constant(TAU_FAN); sr1.sensitivity(SR1_FS)
    print(f"grid: {len(B_vec)} B rows ({B_vec[0]} -> {B_vec[-1]} T) x {N_FAST} n pts "
          f"({n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12, dn {n_vec[1]-n_vec[0]:.4f}e12); "
          f"V_tg {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f}, V_bg {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f} V; "
          f"{len(B_vec)*N_FAST} pts")
    print(f"sr1 sens {sr1.sensitivity()} V ({SR1_FS/10e-9/1e3:.0f} kOhm FS), tau {sr1.time_constant()} s "
          f"@ {sr1.filter_slope()} dB/oct (was {_tau0['sr1']} s / sens {_sens0} V), dwell {FAST_DELAY} s = "
          f"{FAST_DELAY/TAU_FAN:.0f} tau; sr0 tau {sr0.time_constant()} s")

    mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
    mc["comments"] = (f"landau-fan D = 0: n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 ({N_FAST} pts) fast co-swept "
                      f"(Vtg, Vbg); B {B_vec[0]}->{B_vec[-1]} T slow ({len(B_vec)} rows, 50 mT <3 T / 100 mT above); "
                      f"sr1 sens 500 uV, tau 50 ms @ 24 dB, dwell 0.5 s = 10 tau; sr0 tau 50 ms; I_bias 10 nA")
    s = sweep.AsyncStation(mc)
    s.add_comment('landau-fan')
    s.add_comment(f'D = 0 fan (region-A cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, '
                  f'D_offset {CAL["D_offset"]:+.3f} V/nm); fast n = {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 cm^-2 in {N_FAST} pts '
                  f'(Vtg {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f} V); '
                  f'slow B {B_vec[0]}..{B_vec[-1]} T uniform-B, 50 mT below 3 T then 100 mT ({len(B_vec)} rows); '
                  f'Vsi = 0; sr1 500 uV / tau 50 ms / dwell 0.5 s')

    s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
    interruptible_sleep(10)

    # row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
    s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
    s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
    s.plot(k_tg.volt, magnet.field, sr1.X)     # the live fan
    s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
    s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
    s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

    def fan_guard(station, data):
        b, vtg = float(data[1]), float(data[2])
        t_s, i_tg, i_bg = float(data[4]), abs(float(data[5])), abs(float(data[6]))
        if i_tg > I_TRIP or i_bg > I_TRIP:
            print(f"LEAK TRIP at B={b:+.3f} T, Vtg={vtg:+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
            station.interrupt_requested = True
        if t_s > T_TRIP:
            print(f"TEMPERATURE TRIP at B={b:+.3f} T: T_sample={t_s:.3f} K > {T_TRIP} K")
            station.interrupt_requested = True
        frac = abs(float(data[9])) / SR1_FS
        if frac >= 0.95:
            _clip["n"] += 1; _clip["worst"] = max(_clip["worst"], frac)
            if _clip["n"] in (1, 10, 100, 1000):
                print(f"[clip] sr1 at {frac:.2f} FS, B={b:+.3f} T, Vtg={vtg:+.4f} ({_clip['n']} pts so far) "
                      f"-- not a trip; CNP dynamic range is plan step 5")

    s.register_run_after(fan_guard, ())

    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    sr0.time_constant(_tau0["sr0"]); sr1.time_constant(_tau0["sr1"])
    if s is not None:
        s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    else:
        k_tg.volt(0); k_bg.volt(0)
    print(f"restored: sr0 tau {sr0.time_constant()} s, sr1 tau {sr1.time_constant()} s "
          f"(sens left at {sr1.sensitivity()} V); gates {k_tg.volt():+.4f}/{k_bg.volt():+.4f} V; "
          f"B = {magnet.field():+.3f} T (left high on purpose); clipped pts {_clip['n']}, worst {_clip['worst']:.2f} FS")
