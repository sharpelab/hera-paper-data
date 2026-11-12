# Plan step 4 — density–field Landau fan on the calibrated D≈0 line.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Preconditions: these states are inherited, not set by the fan.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_T, _Tv, _B, _Si = T_sample(), T_vaporizer(), magnet.field(), k_si()
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
_hr1, _hr2 = heater.sample_range(), heater.vaporizer_range()
print(f'preconditions: T_sample={_T:.3f} K [1.0,1.5], T_vaporizer={_Tv:.3f} K [0.7,1.5]; '
      f'B={_B:+.4f} T [|B|<0.05], Si={_Si:+.4f} V [|Si|<0.01]; '
      f'heater ranges={_hr1},{_hr2} [0,0], PS={_ps}, output={_out}')
assert 1.0 <= _T <= 1.5 and 0.7 <= _Tv <= 1.5
assert abs(_B) < 0.05 and abs(_Si) < 0.01
assert _hr1 == 0 and _hr2 == 0 and _ps and _out
assert (TG_MIN, TG_MAX, BG_MIN, BG_MAX, SI_MIN, SI_MAX, B_SESSION_CAP, T_SESSION_CAP) == (-0.3, 1.0, -1.3, 2.0, -25.0, 25.0, 10.0, 100.0)
print(f'gate readback: TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V; '
      f'lock-ins: sr0 τ={sr0.time_constant()} s, slope={sr0.filter_slope()} dB/oct; '
      f'sr1 τ={sr1.time_constant()} s, slope={sr1.filter_slope()} dB/oct')

CAL = dict(c_tg=2.7960593093052633e-3, c_bg=2.160696465377614e-3,
           n_offset=-0.08937933224099137, D_offset=-0.013)
n_vec = np.round(np.arange(-1.2, 3.2001, 0.05), 4)   # 1e12 cm^-2
B_vec = np.round(np.arange(1.2, 9.6001, 0.2), 4)    # T, ascending from state0
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), **CAL)
assert np.all((Vtg_vec >= TG_MIN) & (Vtg_vec <= TG_MAX))
assert np.all((Vbg_vec >= BG_MIN) & (Vbg_vec <= BG_MAX))
assert np.all((B_vec >= 0) & (B_vec <= B_SESSION_CAP))
_nr, _Dr = calc_nD(Vtg_vec, Vbg_vec, **CAL)
assert np.max(np.abs(_nr - n_vec)) < 1e-6 and np.max(np.abs(_Dr)) < 1e-6
print(f'fan grid: {len(B_vec)} B rows {B_vec[0]:.1f}..{B_vec[-1]:.1f} T, '
      f'{len(n_vec)} n points {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12, '
      f'TG {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} V, BG {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V')

# 24 dB/oct at τ=0.1 s gives 10τ per 1 s gate point; the magnet adds 3 s at each row.
sr0.time_constant(0.1); sr1.time_constant(0.1)
sr1.sensitivity(200e-6)   # 20 kΩ full scale for a 10 nA drive
assert sr0.filter_slope() == 24 and sr1.filter_slope() == 24
print(f'AC: drive={sr1.amplitude()} V, sr0 sens={sr0.sensitivity()} V; '
      f'sr1 sens={sr1.sensitivity()} V, τ={sr1.time_constant()} s, slope={sr1.filter_slope()} dB/oct')

mc = dict(meas_config); mc['Si (V)'] = _Si; mc['sample_temperature:'] = _T
mc['comments'] = ('landau-fan: D=0, n_A -1.2..+3.2e12 by 0.05e12 (run-5 cal), '
                  'B +1.2..+9.6 T by 0.2 T, Vsi=0, sr1 200 uV, tau 0.1 s, 1 s fast dwell')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment('D=0 density line from run-5 calibration; n_A -1.2..+3.2e12 cm^-2, 0.05e12 step; '
              'B +1.2..+9.6 T, 0.2 T step; Si=0; sr1 200 uV, tau 0.1 s, 1 s fast dwell; '
              'B_1-B_2 Rxx, T_0 to B_3 current')
s.ramp(k_bg.volt, float(Vbg_vec[0])); s.ramp(k_tg.volt, float(Vtg_vec[0]))
interruptible_sleep(10)

# data row: [time, B, Vtg, Vbg, T, Itg, Ibg, sr0 X/P, sr1 X/P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', T_sample); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot(k_tg.volt, sr0.P); s.plot(k_tg.volt, sr1.P)

def fan_guard(station, data):
    itg, ibg = abs(float(data[5])), abs(float(data[6]))
    vx = abs(float(data[9]))
    if itg > 1e-9 or ibg > 1e-9 or vx > 0.9 * 200e-6:
        print(f'FAN TRIP B={float(data[1]):.2f} T, TG={float(data[2]):+.4f} V: '
              f'|Itg|={itg:.2e} A, |Ibg|={ibg:.2e} A, |sr1 X|={vx:.2e} V')
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt],
                     [Vtg_vec, Vbg_vec], slow_delay=0, fast_delay=1.0)
finally:
    s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
    print(f'post-run readback: B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, '
          f'BG={k_bg.volt():+.4f} V, T_sample={T_sample():.3f} K')
