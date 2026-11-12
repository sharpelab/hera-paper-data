# D=0 Landau fan, region-A density coordinate (calibration from data/5).
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Preconditions: state assumed by this cell, read before any write.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
_T0, _Tv0, _B0, _Si0 = T_sample(), T_vaporizer(), magnet.field(), k_si()
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
_nplc_tg, _nplc_bg = k_tg.nplci(), k_bg.nplci()
print(f'precondition T_sample {_T0:.3f} K, T_vaporizer {_Tv0:.3f} K (both 1.0–1.5), '
      f'B {_B0:+.4f} T (|B|<0.05), Si {_Si0:+.3f} V (0); '
      f'PS heater {_ps} (on), output {_out} (on), TG/BG NPLC {_nplc_tg}/{_nplc_bg} (1/1)')
assert 1.0 <= _T0 <= 1.5 and 1.0 <= _Tv0 <= 1.5 and abs(_B0) < .05 and abs(_Si0) < .01
assert _ps and _out and _nplc_tg == 1 and _nplc_bg == 1

CAL_FAN = dict(c_tg=2.7960593093052633e-3, c_bg=2.160696465377614e-3,
               n_offset=-0.08937933224099137, D_offset=-0.013)
n_vec = np.linspace(-1.1, 3.2, 173)     # 1e12 cm^-2, region A; 0.025 increments
D_vec = np.zeros_like(n_vec)            # V/nm, region A
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, D_vec, **CAL_FAN)
B_vec = np.r_[np.arange(.5, 6.01, .5), np.arange(7., 10.01, 1.)]
assert len(B_vec) == 16 and B_vec.max() <= B_SESSION_CAP
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX
assert np.allclose(calc_nD(Vtg_vec, Vbg_vec, **CAL_FAN)[0], n_vec)
print(f'fan: {len(B_vec)} B rows {B_vec[0]}->{B_vec[-1]} T x {len(n_vec)} density points '
      f'{n_vec[0]:+.2f}->{n_vec[-1]:+.2f}e12 at D_A=0; '
      f'TG {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} V, BG {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V')

_tau, _slope = sr1.time_constant(), sr1.filter_slope()
print(f'sr1 settling: tau {_tau} s, slope {_slope}; fast dwell 2.1 s; drive {sr1.amplitude()} V')
assert _tau <= .3, 'sr1 time constant grew; reprice dwell before measuring'
sr1.sensitivity(100e-6)
_sens = sr1.sensitivity()
assert abs(_sens - 100e-6) < 1e-9
I_TRIP, I_MIN = 1e-9, 5e-9
mc = dict(meas_config)
mc['Si (V)'] = _Si0; mc['sample_temperature:'] = _T0
mc['comments'] = ('landau-fan: D_A=0, n_A -1.10..+3.20e12 (173, 0.025e12), '
                  'B 0.5..10 T (16 rows), region B CNP n_A~-0.43e12; run-5 calibration; sr1 100 uV')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment('D_A=0 V/nm; n_A=-1.10..+3.20e12 cm^-2, 173 points/row (0.025e12); '
              'B=0.5..6 T by 0.5 T, 7..10 T by 1 T (16 rows); Vsi=0; '
              'calibration data/5: c_bg/c_tg=0.773, n_offset=-0.089e12, D_offset=-0.013 V/nm; '
              'fixed sr1 sensitivity 100 uV, fast_delay 2.1 s')

# Park at the first density point before the first B row; the magnet itself is the slow axis.
s.ramp(k_bg.volt, float(Vbg_vec[0])); s.ramp(k_tg.volt, float(Vtg_vec[0]))
interruptible_sleep(10)

# Row layout: time, B, Vtg, Vbg, T, I_tg, I_bg, sr0_X/P, sr1_X/P.
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot('time', T_sample)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)

def fan_guard(station, data):
    B, nt = float(data[1]), float(data[2])
    itg, ibg, xcur, xr = abs(float(data[5])), abs(float(data[6])), abs(float(data[7])), abs(float(data[9]))
    if itg > I_TRIP or ibg > I_TRIP or xr >= .9 * _sens or xcur / 1e6 < I_MIN:
        print(f'FAN TRIP B={B:.3f} T Vtg={nt:+.4f} V: I_tg={itg:.2e} A I_bg={ibg:.2e} A '
              f'sr1_X={xr:.2e} V / sens={_sens:.2e} V, I_drain={xcur/1e6:.2e} A')
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt],
                     [Vtg_vec, Vbg_vec], slow_delay=0, fast_delay=2.1)
finally:
    s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
    print(f'post-run readback: B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, '
          f'BG={k_bg.volt():+.4f} V, Si={k_si():+.3f} V, T={T_sample():.3f} K')
