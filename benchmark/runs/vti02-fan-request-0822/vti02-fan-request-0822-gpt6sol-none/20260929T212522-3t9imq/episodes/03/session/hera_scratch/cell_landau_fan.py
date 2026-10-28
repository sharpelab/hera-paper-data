# === Landau fan (`landau-fan`): D≈0, n -1.20..+3.20e12, B 0->10 T, B_1-B_2 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Preconditions: state assumed but not set by the fan.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_Ts, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
_Si, _sr, _vr = k_si(), heater.sample_range(), heater.vaporizer_range()
_drive, _freq = sr1.amplitude(), sr1.frequency()
print(f'precondition: T_sample={_Ts:.3f} K (1.0..1.5), T_vaporizer={_Tv:.3f} K (<1.6), '
      f'B={_B:+.4f} T (|B|<0.02), Si={_Si:+.4f} V (0), heater ranges={_sr}/{_vr} (0/0), '
      f'PS={magnet.persistent_switch_on()}, output={magnet.output_enabled()}, '
      f'drive={_drive:.3f} V at {_freq:.3f} Hz (1 V, 13.777 Hz), '
      f'gate step={k_tg.volt.step}/{k_bg.volt.step} V, NPLC={k_tg.nplci()}/{k_bg.nplci()}')
assert 1.0 <= _Ts <= 1.5 and _Tv < 1.6 and abs(_B) < 0.02 and abs(_Si) < 0.01
assert _sr == 0 and _vr == 0 and magnet.persistent_switch_on() and magnet.output_enabled()
assert abs(_drive - 1.0) < 0.01 and abs(_freq - 13.777) < 0.01
assert k_tg.volt.step == 0.005 and k_bg.volt.step == 0.005 and k_tg.nplci() == 1 and k_bg.nplci() == 1
assert dc205.voltage_range() == 2 and dc205.output() == 1 and abs(dc205.ramp_rate - 0.5) < 1e-9
def _bounds(v): return (float(v._min_value), float(v._max_value))
assert _bounds(k_tg.volt.vals) == (-0.3, 1.0) and _bounds(k_bg.volt.vals) == (-1.3, 2.0)
assert _bounds(k_si.vals) == (-25.0, 25.0) and _bounds(dc205.voltage.vals) == (-25.0, 25.0)
assert _bounds(magnet.field.vals) == (-10.0, 10.0) and B_SESSION_CAP == 10.0
assert _bounds(heater.sample_setpoint.vals) == (0.0, 100.0) and _bounds(heater.vaporizer_setpoint.vals) == (0.0, 100.0)

# Region-A calibration from data/5: ratio fitted to CNP ridge, scale anchored by top-hBN geometry.
CAL = dict(c_tg=2.7960593093052633e-3, c_bg=2.160696465377614e-3,
           n_offset=-0.08937933224099137, D_offset=-0.013)
n_vec = np.round(np.linspace(-1.2, 3.2, 111), 4)  # 1e12 cm^-2, 0.04 spacing
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), **CAL)
n_check, D_check = calc_nD(Vtg_vec, Vbg_vec, **CAL)
assert np.max(np.abs(n_check-n_vec)) < 1e-6 and np.max(np.abs(D_check)) < 1e-6
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX
B_vec = np.unique(np.round(np.r_[np.arange(0.0, 1.0, 0.5), np.arange(1.0, 10.0001, 0.2)], 4))
assert len(B_vec) == 48 and B_vec[0] == 0 and B_vec[-1] == 10 and B_vec.max() <= B_SESSION_CAP
print(f'grid: {len(B_vec)} B rows x {len(n_vec)} densities = {len(B_vec)*len(n_vec)} points; '
      f'B {B_vec[0]:.1f}->{B_vec[-1]:.1f} T, n {n_vec[0]:+.2f}->{n_vec[-1]:+.2f}e12; '
      f'TG {Vtg_vec.min():+.4f}->{Vtg_vec.max():+.4f} V; BG {Vbg_vec.min():+.4f}->{Vbg_vec.max():+.4f} V')

# Reduce τ to allow a full 10τ gate settle in 1 s. Restore these instrument settings on completion or interrupt.
_tau0, _tau1 = sr0.time_constant(), sr1.time_constant()
assert sr0.filter_slope() == 24 and sr1.filter_slope() == 24
sr0.time_constant(0.1); sr1.time_constant(0.1)
try:
    sr1.sensitivity(200e-6)  # 20 kOhm FS at 10 nA; CNP and QH headroom.
    print(f'lock-ins: SR0/SR1 tau={sr0.time_constant()}/{sr1.time_constant()} s, '
          f'SR1 sensitivity={sr1.sensitivity()} V (~{sr1.sensitivity()/(_drive/100e6):.0f} Ohm FS)')
    mc = dict(meas_config); mc['Si (V)'] = _Si; mc['sample_temperature:'] = _Ts
    mc['comments'] = (f'landau-fan D=0, n -1.20..+3.20e12 (111 x 0.04e12), B 0..10 T (48 rows, 0.2 T above 1 T); '
                      f'run-5 cal c_bg/c_tg={CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset={CAL["n_offset"]:+.3f}e12, '
                      f'D_offset={CAL["D_offset"]:+.3f} V/nm; sr1 sens 200 uV, tau 0.1 s, dwell 1.0 s')
    s = sweep.AsyncStation(mc)
    s.add_comment('landau-fan')
    s.add_comment(f'D=0 region-A calibrated density n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 (111); '
                  f'B 0..10 T (48 rows); TG {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} V, '
                  f'BG {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V; Si=0; sr1 200 uV')
    s.ramp(k_bg.volt, float(Vbg_vec[0])); s.ramp(k_tg.volt, float(Vtg_vec[0]))
    interruptible_sleep(10)

    # row layout: time, B, Vtg, Vbg, Ts, Tv, Itg, Ibg, sr0.X, sr0.P, sr1.X, sr1.P
    s.fp(T_sample).fp(T_vaporizer).fp(k_tg.curr).fp(k_bg.curr)
    s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
    s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
    s.plot('time', sr1.P); s.plot('time', sr0.P)
    s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
    s.plot('time', T_sample); s.plot('time', T_vaporizer)

    def safety_guard(station, data):
        if abs(float(data[6])) > 1e-9 or abs(float(data[7])) > 1e-9 or not 1.0 <= float(data[4]) <= 1.6:
            print(f'TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: '
                  f'T={float(data[4]):.3f} K, Itg={float(data[6]):+.3e} A, Ibg={float(data[7]):+.3e} A')
            station.interrupt_requested = True
    s.register_run_after(safety_guard, ())
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=0.0, fast_delay=1.0, init_delay=False)
finally:
    sr0.time_constant(_tau0); sr1.time_constant(_tau1)
print(f'done: B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V, '
      f'T_sample={T_sample():.3f} K; tau restored {_tau0}/{_tau1} s')
