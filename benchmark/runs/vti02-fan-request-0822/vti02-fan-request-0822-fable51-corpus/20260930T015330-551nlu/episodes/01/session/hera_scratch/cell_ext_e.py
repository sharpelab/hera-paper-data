# === Low-field onset extension, electron side (`sdh-spot-check`): n = +3.2e12 at D = 0 (region-A calibration), B 0.25 -> 1.2 T uniform in 1/B ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_spot, D_spot = 3.2, 0.0                       # 1e12 cm^-2, V/nm — same point as run 6
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)
print(f"spot: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm -> (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}) V; "
      f"roundtrip n,D = {calc_nD(Vtg_spot, Vbg_spot, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff left it at 0), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- field grid: uniform in 1/B, ascending 0.25 -> 1.2 T. Delta(1/B) = 0.033 1/T = 3 pts/period at 10 T, 4.2 at 7.1 T.
B_vec = field_invB(0.25, 1.2, 96)
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0 and np.all(np.diff(B_vec) > 0)
_dinv = np.abs(np.diff(1 / B_vec))
I_TRIP = 1e-9
# Fixed sensitivity: 20 uV = 2 kOhm full scale at 10 nA (run 6: R <= 57 Ohm below 1.04 T -> 3 % FS).
sr1.sensitivity(20e-6)
print(f"B grid: {len(B_vec)} pts, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {_dinv.mean():.4f} 1/T (dB {1e3*np.diff(B_vec).min():.1f}-{1e3*np.diff(B_vec).max():.1f} mT); "
      f"sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s / {sr1.filter_slope()} dB (settle_s {magnet.settle_s} s = dwell)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = f"sdh-spot-check electron low-field onset extension: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm (run-5 cal), (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}), B 0.25 -> 1.2 T uniform-1/B 96 pts, sr1 20 uV"
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'low-field onset extension of run 6 (electron side): n = {n_spot:+.2f}e12 cm^-2, D = {D_spot:+.2f} V/nm; (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); '
              f'B 0.25 -> 1.2 T uniform-1/B (96 pts, d(1/B) 0.033 1/T); sr1 20 uV; cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbg_spot); s.ramp(k_tg.volt, Vtg_spot)
interruptible_sleep(10)

# row layout: [time, B, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(magnet.field, sr1.X); s.plot(magnet.field, sr0.X); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[3])), abs(float(data[4]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.sweep(magnet.field, B_vec, delay=0)
# gates stay at the spot; field ends at 1.2 T (the fan starts at its pinned B_lo <= 1 T) — no park here.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
