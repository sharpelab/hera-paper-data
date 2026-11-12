# Plan step 5 — electron Landau fan; run-5 A-region calibration, D=0.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Preconditions: these are assumed rather than set by the sweep.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
T0, Tv0, B0, Vsi0 = T_sample(), T_vaporizer(), magnet.field(), k_si()
print(f'precondition T_sample={T0:.3f} K (1.0–1.5), T_vaporizer={Tv0:.3f} K (0.7–1.5), B={B0:+.4f} T (|B|<0.05), Si={Vsi0:+.4f} V (0)')
print(f'precondition PS={magnet.persistent_switch_on()}, output={magnet.output_enabled()}, heaters={heater.sample_range()}/{heater.vaporizer_range()} (0/0), NPLC TG/BG={k_tg.nplci()}/{k_bg.nplci()} (1/1)')
print(f'precondition gates TG/BG={k_tg.volt():+.4f}/{k_bg.volt():+.4f} V (cell sets both); drive={sr1.amplitude():.4f} V @ {sr1.frequency():.3f} Hz; tau/slope={sr1.time_constant()}/{sr1.filter_slope()}')
assert 1.0 <= T0 <= 1.5 and 0.7 <= Tv0 <= 1.5
assert abs(B0) < 0.05 and abs(Vsi0) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert abs(sr1.amplitude()-1.0) < 0.05 and abs(sr1.frequency()-13.777) < 0.1
assert sr1.time_constant() == 0.3 and sr1.filter_slope() == 24

CAL = dict(c_tg=2.7960593093052633e-3, c_bg=2.160696465377614e-3,
           n_offset=-0.08937933224099137, D_offset=-0.013)
n_vec = np.linspace(0.6, 3.2, 41)  # 1e12 cm^-2 on A-region calibration
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), **CAL)
B_vec = np.round(np.linspace(2.0, 10.0, 41), 6)
assert np.all((Vtg_vec >= TG_MIN) & (Vtg_vec <= TG_MAX))
assert np.all((Vbg_vec >= BG_MIN) & (Vbg_vec <= BG_MAX))
assert np.all(np.abs(B_vec) <= B_SESSION_CAP) and B_SESSION_CAP == 10.0
back_n, back_D = calc_nD(Vtg_vec, Vbg_vec, **CAL)
assert np.max(np.abs(back_n-n_vec)) < 1e-8 and np.max(np.abs(back_D)) < 1e-8
print(f'fan grid: B {B_vec[0]:.1f}→{B_vec[-1]:.1f} T, {len(B_vec)} rows; n {n_vec[0]:.3f}→{n_vec[-1]:.3f}e12, {len(n_vec)} points/row; TG {Vtg_vec[0]:+.4f}→{Vtg_vec[-1]:+.4f} V, BG {Vbg_vec[0]:+.4f}→{Vbg_vec[-1]:+.4f} V')

sr1.sensitivity(100e-6)
print(f'sr1 sensitivity={sr1.sensitivity()} V (10 kΩ nominal FS), sr0 sensitivity={sr0.sensitivity()} V')
mc = dict(meas_config)
mc['Si (V)'] = Vsi0
mc['sample_temperature:'] = T0
mc['comments'] = ('landau-fan electron: A n=+0.6..+3.2e12 cm^-2, D=0, 41 density points; '
                  'B=2..10 T 41 rows/0.2 T; Si=0; run-5 CNP/D calibration; sr1 100 uV')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment('electron A-region D=0; B slow 2.0→10.0 T, 41 rows/0.2 T; n fast +0.6→+3.2e12 cm^-2, 41 pts/0.065e12; TG/BG co-swept; Si=0; run-5 calibration; fast_delay=2.5 s; sr1 sens=100 µV')
s.ramp(k_tg.volt, float(Vtg_vec[0]))
s.ramp(k_bg.volt, float(Vbg_vec[0]))
interruptible_sleep(10)

# Row: time, B, TG set, BG set, T_sample, I_TG, I_BG, sr0.X/P, sr1.X/P.
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot('time', T_sample)
s.plot('time', k_tg.curr)
s.plot('time', k_bg.curr)
s.plot(k_tg.volt, sr0.X)
s.plot('time', sr0.P)
s.plot(k_tg.volt, sr1.X)
s.plot('time', sr1.P)

I_TRIP = 1e-9
def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f'LEAK TRIP B={float(data[1]):.3f} T, TG={float(data[2]):+.4f}, BG={float(data[3]):+.4f} V; |I_TG|={i_tg:.3e}, |I_BG|={i_bg:.3e} A')
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    result = s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt],
                             [Vtg_vec, Vbg_vec], slow_delay=0, fast_delay=2.5)
    print(f'fan run data/{result.id}; interrupted={result.metadata.get("interrupted")}')
finally:
    s.ramp(k_tg.volt, 0.0)
    s.ramp(k_bg.volt, 0.0)
    print(f'after fan: measured B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V, Si={k_si():+.4f} V, T_sample={T_sample():.3f} K')
