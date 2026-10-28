# === Landau fan at D = 0 (`landau-fan`): n fast along D = 0 (co-swept Vtg, Vbg), B slow 1 -> 10 T (1/B-uniform, capped 0.2 T) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (ratio data-calibrated; absolute scale = geometry prior; this fan calibrates it) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_LO, N_HI, N_FAST = -1.25, 3.25, 151                    # 1e12 cm^-2, dn = 0.03e12
n_vec = np.linspace(N_LO, N_HI, N_FAST)
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtg_vec, Vbg_vec = np.round(Vtg_vec, 5), np.round(Vbg_vec, 5)
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
_n_chk, _D_chk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"fast: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 ({N_FAST} pts, dn {n_vec[1]-n_vec[0]:.3f}e12); "
      f"Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} V, Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V; |D| roundtrip max {np.abs(_D_chk).max():.1e} V/nm")

# --- field grid: 1/B-uniform (d(1/B) = 0.009 /T -> F_Nyquist 55 T) from 1 T, step capped at 0.2 T above 4.7 T ---
def _fan_B(B_lo=1.0, B_hi=10.0, dinv=0.009, dB_max=0.2):
    B = [B_lo]
    while B[-1] < B_hi - 1e-9:
        b = B[-1]; x = 1 / b - dinv
        B.append(min(B_hi, b + (min(dB_max, 1 / x - b) if x > 0 else dB_max)))
    return np.round(np.array(B), 4)
B_vec = _fan_B()
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"slow: B {B_vec[0]} -> {B_vec[-1]} T, {len(B_vec)} rows (1/B-uniform to {B_vec[np.argmax(np.diff(B_vec) >= 0.1999)]:.2f} T, then 0.2 T)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_chk = {
    "T_sample 1.0-1.5 K": (1.0 <= _T0 <= 1.5, f"{_T0:.3f}"),
    "B at 0 (|B|<0.05 T)": (abs(_B0) < 0.05, f"{_B0:+.4f}"),
    "V_si = 0": (abs(k_si()) < 0.01, f"{k_si():+.3f}"),
    "gates at 0": (abs(k_tg.volt()) < 1e-3 and abs(k_bg.volt()) < 1e-3, f"{k_tg.volt():+.4f}, {k_bg.volt():+.4f}"),
    "nplci tg/bg = 1": (k_tg.nplci() == 1 and k_bg.nplci() == 1, f"{k_tg.nplci()}/{k_bg.nplci()}"),
    "heaters off": (heater.sample_range() == 0 and heater.vaporizer_range() == 0, f"{heater.sample_range()}/{heater.vaporizer_range()}"),
    "PS heater on, output on": (magnet.persistent_switch_on() and magnet.output_enabled(), f"{magnet.persistent_switch_on()}/{magnet.output_enabled()}"),
    "drive 1 V @ 13.777 Hz": (abs(sr1.amplitude() - 1.0) < 1e-3 and abs(sr1.frequency() - 13.777) < 0.01, f"{sr1.amplitude()} V, {sr1.frequency()} Hz"),
}
for k, (ok, v) in _chk.items():
    print(f"[{'OK  ' if ok else 'FAIL'}] {k}: {v}")
assert all(ok for ok, _ in _chk.values()), "precondition mismatch — not starting"

I_TRIP = 1e-9
FAST_DELAY, SLOW_DELAY = 1.0, 5.0
# Fixed sensitivity for the whole fan: 200 uV = 20 kOhm full scale at 10 nA (handoff restore left sr1 at 2 uV = 200 Ohm FS).
sr1.sensitivity(200e-6)
print(f"sr1 sens {sr1.sensitivity()} V (20 kOhm FS), sr0 sens {sr0.sensitivity()} V, tau {sr1.time_constant()} s / {sr1.filter_slope()} dB")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D=0: n {N_LO:+.2f}..{N_HI:+.2f}e12 ({N_FAST}) fast along D=0 (run-5 cal), "
                  f"B {B_vec[0]}->{B_vec[-1]} T ({len(B_vec)} rows, 1/B-uniform 0.009/T capped 0.2 T), sr1 200 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: n fast {N_LO:+.2f} -> {N_HI:+.2f}e12 cm^-2, {N_FAST} pts (Vtg {Vtg_vec[0]:+.4f}->{Vtg_vec[-1]:+.4f}, '
              f'Vbg {Vbg_vec[0]:+.4f}->{Vbg_vec[-1]:+.4f}); B slow {B_vec[0]} -> {B_vec[-1]} T, {len(B_vec)} rows, 1/B-uniform '
              f'd(1/B)=0.009 capped dB 0.2 T; cal run 5: c_tg {CAL["c_tg"]:.3e}, c_bg {CAL["c_bg"]:.3e}, n_off {CAL["n_offset"]:+.4f}e12, '
              f'D_off {CAL["D_offset"]:+.3f} V/nm; Vsi 0; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s; sr1 200 uV')

# pre-position: gates to the first fast point at B = 0, then the field 0 -> 1 T (~7.5 min, blocking)
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
print(f"ramping field {_B0:+.4f} -> {B_vec[0]} T (~{abs(B_vec[0]-_B0)/0.137:.1f} min)")
s.ramp(magnet.field, B_vec[0])
interruptible_sleep(5)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', T_sample); s.plot('time', magnet.field)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY, init_delay=True)
finally:
    # gates home (cheap, safe); the field is left where the fan stopped (10 T at completion) for step 5 — never re-traverse.
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"end: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
