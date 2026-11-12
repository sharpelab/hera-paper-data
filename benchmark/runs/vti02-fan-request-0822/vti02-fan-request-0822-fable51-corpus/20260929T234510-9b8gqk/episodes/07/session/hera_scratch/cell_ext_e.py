# === SdH spot check, low-field extension (`sdh-spot-check`, landau-fan step-1 lever 1): n = +3.2e12 at D = 0, B 0.3 -> 1.5 T, 4 mT ===
# Pins the light tone's onset (runs 6/7 both 'censored' at their record edge; run 6's sub-1 T leg was 50 mT-stepped = aliased for a 7.2 T tone).
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)   # run-5 calibration (ana)
n_spot, D_spot = 3.2, 0.0                       # same spot as run 6
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)
print(f"spot: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm -> (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}) V")

# --- preconditions (assumed, not set): base T, magnet at 0 (handoff readback +0.0027 T), Si 0, PS heater + output on ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- field grid: uniform in B, 4 mT, 0.3 -> 1.5 T (Nyquist on a 7.2 T tone holds to 0.3 T: d(1/B) = 0.044 <= 1/(3*7.2)); overlaps run 6's 10 mT leg 1.0-1.5 T for grid-change reproduction
B_vec = np.round(np.arange(0.3, 1.5001, 0.004), 4)
assert B_vec.max() <= B_SESSION_CAP
I_TRIP = 1e-9
# Sensitivity 20 uV = 2 kOhm FS at 10 nA: R <= 60 Ohm in this window (run 6), ADC step 0.07 Ohm vs the ~10 Ohm pk-pk tone at 1 T (run 6 at 50 uV: 0.19 Ohm step).
sr1.sensitivity(20e-6)
print(f"B grid: {len(B_vec)} pts, {B_vec[0]} -> {B_vec[-1]} T, 4 mT; sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB (settle_s {magnet.settle_s} s = dwell)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = f"sdh-spot-check electron low-field extension: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm (run-5 cal), (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}), B 0.3 -> 1.5 T, 4 mT, sr1 20 uV"
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'electron side LOW-FIELD EXTENSION of run 6 (onset pin for the fan B_lo): n = {n_spot:+.2f}e12 cm^-2, D = {D_spot:+.2f} V/nm; '
              f'(Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); B 0.3 -> 1.5 T uniform-B 4 mT; sr1 20 uV; cal run 5')
s.ramp(k_bg.volt, Vbg_spot); s.ramp(k_tg.volt, Vtg_spot)
interruptible_sleep(10)

# row layout: [time, B, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(magnet.field, sr1.X); s.plot(magnet.field, sr0.X); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[3])), abs(float(data[4]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.sweep(magnet.field, B_vec, delay=0)
# gates stay at the spot; field ends at 1.5 T — the fan starts from here (ramps down to its B_lo).
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
