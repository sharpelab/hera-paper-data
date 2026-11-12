# === Low-field extension (`sdh-spot-check`): electron n = +2.0e12, D = 0, B 0.3 -> 1.2 T uniform in 1/B ===
# Pins the censored electron-side onset (run 6's Nyquist-valid record starts at 1.01 T) at the fan's
# binding density before the fan commits B_lo. Ends at 1.2 T with the gates at the spot.
from sharpelab_nb.gates import calc_gate_voltages
from hera.analysis import field_invB, luttinger_frequency, open_run, sdh_onset, SdhOnsetError

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)   # run 5 (cnp-and-dline-calibration)
n_ext, D_ext = 2.0, 0.0
Vtg_ext, Vbg_ext = calc_gate_voltages(n_ext, D_ext, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_ext <= TG_MAX and BG_MIN <= Vbg_ext <= BG_MAX, (Vtg_ext, Vbg_ext)

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05, handoff left 0 T), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"sr1 amp {sr1.amplitude()} V (1.0), tau {sr1.time_constant()} s (0.3)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1 and abs(sr1.amplitude() - 1.0) < 1e-6 and sr1.time_constant() == 0.3

# --- grid: uniform in 1/B, Nyquist x3 on F_L(n_ext) ---
F_ext = float(luttinger_frequency(n_ext * 1e16)); DINV = 1 / (3 * F_ext)
N_ext = int(np.ceil((1 / 0.3 - 1 / 1.2) / DINV)) + 1
B_ext = field_invB(0.3, 1.2, N_ext)
assert B_ext.max() <= B_SESSION_CAP
I_TRIP, T_TRIP = 1e-9, 2.0
sr1.sensitivity(20e-6)   # 2 kOhm FS at 10 nA — same scale the fan will use
print(f"n = {n_ext:+.2f}e12 -> (Vtg, Vbg) = ({Vtg_ext:+.4f}, {Vbg_ext:+.4f}); F_L = {F_ext:.1f} T; {N_ext} pts, d(1/B) = {DINV:.4f}; "
      f"sr1 sens {sr1.sensitivity()} V, settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = f"sdh-spot-check low-field extension, electron: n = {n_ext:+.2f}e12, D = 0 (run-5 cal), B 0.3 -> 1.2 T uniform 1/B ({N_ext}), sr1 20 uV"
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'low-field extension (pins censored electron onset for the fan B_lo): n = {n_ext:+.2f}e12, D = 0; (Vtg, Vbg) = ({Vtg_ext:+.4f}, {Vbg_ext:+.4f}); '
              f'B 0.3 -> 1.2 T uniform 1/B, {N_ext} pts, d(1/B) = 1/(3 F_L) = {DINV:.4f}; sr1 20 uV; cal run 5')
s.ramp(k_bg.volt, Vbg_ext); s.ramp(k_tg.volt, Vtg_ext)
interruptible_sleep(10)

# row layout: [time, B, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(magnet.field, sr1.X); s.plot(magnet.field, sr1.P); s.plot(magnet.field, sr0.X); s.plot(magnet.field, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def guard(station, data):
    i_tg, i_bg, T = abs(float(data[3])), abs(float(data[4])), float(data[2])
    if i_tg > I_TRIP or i_bg > I_TRIP or T > T_TRIP:
        print(f"GUARD TRIP at B={float(data[1]):+.3f} T: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A, T={T:.3f} K")
        station.interrupt_requested = True
s.register_run_after(guard, ())

res_ext = s.sweep(magnet.field, B_ext, delay=0)
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}); run {res_ext.id}")

# --- in-kernel onset read (the fan's B_lo input; HERA confirms in scratch before the fan lands) ---
_r = open_run(os.path.join(res_ext.basedir, str(res_ext.id)))
_B = _r.col("magnet_field"); _I = _r.col("sr0_X") / meas_config["sr0_gain"]; _R = np.abs(_r.col("sr1_X") / _I)
try:
    _on = sdh_onset(_R, _B, b_lo=0.3, r_full_scale=20e-6 / np.median(np.abs(_I)))
    print(_on.summary())
    EXT_ONSET = float(_on.onset_b)
except SdhOnsetError as _e:
    print("SdhOnsetError:", _e); EXT_ONSET = None
print(f"EXT_ONSET = {EXT_ONSET} T -> fan B_lo rule: ceil to 0.05 T, clip [0.65, 1.0]")
