# === Step 4 — D = 0 Landau fan (`landau-fan`): n_A -1.25 -> +3.23e12 along region-A D = 0, B 0 -> 10 T ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.25, 3.23, 151)            # 1e12 cm^-2, fast (co-swept gates), hole -> electron
D_fan = 0.0                                      # V/nm
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.full_like(n_vec, D_fan), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
print(f"fast: {len(n_vec)} pts, n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 (dn {n_vec[1]-n_vec[0]:.4f}), D = {D_fan}; "
      f"Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V")

# --- slow axis: 0 T row, uniform 1/B 0.7 -> 3.6 T (d(1/B) = 0.0115), uniform 0.15 T 3.74 -> 10 T ---
B_lo = 1.0 / np.arange(1 / 0.7, 1 / 3.6, -0.0115)
B_hi = np.linspace(3.74, 10.0, 43)
B_vec = np.round(np.hstack(([0.0], B_lo, B_hi)), 4)
assert np.all(np.diff(B_vec) > 0) and B_vec.max() <= B_SESSION_CAP and B_vec.min() >= 0
print(f"slow: {len(B_vec)} rows, B {B_vec[0]} -> {B_vec[-1]} T ({len(B_lo)} uniform-1/B rows 0.7-{B_lo[-1]:.3f} T, {len(B_hi)} rows at {B_hi[1]-B_hi[0]:.3f} T)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_pre = dict(T=_T0, B=_B0, Vsi=k_si(), nplci=(k_tg.nplci(), k_bg.nplci()),
            heaters=(heater.sample_range(), heater.vaporizer_range()),
            PS=magnet.persistent_switch_on(), out=magnet.output_enabled(),
            amp=sr1.amplitude(), f=sr1.frequency(), tau=(sr0.time_constant(), sr1.time_constant()),
            slope=(sr0.filter_slope(), sr1.filter_slope()), Tvap=T_vaporizer())
print("precondition (expect): T 1.0-1.5 K | |B| < 0.05 T | Vsi 0 | nplci 1/1 | heaters 0/0 | PS/out on | "
      "sr1 1.0 V @ 13.777 Hz | tau 0.3/0.3 s | slope 24/24")
print("precondition (actual):", _pre)
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} K off base"
assert abs(_B0) < 0.05, f"magnet not at 0 T: {_B0}"
assert abs(_pre["Vsi"]) < 0.01, "Si gate not at 0"
assert _pre["nplci"] == (1.0, 1.0), "gate nplci not 1"
assert _pre["heaters"] == (0, 0), "heater range not off"
assert _pre["PS"] and _pre["out"], "magnet PS heater / output off"
assert abs(_pre["amp"] - 1.0) < 1e-6 and abs(_pre["f"] - 13.777) < 0.01, "drive changed"
assert _pre["tau"] == (0.3, 0.3) and _pre["slope"] == (24, 24), "lock-in tau/slope differ from the priced 0.3 s / 24 dB"

FAST_DELAY, SLOW_DELAY = 0.8, 5.0
I_TRIP, T_TRIP = 1e-9, 2.0
# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA (state0 left sr1 at 2 uV).
sr1.sensitivity(100e-6)
print(f"sr1 sens {sr1.sensitivity()} V (10 kOhm FS), sr0 sens {sr0.sensitivity()} V; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D = 0: n_A {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 ({len(n_vec)}) along region-A D = 0 (run-5 cal), "
                  f"B 0 -> 10 T ({len(B_vec)} rows: 0 T, uniform 1/B 0.7-3.6 T, 0.15 T to 10 T), sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan; fast: (Vtg, Vbg) co-swept, n_A {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 cm^-2, {len(n_vec)} pts, D = 0 V/nm; '
              f'slow: B {len(B_vec)} rows (0 T; 1/B-uniform 0.7-3.6 T d(1/B) 0.0115; 3.74-10 T at 0.149 T); '
              f'cal run 5: c_tg {CAL["c_tg"]:.3e}, c_bg {CAL["c_bg"]:.3e}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s, tau 0.3 s/24 dB, sr1 100 uV')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def fan_guard(station, data):
    i_tg, i_bg, T_now = abs(float(data[5])), abs(float(data[6])), float(data[4])
    if i_tg > I_TRIP or i_bg > I_TRIP or T_now > T_TRIP:
        print(f"GUARD TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A, T_sample={T_now:.3f} K")
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    # field stays where the fan ended (10 T on completion) — step 5 rides it down; never re-traverse.
    print(f"done/park: B = {magnet.field():+.4f} T, Vtg = {k_tg.volt():+.4f}, Vbg = {k_bg.volt():+.4f}, Vsi = {k_si():+.3f} V, T = {T_sample():.3f} K")
