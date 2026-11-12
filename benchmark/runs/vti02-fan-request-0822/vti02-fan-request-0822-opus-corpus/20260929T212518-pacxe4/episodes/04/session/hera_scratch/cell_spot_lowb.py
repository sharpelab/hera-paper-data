# === SdH spot check, low-field extension of run 6 (`sdh-spot-check`): n = +3.2e12, D = 0, B 0.30 -> 1.00 T uniform in 1/B ===
# Pins the onset of the 7.3 T carrier tone (censored at run 6's well-sampled low edge, 1.0 T) -> sets the fan's B_lo.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)   # run 5 (cnp-and-dline-calibration)
n_spot, D_spot = 3.2, 0.0                       # 1e12 cm^-2, V/nm — identical to run 6
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)
print(f"spot: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm -> (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}) V "
      f"[run 6 used (+0.9836, +1.1661)]")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: post-closeout park), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert sr1.time_constant() == 0.3 and sr1.filter_slope() == 24, (sr1.time_constant(), sr1.filter_slope())  # match run 6

# --- field grid: uniform in 1/B (this leg is ramp-cheap, 0.7 T total), d(1/B) = 0.01006 1/T
#     = run 6's spacing at its 1.0 T low edge, and Nyquist x3 on F_L(3.2e12) = 33.1 T (Nyquist freq 49.7 T).
B_vec = field_invB(0.30, 1.00, 233)
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
_d = np.diff(1.0 / B_vec)
print(f"B grid: {len(B_vec)} pts, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T; d(1/B) = {abs(_d).max():.5f} 1/T "
      f"(Nyquist F = {1/(2*abs(_d).max()):.1f} T > F_L = 33.1 T); dB {np.diff(B_vec).min()*1e3:.2f} - {np.diff(B_vec).max()*1e3:.2f} mT")
I_TRIP = 1e-9

# Sensitivity: run 6 ran the whole 0-10 T sweep at 50 uV (5.0 kOhm FS) because the 10 T corner reaches 530 Ohm.
# Below 1 T the measured R at this spot is 12-57 Ohm, i.e. sr1_X ~ 0.19 uV = 0.4 % of that range — the SR830's
# ~FS/1000 output granularity (~50 nV) then IS the noise (observed 30 nV pt-to-pt, 10x the tau=0.3 s input-noise
# floor). 5 uV = 505 Ohm FS: 8.8x headroom on the measured max, granularity ~5 nV at the lock-in floor.
sr1.sensitivity(5e-6)
print(f"sr1 sens {sr1.sensitivity()} V ({sr1.sensitivity()/9.9e-9:.0f} Ohm FS at 9.9 nA), tau {sr1.time_constant()} s / "
      f"{sr1.filter_slope()} dB; sr0 sens {sr0.sensitivity()} V; settle_s {magnet.settle_s} s = dwell (10 tau)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"sdh-spot-check low-field extension of run 6: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm (run-5 cal), "
                  f"(Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}), B 0.30 -> 1.00 T uniform in 1/B (233 pts, "
                  f"d(1/B) = 0.01006), sr1 5 uV")
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'low-field extension of run 6 (onset pinning for the landau-fan B_lo): electron side, '
              f'n = {n_spot:+.2f}e12 cm^-2, D = {D_spot:+.2f} V/nm; (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); '
              f'B 0.30 -> 1.00 T uniform in 1/B, 233 pts, d(1/B) = 0.01006 1/T (Nyquist 49.7 T vs F_L 33.1 T); '
              f'sr1 5 uV (505 Ohm FS), delay 0 (3 s magnet settle = 10 tau at tau = 0.3 s); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')

# gates to the spot, then position the magnet at the start field (FastBi1K5 set blocks = the settle; landau-fan-vti step 4)
s.ramp(k_bg.volt, Vbg_spot); s.ramp(k_tg.volt, Vtg_spot)
interruptible_sleep(10)
print(f"gates at ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}); positioning magnet 0 -> {B_vec[0]:.3f} T (~2.2 min)")
magnet.field(float(B_vec[0]))
print(f"magnet at {magnet.field():+.4f} T")

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
# ends at 1.00 T with the gates at the spot — exactly where the fan's lowest row will sit if the onset lands near 1 T;
# a lower B_lo costs only a 2-5 min ramp back down.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
