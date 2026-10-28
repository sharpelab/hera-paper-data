# === Landau fan at D = 0 (`landau-fan`): B slow 0 -> 8 T, (Vtg, Vbg) co-swept fast along D = 0, n -1.25 .. +3.25e12 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.linspace(-1.25, 3.25, 181), 4)          # 1e12 cm^-2, 0.025e12 step
D_fan = 0.0                                                 # V/nm
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.full_like(n_vec, D_fan), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtg_vec, Vbg_vec = np.round(np.asarray(Vtg_vec, float), 5), np.round(np.asarray(Vbg_vec, float), 5)
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
_nchk, _Dchk = calc_nD(Vtg_vec[[0, -1]], Vbg_vec[[0, -1]], CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"fast path: n {n_vec[0]:+.3f} .. {n_vec[-1]:+.3f}e12 ({len(n_vec)} pts), D = {D_fan}; "
      f"Vtg {Vtg_vec[0]:+.4f} .. {Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f} .. {Vbg_vec[-1]:+.4f} V; roundtrip ends n {_nchk}, D {_Dchk}")
# --- field grid: uniform in B, ascending from where the magnet sits (0 T). 50 mT to 1.5 T, 100 mT to 8 T.
B_vec = np.unique(np.round(np.hstack((np.arange(0.0, 1.5001, 0.05), np.arange(1.6, 8.0001, 0.1))), 4))
assert B_vec.min() >= 0 and B_vec.max() <= B_SESSION_CAP
# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_amp = sr1.amplitude()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), drive {_amp} V @ {sr1.frequency():.3f} Hz (1.0 V, 13.777), "
      f"tau {sr1.time_constant()} s / {sr1.filter_slope()} dB (0.3/24), PS {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} off base"
assert abs(_B0) < 0.05, f"magnet not at 0: {_B0}"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert abs(_amp - 1.0) < 1e-6 and abs(sr1.frequency() - 13.777) < 0.01, "drive not at the session's 1.0 V / 13.777 Hz"
assert sr1.time_constant() == 0.3 and sr0.time_constant() == 0.3, "tau differs from the calibrated 0.3 s (fast_delay priced on it)"
assert magnet.persistent_switch_on() and magnet.output_enabled()
FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA (run 5 read 50 Ohm cleanly at this range;
# runs 6/7 peaked at 530-590 Ohm at 10 T off-CNP; headroom for the CNP stripe at high B).
sr1.sensitivity(100e-6)
print(f"B grid: {len(B_vec)} rows, {B_vec[0]} -> {B_vec[-1]} T; sr1 sens {sr1.sensitivity()} V (10 kOhm FS); sr0 sens {sr0.sensitivity()} V")
mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D=0: B 0->8 T (50 mT to 1.5 T, 100 mT above), fast (Vtg,Vbg) along D=0, n -1.25..+3.25e12 (181, 0.025e12); "
                  f"cal run 5 {CAL}; sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = {D_fan} V/nm; n {n_vec[0]:+.3f}..{n_vec[-1]:+.3f}e12 cm^-2, {len(n_vec)} pts (0.025e12); fast = co-swept (k_tg.volt, k_bg.volt) '
              f'Vtg {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f}; slow B 0 -> 8 T ({len(B_vec)} rows: 50 mT to 1.5 T, 100 mT to 8 T); '
              f'cal run 5: c_tg {CAL["c_tg"]:.4e}, c_bg {CAL["c_bg"]:.4e} F/m2, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm; '
              f'Vsi 0; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s; sr1 100 uV')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)
# row layout: [time, magnet_field, k_2400_tg_volt, k_2400_bg_volt, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)
_leak_idx = {}
def leak_guard(station, writer, data):
    if not _leak_idx:
        cols = writer.metadata["columns"]
        _leak_idx.update(tg=cols.index("k_2400_tg_curr"), bg=cols.index("k_2400_bg_curr"))
    i_tg, i_bg = abs(float(data[_leak_idx["tg"]])), abs(float(data[_leak_idx["bg"]]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())
try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates parked; the field stays where the fan left it (8 T on completion) — the next step starts there.
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"end: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
