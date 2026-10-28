# D=0 electron stacking fan; landau-fan-vti; region-A calibration from gatemap run 5.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL_FAN = dict(c_tg=2.7960593093052633e-3, c_bg=2.160696465377614e-3,
               n_offset=-0.08937933224099137, D_offset=-0.013)
ns = np.linspace(2.50, 3.20, 18)                # 1e12 cm^-2, ascending: low-n corner first
Ds = np.zeros_like(ns)                          # V/nm, physical D=0
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL_FAN['c_tg'], CAL_FAN['c_bg'],
                                 CAL_FAN['n_offset'], CAL_FAN['D_offset'])
B_vec = field_invB(0.9, 10.0, 102)             # uniform in 1/B; ascend from present ~0 T
assert np.all((TG_MIN <= Vtgs) & (Vtgs <= TG_MAX))
assert np.all((BG_MIN <= Vbgs) & (Vbgs <= BG_MAX))
assert np.max(B_vec) <= B_SESSION_CAP and len(B_vec) == 102
assert np.max(np.abs(np.diff(1/B_vec))) <= 1/(3*33.1)
print(f'fan design: n {ns[0]:.2f}..{ns[-1]:.2f}e12, D=0, TG {Vtgs.min():+.4f}..{Vtgs.max():+.4f} V, '
      f'BG {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V; B {B_vec[0]:.3f}..{B_vec[-1]:.3f} T, '
      f'{len(B_vec)}x{len(ns)} points; max d(1/B) {np.max(np.abs(np.diff(1/B_vec))):.5f} T^-1')
print('roundtrip endpoints:', calc_nD(Vtgs[[0,-1]], Vbgs[[0,-1]],
      CAL_FAN['c_tg'], CAL_FAN['c_bg'], CAL_FAN['n_offset'], CAL_FAN['D_offset']))

# Preconditions are state this cell does not set. The ramp begins only after these pass.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_Ts, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
_Si = k_si(); _PS, _out = magnet.persistent_switch_on(), magnet.output_enabled()
_hr1, _hr2 = heater.sample_range(), heater.vaporizer_range()
_drive, _tau, _slope = sr1.amplitude(), sr1.time_constant(), sr1.filter_slope()
print(f'preconditions actual: T_sample={_Ts:.3f} K (1.0..1.5), T_vaporizer={_Tv:.3f} K (0.7..1.5), '
      f'B={_B:+.4f} T (|B|<0.05), Si={_Si:+.4f} V (0); '
      f'heater ranges={_hr1},{_hr2} (0,0), PS={_PS}, output={_out}; '
      f'sr1 drive={_drive:.3f} V (1), tau={_tau:.3f} s (0.3), slope={_slope} dB/oct (24)')
assert 1.0 <= _Ts <= 1.5 and 0.7 <= _Tv <= 1.5 and abs(_B) < 0.05
assert abs(_Si) < 0.01 and _PS and _out and _hr1 == 0 and _hr2 == 0
assert abs(_drive - 1.0) < 0.01 and abs(_tau - 0.3) < 1e-3 and _slope == 24

I_TRIP_FAN = 1e-9
sr1.sensitivity(50e-6)                       # 5 kOhm Rxx full scale at 10 nA
print(f'sr1 sensitivity set: {sr1.sensitivity()} V; 2.4 s fast dwell = 8 tau')
mc = dict(meas_config); mc['Si (V)'] = _Si; mc['sample_temperature:'] = _Ts
mc['comments'] = ('landau-fan-vti electron D=0: n +2.50..+3.20e12 cm^-2 (18 pts), '
                  'B +0.9..+10 T (102 uniform-1/B rows), TG +0.783..+0.984 V, '
                  'BG +0.907..+1.166 V, fast_delay 2.4 s, sr1 50 uV, '
                  'calibration run 5 region A; 1 nA gate-current trip')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(mc['comments'])

s.ramp(k_bg.volt, float(Vbgs[0])); s.ramp(k_tg.volt, float(Vtgs[0]))
interruptible_sleep(10)
_Itg, _Ibg = k_tg.curr(), k_bg.curr()
print(f'post-ramp gate currents: TG={_Itg*1e12:+.1f} pA, BG={_Ibg*1e12:+.1f} pA (trip 1000 pA)')
assert abs(_Itg) < I_TRIP_FAN and abs(_Ibg) < I_TRIP_FAN

# data layout: time, B, TG V, BG V, T_sample, T_vaporizer, TG I, BG I, sr0 X/P, sr1 X/P.
s.fp(T_sample).fp(T_vaporizer).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot('time', T_sample); s.plot('time', T_vaporizer)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot(magnet.field, sr0.X); s.plot(magnet.field, sr0.P)
s.plot(magnet.field, sr1.X); s.plot(magnet.field, sr1.P)

def fan_leak_guard(station, data):
    itg, ibg = abs(float(data[6])), abs(float(data[7]))
    if itg > I_TRIP_FAN or ibg > I_TRIP_FAN:
        print(f'LEAK TRIP at B={float(data[1]):+.3f} T, n point TG={float(data[2]):+.4f} V: '
              f'|I_tg|={itg:.3e}, |I_bg|={ibg:.3e} A')
        station.interrupt_requested = True
s.register_run_after(fan_leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=0, fast_delay=2.4)
print(f'done: B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V')
