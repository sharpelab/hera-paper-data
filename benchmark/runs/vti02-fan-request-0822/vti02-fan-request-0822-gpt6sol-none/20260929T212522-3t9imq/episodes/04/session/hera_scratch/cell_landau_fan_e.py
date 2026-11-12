# Plan step 4: electron Landau fan on the run-5 D_A=0 calibration, B 2->10 T.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL_FAN = dict(c_tg=2.796e-3, c_bg=2.161e-3, n_offset=-0.0894, D_offset=-0.013)
n_fan = np.round(np.linspace(0.4, 3.2, 71), 5)  # 1e12 cm^-2, ridge A; spacing 0.04
B_fan = np.round(np.linspace(2.0, 10.0, 41), 4)
Vtg_fan, Vbg_fan = calc_gate_voltages(n_fan, np.zeros_like(n_fan), **CAL_FAN)
assert np.all((Vtg_fan >= TG_MIN) & (Vtg_fan <= TG_MAX))
assert np.all((Vbg_fan >= BG_MIN) & (Vbg_fan <= BG_MAX))
assert np.max(np.abs(B_fan)) <= B_SESSION_CAP
assert (TG_MIN, TG_MAX, BG_MIN, BG_MAX, SI_MIN, SI_MAX, B_SESSION_CAP, T_SESSION_CAP) == (-0.3, 1.0, -1.3, 2.0, -25.0, 25.0, 10.0, 100.0), 'SAFETIES constants differ from card'
print(f'fan geometry: {len(B_fan)} B rows {B_fan[0]:.1f}->{B_fan[-1]:.1f} T x {len(n_fan)} density points {n_fan[0]:.2f}->{n_fan[-1]:.2f}e12; gate endpoints TG {Vtg_fan[0]:+.4f}->{Vtg_fan[-1]:+.4f}, BG {Vbg_fan[0]:+.4f}->{Vbg_fan[-1]:+.4f} V')
print('n,D closure:', calc_nD(Vtg_fan[[0,-1]], Vbg_fan[[0,-1]], **CAL_FAN))

# Silent preconditions; all are reads of state this cell does not set.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
T0_fan, Tv0_fan, B0_fan, Si0_fan = T_sample(), T_vaporizer(), magnet.field(), k_si()
print(f'preconditions actual: T_sample={T0_fan:.3f} K (expected 1.0..1.5), T_vaporizer={Tv0_fan:.3f} K (base tracking); B={B0_fan:+.4f} T (expected |B|<0.02); Si={Si0_fan:+.4f} V (expected 0)')
print(f'preconditions actual: heaters sample/vaporizer ranges={heater.sample_range()}/{heater.vaporizer_range()} (expected 0/0); PS={magnet.persistent_switch_on()}, output={magnet.output_enabled()} (expected True/True); TG/BG NPLC={k_tg.nplci()}/{k_bg.nplci()} (expected 1/1)')
print(f'preconditions actual: sr0/sr1 tau={sr0.time_constant()}/{sr1.time_constant()} s, slopes={sr0.filter_slope()}/{sr1.filter_slope()} dB/oct (expected 0.3/0.3 s, 24/24); drive={sr1.amplitude()} V (expected 1)')
print(f'validator readback: TG {k_tg.volt.vals}, BG {k_bg.volt.vals}, Si smart {dc205.smart_voltage.vals}, Si raw {dc205.voltage.vals}, field {magnet.field.vals}, T sample/vap setpoint {heater.sample_setpoint.vals}/{heater.vaporizer_setpoint.vals}')
for param, limits in ((k_tg.volt, (TG_MIN, TG_MAX)), (k_bg.volt, (BG_MIN, BG_MAX)),
                      (dc205.smart_voltage, (SI_MIN, SI_MAX)), (dc205.voltage, (SI_MIN, SI_MAX)),
                      (magnet.field, (-B_SESSION_CAP, B_SESSION_CAP)),
                      (heater.sample_setpoint, (0, T_SESSION_CAP)),
                      (heater.vaporizer_setpoint, (0, T_SESSION_CAP))):
    assert (param.vals._min_value, param.vals._max_value) == limits, f'validator mismatch: {param.full_name}'
assert 1.0 <= T0_fan <= 1.5 and abs(Tv0_fan - T0_fan) < 0.5 and abs(B0_fan) < 0.02 and abs(Si0_fan) < 0.01
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert sr0.time_constant() == 0.3 and sr1.time_constant() == 0.3 and sr0.filter_slope() == 24 and sr1.filter_slope() == 24
assert abs(sr1.amplitude() - 1.0) < 1e-3

I_TRIP_FAN = 1e-9
SENS_FAN = 200e-6  # 20 kOhm nominal resistance full scale at 10 nA
SR0_SENS_FAN = sr0.sensitivity()
sr1.sensitivity(SENS_FAN)
print(f'sr1 sensitivity {sr1.sensitivity()} V; field ramp floor {(B_fan[-1]-B0_fan)/(1/7.3/60)/60:.1f} min')

mc_fan = dict(meas_config)
mc_fan['Si (V)'] = Si0_fan
mc_fan['sample_temperature:'] = T0_fan
mc_fan['comments'] = ('landau-fan electron: region-A D=0 n=+0.4..+3.2e12 (71), B=2..10 T (41), '
                      'run-5 ratio 0.773 and geometry-anchored c_tg, sr1 200 uV, 2.4 s fast dwell')
s = sweep.AsyncStation(mc_fan)
s.add_comment('landau-fan')
s.add_comment('B slow +2..+10 T, 0.2 T/row; co-swept TG/BG fast at D_A=0, n_A +0.4..+3.2e12 cm^-2, 0.04e12/point; '
              'TG +0.1814..+0.9836 V, BG +0.1282..+1.1661 V; Vsi=0; base T; run-5 c_bg/c_tg=0.773, c_tg=2.796 mF/m2 geometry prior; sr1 200 uV; fast_delay 2.4 s')
s.ramp(k_bg.volt, float(Vbg_fan[0])); s.ramp(k_tg.volt, float(Vtg_fan[0]))
interruptible_sleep(10)

# Rows: time, B, TG, BG, T, I_TG, I_BG, sr0_X, sr0_P, sr1_X, sr1_P.
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot('time', T_sample)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)

def fan_guard(station, data):
    B_now = float(data[1])
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    x1, x0 = abs(float(data[9])), abs(float(data[7]))
    if i_tg > I_TRIP_FAN or i_bg > I_TRIP_FAN or x1 > 0.85*SENS_FAN or x0 > 0.85*SR0_SENS_FAN:
        print(f'FAN TRIP B={B_now:+.3f} T, n_A={float(n_fan[np.argmin(abs(Vtg_fan-float(data[2]))) ]):.2f}e12: |I_TG|={i_tg:.3e}, |I_BG|={i_bg:.3e} A, |sr1_X|={x1:.3e}, |sr0_X|={x0:.3e} V')
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

fan_result = s.multimegasweep([magnet.field], [B_fan], [k_tg.volt, k_bg.volt], [Vtg_fan, Vbg_fan], slow_delay=0.0, fast_delay=2.4)
print(f'fan run {fan_result.id}: B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V, Si={k_si():+.4f} V')
