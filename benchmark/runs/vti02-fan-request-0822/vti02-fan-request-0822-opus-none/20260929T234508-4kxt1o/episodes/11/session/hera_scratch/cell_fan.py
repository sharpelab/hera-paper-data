# === Landau fan at D = 0 (`landau-fan`): B slow (0.25 -> 10 T, 79 rows) x (Vtg, Vbg) fast along D = 0 (121 pts) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- fast axis: the D = 0 line, n = 0 exactly on-grid (index 33), ends = TG-limited ends of the realized window ---
DN = 0.037                                          # 1e12 cm^-2 per point
n_vec = np.round(np.arange(-33, 88) * DN, 6)        # -1.221 .. +3.219 e12, 121 pts
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
_nr, _Dr = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"fast: {len(n_vec)} pts, n {n_vec[0]:+.3f}..{n_vec[-1]:+.3f}e12 (dn {DN}e12, n=0 at idx {int(np.argmin(abs(n_vec)))}); "
      f"Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} (margin {Vtg_vec.min()-TG_MIN:+.4f}/{TG_MAX-Vtg_vec.max():+.4f} V), "
      f"Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f}; roundtrip max|D| {abs(_Dr).max():.1e} V/nm")

# --- slow axis: 4 apex rows (visual only) + uniform-1/B core + uniform-B high-field cap ---
B_apex = np.array([0.25, 0.50, 0.75, 1.00])                       # under-Nyquist by design; excluded from the FFT window
B_core = 1.0 / np.linspace(1/1.2, 1/5.0, 55)                      # 1.2 -> 5.0 T, d(1/B) = 0.0117 -> F_Nyq 42.6 T
B_high = np.arange(5.25, 10.0 + 1e-9, 0.25)                       # 5.25 -> 10.0 T, F_Nyq 57.8 T
B_vec = np.round(np.concatenate([B_apex, B_core, B_high]), 4)
assert np.all(np.diff(B_vec) > 0), "B grid must be monotonic (single traverse)"
assert B_vec.max() <= B_SESSION_CAP, (B_vec.max(), B_SESSION_CAP)
print(f"slow: {len(B_vec)} rows = {len(B_apex)} apex + {len(B_core)} core(1/B) + {len(B_high)} high(B); "
      f"B {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T; FFT window 1.2-10 T -> dF = {1/(1/1.2-1/10):.2f} T; "
      f"max d(1/B) over core+high = {np.abs(np.diff(1/B_vec[4:])).max():.5f} -> F_Nyq = {1/(2*np.abs(np.diff(1/B_vec[4:])).max()):.1f} T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"T_vap = {T_vaporizer():.3f} K")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

I_TRIP = 1e-9
# Fixed sensitivity for the whole fan (no autorange mid-row — a gain change would corrupt both the n-trace and the 1/B record).
# 200 uV = 20 kOhm full scale at 10 nA: 38x the largest R seen at 10 T (587 Ohm, run 7), headroom for a QH-gapped nu = 0 at the
# apex (run 4's lesson: size for the corner that rails, not the peak already seen); 0.6 Ohm quantization vs ~15 Ohm low-B oscillations.
sr1.sensitivity(200e-6)
assert 20e-3 <= sr0.sensitivity() <= 100e-3, f"sr0 sensitivity {sr0.sensitivity()} V — drain signal is 10 mV, expect 20 mV range"
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (20 kOhm FS), tau {sr1.time_constant()} s, "
      f"slope {sr1.filter_slope()} dB/oct; sr0 sens {sr0.sensitivity()} V; magnet settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D = 0: B slow {B_vec[0]}->{B_vec[-1]} T ({len(B_vec)} rows: 4 apex + 55 uniform-1/B 1.2-5 T + 20 uniform-B 5.25-10 T), "
                  f"(Vtg, Vbg) fast along D = 0, n {n_vec[0]:+.3f}..{n_vec[-1]:+.3f}e12 ({len(n_vec)} pts), sr1 200 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: fast (Vtg, Vbg) co-swept along D = 0, n {n_vec[0]:+.3f} .. {n_vec[-1]:+.3f}e12 cm^-2, {len(n_vec)} pts (dn {DN}e12); '
              f'slow B {B_vec[0]} -> {B_vec[-1]} T, {len(B_vec)} rows = 4 apex (0.25-1.0 T, visual only) + 55 uniform-1/B (1.2-5 T) + 20 uniform-B (5.25-10 T, 0.25 T); '
              f'FFT window 1.2-10 T, dF 1.36 T, F_Nyq 42.6 T; sr1 200 uV (20 kOhm FS); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B_set, Vtg, Vbg, B_meas, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
#   magnet.field is fp'd as well as swept: the slow column is the SETPOINT, the fp column is the MEASURED readback
#   (rig card read-truth) — the FFT in 1/B must use the measured one. Duplicate column name: resolve with col_indices/col_at.
s.fp(magnet.field).fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', magnet.field); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[6])), abs(float(data[7]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=2.0, fast_delay=1.0)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.4f} T (field left at the fan's end — close-out ramps it to 0), "
          f"(Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) parked, T_sample = {T_sample():.3f} K")
