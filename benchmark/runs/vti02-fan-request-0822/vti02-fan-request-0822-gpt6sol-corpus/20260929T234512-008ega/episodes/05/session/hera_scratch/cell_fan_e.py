# === Electron D=0 Landau fan (`landau-fan-vti`), run-5 region-A calibration ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
CAL = dict(c_tg=2.7960593093052633e-3, c_bg=2.160696465377614e-3,
           n_offset=-0.08937933224099137, D_offset=-0.013)

# State the cell inherits but does not set.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
_T0, _B0, _Si = T_sample(), magnet.field(), k_si()
_tau, _slope = sr1.time_constant(), sr1.filter_slope()
print(f'precondition: T_sample={_T0:.3f} K (1.0..1.5), B={_B0:+.4f} T (near 0), '
      f'Si={_Si:+.3f} V (0), PS={magnet.persistent_switch_on()}, output={magnet.output_enabled()}, '
      f'sr1 tau/slope={_tau}s/{_slope}dB (0.3/24), gate NPLC={k_tg.nplci()}/{k_bg.nplci()} (1/1)')
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(_Si) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert abs(_tau - 0.3) < 1e-6 and _slope == 24
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert sr1.amplitude() == 1.0 and sr0.sensitivity() == 0.02

ns = np.linspace(3.2, 2.4, 22)  # 1e12 cm^-2; descending fast axis, fixed D
Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, **CAL)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX
n_back, D_back = calc_nD(Vtgs, Vbgs, **CAL)
assert np.max(np.abs(n_back-ns)) < 1e-9 and np.max(np.abs(D_back)) < 1e-9
B_vec = field_invB(0.8, 10.0, 116)
assert np.all(np.diff(B_vec)>0) and B_vec.max() <= B_SESSION_CAP
assert np.max(np.abs(np.diff(1/B_vec))) <= 1/(3*33.1)
I_TRIP = 1e-9
sr1.sensitivity(50e-6)  # 5 kΩ full scale at 10 nA; run 6 peaked at 530 Ω
print(f'fan grid: {len(B_vec)} B rows {B_vec[0]:.3f}->{B_vec[-1]:.3f} T, '
      f'{len(ns)} n pts {ns[0]:.2f}->{ns[-1]:.2f}e12, D=0; '
      f'Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f}, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f}; '
      f'sr1 sens={sr1.sensitivity()} V, drive={sr1.amplitude()} V')

mc = dict(meas_config); mc['Si (V)'] = _Si; mc['sample_temperature:'] = _T0
mc['comments'] = ('landau-fan-vti electron region A: run-5 cal, n +3.2..+2.4e12 cm^-2, '
                  'D=0 V/nm, B 0.8..10 T uniform-1/B 116 rows, 22 n pts, fast_delay 2.1s, sr1 50uV')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('electron region A; n +3.2 to +2.4e12 cm^-2, D=0 V/nm; '
              'B +0.8 to +10 T uniform-1/B 116 rows; 22 n pts; cal run 5; '
              'Vtg +0.754..+0.984 V, Vbg +0.870..+1.166 V; Si 0 V; fast_delay 2.1 s')
# Set the gates, then position from measured ~0 T to the first B row.
s.ramp(k_bg.volt, float(Vbgs[0])); s.ramp(k_tg.volt, float(Vtgs[0]))
interruptible_sleep(10)
s.ramp(magnet.field, float(B_vec[0]))  # blocking 0 -> 0.8 T ≈ 6 min, 3 s settle

# Multimegasweep row: time, B, Vtg, Vbg, T, Itg, Ibg, sr0.X/P, sr1.X/P.
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', sr1.P); s.plot('time', sr0.P)
s.plot('time', T_sample); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f'LEAK TRIP: B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f} V, '
              f'Vbg={float(data[3]):+.4f} V, |Itg|={i_tg:.3e} A, |Ibg|={i_bg:.3e} A')
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())
s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=0, fast_delay=2.1)
print(f'done: B={magnet.field():+.3f} T, Vtg={k_tg.volt():+.4f} V, Vbg={k_bg.volt():+.4f} V')
