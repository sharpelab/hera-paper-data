# Electron-side D = 0 Landau fan (`landau-fan-vti`), run-5 in-session calibration.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB, luttinger_frequency

CAL_FAN = dict(c_tg=2.7960593093052633e-3, c_bg=2.160696465377614e-3,
               n_offset=-0.08937933224099137, D_offset=-0.013)
n_line = np.linspace(3.2, 2.4, 24)  # 1e12 cm^-2; begin at high n, away from CNP
D_line = np.zeros_like(n_line)
Vtgs, Vbgs = calc_gate_voltages(n_line, D_line, CAL_FAN['c_tg'], CAL_FAN['c_bg'],
                                CAL_FAN['n_offset'], CAL_FAN['D_offset'])
B_vec = field_invB(0.85, 10.0, 110)
assert np.all((TG_MIN <= Vtgs) & (Vtgs <= TG_MAX))
assert np.all((BG_MIN <= Vbgs) & (Vbgs <= BG_MAX))
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP
for i in (0, -1):
    nr, Dr = calc_nD(Vtgs[i], Vbgs[i], CAL_FAN['c_tg'], CAL_FAN['c_bg'],
                     CAL_FAN['n_offset'], CAL_FAN['D_offset'])
    assert abs(nr - n_line[i]) < 1e-6 and abs(Dr) < 1e-6
print(f'fan: {len(B_vec)} B rows {B_vec[0]:.3f}->{B_vec[-1]:.3f} T; '
      f'{len(n_line)} n points {n_line[0]:+.2f}->{n_line[-1]:+.2f}e12; '
      f'Vtg {Vtgs[0]:+.4f}->{Vtgs[-1]:+.4f} V, Vbg {Vbgs[0]:+.4f}->{Vbgs[-1]:+.4f} V')
print(f'du={abs(1/B_vec[1]-1/B_vec[0]):.5f} T^-1; dn={abs(n_line[1]-n_line[0]):.5f}e12; '
      f'F_L,max={float(luttinger_frequency(n_line[0]*1e16)):.2f} T')

# Preconditions: only state inherited rather than set by this cell.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'],
                        max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'],
                        max_age=15, max_period=12)
_Ts, _Tv, _B, _Si = T_sample(), T_vaporizer(), magnet.field(), k_si()
_slope, _tau, _drive = sr1.filter_slope(), sr1.time_constant(), sr1.amplitude()
_sr, _vr = heater.sample_range(), heater.vaporizer_range()
print(f'precondition: Ts={_Ts:.3f} K [1.0,1.5], Tv={_Tv:.3f} K [<1.6], '
      f'B={_B:+.4f} T [|B|<0.05], Si={_Si:+.3f} V [0], '
      f'heaters={_sr}/{_vr} [0/0], PS/output={magnet.persistent_switch_on()}/{magnet.output_enabled()} [True/True], '
      f'drive={_drive:.3f} V [1], tau={_tau:.3f} s [0.3], slope={_slope} dB/oct [24], '
      f'NPLC tg/bg={k_2400_tg.nplci()}/{k_2400_bg.nplci()} [1/1]')
assert 1.0 <= _Ts <= 1.5 and _Tv < 1.6 and abs(_Tv - _Ts) < 0.6
assert abs(_B) < 0.05 and abs(_Si) < 0.01 and _sr == 0 and _vr == 0
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert abs(_drive - 1.0) < 0.01 and abs(_tau - 0.3) < 1e-6 and _slope == 24
assert k_2400_tg.nplci() == 1 and k_2400_bg.nplci() == 1
assert (TG_MIN, TG_MAX, BG_MIN, BG_MAX, B_SESSION_CAP) == (-0.3, 1.0, -1.3, 2.0, 10.0)
assert (k_tg.volt.vals._min_value, k_tg.volt.vals._max_value) == (TG_MIN, TG_MAX)
assert (k_bg.volt.vals._min_value, k_bg.volt.vals._max_value) == (BG_MIN, BG_MAX)
assert (magnet.field.vals._min_value, magnet.field.vals._max_value) == (-B_SESSION_CAP, B_SESSION_CAP)

sr1.sensitivity(50e-6)  # 5 kΩ full scale at I_bias=10 nA
mc = dict(meas_config)
mc['Si (V)'] = _Si
mc['sample_temperature:'] = _Ts
mc['comments'] = ('landau-fan-vti electron: n +3.2 to +2.4e12 cm^-2, D=0 V/nm '
                  '(run-5 calibration), B +0.85 to +10 T, 110 uniform-1/B rows, '
                  '24 n points, fast delay 3 s, sr1 50 uV')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('tetralayer-stacking-fs-count')
s.add_comment(f'electron D=0 fan; n {n_line[0]:+.2f} to {n_line[-1]:+.2f}e12 cm^-2; '
              f'B {B_vec[0]:+.2f} to {B_vec[-1]:+.2f} T; 110x24 uniform 1/B; '
              f'Vtg {Vtgs[0]:+.4f} to {Vtgs[-1]:+.4f} V, '
              f'Vbg {Vbgs[0]:+.4f} to {Vbgs[-1]:+.4f} V; '
              'run-5 CNP/D calibration; fast_delay 3 s; sr1 sensitivity 50 uV')
s.ramp(k_bg.volt, float(Vbgs[0]))
s.ramp(k_tg.volt, float(Vtgs[0]))
interruptible_sleep(10)
_Itg, _Ibg = k_tg.curr(), k_bg.curr()
print(f'gate-set readback: Vtg={k_tg.volt():+.4f}/{Vtgs[0]:+.4f} V, '
      f'Vbg={k_bg.volt():+.4f}/{Vbgs[0]:+.4f} V; '
      f'Itg={_Itg*1e12:+.1f} pA, Ibg={_Ibg*1e12:+.1f} pA')
assert abs(k_tg.volt()-Vtgs[0]) < 0.01 and abs(k_bg.volt()-Vbgs[0]) < 0.01
assert abs(_Itg) < 1e-9 and abs(_Ibg) < 1e-9

# Row layout: time, B, Vtg, Vbg, T_sample, Itg, Ibg, sr0.X/P, sr1.X/P.
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot('time', T_sample)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', sr0.X); s.plot('time', sr0.P)
s.plot('time', sr1.X); s.plot('time', sr1.P)
s.plot(magnet.field, sr1.X)

def fan_quality_guard(station, data):
    itg, ibg = abs(float(data[5])), abs(float(data[6]))
    rxx_v = abs(float(data[9]))
    if itg > 1e-9 or ibg > 1e-9 or rxx_v > 0.9 * 50e-6:
        print(f'FAN TRIP B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f} V: '
              f'|Itg|={itg*1e12:.1f} pA, |Ibg|={ibg*1e12:.1f} pA, '
              f'|sr1.X|={rxx_v*1e6:.2f} uV')
        station.interrupt_requested = True
s.register_run_after(fan_quality_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=0, fast_delay=3.0)
print(f'fan complete: B={magnet.field():+.3f} T, '
      f'Vtg={k_tg.volt():+.4f} V, Vbg={k_bg.volt():+.4f} V')
