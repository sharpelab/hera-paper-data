# === D = 0 Landau fan (`landau-fan`): B slow 10 -> 0.8 T (descending), n fast -1.24 .. +3.24e12 on the region-A D = 0 line ===
# Plan step 4. Pre-ramp 0 -> 10 T (gates at 0 V, unrecorded), then multimegasweep: slow = magnet.field,
# fast = (k_tg.volt, k_bg.volt) co-swept along D = 0. Ends at 0.8 T; gates parked at 0 V.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, c_tg = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.linspace(-1.24, 3.24, 113), 4)                 # 1e12 cm^-2, 0.04 step; n = 0 at index 31
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtg_vec, Vbg_vec = np.round(Vtg_vec, 5), np.round(Vbg_vec, 5)
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
_n_chk, _D_chk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.abs(_n_chk - n_vec).max() < 1e-3 and np.abs(_D_chk).max() < 1e-3

# --- field grid: 0.2 T steps 10 -> 5.2 T (QH region, crossings legible), then uniform in 1/B, d(1/B) = 0.008, 5.0 -> 0.8 T ---
B_hi = np.round(np.arange(10.0, 5.1999, -0.2), 4)
B_lo = np.round(1.0 / np.linspace(0.2, 1.25, 132), 5)
B_vec = np.concatenate([B_hi, B_lo])
assert np.all(np.diff(B_vec) < 0) and B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
print(f"n: {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12, {len(n_vec)} pts | Vtg {Vtg_vec[0]:+.4f} .. {Vtg_vec[-1]:+.4f} V, "
      f"Vbg {Vbg_vec[0]:+.4f} .. {Vbg_vec[-1]:+.4f} V | B: {len(B_vec)} rows {B_vec[0]} -> {B_vec[-1]} T")

# --- preconditions (state this cell assumes but does not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_chk = {
    "T_sample (K)":      (_T0, "1.0-1.5", 1.0 <= _T0 <= 1.5),
    "B (T)":             (_B0, "|B| < 0.02 (handoff parked 0 T)", abs(_B0) < 0.02),
    "V_si (V)":          (k_si(), "0", abs(k_si()) < 0.01),
    "V_tg, V_bg (V)":    ((k_tg.volt(), k_bg.volt()), "0, 0", abs(k_tg.volt()) < 1e-3 and abs(k_bg.volt()) < 1e-3),
    "nplci tg/bg":       ((k_tg.nplci(), k_bg.nplci()), "1, 1", k_tg.nplci() == 1 and k_bg.nplci() == 1),
    "PS heater, output": ((magnet.persistent_switch_on(), magnet.output_enabled()), "True, True",
                          magnet.persistent_switch_on() and magnet.output_enabled()),
    "sr1 drive":         ((sr1.amplitude(), sr1.frequency()), "1.0 V, 13.777 Hz",
                          abs(sr1.amplitude() - 1.0) < 1e-6 and abs(sr1.frequency() - 13.777) < 0.01),
    "tau sr0/sr1 (s)":   ((sr0.time_constant(), sr1.time_constant()), "0.3, 0.3",
                          sr0.time_constant() == 0.3 and sr1.time_constant() == 0.3),
}
for _k, (_v, _exp, _ok) in _chk.items():
    print(f"[{'OK  ' if _ok else 'FAIL'}] {_k}: {_v} (expect {_exp})")
assert all(_ok for _, _, _ok in _chk.values()), "precondition mismatch — not starting"

# Fixed sensitivity for the whole fan: 200 uV = 20 kOhm FS at 10 nA. Largest off-CNP R seen (runs 6/7 at 10 T) 0.59 kOhm;
# headroom is for the CNP (nu = 0) at high B. Noise is not sensitivity-limited (run 5 @100 uV ~2 Ohm, run 6 @50 uV ~4 Ohm).
sr1.sensitivity(200e-6)
print(f"sr1 sens {sr1.sensitivity()} V (20 kOhm FS); sr0 sens {sr0.sensitivity()} V")

# --- pre-ramp 0 -> 10 T, gates at 0 V (blocking, ~73 min at 0.137 T/min; unrecorded) ---
print(f"{time.strftime('%H:%M:%S')} pre-ramp {_B0:+.4f} -> {B_vec[0]} T ...")
magnet.field(float(B_vec[0]))
_T1 = T_sample()
print(f"{time.strftime('%H:%M:%S')} at B = {magnet.field():+.4f} T; T_sample = {_T1:.3f} K")
assert 1.0 <= _T1 <= 1.5, f"T_sample {_T1} K off base after the pre-ramp — not starting the fan"

# --- station ---
mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T1
mc["comments"] = (f"landau-fan D=0: n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 ({len(n_vec)} pts) fast, co-swept (Vtg, Vbg) on region-A D=0; "
                  f"B {B_vec[0]}->{B_vec[-1]} T slow ({len(B_vec)} rows: 0.2 T to 5.2 T, then d(1/B)=0.008); Vsi 0; sr1 200 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 (region A, run-5 cal: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.3e} prior, n_offset {CAL["n_offset"]:+.4f}e12, '
              f'D_offset {CAL["D_offset"]:+.3f}); fast n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 step 0.04 ({len(n_vec)}); '
              f'slow B {B_vec[0]}->{B_vec[-1]} T descending ({len(B_vec)} rows; 0.2 T steps to 5.2 T, uniform 1/B below, d(1/B) 0.008); '
              f'fast_delay 1 s, slow_delay 3 s; sr1 200 uV; Vsi 0')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg, Vbg (fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

I_TRIP, T_TRIP = 1e-9, 2.5          # A (either gate), K (3 consecutive points)
_hot = [0]
def fan_guard(station, data):
    i_tg, i_bg, t = abs(float(data[5])), abs(float(data[6])), float(data[4])
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    _hot[0] = _hot[0] + 1 if t > T_TRIP else 0
    if _hot[0] >= 3:
        print(f"T TRIP at B={float(data[1]):.3f} T: T_sample = {t:.3f} K > {T_TRIP} K for 3 points")
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=3.0, fast_delay=1.0, init_delay=True)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"{time.strftime('%H:%M:%S')} end: B = {magnet.field():+.4f} T (field left here), (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
