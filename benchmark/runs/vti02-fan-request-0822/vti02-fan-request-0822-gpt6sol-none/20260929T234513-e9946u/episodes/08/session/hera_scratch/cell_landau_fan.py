# Step 4: D=0 Landau fan, calibrated from run 5, B slow and density fast.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Silent preconditions: this cell sets B and TG/BG, but assumes base T, Si=0,
# live thermometry, drive/settling, and enabled magnet output.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_Ts, _Tv, _B0, _Si = T_sample(), T_vaporizer(), magnet.field(), k_si()
_hr = (heater.sample_range(), heater.vaporizer_range())
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
_drive, _tau, _slope = sr1.amplitude(), sr1.time_constant(), sr1.filter_slope()
_tau0, _slope0 = sr0.time_constant(), sr0.filter_slope()
_nplc = (k_tg.nplci(), k_bg.nplci())
print(f'precondition: T_sample {_Ts:.3f} K (1.0..1.5), T_vaporizer {_Tv:.3f} K (0.7..1.5), '
      f'B {_B0:+.4f} T (|B|<0.05), Si {_Si:+.4f} V (0), heater ranges {_hr} (0,0), '
      f'PS heater {_ps}, output {_out}')
print(f'precondition: drive {_drive:.3f} V (1.0), sr1 tau/slope {_tau}/{_slope} (0.3/24), '
      f'sr0 tau/slope {_tau0}/{_slope0} (0.3/24), TG/BG NPLC {_nplc} (1,1)')
assert 1.0 <= _Ts <= 1.5 and 0.7 <= _Tv <= 1.5
assert abs(_B0) < 0.05 and abs(_Si) < 0.01 and _hr == (0, 0)
assert _ps and _out
assert abs(_drive - 1.0) < 0.01 and _tau == _tau0 == 0.3 and _slope == _slope0 == 24
assert _nplc == (1.0, 1.0)

# c_bg/c_tg, n_offset and D_offset from run 5. Absolute c_tg is geometry-prior anchored.
CAL = dict(c_tg=2.7960593093052633e-3, c_bg=2.160696465377614e-3,
           n_offset=-0.08937933224099137, D_offset=-0.013)
n_vec = np.linspace(-1.2, +3.2, 81)   # 10^12 cm^-2, 0.055 step
D_vec = np.zeros_like(n_vec)
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, D_vec, **CAL)
B_vec = np.r_[0.0, 0.5, 1.0, np.arange(1.5, 10.0001, 0.2), 10.0]
assert np.all(np.diff(B_vec) > 0) and B_vec[-1] <= B_SESSION_CAP
assert np.all((Vtg_vec >= TG_MIN) & (Vtg_vec <= TG_MAX))
assert np.all((Vbg_vec >= BG_MIN) & (Vbg_vec <= BG_MAX))
_nback, _Dback = calc_nD(Vtg_vec, Vbg_vec, **CAL)
assert np.max(np.abs(_nback - n_vec)) < 1e-8 and np.max(np.abs(_Dback)) < 1e-8
print(f'grid: B {len(B_vec)} rows {_B0:+.3f} -> {B_vec[-1]:.1f} T; '
      f'n {len(n_vec)} pts {n_vec[0]:+.3f}..{n_vec[-1]:+.3f}e12, D=0; '
      f'TG {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f} V, '
      f'BG {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f} V; {len(B_vec)*len(n_vec)} points')

FAST_DELAY, SLOW_DELAY = 2.5, 0.0
I_TRIP, V_RAIL, I_MIN = 1e-9, 0.9e-3, 1e-9
sr1.sensitivity(1e-3)
print(f'sr1 sensitivity {sr1.sensitivity():.4g} V (100 kOhm nominal at 10 nA); '
      f'fast delay {FAST_DELAY} s, B driver settle {magnet.settle_s} s')

mc = dict(meas_config)
mc['Si (V)'] = _Si
mc['sample_temperature:'] = _Ts
mc['comments'] = ('landau-fan: run-5 calibrated D=0; n -1.2..+3.2e12 (81, step 0.055); '
                  'B 0..10 T (47 rows, 0.2 T above 1.5); sr1 sens 1 mV; 2.5 s fast delay')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment('region A calibration run 5: c_tg=2.796059e-3 F/m2 (geometry anchor), '
              'c_bg/c_tg=0.772765, n_offset=-0.089379e12 cm^-2, D_offset=-0.013 V/nm; '
              'D=0, n=-1.2..+3.2e12 cm^-2, 81 fast points; B=0..10 T, 47 slow rows; '
              'T base, Si=0 V, sr1 sensitivity 1 mV, fast_delay=2.5 s')

# Set the first fast-axis point before recording; these are ordinary in-box gate ramps.
s.ramp(k_bg.volt, float(Vbg_vec[0]))
s.ramp(k_tg.volt, float(Vtg_vec[0]))
interruptible_sleep(10)

# Row: time, B, Vtg, Vbg, T, Itg, Ibg, sr0 X/P, sr1 X/P.
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X)
s.plot('time', T_sample)
s.plot('time', k_tg.curr)
s.plot('time', k_bg.curr)
s.plot('time', sr0.X)
s.plot('time', sr0.P)
s.plot('time', sr1.P)

def fan_guard(station, data):
    itg, ibg = abs(float(data[5])), abs(float(data[6]))
    vxx, idrain = abs(float(data[9])), abs(float(data[7]) / -1e6)
    if itg > I_TRIP or ibg > I_TRIP or vxx > V_RAIL or idrain < I_MIN:
        print(f'FAN STOP at B={float(data[1]):+.3f} T, n≈{calc_nD(float(data[2]), float(data[3]), **CAL)[0]:+.3f}e12: '
              f'|Itg|={itg:.3e} A, |Ibg|={ibg:.3e} A, |Vxx|={vxx:.3e} V, |I|={idrain:.3e} A')
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt],
                     [Vtg_vec, Vbg_vec], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # Avoid holding the device near the TG limit while the fan is analyzed.
    s.ramp(k_tg.volt, 0.0)
    s.ramp(k_bg.volt, 0.0)
    print(f'post-run readback: B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, '
          f'BG={k_bg.volt():+.4f} V, Si={k_si():+.4f} V, T_sample={T_sample():.3f} K')
