# === Landau fan at D = 0 (`landau-fan`): B slow [0, 1.0 -> 10 T], n fast -1.25 -> +3.25e12 along the calibrated D = 0 line ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) — same CAL as runs 6–7 ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D_fan = 0.0                                                     # V/nm
n_vec = np.round(np.arange(-1.25, 3.25 + 1e-9, 0.03), 4)        # 1e12 cm^-2, 151 pts
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, D_fan, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtg_vec, Vbg_vec = np.asarray(Vtg_vec), np.asarray(Vbg_vec)
Vtg_s, Vbg_s = sanitize_tg_bg(Vtg_vec, Vbg_vec, tg_lims, bg_lims)
assert len(Vtg_s) == len(n_vec), f"D = 0 line leaves the operating box: {len(n_vec) - len(Vtg_s)} pts dropped"
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX
n_chk, D_chk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(n_chk, n_vec, atol=1e-6) and np.allclose(D_chk, D_fan, atol=1e-6)
print(f"fast line: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts, {np.diff(n_vec).mean():.3f}e12/pt) at D = {D_fan:+.2f} V/nm; "
      f"Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} V ({np.diff(Vtg_vec).mean()*1e3:.1f} mV/pt), Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V ({np.diff(Vbg_vec).mean()*1e3:.1f} mV/pt)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"drive {sr1.amplitude()} V @ {sr1.frequency():.3f} Hz (1.0 V -> 10 nA)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert abs(sr1.amplitude() - 1.0) < 1e-3

# --- slow axis: B = 0 reference row, then 1.0 -> 10.0 T in 100 mT (blocking rate-limited magnet, ~44 s + 3 s settle per row)
B_vec = np.unique(np.round(np.hstack(([0.0], np.arange(1.0, 10.0 + 1e-9, 0.1))), 4))
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() >= 0
FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan (no autorange mid-row): 100 uV = 10 kOhm full scale at 10 nA (sized to the nu = 0 ridge at 10 T).
sr1.sensitivity(100e-6)
print(f"slow axis: {len(B_vec)} rows, B {B_vec[0]} .. {B_vec[-1]} T (100 mT above 1 T); sr1 sens {sr1.sensitivity()} V (10 kOhm FS), sr0 sens {sr0.sensitivity()} V, "
      f"tau {sr1.time_constant()} s / {sr1.filter_slope()} dB; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s, magnet settle_s {magnet.settle_s} s")
print(f"price: {len(B_vec)} rows x ({len(n_vec)} pts x 1.23 s + 7 s) + 73 min ramp ~ {(len(B_vec)*(len(n_vec)*1.23+7) + 73*60)/3600:.1f} h")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D = {D_fan:+.2f} V/nm: n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 fast ({len(n_vec)} pts, co-swept TG/BG, run-5 cal), "
                  f"B slow 0 then 1.0..10.0 T 100 mT ({len(B_vec)} rows), Vsi = 0, sr1 100 uV, fast_delay 1 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = {D_fan:+.2f} V/nm; fast: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 cm^-2 in {np.diff(n_vec).mean():.3f} steps ({len(n_vec)} pts) '
              f'co-swept (Vtg {Vtg_vec[0]:+.4f}->{Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f}->{Vbg_vec[-1]:+.4f} V); slow: B {B_vec[0]} then {B_vec[1]} -> {B_vec[-1]} T in 0.1 T ({len(B_vec)} rows); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.3e} F/m2 (geometry prior), n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm; Vsi = 0; T ~ 1.2 K')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

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
    # gates parked at 0 V; the field stays where the fan ended (10 T) — the next step rides it down, never re-traversing.
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"end state: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
