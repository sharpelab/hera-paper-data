# === Landau fan, electron side, D = 0 (`landau-fan-vti`) — per-column SdH-FFT fan for the stacking call ===
# B slow 1.0 -> 10.0 T uniform in 1/B (114 rows, d(1/B) = 0.0080 T^-1); n fast +1.6 -> +3.2e12 at D = 0 (41 pts, dn = 0.04e12).
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
ns = np.round(np.linspace(1.6, 3.2, 41), 4)          # 1e12 cm^-2, fast axis ascending
Ds = np.zeros_like(ns)                               # D = 0 V/nm (R_CNP(D) vertex, run 5)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs, Vbgs)
_rt = calc_nD(Vtgs[[0, -1]], Vbgs[[0, -1]], CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"n-line: {len(ns)} pts, n {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 (dn {ns[1]-ns[0]:.3f}), D = 0; Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f}, "
      f"Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V; roundtrip ends n,D = {np.round(_rt, 4).tolist()}")

B_vec = field_invB(1.0, 10.0, 114)                   # ascending (magnet sits at 0 T); ends at 10 T for the next step
assert B_vec.min() > 0 and np.abs(B_vec).max() <= B_SESSION_CAP
print(f"B grid: {len(B_vec)} rows {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {abs(1/B_vec[1]-1/B_vec[0]):.5f} T^-1 "
      f"(Nyquist {0.5/abs(1/B_vec[1]-1/B_vec[0]):.1f} T), dB {B_vec[1]-B_vec[0]:.4f} ... {B_vec[-1]-B_vec[-2]:.3f} T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), T_vap = {T_vaporizer():.3f} K, B = {_B0:+.4f} T (|B| < 0.05), V_si = {k_si():+.3f} V (0), "
      f"heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0), PS {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
# dwell is priced against tau = 0.3 s at 24 dB/oct and I_bias = 10 nA — read, don't assume
print(f"lock-in: drive {sr1.amplitude()} V @ {sr1.frequency()} Hz; sr1 tau {sr1.time_constant()} s / {sr1.filter_slope()} dB; "
      f"sr0 tau {sr0.time_constant()} s, sens {sr0.sensitivity()} V")
assert abs(sr1.amplitude() - 1.0) < 1e-3 and sr1.time_constant() == 0.3 and sr1.filter_slope() == 24
assert sr0.sensitivity() >= 0.02   # drain 10 nA x 1e6 = 10 mV

# --- fixed sensitivity for the whole fan (inherits the spot checks' 50 uV = 5 kOhm FS at 10 nA) ---
sr1.sensitivity(50e-6)
R_FS = sr1.sensitivity() / (sr1.amplitude() / 100e6)
FAST_DELAY, SLOW_DELAY = 1.8, 3.0                    # 6 tau (per-column-FFT fan); 10 tau after each row's flyback
I_TRIP = 1e-9
print(f"sr1 sens {sr1.sensitivity()} V -> FS {R_FS:.0f} Ohm; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s, magnet settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron D=0: n +1.6..+3.2e12 (41), B 1.0->10.0 T uniform 1/B (114), run-5 cal, "
                  f"sr1 50 uV, fast 1.8 s / slow 3 s, T {_T0:.3f} K")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = 0 V/nm, n = +1.6 to +3.2e12 cm^-2 (41 pts, dn 0.04), B = 1.0 to 10.0 T uniform in 1/B (114 rows, d(1/B) 0.0080); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.3e}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'purpose: tetralayer-stacking-fs-count Step 4 per-column FFT + nu-ray scale pin')

s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot(k_bg.volt, k_bg.curr); s.plot('time', k_tg.curr); s.plot('time', T_sample)

_ix = {}
_rail = {"n": 0, "B": None}
def fan_guard(station, data, writer):
    if not _ix:
        cols = writer.metadata["columns"]
        _ix.update(tg=cols.index("k_2400_tg_curr"), bg=cols.index("k_2400_bg_curr"), x=cols.index("sr1_X"), B=cols.index("magnet_field"))
    i_tg, i_bg = abs(float(data[_ix["tg"]])), abs(float(data[_ix["bg"]]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[_ix['B']]):.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if abs(float(data[_ix["x"]])) > 0.9 * sr1.sensitivity():   # rail warning only (clip = lost columns, not a hazard)
        _rail["n"] += 1
        if _rail["B"] != float(data[_ix["B"]]):
            _rail["B"] = float(data[_ix["B"]]); print(f"RAIL WARN: |sr1.X| > 90% FS at B = {_rail['B']:.3f} T, Vtg = {float(data[2]):+.4f} (count {_rail['n']})")
s.register_run_after(fan_guard, ())

# position: gates to the line start, magnet to B_lo (blocking ramp ~7 min from 0 T), then the fan
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
magnet.field(B_vec[0])
print(f"positioned: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # park gates; the field stays where the fan ended (10 T on completion) — the next step rides it down, never re-traverses
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"end: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K, rail count {_rail['n']}")
