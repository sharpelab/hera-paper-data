# === Landau fan (`landau-fan-vti`): electron side, D = 0, n = +3.2 -> +1.0e12 (fast, paired n-line), B 0.5 -> 10 T slow (uniform in 1/B, two segments) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D0 = 0.0
n_hi, n_lo, N_n = 3.2, 1.0, 56                       # 1e12 cm^-2; dn = 0.04e12 (>= 2 pts/ray for a full-density pocket down to 0.83 T, for a 0.25-n pocket down to 0.2 T)
ns = np.linspace(n_hi, n_lo, N_n)
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs, float), np.asarray(Vbgs, float)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
print(f"fast axis: n = {n_hi:+.2f} -> {n_lo:+.2f}e12 ({N_n} pts, dn {abs(ns[1]-ns[0]):.3f}e12) at D = {D0:+.2f}; "
      f"Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f}, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V (validators TG [{TG_MIN},{TG_MAX}] BG [{BG_MIN},{BG_MAX}])")

# --- slow axis: uniform in 1/B. Low segment 0.5 -> 1.4 T at d(1/B) = 0.020 /T (Nyquist 25 T: only the <= 7.5 T light tone is
#     above onset there, run 6); high segment 1.4 -> 10 T at d(1/B) = 0.00975 /T (Nyquist 51 T = 1/3-Nyquist on F_L(3.2) = 33 T).
B_lo, B_mid, B_hi = 0.5, 1.4, 10.0
N1 = int(round((1 / B_lo - 1 / B_mid) / 0.020)) + 1          # 65
N2 = int(np.ceil((1 / B_mid - 1 / B_hi) / 0.0099)) + 1       # 64
seg1 = 1.0 / np.linspace(1 / B_lo, 1 / B_mid, N1)
seg2 = 1.0 / np.linspace(1 / B_mid, 1 / B_hi, N2)
B_vec = np.round(np.hstack((seg1, seg2[1:])), 5)
assert np.all(np.diff(B_vec) > 0) and B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
d1 = np.diff(1 / B_vec)
print(f"slow axis: {len(B_vec)} rows, B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T; d(1/B) low {abs(d1[:N1-1]).mean():.4f}, high {abs(d1[N1:]).mean():.5f} /T "
      f"(Nyquist {1/(2*abs(d1[N1:]).mean()):.1f} T vs F_L(n_hi) = {abs(n_hi)*1e16*6.626e-34/(4*1.602e-19):.1f} T); largest B step {np.diff(B_vec).max()*1e3:.0f} mT")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), T_vap = {T_vaporizer():.3f} K, B = {_B0:+.4f} T (|B| < 0.05: fan starts by ramping 0 -> 0.5 T), "
      f"V_si = {k_si():+.3f} V (0), heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, nplci tg/bg {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert int(heater.sample_range()) == 0 and int(heater.vaporizer_range()) == 0, "heaters not off"
assert k_tg.nplci() == 1 and k_bg.nplci() == 1

FAST_DELAY, SLOW_DELAY = 1.0, 3.0      # run-5 calibration: 1.17 s/pt all-in at fast_delay 1.0; slow_delay covers the gate flyback transient
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA. Worst corner is n = 1.0 x 10 T: R(B=0) = 117 Ohm (run 5),
# QH-regime Rxx maxima ~0.5-0.6 kOhm at |n| ~ 1.2-3.2 (runs 6/7) -> ~1 kOhm expected, >= 5x headroom; costs 2x resolution at the 10-Ohm high-n low-B corner.
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS), tau {sr1.time_constant()} s / {sr1.filter_slope()} dB; sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side: D = {D0:+.2f} V/nm, n = {n_hi:+.2f} -> {n_lo:+.2f}e12 ({N_n} pts) fast, "
                  f"B {B_vec[0]:.2f} -> {B_vec[-1]:.1f} T slow uniform-1/B ({len(B_vec)} rows: 0.5-1.4 T d(1/B) 0.020, 1.4-10 T 0.00975), "
                  f"fast_delay {FAST_DELAY}, slow_delay {SLOW_DELAY}, sr1 100 uV; cal run 5")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0:+.2f} V/nm, n = {n_hi:+.2f} to {n_lo:+.2f}e12 cm^-2 ({N_n} pts, paired TG/BG n-line), B = {B_vec[0]:.2f} to {B_vec[-1]:.1f} T '
              f'({len(B_vec)} rows, uniform in 1/B: d(1/B) = 0.020 /T below 1.4 T, 0.00975 /T above); cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; electron side chosen from spot checks runs 6/7')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_rail = {"n": 0}
def guards(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if abs(float(data[9])) > 0.95 * 100e-6:
        _rail["n"] += 1
        if _rail["n"] in (1, 10, 100):
            print(f"RAIL sr1 |X| > 95 % FS at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f} V (count {_rail['n']}) — corner saturating, fan continues")
s.register_run_after(guards, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
# field stays at 10 T (next step decides the ride-down); gates park at the fan's high-n start point (metallic, D = 0).
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), rail count {_rail['n']}, T_sample {T_sample():.3f} K")
