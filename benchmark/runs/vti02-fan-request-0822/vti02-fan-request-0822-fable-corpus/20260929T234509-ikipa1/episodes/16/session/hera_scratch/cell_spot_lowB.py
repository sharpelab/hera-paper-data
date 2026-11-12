# === SdH spot check, low-field extension (`sdh-spot-check`): n = +3.2e12 at D = 0, B 0.15 -> 0.7 T uniform in 1/B ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_spot, D_spot = 3.2, 0.0                       # same spot as run 6 — direct comparability
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)
print(f"spot: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm -> (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}) V")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff left 0), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- field grid: uniform in 1/B, 0.15 -> 0.7 T ascending. Delta(1/B) = 0.012 /T (Nyquist x2.5 on F_L = 33.1 T:
#     no fast tone can alias down into the 3-10 T band under test). Heavy tones (onsets >= 1.36 T, run 6) are dead here.
invB = np.linspace(1/0.15, 1/0.7, 438)
B_vec = np.round(1.0/invB, 5)
assert len(np.unique(B_vec)) == len(B_vec) and B_vec.max() <= B_SESSION_CAP
I_TRIP = 1e-9
# Sensitivity: run 6 measured R = 12-57 Ohm over B <= 0.75 T -> at 10 nA the 50 uV scale had this whole window
# under 1.2% FS (grainy-ADC risk). 2 uV = 200 Ohm FS: max 29% FS, 3.5x headroom over the measured max.
sr1.sensitivity(2e-6)
print(f"B grid: {len(B_vec)} pts, {B_vec[0]:.5f} -> {B_vec[-1]:.5f} T uniform-1/B; sr1 sens {sr1.sensitivity()} V, "
      f"tau {sr1.time_constant()} s (settle_s {magnet.settle_s} s = dwell)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = f"sdh-spot-check low-B extension: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm (run-5 cal), B 0.15 -> 0.7 T uniform-1/B d(1/B)=0.012, sr1 2 uV"
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'low-field extension of run 6: n = {n_spot:+.2f}e12 cm^-2, D = {D_spot:+.2f} V/nm; (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); '
              f'B 0.15 -> 0.7 T uniform-1/B, d(1/B) = 0.012 /T, 438 pts; pins the censored onset + tests the 3.0-5.1/9.5 T cluster; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')
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
# gates stay at the spot; field ends at 0.7 T — the fan (next cell) starts at 0.5 T, 0.2 T away.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
