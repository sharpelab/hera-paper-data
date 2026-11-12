# === Plan Step 4: D_A = 0 Landau fan; B slow upward, n_A fast ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL_FAN = dict(c_tg=2.796e-3, c_bg=2.161e-3, n_offset=-0.0894, D_offset=-0.013)
N_vec = np.linspace(-1.10, 3.20, 109)  # 1e12 cm^-2; 0.0398 step
Vtg_vec, Vbg_vec = calc_gate_voltages(N_vec, np.zeros_like(N_vec), **CAL_FAN)
B_vec = np.round(np.r_[np.arange(0.50, 3.001, 0.05), np.arange(3.20, 10.001, 0.20)], 4)
assert len(N_vec) == 109 and len(B_vec) == 86 and B_vec[-1] <= B_SESSION_CAP
assert np.min(Vtg_vec) >= TG_MIN and np.max(Vtg_vec) <= TG_MAX
assert np.min(Vbg_vec) >= BG_MIN and np.max(Vbg_vec) <= BG_MAX
assert np.max(np.abs(calc_nD(Vtg_vec, Vbg_vec, **CAL_FAN)[1])) < 1e-9

# Preconditions: states this cell assumes and does not set.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_T, _Tv, _B, _Si = T_sample(), T_vaporizer(), magnet.field(), k_si()
_switch, _output = magnet.persistent_switch_on(), magnet.output_enabled()
_ranges = (heater.sample_range(), heater.vaporizer_range())
_drive, _tau, _slope = sr1.amplitude(), sr1.time_constant(), sr1.filter_slope()
_nplc = (k_tg.nplci(), k_bg.nplci())
print(f'precondition: T_sample {_T:.3f} K (1.0–1.5), T_vaporizer {_Tv:.3f} K (<1.5), B {_B:+.4f} T (near 0), Si {_Si:+.3f} V (0)')
print(f'precondition: heater ranges {_ranges} (0,0), PS/output {_switch}/{_output} (True/True), drive {_drive:.3f} V (1), sr1 tau/slope {_tau}/{_slope} (0.3 s/24 dB), gate NPLC {_nplc} (1,1)')
assert 1.0 <= _T <= 1.5 and 0.7 <= _Tv <= 1.5 and abs(_B) < 0.05 and abs(_Si) < 0.01
assert _ranges == (0, 0) and _switch and _output
assert abs(_drive - 1.0) < 0.01 and _tau == 0.3 and _slope == 24 and _nplc == (1, 1)

sr1.sensitivity(100e-6)
print(f'grid: {len(B_vec)} B rows {B_vec[0]:.2f}→{B_vec[-1]:.2f} T × {len(N_vec)} n points {N_vec[0]:+.2f}→{N_vec[-1]:+.2f}e12; gate endpoints TG {Vtg_vec[0]:+.4f}→{Vtg_vec[-1]:+.4f} V, BG {Vbg_vec[0]:+.4f}→{Vbg_vec[-1]:+.4f} V; sr1 sensitivity {sr1.sensitivity()} V')

mc = dict(meas_config)
mc['Si (V)'] = _Si
mc['sample_temperature:'] = _T
mc['comments'] = 'landau-fan: D_A=0; n_A -1.10..+3.20e12 cm^-2 109 points; B +0.50..+10.00 T 86 rows; run-5 calibration; sr1 100 uV, fast_delay 1 s'
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment('run-5 A calibration: c_tg=2.796e-3, c_bg=2.161e-3 F/m2, n_offset=-0.0894e12 cm^-2, D_offset=-0.013 V/nm; D_A=0; n_A -1.10..+3.20e12 (109); B +0.50..+10.00 T (86, 0.05 T to 3 T, 0.20 T above); Si=0 V; sr1 sens=100 uV')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# Rows: time, B, Vtg, Vbg, T_sample, I_tg, I_bg, sr0.X, sr1.X.
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr).fp(sr0.X).fp(sr1.X)
s.plot(k_tg.volt, sr1.X)
s.plot(k_tg.volt, sr0.X)
s.plot('time', T_sample)
s.plot('time', k_tg.curr)
s.plot('time', k_bg.curr)

def fan_guard(station, data):
    itg, ibg, vx = abs(float(data[5])), abs(float(data[6])), abs(float(data[8]))
    if itg > 1e-9 or ibg > 1e-9 or vx > 0.90 * 100e-6:
        print(f'FAN TRIP: B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f} V, Vbg={float(data[3]):+.4f} V, |I_tg|={itg:.3e} A, |I_bg|={ibg:.3e} A, |sr1.X|={vx:.3e} V')
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec], slow_delay=0, fast_delay=1.0)
finally:
    s.ramp(k_tg.volt, 0.0)
    s.ramp(k_bg.volt, 0.0)
    print(f'post-fan readback: B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V, T_sample={T_sample():.3f} K')
