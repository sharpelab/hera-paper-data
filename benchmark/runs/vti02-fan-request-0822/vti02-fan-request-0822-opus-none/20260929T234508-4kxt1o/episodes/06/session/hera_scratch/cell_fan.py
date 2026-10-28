# === Step 4: Landau fan at D = 0 (`landau-fan`) — n = -1.27 .. +3.25e12, B 0 -> 10 T ===
# Density on the fast axis is what runs 6/7 could not buy: a real Fermi surface
# has F = alpha*n*h/4e (a line through the CNP with its own slope), a harmonic is
# an exact integer multiple of its parent at every n. Same run gives the fan-line
# families and the filling sequence around the CNP off the image.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- fast axis: the D = 0 line, uniform in n over the full validator-allowed span ---
N_FAST = 164
n_vec = np.linspace(-1.27, 3.25, N_FAST)                      # 1e12 cm^-2
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, CAL["c_tg"], CAL["c_bg"],
                                      CAL["n_offset"], CAL["D_offset"])
_n_rt, _D_rt = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"],
                       CAL["n_offset"], CAL["D_offset"])
# committed validators are the fence: sanitize must be a no-op, else the axis is wrong
_vt_s, _vb_s = sanitize_tg_bg(Vtg_vec, Vbg_vec, tg_lims, bg_lims)
assert len(_vt_s) == N_FAST, f"fast axis leaves the operating box: {N_FAST - len(_vt_s)} pts dropped"
assert TG_MIN <= Vtg_vec.min() and Vtg_vec.max() <= TG_MAX
assert BG_MIN <= Vbg_vec.min() and Vbg_vec.max() <= BG_MAX
print(f"fast: {N_FAST} pts on D = 0; n {n_vec[0]:+.3f} -> {n_vec[-1]:+.3f}e12 (dn {n_vec[1]-n_vec[0]:.4f}e12/pt); "
      f"Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} V (step {(Vtg_vec[1]-Vtg_vec[0]):+.4f}), "
      f"Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V; roundtrip max|D| = {np.abs(_D_rt).max():.2e} V/nm")

# --- slow axis: B uniform 0 -> 10 T, 0.25 T rows ---
B_vec = np.round(np.arange(0.0, 10.0001, 0.25), 4)
assert B_vec.max() <= B_SESSION_CAP, (B_vec.max(), B_SESSION_CAP)
print(f"slow: {len(B_vec)} rows, B {B_vec[0]} -> {B_vec[-1]} T, step {B_vec[1]-B_vec[0]} T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: grid starts at 0), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- sensitivity: 200 uV = 20 kOhm FS at ~10 nA. sr1_X noise is an ABSOLUTE ~47 nV floor
# (identical in runs 5/6/7 across 100/50/50 uV ranges) = 4.7 Ohm, so headroom is free;
# the CNP column at 10 T is what needs it (run 4's lesson: size to the window's corner). ---
sr1.sensitivity(200e-6)
I_TRIP, TRIP_N = 1e-9, 3     # 3 consecutive points: the row-start flyback transient is not a leak
print(f"sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB/oct "
      f"(fast_delay 1.0 s = 3.3 tau: a ~4-tau lag along a 8 mV/pt axis, not a contrast loss); "
      f"sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D = 0: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 ({N_FAST} pts), "
                  f"B 0 -> 10 T x 0.25 T ({len(B_vec)} rows), sr1 200 uV, fast_delay 1.0 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: fast (Vtg, Vbg) co-swept on the D = 0 line, n {n_vec[0]:+.3f} -> {n_vec[-1]:+.3f}e12, '
              f'{N_FAST} pts (dn {n_vec[1]-n_vec[0]:.4f}e12); slow B {B_vec[0]} -> {B_vec[-1]} T uniform {B_vec[1]-B_vec[0]} T, '
              f'{len(B_vec)} rows; Vtg {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f}; '
              f'sr1 200 uV; cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')

# park the gates at the first fast point before the field moves (Keithley volt.step paces it)
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_trip = {"n": 0}
def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        _trip["n"] += 1
        if _trip["n"] >= TRIP_N:
            print(f"LEAK TRIP ({TRIP_N} consecutive) at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
                  f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
            station.interrupt_requested = True
    else:
        _trip["n"] = 0
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                 slow_delay=2.0, fast_delay=1.0)
# ends at B = 10 T with the gates at the electron end — plan step 5 rides the field down, no re-traverse.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
