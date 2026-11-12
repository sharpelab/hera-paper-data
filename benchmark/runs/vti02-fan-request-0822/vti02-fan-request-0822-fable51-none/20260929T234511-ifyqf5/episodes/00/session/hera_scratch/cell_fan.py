# === Landau fan at D = 0 (`landau-fan`): B slow 0.8 -> 10 T (1/B-uniform then 0.15 T) x n fast along the run-5 D = 0 line ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration (run 5, ana; run-7 SdH F = 12.6 T confirms the n scale to ~2 %) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- fast axis: n along D = 0 in 0.04e12 steps, both gates >= 8 mV inside the committed validators
DN, MARGIN = 0.04, 0.008
n_vec = np.round(np.arange(-1.40, 3.40 + 1e-9, DN), 3)
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
ok = (Vtg_vec >= TG_MIN + MARGIN) & (Vtg_vec <= TG_MAX - MARGIN) & (Vbg_vec >= BG_MIN + MARGIN) & (Vbg_vec <= BG_MAX - MARGIN)
n_vec, Vtg_vec, Vbg_vec = n_vec[ok], Vtg_vec[ok], Vbg_vec[ok]
assert len(n_vec) == 112, len(n_vec)
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX
_nchk, _Dchk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.abs(_Dchk).max() < 1e-6 and np.allclose(_nchk, n_vec)

# --- slow axis: uniform 1/B (d = 0.008 T^-1) from 0.8 T until dB reaches 0.15 T (~4.27 T), then 0.15 T steps to 10 T
d, dBmax = 0.008, 0.15
Bc = np.sqrt(dBmax / d)
seg1 = 1 / np.arange(1 / 0.8, 1 / Bc - 1e-12, -d)
seg2 = np.arange(seg1[-1] + dBmax, 10.0 + 1e-9, dBmax); seg2[-1] = 10.0
B_vec = np.round(np.hstack((seg1, seg2)), 4)
assert np.all(np.diff(B_vec) > 0) and B_vec.max() <= B_SESSION_CAP and len(B_vec) == 167, len(B_vec)
print(f"fast: {len(n_vec)} pts, n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 (0.04); Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} V, Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V")
print(f"slow: {len(B_vec)} rows, B {B_vec[0]} -> {B_vec[-1]} T ({len(seg1)} rows uniform-1/B to {seg1[-1]:.3f} T, dB {np.diff(B_vec)[0]*1e3:.1f} -> {np.diff(B_vec)[len(seg1)-2]*1e3:.0f} mT; then {len(seg2)} rows at {dBmax} T)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff left the magnet at 0), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

FAST_DELAY, SLOW_DELAY, I_TRIP = 1.0, 2.0, 1e-9
# Fixed sensitivity for the whole fan (no autorange mid-row): 100 uV = 10 kOhm FS at 10 nA.
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS), tau {sr1.time_constant()} s / {sr1.filter_slope()} dB; "
      f"sr0 sens {sr0.sensitivity()} V; magnet settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D=0: B slow {B_vec[0]}->{B_vec[-1]} T, {len(B_vec)} rows (uniform 1/B d=0.008 T^-1 to {seg1[-1]:.2f} T, then 0.15 T); "
                  f"fast n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 in 0.04 ({len(n_vec)} pts) co-swept (Vtg, Vbg) on the run-5 D=0 line; "
                  f"sr1 100 uV; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s; T base")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan, region-A cal run 5 (ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm); '
              f'slow B {B_vec[0]} -> {B_vec[-1]} T, {len(B_vec)} rows (1/B-uniform 0.008 T^-1 to {seg1[-1]:.2f} T, 0.15 T above); '
              f'fast n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f} e12 in 0.04 ({len(n_vec)} pts): Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f}, Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f}')
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
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}, Vbg={float(data[3]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates home; the field stays where the sweep left it (10 T on completion) — the next step rides it down, never re-traverses
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"end: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
