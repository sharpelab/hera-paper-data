# === Landau fan (`landau-fan`), plan step 4: D = 0 line, n fast (co-swept Vtg/Vbg), B slow 0.8 -> 8 T uniform in 1/B ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
# --- session calibration from run 5 (region-A ridge; ratio data-calibrated, absolute scale = 9.5 nm prior — the fan's QH lines calibrate it) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.arange(-1.20, 3.2001, 0.04), 3)          # 1e12 cm^-2, 111 pts; TG limit caps the e-side at +3.22
D_fan = 0.0                                                   # V/nm
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.full_like(n_vec, D_fan), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtg_vec, Vbg_vec = np.round(Vtg_vec, 5), np.round(Vbg_vec, 5)
_vt, _vb = sanitize_tg_bg(Vtg_vec, Vbg_vec, tg_lims, bg_lims)
assert len(_vt) == len(n_vec), "fan path leaves the committed gate box"
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX
_n_rt, _D_rt = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"fast path: {len(n_vec)} pts, n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 (roundtrip max|dn| {np.abs(_n_rt - n_vec).max():.1e}, max|D| {np.abs(_D_rt).max():.1e}); "
      f"Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} V, Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V")
B_vec = np.round(field_invB(0.8, 8.0, 113), 5)                # T, ascending, uniform in 1/B (d(1/B) = 0.0100 /T)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP
print(f"slow axis: {len(B_vec)} rows, B {B_vec[0]} -> {B_vec[-1]} T, dB {np.diff(B_vec)[0]*1e3:.1f} mT (first) .. {np.diff(B_vec)[-1]*1e3:.0f} mT (last)")
# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff left 0 T), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, settle_s {magnet.settle_s} s (3)")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} K off base"
assert abs(_B0) < 0.05, f"magnet not at 0 T: {_B0}"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert magnet.persistent_switch_on() and magnet.output_enabled()
# --- acquisition settings this cell owns ---
k_tg.nplci(1); k_bg.nplci(1)
sr1.sensitivity(100e-6)          # 10 kOhm FS at 10 nA: 17x over the largest D = 0 value seen (590 Ohm, run 7 @ 10 T); CNP column at high B may rail (accepted)
FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP = 1e-9
print(f"drive {sr1.amplitude()} V -> {sr1.amplitude()/100e6*1e9:.1f} nA; sr1 sens {sr1.sensitivity()} V; sr0 sens {sr0.sensitivity()} V; "
      f"tau {sr1.time_constant()} s / {sr1.filter_slope()} dB; nplci {k_tg.nplci()}/{k_bg.nplci()}")
mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan: D = 0 (run-5 cal), n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 fast ({len(n_vec)} pts, co-swept Vtg/Vbg), "
                  f"B {B_vec[0]}..{B_vec[-1]} T slow ({len(B_vec)} rows, uniform 1/B), sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = {D_fan:+.2f} V/nm line (region-A cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.3e} prior, '
              f'n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}); fast n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 step 0.04 '
              f'({len(n_vec)} pts; Vtg {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f}); '
              f'slow B {B_vec[0]} -> {B_vec[-1]} T uniform 1/B d(1/B)=0.01 ({len(B_vec)} rows); fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s; Vsi 0')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(5)
# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)
def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())
try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates parked at 0 (cheap, reversible); the FIELD STAYS where the fan ended (8 T on completion) — step 5 starts there
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"end state: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample = {T_sample():.3f} K")
