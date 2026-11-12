# === D = 0 electron fan (landau-fan-vti), region A calibration from run 5 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

CAL = dict(c_tg=0.0027960593093052633, c_bg=0.002160696465377614,
           n_offset=-0.08937933224099137, D_offset=-0.013)

# Preconditions: state inherited from the operator's state0 handoff, never assumed silently.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_Ts, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
_Vsi, _Vtg, _Vbg = k_si(), k_tg.volt(), k_bg.volt()
_sr, _vr = heater.sample_range(), heater.vaporizer_range()
_tau, _slope, _amp = sr1.time_constant(), sr1.filter_slope(), sr1.amplitude()
print(f'precondition: T_sample={_Ts:.3f} K (1.0–1.5), T_vaporizer={_Tv:.3f} K (<1.6, tracks sample); '
      f'heater ranges={_sr}/{_vr} (0/0); B={_B:+.4f} T (0±0.05); '
      f'gates TG/BG/Si={_Vtg:+.4f}/{_Vbg:+.4f}/{_Vsi:+.4f} V (0/0/0)')
print(f'precondition: magnet PS={magnet.persistent_switch_on()}, output={magnet.output_enabled()}; '
      f'gate nplci={k_tg.nplci()}/{k_bg.nplci()} (1/1), steps={k_tg.volt.step}/{k_bg.volt.step} V (0.005/0.005); '
      f'sr1 τ={_tau} s, slope={_slope} dB/oct, drive={_amp} V, sr0 sens={sr0.sensitivity()} V')
assert 1.0 <= _Ts <= 1.5 and _Tv < 1.6 and abs(_Tv-_Ts) < 0.6 and _sr == 0 and _vr == 0
assert abs(_B) < 0.05 and abs(_Vsi) < 0.01 and abs(_Vtg) < 0.01 and abs(_Vbg) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert k_tg.volt.step == 0.005 and k_bg.volt.step == 0.005
assert abs(_tau-0.3) < 1e-6 and _slope == 24 and abs(_amp-1.0) < 0.01
assert (k_tg.volt.vals._min_value, k_tg.volt.vals._max_value) == (-0.3, 1.0)
assert (k_bg.volt.vals._min_value, k_bg.volt.vals._max_value) == (-1.3, 2.0)
assert (magnet.field.vals._min_value, magnet.field.vals._max_value) == (-10.0, 10.0)
assert B_SESSION_CAP == 10.0

# Fixed D=0 paired gate line. High-to-low n makes the first point metallic.
ns = np.linspace(3.2, 2.2, 33)  # 1e12 cm^-2, region A
Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])
assert np.all((TG_MIN <= Vtgs) & (Vtgs <= TG_MAX)) and np.all((BG_MIN <= Vbgs) & (Vbgs <= BG_MAX))
_ncheck, _Dcheck = calc_nD(Vtgs, Vbgs, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])
assert np.max(np.abs(_ncheck-ns)) < 1e-6 and np.max(np.abs(_Dcheck-Ds)) < 1e-6
print(f'n={ns[0]:+.3f}→{ns[-1]:+.3f}e12, D=0; TG={Vtgs.min():+.4f}..{Vtgs.max():+.4f} V, '
      f'BG={Vbgs.min():+.4f}..{Vbgs.max():+.4f} V; roundtrip max |D|={np.max(np.abs(_Dcheck)):.2e} V/nm')

B_vec = field_invB(0.7, 10.0, 101)  # monotone positive, uniform 1/B
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
I_TRIP = 1e-9
FAST_DELAY, SLOW_DELAY = 1.8, 0.0
sr1.sensitivity(50e-6)  # 5 kOhm full scale at 10 nA; worst corner is low n, high B
print(f'fan {len(B_vec)} B rows x {len(ns)} n points = {len(B_vec)*len(ns)} points; '
      f'B={B_vec[0]:.3f}→{B_vec[-1]:.3f} T, Δ(1/B)={abs(np.diff(1/B_vec)[0]):.5f} 1/T; '
      f'sr1 sens={sr1.sensitivity()} V, dwell={FAST_DELAY} s')

mc = dict(meas_config); mc['Si (V)'] = _Vsi; mc['sample_temperature:'] = _Ts
mc['comments'] = ('landau-fan-vti: region A, n +3.2→+2.2e12 cm^-2, D=0 V/nm, '
                  'B 0.7→10 T uniform-1/B 101 rows, 33 n pts, fast_delay 1.8 s, sr1 50 uV; cal run 5')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('region A; D=0 V/nm; n +3.2 to +2.2e12 cm^-2 (33 pts); '
              'B +0.7 to +10.0 T (101 uniform-1/B rows); fast_delay=1.8 s, slow_delay=0; '
              'sr1 sensitivity=50 uV; Vsi=0 V; cal run 5 ratio=0.772765, n_offset=-0.089379e12, D_offset=-0.013')

# Starting at B≈0; the 0→0.7 T position is a blocking ~5.1 min ramp.
s.ramp(magnet.field, B_vec[0])
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# Data row: [time, B, Vtg, Vbg, T_sample, I_tg, I_bg, sr0.X, sr0.P, sr1.X, sr1.P].
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot('time', T_sample); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr1.X)
s.plot('time', sr0.P); s.plot('time', sr1.P)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f'LEAK TRIP at B={float(data[1]):+.3f} T, TG={float(data[2]):+.4f} V, BG={float(data[3]):+.4f} V: '
              f'|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A')
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
print(f'done: B={magnet.field():+.3f} T, TG/BG={k_tg.volt():+.4f}/{k_bg.volt():+.4f} V')
