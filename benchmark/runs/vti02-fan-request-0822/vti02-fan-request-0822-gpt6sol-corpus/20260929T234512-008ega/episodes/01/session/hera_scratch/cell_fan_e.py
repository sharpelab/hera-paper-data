# === Electron D=0 Landau fan: 133 B rows x 37 paired-gate density points ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# State inherited from operator's handoff (cell 44); this cell sets gates, sensitivity and B itself.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_T, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
_Vsi, _Vtg, _Vbg = k_si(), k_tg.volt(), k_bg.volt()
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
print(f'precondition T_sample={_T:.3f} K, T_vaporizer={_Tv:.3f} K (base); B={_B:+.4f} T (0); '
      f'Vsi={_Vsi:+.4f}, Vtg={_Vtg:+.4f}, Vbg={_Vbg:+.4f} V (all 0); PS_on={_ps}, output={_out}')
assert 1.0 <= _T <= 1.5 and _Tv < 1.6 and abs(_Tv-_T) < 0.6
assert abs(_B) < 0.05 and abs(_Vsi) < 0.01 and abs(_Vtg) < 0.01 and abs(_Vbg) < 0.01
assert _ps and _out and heater.sample_range() == 0 and heater.vaporizer_range() == 0
assert abs(sr1.amplitude()-1.0) < 0.01 and abs(sr1.frequency()-13.777) < 0.01
assert sr1.time_constant() == 0.3 and sr1.filter_slope() == 24
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert (TG_MIN, TG_MAX, BG_MIN, BG_MAX, B_SESSION_CAP) == (-0.3, 1.0, -1.3, 2.0, 10.0)
assert (k_tg.volt.vals._min_value, k_tg.volt.vals._max_value) == (TG_MIN, TG_MAX)
assert (k_bg.volt.vals._min_value, k_bg.volt.vals._max_value) == (BG_MIN, BG_MAX)
assert (dc205.smart_voltage.vals._min_value, dc205.smart_voltage.vals._max_value) == (-25.0, 25.0)
assert (dc205.voltage.vals._min_value, dc205.voltage.vals._max_value) == (-25.0, 25.0)
assert (magnet.field.vals._min_value, magnet.field.vals._max_value) == (-10.0, 10.0)
assert T_SESSION_CAP == 100.0
assert (heater.sample_setpoint.vals._min_value, heater.sample_setpoint.vals._max_value) == (0.0, 100.0)
assert (heater.vaporizer_setpoint.vals._min_value, heater.vaporizer_setpoint.vals._max_value) == (0.0, 100.0)

CAL = dict(c_tg=2.796e-3, c_bg=2.161e-3, n_offset=-0.0894, D_offset=-0.013)
ns = np.linspace(2.4, 3.2, 37)  # 1e12 cm^-2, low n first to expose worst-corner railing early in each row
Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])
B_vec = field_invB(0.70, 10.0, 133)  # uniform 1/B, ascending from the zero-field handoff
assert len(Vtgs) == len(Vbgs) == len(ns) == 37 and len(B_vec) == 133
assert np.all((TG_MIN <= Vtgs) & (Vtgs <= TG_MAX)) and np.all((BG_MIN <= Vbgs) & (Vbgs <= BG_MAX))
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP
_nr, _dr = calc_nD(Vtgs, Vbgs, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])
assert np.max(abs(_nr-ns)) < 1e-8 and np.max(abs(_dr)) < 1e-8
print(f'fan grid {len(B_vec)} B x {len(ns)} n; B {B_vec[0]:.2f}->{B_vec[-1]:.2f} T; '
      f'n {ns[0]:.2f}->{ns[-1]:.2f}e12; TG {Vtgs.min():+.4f}..{Vtgs.max():+.4f} V; BG {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V')

sr1.sensitivity(50e-6)  # fixed throughout; 5 kΩ full scale at 10 nA
assert sr1.sensitivity() == 50e-6
I_TRIP = 1e-9
mc = dict(meas_config); mc['Si (V)'] = _Vsi; mc['sample_temperature:'] = _T
mc['comments'] = ('landau-fan-vti electron D=0: run-5 region-A calibration, n +2.4..+3.2e12 (37), '
                  'B 0.70..10 T uniform 1/B (133), Vsi=0, sr1 50uV, tau=0.3s/24dB, fast_delay=2.4s')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('landau-fan')
s.add_comment('electron side; D=0 V/nm; n=+2.4..+3.2e12 cm^-2, 37 paired TG/BG points; '
              'B=0.70..10.0 T, 133 rows uniform 1/B; cal run 5; Vsi=0; sr1 50uV; fast_delay=2.4s')

# Layout: [time, B, Vtg, Vbg, T_sample, I_tg, I_bg, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(magnet.field, sr1.X); s.plot(magnet.field, sr0.X)
s.plot('time', sr1.P); s.plot('time', sr0.P); s.plot('time', T_sample)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    itg, ibg = abs(float(data[5])), abs(float(data[6]))
    if itg > I_TRIP or ibg > I_TRIP:
        print(f'LEAK TRIP B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}, Vbg={float(data[3]):+.3f}: '
              f'|I_tg|={itg:.3e}, |I_bg|={ibg:.3e} A')
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.ramp(k_bg.volt, float(Vbgs[0])); s.ramp(k_tg.volt, float(Vtgs[0]))
magnet.field(float(B_vec[0]))  # blocking 0 -> 0.70 T ramp, includes driver's 3 s settle
print(f'positioned at B={magnet.field():+.4f} T; start fan')
try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=1.0, fast_delay=2.4)
finally:
    s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
    print(f'end/interrupt readback: B={magnet.field():+.4f} T, Vtg={k_tg.volt():+.4f}, Vbg={k_bg.volt():+.4f} V')
