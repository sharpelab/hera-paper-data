# Step 4, landau-fan: field-slow, fixed-D co-swept gate line, both carrier signs.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Preconditions: inherited state that this cell does not set.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_T, _Tv, _B, _Si = T_sample(), T_vaporizer(), magnet.field(), k_si()
_PS, _out = magnet.persistent_switch_on(), magnet.output_enabled()
_drive, _tau, _slope = sr1.amplitude(), sr1.time_constant(), sr1.filter_slope()
print(f'preconditions: T_sample={_T:.3f} K (1.0..1.5), T_vaporizer={_Tv:.3f} K (<1.6), '
      f'B={_B:+.4f} T (near 0), Si={_Si:+.4f} V (0), PS={_PS}, output={_out}, '
      f'drive={_drive:.3f} V (1), sr1 tau={_tau:.3f} s (<=0.3), slope={_slope} dB/oct (24)')
assert 1.0 <= _T <= 1.5 and _Tv < 1.6 and abs(_B) < 0.05 and abs(_Si) < 0.01
assert _PS and _out and abs(_drive - 1.0) < 0.01 and _tau <= 0.3 and _slope == 24
assert B_SESSION_CAP == 10.0 and (TG_MIN,TG_MAX,BG_MIN,BG_MAX) == (-0.3,1.0,-1.3,2.0)

# Data/5 calibration: ratio and CNP offsets measured, absolute capacitance anchored to geometry.
_cal = dict(c_tg=0.0027960593093052633, c_bg=0.002160696465377614,
            n_offset=-0.08937933224099137, D_offset=-0.013)
_n = np.linspace(-1.0, 3.2, 85)  # 1e12 cm^-2, 0.05 spacing
_D = np.zeros_like(_n)
_Vtg, _Vbg = calc_gate_voltages(_n, _D, **_cal)
_Bvec = np.round(np.arange(1.0, 10.0001, 0.2), 4)  # 46 rows, increasing from parked zero
assert len(_Bvec) == 46 and _Bvec[-1] <= B_SESSION_CAP
assert np.all((_Vtg >= TG_MIN) & (_Vtg <= TG_MAX) & (_Vbg >= BG_MIN) & (_Vbg <= BG_MAX))
_n_back, _D_back = calc_nD(_Vtg, _Vbg, **_cal)
assert np.max(np.abs(_n_back-_n)) < 1e-8 and np.max(np.abs(_D_back)) < 1e-8
print(f'fan: B {_Bvec[0]:.1f}..{_Bvec[-1]:.1f} T, {len(_Bvec)} rows; '
      f'n {_n[0]:+.2f}..{_n[-1]:+.2f}e12, {len(_n)} points; '
      f'Vtg {_Vtg.min():+.4f}..{_Vtg.max():+.4f} V, Vbg {_Vbg.min():+.4f}..{_Vbg.max():+.4f} V')

# 500 uV gives 50 kOhm nominal Rxx full scale at 10 nA; spot maxima were <0.6 kOhm,
# but the unknown high-field CNP resistance sizes headroom. Point dwell is 8 tau.
sr1.sensitivity(500e-6)
print(f'sr1 sensitivity={sr1.sensitivity():.6g} V, fast delay=2.4 s, magnet settle={magnet.settle_s} s')
_mc = dict(meas_config)
_mc['Si (V)'] = _Si
_mc['sample_temperature:'] = _T
_mc['comments'] = ('landau-fan D~0 both signs; data/5 calibrated ratio 0.772765; '
                   'n -1.0..+3.2e12 in 0.05e12, B 1..10 T in 0.2 T, 500 uV sr1, '
                   'fast_delay 2.4 s, Si 0')
s = sweep.AsyncStation(_mc)
s.add_comment('landau-fan')
s.add_comment('B slow 1.0..10.0 T by 0.2; density fast -1.0..+3.2e12 cm^-2 by 0.05 '
              'at D=0 (data/5 calibration, c_tg geometry prior); TG/BG co-swept, Si=0; '
              'B_1-B_2, T_0 source/B_3 drain, base T; sr1 500 uV, fast_delay 2.4 s')
s.ramp(k_bg.volt, float(_Vbg[0]))
s.ramp(k_tg.volt, float(_Vtg[0]))
interruptible_sleep(8)
_Itg, _Ibg = k_tg.curr(), k_bg.curr()
print(f'after initial gate ramp: Vtg={k_tg.volt():+.4f} V, Vbg={k_bg.volt():+.4f} V; '
      f'I_tg={_Itg*1e12:+.1f} pA, I_bg={_Ibg*1e12:+.1f} pA (trip 1000 pA)')
assert abs(_Itg) < 1e-9 and abs(_Ibg) < 1e-9

# Layout: time, B set, Vtg set, Vbg set, T_sample, B read, I_tg, I_bg,
# sr0.X, sr0.P, sr1.X, sr1.P. The duplicate B name is intentional; first is
# the setpoint axis, second is the independent measured readback.
s.fp(T_sample).fp(magnet.field).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X)
s.plot(k_tg.volt, sr0.X)
s.plot('time', T_sample)
s.plot('time', magnet.field)
s.plot('time', k_tg.curr)
s.plot('time', k_bg.curr)
s.plot('time', sr0.P)
s.plot('time', sr1.P)

def fan_guard(station, data):
    B_set, B_read = float(data[1]), float(data[5])
    i_tg, i_bg = abs(float(data[6])), abs(float(data[7]))
    i_drain = abs(float(data[8]) / -1e6)
    v_xx = abs(float(data[10]))
    if i_tg > 1e-9 or i_bg > 1e-9 or abs(B_read-B_set) > 0.05 or i_drain < 2e-9 or v_xx > 0.95*500e-6:
        print(f'FAN TRIP: B set/read={B_set:.3f}/{B_read:.3f} T, '
              f'I_tg/bg={i_tg*1e12:.0f}/{i_bg*1e12:.0f} pA, '
              f'I_drain={i_drain*1e9:.2f} nA, |Vxx|={v_xx*1e6:.1f} uV')
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

s.multimegasweep([magnet.field], [_Bvec], [k_tg.volt, k_bg.volt], [_Vtg, _Vbg],
                 slow_delay=0, fast_delay=2.4)
print(f'fan end: B={magnet.field():+.4f} T, Vtg={k_tg.volt():+.4f} V, '
      f'Vbg={k_bg.volt():+.4f} V, T_sample={T_sample():.3f} K')
