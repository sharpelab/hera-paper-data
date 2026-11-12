# === SdH low-field extension (`sdh-spot-check`): n = +2.0e12 at D = 0, B 0.45 -> 1.50 T uniform-B ===
# Pins the Landau fan's B_lo (run 6's onset is censored at its record edge) at the
# fan's BINDING column (its lowest density), and returns a second F(n) point.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)   # run-5 cal
n_spot, D_spot = 2.0, 0.0                       # 1e12 cm^-2, V/nm  (= the fan's n_lo)
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, **CAL)
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)
F_L = cst.h / (4 * cst.e) * (n_spot * 1e16)     # Luttinger frequency, T (g = 4)
print(f"spot: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm -> (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}) V; "
      f"roundtrip n,D = {calc_nD(Vtg_spot, Vbg_spot, **CAL)}; F_L = {F_L:.2f} T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: bring-up state), "
      f"V_si = {k_si():+.3f} V (0), heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- field grid: uniform in B (sdh-spot-check step 1, blocking rate-limited magnet):
#     dB = d(1/B) * B_lo^2 holds Nyquist at the low-B edge. d(1/B) = 1/(2*F_L) = 0.0242 /T
#     -> dB = 4.9 mT at B_lo = 0.45; take 4.5 mT (Nyquist F_max = 22.2 T > F_L = 20.7 T).
B_LO, B_HI, DB = 0.45, 1.50, 0.0045
B_vec = np.round(np.arange(B_LO, B_HI + 1e-9, DB), 5)
assert B_vec.max() <= B_SESSION_CAP
I_TRIP = 1e-9
# Sensitivity 10 uV = 1 kOhm full scale at 10 nA. Bracketing measurements below 1.5 T:
# run 6 (n = +3.2e12) <= 25 Ohm, run 7 (n = -1.2e12) <= 136 Ohm -> n = +2.0e12 lands between;
# 1 kOhm FS keeps the band at 2-14 % of range (out of the coarse-ADC zone that grains the FFT)
# with >3x headroom even on a 300 Ohm SdH maximum.
sr1.sensitivity(10e-6)
print(f"B grid: {len(B_vec)} pts, {B_vec[0]} -> {B_vec[-1]} T, dB = {DB*1e3:.1f} mT "
      f"(d(1/B) at B_lo = {DB/B_LO**2:.4f} /T -> Nyquist F_max = {B_LO**2/(2*DB):.1f} T); "
      f"sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s / {sr1.filter_slope()} dB "
      f"(settle_s {magnet.settle_s} s = dwell, delay=0)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"sdh-spot-check low-field extension: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm (run-5 cal), "
                  f"(Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}), B {B_LO} -> {B_HI} T uniform-B {DB*1e3:.1f} mT, sr1 10 uV")
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'low-field extension at the fan n_lo: n = {n_spot:+.2f}e12 cm^-2, D = {D_spot:+.2f} V/nm; '
              f'(Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); B {B_LO} -> {B_HI} T uniform-B {DB*1e3:.1f} mT '
              f'(Nyquist F_max {B_LO**2/(2*DB):.1f} T vs F_L {F_L:.1f} T); pins the landau-fan B_lo '
              f'(run 6 onset censored at its record edge); cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbg_spot); s.ramp(k_tg.volt, Vtg_spot)
interruptible_sleep(10)

# row layout: [time, magnet_field, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
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
# gates stay at the n = +2.0e12 spot; field ends at 1.50 T — the fan then steps down to its B_lo.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
