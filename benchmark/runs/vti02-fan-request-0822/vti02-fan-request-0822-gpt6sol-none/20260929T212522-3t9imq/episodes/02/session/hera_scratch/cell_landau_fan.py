# Step 4, Landau fan: B slow 0.25 -> 10 T; calibrated D=0 co-swept gates, n_A -1.2 -> +3.2e12 cm^-2.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Preconditions: these are inherited state; print actual and expected before any write.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_T0, _Tv0, _B0 = T_sample(), T_vaporizer(), magnet.field()
_Vsi0, _Vtg0, _Vbg0 = k_si(), k_tg.volt(), k_bg.volt()
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
_tau1, _slope1 = sr1.time_constant(), sr1.filter_slope()
_tau0, _slope0 = sr0.time_constant(), sr0.filter_slope()
print(f'precondition: T_sample={_T0:.3f} K (1.0–1.5), T_vaporizer={_Tv0:.3f} K (0.6–1.5), '
      f'B={_B0:+.4f} T (|B|<0.05), Si={_Vsi0:+.4f} V (0); '
      f'TG/BG={_Vtg0:+.4f}/{_Vbg0:+.4f} V (handoff 0/0), PS={_ps} (True), output={_out} (True)')
print(f'precondition: heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0), '
      f'DC205 range/output {dc205.voltage_range()}/{dc205.output()} (2/1), '
      f'sr0 τ/slope={_tau0}/{_slope0}, sr1 τ/slope={_tau1}/{_slope1} (0.3 s/24 dB), '
      f'gate NPLC={k_tg.nplci()}/{k_bg.nplci()} (1/1), drive={sr1.amplitude()} V (1.0)')
assert 1.0 <= _T0 <= 1.5 and 0.6 <= _Tv0 <= 1.5 and abs(_B0) < 0.05
assert abs(_Vsi0) < 0.01 and _ps and _out
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0
assert dc205.voltage_range() == 2 and dc205.output() == 1
assert _tau0 <= 0.3 and _tau1 <= 0.3 and _slope0 == 24 and _slope1 == 24
assert k_tg.nplci() == 1 and k_bg.nplci() == 1 and abs(sr1.amplitude() - 1.0) < 0.01
assert (TG_MIN, TG_MAX, BG_MIN, BG_MAX, SI_MIN, SI_MAX, B_SESSION_CAP, T_SESSION_CAP) == (-0.3, 1.0, -1.3, 2.0, -25.0, 25.0, 10.0, 100.0)

# Run-5 calibration: ratio measured from ridge A; absolute c_tg remains the geometry prior.
CAL = dict(c_tg=0.0027960593093052633, c_bg=0.002160696465377614,
           n_offset=-0.08937933224099137, D_offset=-0.013)
n_vec = np.linspace(-1.2, +3.2, 111)  # 1e12 cm^-2; 0.04 increments
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec),
                                      CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])
B_vec = np.round(np.arange(0.25, 10.0001, 0.25), 4)
assert len(B_vec) == 40 and len(n_vec) == 111
assert TG_MIN <= np.min(Vtg_vec) and np.max(Vtg_vec) <= TG_MAX
assert BG_MIN <= np.min(Vbg_vec) and np.max(Vbg_vec) <= BG_MAX
assert np.max(np.abs(B_vec)) <= B_SESSION_CAP
_ncheck, _Dcheck = calc_nD(Vtg_vec, Vbg_vec, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])
assert np.max(np.abs(_ncheck - n_vec)) < 1e-6 and np.max(np.abs(_Dcheck)) < 1e-6
print(f'grid: B {B_vec[0]:.2f}->{B_vec[-1]:.2f} T x {len(B_vec)} rows; '
      f'n_A {n_vec[0]:+.2f}->{n_vec[-1]:+.2f}e12 x {len(n_vec)} points at D=0; '
      f'TG {Vtg_vec[0]:+.4f}->{Vtg_vec[-1]:+.4f} V, BG {Vbg_vec[0]:+.4f}->{Vbg_vec[-1]:+.4f} V')

# Fixed sensitivity gives 20 kΩ nominal full scale at 10 nA. Abort on 85% of voltage range.
SR1_SENS = 200e-6
I_TRIP = 1e-9
FAST_DELAY = 2.4  # 8 tau at the recorded 0.3 s/24 dB lock-in setting
sr1.sensitivity(SR1_SENS)
print(f'sr1 sensitivity={sr1.sensitivity():.1e} V, drive={sr1.amplitude():.3f} V '
      f'(~{sr1.amplitude()/100e6*1e9:.1f} nA), fast delay={FAST_DELAY:.1f} s')

mc = dict(meas_config)
mc['Si (V)'] = _Vsi0
mc['sample_temperature:'] = _T0
mc['comments'] = ('landau-fan: run-5 calibrated D=0; n_A=-1.2..+3.2e12 (111, 0.04 step), '
                  'B=0.25..10 T (40, 0.25 step), sr1 200uV, 2.4s fast delay, Si=0')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment('B slow +0.25 to +10.00 T in 0.25 T steps (40 rows); (TG,BG) fast co-sweep '
              'on run-5 ridge-A D=0 line, n_A=-1.20 to +3.20 x10^12 cm^-2 in 0.04 steps (111 pts); '
              'Si=0 V; c_bg/c_tg=0.772765, n_offset=-0.089379 x10^12, D_offset=-0.013 V/nm; '
              'sr1 sensitivity=200 uV, fast delay=2.4 s; hardwired B_1-B_2 Rxx')

# Row layout: time, B, Vtg, Vbg, T, I_tg, I_bg, sr0.X, sr0.P, sr1.X, sr1.P.
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, T_sample)
s.plot(k_tg.volt, k_tg.curr); s.plot(k_bg.volt, k_bg.curr)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)

def fan_guard(station, data):
    i_tg, i_bg, vxx = abs(float(data[5])), abs(float(data[6])), abs(float(data[9]))
    if i_tg > I_TRIP or i_bg > I_TRIP or vxx > 0.85 * SR1_SENS:
        print(f'FAN TRIP: B={float(data[1]):.2f} T, TG={float(data[2]):+.4f} V, BG={float(data[3]):+.4f} V, '
              f'|I_tg/bg|={i_tg*1e12:.0f}/{i_bg*1e12:.0f} pA, |Vxx|/range={vxx/SR1_SENS:.3f}')
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

# Magnet starts at the handoff field and rises once. Its set blocks at 0.137 T/min plus 3 s settle.
# On a trip, the sweep finishes the current point and parks gates; the magnet holds at its actual field.
try:
    s.ramp(k_bg.volt, float(Vbg_vec[0])); s.ramp(k_tg.volt, float(Vtg_vec[0]))
    interruptible_sleep(10)
    result = s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt],
                              [Vtg_vec, Vbg_vec], slow_delay=0, fast_delay=FAST_DELAY)
    print(f'fan result: data/{result.id}, interrupted={result.metadata.get("interrupted")}')
finally:
    s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
    print(f'after fan: B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, '
          f'BG={k_bg.volt():+.4f} V, Si={k_si():+.4f} V, T_sample={T_sample():.3f} K')
