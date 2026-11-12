# === Landau fan along D = 0 (`landau-fan`): B slow 1 -> 10 T (0.15 T), (Vtg, Vbg) co-swept fast, n -1.2 -> +3.2e12 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.2, 3.2, 89)                 # 1e12 cm^-2, dn = 0.05
D_fan = 0.0                                        # V/nm
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.full_like(n_vec, D_fan), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtg_vec, Vbg_vec = np.asarray(Vtg_vec, float), np.asarray(Vbg_vec, float)
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
B_vec = np.round(np.arange(1.0, 10.0001, 0.15), 4)  # 61 rows, ascending: start where the magnet sits (0 T), end at 10 T
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
nD0 = calc_nD(Vtg_vec[0], Vbg_vec[0], CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
nD1 = calc_nD(Vtg_vec[-1], Vbg_vec[-1], CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"fast: {len(n_vec)} pts along D = {D_fan:+.2f}: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f} e12; Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} V, Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V; "
      f"roundtrip ends (n, D) = ({nD0[0]:+.3f}, {nD0[1]:+.4f}), ({nD1[0]:+.3f}, {nD1[1]:+.4f})")
print(f"slow: {len(B_vec)} rows, B {B_vec[0]} -> {B_vec[-1]} T, step {B_vec[1]-B_vec[0]:.2f} T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts with a 0 -> 1 T ramp), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

FAST_DELAY, SLOW_DELAY = 1.5, 3.0     # 5 tau at tau = 0.3 s / 24 dB (settling trade stated in the markdown); 10 tau after each B step + flyback
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA (run-5 setting); the nu = 0 column may rail at high B - accepted.
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS); sr0 sens {sr0.sensitivity()} V; tau sr1 {sr1.time_constant()} s / {sr1.filter_slope()} dB")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D = {D_fan:+.2f}: B slow {B_vec[0]}..{B_vec[-1]} T ({len(B_vec)} rows, 0.15 T); fast (Vtg, Vbg) co-swept along D = 0, "
                  f"n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f} e12 ({len(n_vec)} pts); run-5 cal; sr1 100 uV; fast_delay {FAST_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = {D_fan:+.2f} V/nm line; fast (Vtg, Vbg) co-swept n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f} e12 ({len(n_vec)} pts, dn 0.05); '
              f'Vtg {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f}; slow B {B_vec[0]} -> {B_vec[-1]} T, {len(B_vec)} rows x 0.15 T; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; Vsi = 0; base T')
# park the gates at the fast-axis start before the first ramp so the row-0 flyback is a no-op
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot(k_tg.volt, k_tg.curr); s.plot(k_tg.volt, k_bg.curr)
s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY, init_delay=True)
finally:
    # field stays where the sweep left it (10 T if complete; the next step rides it down). Gates park at the fast-axis END (n = +3.2), the
    # last point already visited - no extra traverse. Read back the actual state either way.
    print(f"end state: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample = {T_sample():.3f} K")
