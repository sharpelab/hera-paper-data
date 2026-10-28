# === Landau fan (`landau-fan`) at D = 0: B slow 0.5 -> 10 T uniform in 1/B, (Vtg, Vbg) co-swept fast along D = 0 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- fast axis: (Vtg, Vbg) co-swept along D = 0; n spans the full window the validators allow on that line,
#     backed off so both TG ends keep >= 5 mV of margin.
N_FAST = 101
n_vec = np.linspace(-1.260, 3.235, N_FAST)                 # 1e12 cm^-2, dn = 0.0450e12
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec),
                                      CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
_n_rt, _D_rt = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.abs(_D_rt).max() < 1e-9, np.abs(_D_rt).max()     # the fast line really is D = 0
print(f"fast: n {n_vec[0]:+.3f} .. {n_vec[-1]:+.3f}e12 ({N_FAST} pts, dn {n_vec[1]-n_vec[0]:.4f}e12) at D = 0; "
      f"Vtg {Vtg_vec.min():+.4f} .. {Vtg_vec.max():+.4f} V (margin {Vtg_vec.min()-TG_MIN:+.4f} / {TG_MAX-Vtg_vec.max():+.4f}), "
      f"Vbg {Vbg_vec.min():+.4f} .. {Vbg_vec.max():+.4f} V (margin {Vbg_vec.min()-BG_MIN:+.4f} / {BG_MAX-Vbg_vec.max():+.4f})")

# --- slow axis: uniform in 1/B (SdH is periodic in 1/B -> hands sdh_fft an already-even record, no resample),
#     with dB capped so the high-field end stays dense enough to read fan lines by eye.
def _invB_grid(b_lo, b_hi, d_invB, db_max):
    out, b = [b_hi], b_hi
    while b > b_lo:
        nb = 1.0 / (1.0 / b + d_invB)
        if b - nb > db_max:
            nb = b - db_max
        b = nb
        out.append(b)
    return np.round(np.array(sorted(x for x in out if x >= b_lo - 1e-9)), 4)

B_LO, B_HI, D_INVB, DB_MAX = 0.5, 10.0, 0.0125, 0.25
B_vec = _invB_grid(B_LO, B_HI, D_INVB, DB_MAX)
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
_df = 1.0 / (1.0 / B_vec[0] - 1.0 / B_vec[-1])
_fnyq = 0.5 / np.abs(np.diff(1.0 / B_vec)).max()
print(f"slow: {len(B_vec)} B rows {B_vec[0]:.4f} -> {B_vec[-1]:.2f} T, uniform in 1/B (d(1/B) = {D_INVB} /T, dB cap {DB_MAX} T); "
      f"FFT df = {_df:.2f} T, F_Nyquist = {_fnyq:.0f} T; rows <1 T: {(B_vec<1).sum()}, 1-2 T: {((B_vec>=1)&(B_vec<2)).sum()}, "
      f"2-4 T: {((B_vec>=2)&(B_vec<4)).sum()}, >=4 T: {(B_vec>=4).sum()}")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: the handoff park), "
      f"V_si = {k_si():+.3f} V (0), V_tg = {k_tg.volt():+.4f} V / V_bg = {k_bg.volt():+.4f} V (0 / 0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, "
      f"output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

FAST_DELAY, SLOW_DELAY = 0.7, 2.0
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan (no autorange mid-row): 200 uV = 20 kOhm FS at 10 nA. Runs 6/7 peaked at
# 590 Ohm away from the CNP; this map crosses the CNP on every row and the nu = 0 peak grows with B, so size to
# ~34x the highest R measured so far (session-notes recipe fix: size to the map's worst corner, not the 1D peak).
# Point noise at 50 uV was ~23 nV and is input-referred, so the 4x range step costs little SNR - verified at the
# first-rows checkpoint.
sr1.sensitivity(200e-6)
print(f"drive {sr1.amplitude()} V / {meas_config['bias_resistor']:.0e} Ohm; sr1 sens {sr1.sensitivity()} V "
      f"({sr1.sensitivity()/1e-8:.0f} Ohm FS at 10 nA), tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB/oct; "
      f"sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan at D = 0: B slow {B_vec[0]:.3f} -> {B_vec[-1]:.1f} T uniform in 1/B ({len(B_vec)} rows), "
                  f"(Vtg, Vbg) co-swept fast along D = 0, n = {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 ({N_FAST} pts), "
                  f"Vsi = 0, sr1 200 uV, fast_delay {FAST_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 line, run-5 cal (ratio {CAL["c_bg"]/CAL["c_tg"]:.3f} from data, c_tg {CAL["c_tg"]:.3e} F/m2 geometry prior, '
              f'n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm); '
              f'fast (Vtg, Vbg) co-swept: n {n_vec[0]:+.3f} -> {n_vec[-1]:+.3f}e12, {N_FAST} pts, dn {n_vec[1]-n_vec[0]:.4f}e12, '
              f'Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} V, Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V; '
              f'slow B {B_vec[0]:.4f} -> {B_vec[-1]:.2f} T, {len(B_vec)} rows uniform in 1/B (d(1/B) {D_INVB} /T, dB cap {DB_MAX} T), '
              f'FFT df {_df:.2f} T, F_Nyquist {_fnyq:.0f} T; sr1 200 uV, fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s; '
              f'expect two fan origins (region A at n = 0, region B at n ~ -0.43e12)')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.3f} T (left where the fan ended - the next step rides it down), "
          f"(Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V")
