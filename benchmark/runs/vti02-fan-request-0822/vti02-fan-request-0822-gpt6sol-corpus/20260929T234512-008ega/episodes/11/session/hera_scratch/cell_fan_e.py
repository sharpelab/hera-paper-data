# D = 0 electron Landau fan, first-session tetralayer FS-count arc.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
ns = np.linspace(3.2, 2.7, 17)       # 1e12 cm^-2; n step 0.03125
Ds = np.zeros_like(ns)                # V/nm, D = 0
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])
B_vec = 1 / np.linspace(1/1.0, 1/10.0, 91)  # uniform 1/B, 1 -> 10 T
assert np.all((TG_MIN <= Vtgs) & (Vtgs <= TG_MAX))
assert np.all((BG_MIN <= Vbgs) & (Vbgs <= BG_MAX))
assert B_vec.max() <= B_SESSION_CAP
assert np.allclose(calc_nD(Vtgs, Vbgs, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])[0], ns)
print(f'fan geometry: {len(B_vec)} B rows × {len(ns)} n points; B {B_vec[0]:.3f}->{B_vec[-1]:.3f} T, '
      f'n {ns[0]:.3f}->{ns[-1]:.3f}e12, D=0; Vtg {Vtgs[0]:+.4f}->{Vtgs[-1]:+.4f}, '
      f'Vbg {Vbgs[0]:+.4f}->{Vbgs[-1]:+.4f} V')

# Silent preconditions: this cell does not set T, Si, or PS/output state.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
_T0, _B0, _Si0 = T_sample(), magnet.field(), k_si()
_PS0, _out0 = magnet.persistent_switch_on(), magnet.output_enabled()
print(f'preconditions: T_sample {_T0:.3f} K [1.0,1.5], B {_B0:+.4f} T [|B|<0.05], '
      f'Si {_Si0:+.3f} V [|V|<0.01], PS heater {_PS0}, output {_out0}')
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(_Si0) < 0.01
assert _PS0 and _out0
assert TG_MIN == -0.3 and TG_MAX == 1.0 and BG_MIN == -1.3 and BG_MAX == 2.0
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0
assert abs(sr1.amplitude() - 1.0) < 0.01  # 10 nA nominal current bias
assert abs(sr1.time_constant() - 0.3) < 1e-6 and sr1.filter_slope() == 24

sr1.sensitivity(50e-6)  # fixed for the whole fan; 5 kOhm full scale at 10 nA
magnet.field(float(B_vec[0]))  # blocking position from 0 T; driver includes 3 s settle
s = sweep.AsyncStation(dict(meas_config, **{'Si (V)': _Si0, 'sample_temperature:': _T0,
    'comments': 'landau-fan-vti electron D=0, n +3.2 to +2.7e12, B 1 to 10 T uniform 1/B 91x17, run-5 calibration, sr1 50uV'}))
s.add_comment('landau-fan-vti')
s.add_comment('electron B1-B2 Rxx; n=+3.2 to +2.7e12 cm^-2, D=0 V/nm; '
              'B=1 to 10 T uniform 1/B (91 rows), 17 paired gate points; '
              'run-5 cal c_tg=2.796e-3, c_bg=2.161e-3, n_offset=-0.0894, D_offset=-0.013; '
              'sr1=50uV fixed, tau=0.3s/24dB, fast_delay=1.8s')
s.ramp(k_bg.volt, float(Vbgs[0])); s.ramp(k_tg.volt, float(Vtgs[0]))
interruptible_sleep(10)

# Row layout: time, B, Vtg, Vbg, T_sample, I_tg, I_bg, sr0.X/P, sr1.X/P.
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot('time', T_sample)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot(magnet.field, sr0.X); s.plot(magnet.field, sr0.P)
s.plot(magnet.field, sr1.X); s.plot(magnet.field, sr1.P)

def fan_leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > 1e-9 or i_bg > 1e-9:
        print(f'LEAK TRIP B={float(data[1]):.3f} T, n-row Vtg={float(data[2]):+.4f}, '
              f'Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A')
        station.interrupt_requested = True
s.register_run_after(fan_leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=1.0, fast_delay=1.8)
print(f'fan done: B={magnet.field():+.3f} T, gates=({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V')
