# === Landau fan (`landau-fan-vti`): electron side, D = 0, n = 1.30 -> 3.24e12, B 0.75 -> 10 T ===
# tetralayer-stacking-fs-count Step 4. Per-column SdH FFT in 1/B; field slow, paired (Vtg, Vbg) n-line fast.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_HI, N_LO, N_N = 3.24, 1.30, 57          # 1e12 cm^-2, at D = 0; N_HI is the TG-limited end of the D = 0 line
B_LO, B_HI, N_B = 0.75, 10.0, 127         # T, uniform in 1/B

# --- fast axis: paired n-line at D = 0 (landau-fan-vti step 2 helper form) ---
ns = np.linspace(N_HI, N_LO, N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, np.zeros_like(ns), **CAL)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
_nrt, _Drt = calc_nD(Vtgs, Vbgs, **CAL)
assert np.abs(_nrt - ns).max() < 1e-9 and np.abs(_Drt).max() < 1e-9
print(f"n-line: {N_N} pts, n = {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 at D = 0, dn = {abs(ns[1]-ns[0]):.4f}e12; "
      f"Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f} (limit {TG_MAX:+.2f}, headroom {TG_MAX-Vtgs.max():+.4f}), "
      f"Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} (limit {BG_MAX:+.2f})")

# --- slow axis: uniform in 1/B (per-column SdH-FFT fan; both endpoints > 0) ---
B_vec = field_invB(B_LO, B_HI, N_B)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP, (B_vec.min(), B_vec.max(), B_SESSION_CAP)
_dinv = abs(np.diff(1.0 / B_vec)[0])
_FL_max = 3.24e16 * cst.h / (4 * cst.e)        # Luttinger frequency at n_max, T
print(f"B grid: {N_B} rows, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {_dinv:.5f} 1/T "
      f"(Nyquist F = {1/(2*_dinv):.1f} T vs F_L(n_max) = {_FL_max:.1f} T, i.e. "
      f"{1/(_dinv*_FL_max):.2f} samples per F_L period, floor 2 / preferred 3); "
      f"dF = {1/(1/B_LO - 1/B_HI):.2f} T; B step {np.diff(B_vec).min():.4f} .. {np.diff(B_vec).max():.3f} T; "
      f"rays/pt at B_lo = {(4*cst.e/cst.h*B_LO/1e16)/abs(ns[1]-ns[0]):.2f}")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: magnet parked at 0 after handoff), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
print(f"validators (gate B): k_tg {k_tg.volt.vals}, k_bg {k_bg.volt.vals}, field {magnet.field.vals}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

# Fixed sensitivity for the whole fan (landau-fan step 3). 50 uV = 5 kOhm FS at 10 nA; worst corner is
# low n x high B (run 7 reached 587 Ohm at 10 T still climbing, run 5 gives 96 Ohm at n = 1.30, B = 0).
sr1.sensitivity(50e-6)
print(f"sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB "
      f"(fast_delay 1.8 s = 6 tau); sr0 sens {sr0.sensitivity()} V")

# --- position the magnet at the fan start (FastBi1K5 set blocks through the ramp; no pre-settle sleep) ---
magnet.field(B_LO)
print(f"positioned: B = {magnet.field():+.4f} T (target {B_LO})")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = T_sample()
mc["comments"] = (f"landau-fan electron side: D = 0, n = {N_HI:+.2f} -> {N_LO:+.2f}e12 ({N_N} pts), "
                  f"B {B_LO} -> {B_HI} T ({N_B} rows, uniform 1/B), sr1 50 uV, fast_delay 1.8 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = 0 V/nm, n = {N_LO:+.2f} to {N_HI:+.2f}e12 cm^-2 ({N_N} pts, dn {abs(ns[1]-ns[0]):.4f}e12), '
              f'B = {B_LO} to {B_HI} T ({N_B} rows uniform in 1/B, d(1/B) {_dinv:.5f} 1/T, dF {1/(1/B_LO-1/B_HI):.2f} T); '
              f'tetralayer-stacking-fs-count Step 4, per-column SdH FFT; sr1 50 uV, slow_delay 1.0, fast_delay 1.8 (6 tau); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.4e}, n_offset {CAL["n_offset"]:+.4f}e12, '
              f'D_offset {CAL["D_offset"]:+.3f} V/nm')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout (multimegasweep): [time, magnet_field, k_tg_volt, k_bg_volt, T_sample, k_2400_tg_curr,
#                               k_2400_bg_curr, sr0_X, sr0_P, sr1_X, sr1_P]  -> gate currents at idx 5, 6
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', sr1.P); s.plot('time', sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

I_TRIP = 1e-9
_trip = {"n": 0}

def leak_guard(station, data):
    # two consecutive over-trip points: the per-row gate flyback transient (session_notes, run 4/5)
    # is a sub-nA single-point excursion and must not kill a 5.5 h fan.
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        _trip["n"] += 1
        if _trip["n"] >= 2:
            print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
                  f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
            station.interrupt_requested = True
    else:
        _trip["n"] = 0

s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=1.0, fast_delay=1.8)

# Ends at 10 T with the gates at the n-line's low end (n = 1.30) — the LK mass series rides the magnet
# back down from here; no park, no re-traverse.
print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
      f"n = {calc_nD(k_tg.volt(), k_bg.volt(), **CAL)[0]:+.3f}e12, T_sample = {T_sample():.3f} K")
