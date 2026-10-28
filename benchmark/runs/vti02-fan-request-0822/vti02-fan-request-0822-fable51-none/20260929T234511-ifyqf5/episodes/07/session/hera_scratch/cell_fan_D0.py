# === Landau fan on the D = 0 line (`landau-fan`): n fast [-1.28, +3.26]e12 (100 pts) x B slow 1 -> 10 T (100 mT, 91 rows) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, absolute scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff left 0 T), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- fast axis: the D = 0 line (region-A calibration), hole edge -> electron edge, both ends TG-limited ---
N_FAST = 100
_ns = np.linspace(-2, 4, 6001); _Vt, _Vb = calc_gate_voltages(_ns, 0.0, **CAL)
_ok = (_Vt >= TG_MIN) & (_Vt <= TG_MAX) & (_Vb >= BG_MIN) & (_Vb <= BG_MAX)
n_vec = np.linspace(_ns[_ok].min() + 0.005, _ns[_ok].max() - 0.005, N_FAST)          # 1e12 cm^-2
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, **CAL)
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, "fast line leaves the validator box"
assert len(Vtg_vec) == len(Vbg_vec) == N_FAST
_nchk, _Dchk = calc_nD(Vtg_vec, Vbg_vec, **CAL)
assert np.allclose(_nchk, n_vec) and np.abs(_Dchk).max() < 1e-6
print(f"fast line: n {n_vec[0]:+.3f} -> {n_vec[-1]:+.3f} e12 ({N_FAST} pts, dn {n_vec[1]-n_vec[0]:.4f}e12); "
      f"Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} V ({(Vtg_vec[1]-Vtg_vec[0])*1e3:.1f} mV), Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V ({(Vbg_vec[1]-Vbg_vec[0])*1e3:.1f} mV)")

# --- slow axis: B 1 -> 10 T, 100 mT, ascending (magnet sits at 0; ends at the cap so the next step rides down) ---
B_vec = np.round(np.arange(1.0, 10.0001, 0.1), 4)
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
FAST_DELAY, SLOW_DELAY = 1.0, 4.0     # 1 s/pt (run-5 calibrated 1.10 s/pt incl. reads); 4 s after the 1.3 V flyback (> 10 tau)
I_TRIP = 1e-9

# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA. LL minima (tens of Ohm) sit at 0.2-0.5 % of FS,
# readable per run 5; only a CNP column > 10.9 kOhm at high B would rail, and that column is not what the read needs.
sr1.sensitivity(100e-6)
print(f"B grid: {len(B_vec)} rows, {B_vec[0]} -> {B_vec[-1]} T; drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS); "
      f"sr0 sens {sr0.sensitivity()} V; tau {sr1.time_constant()} s / {sr1.filter_slope()} dB")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D=0: n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 fast ({N_FAST} pts, co-swept Vtg/Vbg on the run-5 D=0 line), "
                  f"B 1->10 T slow 100 mT ({len(B_vec)} rows), sr1 100 uV, fast_delay {FAST_DELAY} s, base T, Vsi 0")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 line (run-5 cal: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm); '
              f'fast n {n_vec[0]:+.3f} -> {n_vec[-1]:+.3f} e12 cm^-2, {N_FAST} pts (Vtg {Vtg_vec[0]:+.3f}..{Vtg_vec[-1]:+.3f}, Vbg {Vbg_vec[0]:+.3f}..{Vbg_vec[-1]:+.3f} V); '
              f'slow B 1 -> 10 T, 100 mT, {len(B_vec)} rows; T = base; Vsi = 0; sr1 100 uV; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot(k_tg.volt, k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}, Vbg={float(data[3]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)    # gates parked; the field stays where the sweep left it (10 T on completion)
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
