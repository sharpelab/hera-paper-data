# Plan step 4 — D=0 electron Landau fan, hardwired B_1–B_2 pair.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Preconditions: all state inherited from the operator's state0 replay, not set by this cell.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
_T, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
_vt, _vb, _vs = k_tg.volt(), k_bg.volt(), k_si()
print(f'preflight: T_sample={_T:.3f} K (1.0..1.5), T_vaporizer={_Tv:.3f} K, '
      f'B={_B:+.4f} T (|B|<0.05), TG/BG/Si=({_vt:+.4f},{_vb:+.4f},{_vs:+.4f}) V (zero)')
print(f'preflight: PS={magnet.persistent_switch_on()}, output={magnet.output_enabled()}, '
      f'heater ranges={heater.sample_range()}/{heater.vaporizer_range()} (0/0), '
      f'gate nplci={k_tg.nplci()}/{k_bg.nplci()} (1/1), step={k_tg.volt.step}/{k_bg.volt.step} V')
print(f'preflight: drive={sr1.amplitude()} V, sr0/sr1 tau={sr0.time_constant()}/{sr1.time_constant()} s, '
      f'slopes={sr0.filter_slope()}/{sr1.filter_slope()} dB/oct')
assert 1.0 <= _T <= 1.5 and 0.7 <= _Tv <= 1.5
assert abs(_B) < 0.05 and max(abs(_vt), abs(_vb), abs(_vs)) < 0.01
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert abs(k_tg.volt.step - 0.005) < 1e-9 and abs(k_bg.volt.step - 0.005) < 1e-9
assert abs(sr1.amplitude() - 1.0) < 0.01 and sr0.filter_slope() == 24 and sr1.filter_slope() == 24
assert (TG_MIN, TG_MAX, BG_MIN, BG_MAX, SI_MIN, SI_MAX, B_SESSION_CAP) == (-0.3, 1.0, -1.3, 2.0, -25.0, 25.0, 10.0)
assert (k_tg.volt.vals._min_value, k_tg.volt.vals._max_value) == (TG_MIN, TG_MAX)
assert (k_bg.volt.vals._min_value, k_bg.volt.vals._max_value) == (BG_MIN, BG_MAX)
assert (k_si.vals._min_value, k_si.vals._max_value) == (SI_MIN, SI_MAX)
assert (magnet.field.vals._min_value, magnet.field.vals._max_value) == (-B_SESSION_CAP, B_SESSION_CAP)

# Run-5 ridge-A calibration: ratio is data-calibrated, absolute c_tg remains a geometry prior.
CAL = dict(c_tg=0.0027960593093052633, c_bg=0.002160696465377614,
           n_offset=-0.08937933224099137, D_offset=-0.013)
n_vec = np.round(np.arange(0.4, 3.20001, 0.05), 5)
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), **CAL)
B_vec = np.round(np.r_[np.arange(0, 1.50001, 0.1),
                       np.arange(1.55, 3.00001, 0.05),
                       np.arange(3.1, 10.00001, 0.1)], 4)
assert len(n_vec) == 57 and len(B_vec) == 116 and np.all(np.diff(B_vec) > 0)
assert np.all((TG_MIN <= Vtg_vec) & (Vtg_vec <= TG_MAX))
assert np.all((BG_MIN <= Vbg_vec) & (Vbg_vec <= BG_MAX))
assert B_vec.min() >= 0 and B_vec.max() <= B_SESSION_CAP
_nr, _dr = calc_nD(Vtg_vec, Vbg_vec, **CAL)
assert np.max(np.abs(_nr - n_vec)) < 1e-9 and np.max(np.abs(_dr)) < 1e-9
print(f'fan: {len(B_vec)} B rows x {len(n_vec)} n points = {len(B_vec)*len(n_vec)} points; '
      f'B {B_vec[0]:.2f}..{B_vec[-1]:.2f} T; '
      f'TG {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f} V; BG {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f} V')

# Signal is large in runs 6–7, so τ=0.1 s permits a 1 s/point (10τ) dwell.
sr0.time_constant(0.1); sr1.time_constant(0.1)
sr1.sensitivity(200e-6)
print(f'lock-ins: tau={sr0.time_constant()}/{sr1.time_constant()} s, sr1 sensitivity={sr1.sensitivity()} V '
      f'(20 kΩ FS at 10 nA)')
assert sr0.time_constant() == 0.1 and sr1.time_constant() == 0.1 and sr1.sensitivity() == 200e-6

mc = dict(meas_config)
mc['Si (V)'] = _vs; mc['sample_temperature:'] = _T
mc['comments'] = ('landau-fan: D=0 electron line, run-5 ridge-A calibration; n_A +0.4..+3.2e12 '
                  'in 0.05e12 steps, B 0..10 T (0.1/0.05/0.1 T segments), 1 s fast dwell, sr1 200 uV, tau 0.1 s')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D=0, n_A={n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 cm^-2 (57 pts); '
              f'TG {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f} V, BG {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f} V; '
              f'B 0..10 T (116 rows; 0.1/0.05/0.1 T segments); run-5 cal c_bg/c_tg={CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n0={CAL["n_offset"]:+.3f}e12, D0={CAL["D_offset"]:+.3f} V/nm; sr1=200 uV, tau=0.1 s')
s.ramp(k_bg.volt, float(Vbg_vec[0])); s.ramp(k_tg.volt, float(Vtg_vec[0]))
interruptible_sleep(3)

# row = [time, B, Vtg_set, Vbg_set, T_sample, I_tg, I_bg, Vtg_read, Vbg_read, sr0_X, sr0_P, sr1_X, sr1_P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr).fp(k_tg.volt).fp(k_bg.volt)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', T_sample); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', k_tg.volt); s.plot('time', k_bg.volt)
s.plot('time', sr0.P); s.plot('time', sr1.P)

def fan_guard(station, data):
    itg, ibg, x = abs(float(data[5])), abs(float(data[6])), abs(float(data[11]))
    if itg >= 1e-9 or ibg >= 1e-9 or x >= 0.9 * 200e-6:
        print(f'FAN TRIP at B={float(data[1]):.3f} T, n_A~{float(data[2]):.4f} V TG: '
              f'|I_tg|={itg:.3e} A, |I_bg|={ibg:.3e} A, |sr1_X|={x:.3e} V')
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

fan_result = s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                              slow_delay=0, fast_delay=1.0)
print(f'fan ended: B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V; '
      f'interrupted={fan_result.metadata.get("interrupted")}')
