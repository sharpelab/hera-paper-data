# D = 0 electron fan for FS count: run-5 calibration; run-6 onset and tones.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL_FAN = dict(c_tg=2.796e-3, c_bg=2.161e-3, n_offset=-0.0894, D_offset=-0.013)
n_fan = np.linspace(2.5, 3.2, 27)  # 1e12 cm^-2, region A
D_fan = np.zeros_like(n_fan)
Vtg_fan, Vbg_fan = calc_gate_voltages(n_fan, D_fan, **CAL_FAN)
B_fan = 1.0 / np.linspace(1/0.9, 1/8.0, 100)  # uniform in 1/B, ascending B

# Session caps and whole-grid validators: all failures happen before movement.
assert (TG_MIN, TG_MAX, BG_MIN, BG_MAX, SI_MIN, SI_MAX, B_SESSION_CAP, T_SESSION_CAP) == (-0.3, 1.0, -1.3, 2.0, -25.0, 25.0, 10.0, 100.0)
assert np.all((Vtg_fan >= TG_MIN) & (Vtg_fan <= TG_MAX))
assert np.all((Vbg_fan >= BG_MIN) & (Vbg_fan <= BG_MAX))
assert np.all(np.abs(B_fan) <= B_SESSION_CAP)
for p, values in ((k_tg.volt, Vtg_fan), (k_bg.volt, Vbg_fan), (magnet.field, B_fan)):
    p.vals.validate(float(values.min()))
    p.vals.validate(float(values.max()))
_ncheck, _Dcheck = calc_nD(Vtg_fan, Vbg_fan, **CAL_FAN)
assert np.max(np.abs(_ncheck - n_fan)) < 1e-3 and np.max(np.abs(_Dcheck)) < 1e-3

# Silent preconditions: state inherited from the handoff/state0, not set by this cell.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_T, _Tv, _B, _Si = T_sample(), T_vaporizer(), magnet.field(), k_si()
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
_tau, _slope, _drive = sr1.time_constant(), sr1.filter_slope(), sr1.amplitude()
print(f'precondition T_sample={_T:.3f} K (1.0..1.5), T_vaporizer={_Tv:.3f} K (0.8..1.6), '
      f'B={_B:+.4f} T (|B|<0.05), Si={_Si:+.3f} V (0), PS={_ps}, output={_out}; '
      f'sr1 tau={_tau} s (0.3), slope={_slope} dB (24), drive={_drive:.3f} V (~1)')
assert 1.0 <= _T <= 1.5 and 0.8 <= _Tv <= 1.6
assert abs(_B) < 0.05 and abs(_Si) < 0.01 and _ps and _out
assert abs(_tau - 0.3) < 0.03 and _slope == 24 and 0.9 <= _drive <= 1.1
print(f'fan grid: {len(B_fan)} B x {len(n_fan)} n; B {B_fan[0]:.3f}..{B_fan[-1]:.3f} T, '
      f'n {n_fan[0]:.3f}..{n_fan[-1]:.3f}e12, '
      f'TG {Vtg_fan.min():+.4f}..{Vtg_fan.max():+.4f} V, BG {Vbg_fan.min():+.4f}..{Vbg_fan.max():+.4f} V')

sr1.sensitivity(50e-6)  # 5 kOhm full scale at ~10 nA
mc = dict(meas_config)
mc['Si (V)'] = _Si
mc['sample_temperature:'] = _T
mc['comments'] = 'landau-fan-vti electron: region A, run-5 D=0 calibration; n +2.5..+3.2e12, B 0.9..8 T, 100x27 uniform-1/B, fast_delay 2.7 s, sr1 50 uV'
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('region A electron, D=0 V/nm, n=+2.5..+3.2e12 cm^-2, B=0.9..8.0 T ascending uniform-1/B 100 rows x 27 n; run-5 c_bg/c_tg=0.773, n_offset=-0.0894e12, D_offset=-0.013 V/nm; sr1 50 uV, tau 0.3 s, 24 dB, fast_delay 2.7 s')

# Move gates at base field, then position magnet (blocking ~7 min). No separate settle sleep.
s.ramp(k_bg.volt, float(Vbg_fan[0]))
s.ramp(k_tg.volt, float(Vtg_fan[0]))
interruptible_sleep(10)
s.ramp(magnet.field, float(B_fan[0]))

# [time, B, Vtg, Vbg, T, I_tg, I_bg, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot('time', T_sample)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot(magnet.field, sr0.X); s.plot('time', sr0.P)
s.plot(magnet.field, sr1.X); s.plot('time', sr1.P)

def fan_leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if not np.isfinite(i_tg + i_bg) or i_tg > 1e-9 or i_bg > 1e-9:
        print(f'LEAK TRIP at B={float(data[1]):.3f} T: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A')
        station.interrupt_requested = True
s.register_run_after(fan_leak_guard, ())

s.multimegasweep([magnet.field], [B_fan], [k_tg.volt, k_bg.volt], [Vtg_fan, Vbg_fan], slow_delay=0, fast_delay=2.7)
# The field remains at the run endpoint; the gates return to the bring-up value.
s.ramp(k_bg.volt, 0.0); s.ramp(k_tg.volt, 0.0)
print(f'fan done: B={magnet.field():+.3f} T, gates=({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V')
