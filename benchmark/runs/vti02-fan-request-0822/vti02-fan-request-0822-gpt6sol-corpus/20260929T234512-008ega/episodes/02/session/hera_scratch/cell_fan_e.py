# === Electron-side D = 0 Landau fan (`landau-fan-vti`), run-5 calibration ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Preconditions: read the state this cell assumes and does not set.
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
assert_thermometry_live("T_vaporizer", VTI.temp_logfile_candidates["T_vaporizer"], max_age=15, max_period=12)
_Ts, _Tv, _B, _Si = T_sample(), T_vaporizer(), magnet.field(), k_si()
_drive, _tau, _slope = sr1.amplitude(), sr1.time_constant(), sr1.filter_slope()
print(f"precondition T_sample={_Ts:.3f} K [1.0,1.5], T_vaporizer={_Tv:.3f} K (<1.6), "
      f"B={_B:+.4f} T (expect 0), V_si={_Si:+.3f} V (expect 0); "
      f"PS heater={magnet.persistent_switch_on()}, output={magnet.output_enabled()}, "
      f"heater ranges={heater.sample_range()}/{heater.vaporizer_range()}")
print(f"drive={_drive:.3f} V ({_drive/100e6*1e9:.2f} nA), sr1 tau={_tau:.3f} s, slope={_slope} dB/oct; "
      f"gate NPLC TG/BG={k_tg.nplci()}/{k_bg.nplci()}")
assert 1.0 <= _Ts <= 1.5 and _Tv < 1.6 and abs(_Tv-_Ts) < 0.6
assert abs(_B) < 0.03 and abs(_Si) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0
assert abs(_drive-1.0) < .01 and abs(_tau-.3) < .001 and _slope == 24
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert (TG_MIN,TG_MAX,BG_MIN,BG_MAX,B_SESSION_CAP) == (-.3,1.0,-1.3,2.0,10.0)
assert (k_tg.volt.vals._min_value,k_tg.volt.vals._max_value) == (-.3,1.0)
assert (k_bg.volt.vals._min_value,k_bg.volt.vals._max_value) == (-1.3,2.0)
assert (magnet.field.vals._min_value,magnet.field.vals._max_value) == (-10.0,10.0)

CAL = dict(c_tg=0.0027960593093052633, c_bg=0.002160696465377614,
           n_offset=-0.08937933224099137, D_offset=-0.013)
ns = np.linspace(2.4, 3.2, 22)   # density in 1e12 cm^-2, ascending
Ds = np.zeros_like(ns)            # physical D = 0 V/nm, run-5 offset included
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL['c_tg'], CAL['c_bg'],
                                CAL['n_offset'], CAL['D_offset'])
assert np.all((Vtgs >= TG_MIN) & (Vtgs <= TG_MAX))
assert np.all((Vbgs >= BG_MIN) & (Vbgs <= BG_MAX))
_ncheck, _Dcheck = calc_nD(Vtgs, Vbgs, CAL['c_tg'], CAL['c_bg'],
                           CAL['n_offset'], CAL['D_offset'])
assert np.max(np.abs(_ncheck-ns)) < 1e-8 and np.max(np.abs(_Dcheck)) < 1e-8
B_start, B_end, N_B = 0.8, 10.0, 116
B_vec = 1.0/np.linspace(1.0/B_start, 1.0/B_end, N_B)
assert np.all(np.diff(B_vec) > 0) and B_vec[-1] <= B_SESSION_CAP
assert np.max(np.abs(np.diff(1.0/B_vec))) < 1.0/(3.0*33.09)
FAST_DELAY, SLOW_DELAY, I_TRIP = 2.4, 1.0, 1e-9
sr1.sensitivity(50e-6)
print(f"fan grid: n={ns[0]:.2f}..{ns[-1]:.2f} ({len(ns)}), B={B_vec[0]:.2f}..{B_vec[-1]:.2f} ({len(B_vec)}), "
      f"D=0; TG={Vtgs.min():+.4f}..{Vtgs.max():+.4f} V, "
      f"BG={Vbgs.min():+.4f}..{Vbgs.max():+.4f} V; sr1 sensitivity={sr1.sensitivity():.0e} V")

mc = dict(meas_config); mc['Si (V)'] = _Si; mc['sample_temperature:'] = _Ts
mc['comments'] = (f"landau-fan-vti: region-A electron D=0, n={ns[0]:+.2f}..{ns[-1]:+.2f}e12 "
                  f"({len(ns)} points), B={B_start:.2f}..{B_end:.2f} T ({N_B} uniform-1/B rows), "
                  f"fast_delay={FAST_DELAY}s, sr1=50uV; run-5 calibration, runs 6/7 spot checks")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'region-A electron n {ns[0]:+.2f}..{ns[-1]:+.2f}e12 cm^-2, D=0 V/nm; '
              f'B {B_start:.2f}..{B_end:.2f} T, {N_B} uniform-1/B rows x {len(ns)} paired-gate points; '
              f'cal run 5 c_bg/c_tg={CAL["c_bg"]/CAL["c_tg"]:.3f}, n0={CAL["n_offset"]:+.3f}e12, '
              f'D0={CAL["D_offset"]:+.3f} V/nm; sr1 50uV, tau={_tau}s, fast_delay={FAST_DELAY}s')

# The blocking field set is the settle; 0 -> 0.8 T costs about 5.8 min.
s.ramp(k_tg.volt, Vtgs[0]); s.ramp(k_bg.volt, Vbgs[0])
s.ramp(magnet.field, B_start)
interruptible_sleep(10)

# Row layout: time, B(slow), Vtg(fast), Vbg(fast), T_sample, I_tg, I_bg,
# sr0.X, sr0.P, sr1.X, sr1.P. Follow and plot every recorded channel.
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot('time', T_sample)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', sr0.X); s.plot('time', sr0.P)
s.plot('time', sr1.X); s.plot('time', sr1.P)
s.plot(k_tg.volt, sr1.X)

def fan_leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f} V, "
              f"Vbg={float(data[3]):+.3f} V: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(fan_leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
# Field and gates deliberately remain at the last row/point for the next step.
print(f"done: B={magnet.field():+.3f} T, TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V")
