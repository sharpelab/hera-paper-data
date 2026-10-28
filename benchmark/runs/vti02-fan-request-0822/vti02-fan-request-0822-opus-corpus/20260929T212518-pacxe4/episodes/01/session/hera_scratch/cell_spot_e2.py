# === SdH spot check, electron side RE-ACQUISITION (`sdh-spot-check`): n = +3.2e12 at D = 0,
#     uniform in 1/B, 0.30 -> 10 T. Run 6 was under-ranged (0.25-1.6 % of full scale => ADC/noise
#     floor); this leg re-acquires it at 4x the bias current AND positions the magnet at 10 T,
#     which is where the descending Landau fan (Step 4) starts. ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration, ana cell 13) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_spot, D_spot = 3.2, 0.0                       # 1e12 cm^-2, V/nm
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)
F_L = n_spot * 1e16 * cst.h / (4 * cst.e)       # Luttinger frequency at n_spot (g = 4), Tesla
print(f"spot: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm -> (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}) V; "
      f"roundtrip n,D = {calc_nD(Vtg_spot, Vbg_spot, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}; "
      f"F_L = {F_L:.2f} T (same spot as run 6 -> grid-change reproduction)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: sweep starts at 0.30 T), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- field grid: uniform in 1/B, Nyquist x3 on F_L at every point (see the markdown for why
#     not the recipe's uniform-B branch: at B_lo = 0.3 T it needs dB = 0.9 mT = 10800 points,
#     whose 4.0 s/pt overhead (run 6) dwarfs the 0.4 s ramp between neighbours).
B_vec = np.round(field_invB(0.30, 10.0, 321), 5)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP, (B_vec.min(), B_vec.max())
_dinv = np.diff(1.0 / B_vec)
print(f"B grid: {len(B_vec)} pts, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T; d(1/B) = {_dinv.mean():.5f} "
      f"(spread {_dinv.std():.1e}) 1/T -> Nyquist factor on F_L = {1/(abs(_dinv.mean())*F_L):.2f}; "
      f"dB {abs(np.diff(B_vec)).min()*1e3:.2f} -> {abs(np.diff(B_vec)).max()*1e3:.0f} mT; "
      f"dF = 1/(1/{B_vec[0]:.2f} - 1/{B_vec[-1]:.1f}) = {1/(1/B_vec[0]-1/B_vec[-1]):.2f} T")

# --- excitation + fixed sensitivity (the run-6 fix) ---
# Run 6: X = 0.13-0.80 uV on 50 uV FS = 0.25-1.6 % => ADC granularity (1.86 nV) + input noise
# (~2.5 nV at tau 0.3 s / 24 dB) floor. The floor is an ABSOLUTE voltage, so the lever is current,
# not range: I_bias 10 -> 40 nA via drive 1 -> 4 V (SR830 max 5 V) across the 100 MOhm bias
# resistor. Heating at the worst corner P = I^2 R = (40 nA)^2 x 600 Ohm ~ 1 pW; V_sample <= 24 uV
# ~ 0.3 K << T_e ~ 8 K. sr1 50 uV = 1.25 kOhm FS at 40 nA (run-6 max 522 Ohm = 42 % FS, run-6
# low-B min 12 Ohm = 1.0 % FS). sr0 (Ithaco 1e6) reads 40 mV at 40 nA -> its 20 mV range would
# overload, so move it to 100 mV. tau / filter slope untouched.
DRIVE_V = 4.0
sr1.sensitivity(50e-6)
sr0.sensitivity(0.1)
I_TRIP = 1e-9

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"sdh-spot-check electron RE-ACQUISITION of run 6: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm "
                  f"(run-5 cal), (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}), B 0.30 -> 10 T uniform-1/B 321 pts, "
                  f"drive {DRIVE_V} V = 40 nA (run 6 was 1 V = 10 nA), sr1 50 uV, sr0 100 mV")
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'electron side RE-ACQUISITION (run 6 was under-ranged at 0.25-1.6 % FS): n = {n_spot:+.2f}e12 cm^-2, '
              f'D = {D_spot:+.2f} V/nm; (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); B 0.30 -> 10 T uniform in 1/B, '
              f'321 pts, d(1/B) = {abs(_dinv.mean()):.5f} 1/T = Nyquist x{1/(abs(_dinv.mean())*F_L):.1f} on F_L = {F_L:.1f} T; '
              f'I_bias 40 nA (drive {DRIVE_V} V / 100 MOhm), sr1 sens 50 uV = 1.25 kOhm FS, tau 0.3 s / 24 dB, delay 0 '
              f'(magnet settle_s {magnet.settle_s} s = 10 tau); cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; positions the magnet at 10 T for the Step-4 fan')
s.ramp(k_bg.volt, Vbg_spot); s.ramp(k_tg.volt, Vtg_spot)
s.ramp(sr1.amplitude, DRIVE_V)
interruptible_sleep(10)
_I = sr1.amplitude() / mc["bias_resistor"]
print(f"drive {sr1.amplitude()} V -> I_bias = {_I*1e9:.2f} nA; sr1 sens {sr1.sensitivity()} V "
      f"({sr1.sensitivity()/_I:.0f} Ohm FS), sr0 sens {sr0.sensitivity()} V; tau {sr1.time_constant()} s / "
      f"{sr1.filter_slope()} dB; gates at (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")

# row layout: [time, B, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]  (same as run 6)
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(magnet.field, sr1.X); s.plot(magnet.field, sr1.P)
s.plot(magnet.field, sr0.X); s.plot(magnet.field, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[3])), abs(float(data[4]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.sweep(magnet.field, B_vec, delay=0)
# Gates stay at the spot and the field stays at 10 T — the descending Step-4 fan starts exactly here.
print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
      f"T_sample = {T_sample():.3f} K, drive = {sr1.amplitude()} V")
