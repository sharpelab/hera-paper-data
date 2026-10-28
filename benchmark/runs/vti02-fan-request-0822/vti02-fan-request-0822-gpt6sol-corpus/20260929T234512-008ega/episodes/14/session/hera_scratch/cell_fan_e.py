# Electron-side per-column SdH fan — landau-fan-vti; region-A calibration from run 5.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

CAL = dict(c_tg=0.0027960593093052633, c_bg=0.002160696465377614,
           n_offset=-0.08937933224099137, D_offset=-0.013)

# Silent-state preflight: this cell sets the gates and starting field, but inherits T, Si,
# magnet output, lock-in drive/settling, gate-current NPLC, and committed SAFETIES.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
T0, Tv0, B0, Vsi0 = T_sample(), T_vaporizer(), magnet.field(), k_si()
A, tau, slope = sr1.amplitude(), sr1.time_constant(), sr1.filter_slope()
print(f'precondition: T_sample={T0:.3f} K (1.0–1.5), T_vaporizer={Tv0:.3f} K (0.8–1.5); '
      f'B={B0:+.4f} T (0); Si={Vsi0:+.3f} V (0); PS={magnet.persistent_switch_on()}, '
      f'output={magnet.output_enabled()}; drive={A:.3f} V, tau={tau:.3f} s, slope={slope} dB/oct; '
      f'NPLC tg/bg={k_tg.nplci()}/{k_bg.nplci()}')
assert 1.0 <= T0 <= 1.5 and 0.8 <= Tv0 <= 1.5 and abs(B0) < 0.05 and abs(Vsi0) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert 0.95 <= A <= 1.05 and abs(tau - 0.3) < 0.02 and int(slope) == 24
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert (TG_MIN, TG_MAX, BG_MIN, BG_MAX, B_SESSION_CAP) == (-0.3, 1.0, -1.3, 2.0, 10.0)

ns = np.linspace(2.6, 3.2, 21)  # 1e12 cm^-2, n ascending within each B row
Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])
B_vec = field_invB(0.7, 10.0, 135)
assert np.all((TG_MIN <= Vtgs) & (Vtgs <= TG_MAX)) and np.all((BG_MIN <= Vbgs) & (Vbgs <= BG_MAX))
assert B_vec.min() >= 0 and B_vec.max() <= B_SESSION_CAP
assert np.allclose(calc_nD(Vtgs, Vbgs, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])[0], ns)
print(f'grid: n {ns[0]:+.2f}..{ns[-1]:+.2f} e12 ({len(ns)}), D=0; '
      f'TG {Vtgs[0]:+.4f}..{Vtgs[-1]:+.4f} V, BG {Vbgs[0]:+.4f}..{Vbgs[-1]:+.4f} V; '
      f'B {B_vec[0]:.2f}..{B_vec[-1]:.2f} T ({len(B_vec)}); '
      f'd(1/B)={abs(1/B_vec[1]-1/B_vec[0]):.5f} T^-1')

sr1.sensitivity(50e-6)  # 5 kΩ full scale at 10 nA; run 6 max 530 Ω, run 7 max 587 Ω
print(f'sr1 sensitivity={sr1.sensitivity():.2g} V (5 kΩ at {A/100e6*1e9:.1f} nA)')
I_TRIP = 1e-9
mc = dict(meas_config); mc['Si (V)'] = Vsi0; mc['sample_temperature:'] = T0
mc['comments'] = ('landau-fan-vti electron: run-5 region-A cal, D=0, n=+2.6..+3.2e12 '
                  '(21 pts), B=0.7->10 T uniform-1/B (135), sr1 50 uV, fast_delay=3 s, Si=0')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side; region A D=0 V/nm; n={ns[0]:+.2f}..{ns[-1]:+.2f}e12 cm^-2 / 21; '
              f'TG={Vtgs[0]:+.4f}..{Vtgs[-1]:+.4f} V; BG={Vbgs[0]:+.4f}..{Vbgs[-1]:+.4f} V; '
              f'B={B_vec[0]:.2f}->{B_vec[-1]:.2f} T / 135 uniform-1/B; '
              f'cal run 5 ratio={CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n_offset={CAL["n_offset"]:+.4f}e12, D_offset={CAL["D_offset"]:+.3f} V/nm; '
              'sr1=50uV; delay=3s; Si=0')

# First fast point is n=2.6; read gate currents after positioning and before field ramp.
s.ramp(k_bg.volt, float(Vbgs[0])); s.ramp(k_tg.volt, float(Vtgs[0]))
interruptible_sleep(10)
Itg0, Ibg0 = k_tg.curr(), k_bg.curr()
print(f'at fan start gates: I_tg={Itg0*1e12:+.0f} pA, I_bg={Ibg0*1e12:+.0f} pA (trip 1000 pA)')
assert abs(Itg0) < I_TRIP and abs(Ibg0) < I_TRIP
magnet.field(float(B_vec[0]))  # blocking 0 -> 0.7 T ~5.1 min + driver settle
print(f'field at fan start: {magnet.field():+.4f} T (target {B_vec[0]:.4f})')
assert abs(magnet.field() - B_vec[0]) < 0.03

# row layout: [time, B, TG, BG, T_sample, T_vaporizer, I_tg, I_bg, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(T_vaporizer).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot('time', T_sample); s.plot('time', T_vaporizer)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)

def fan_leak_guard(station, data):
    i_tg, i_bg = abs(float(data[6])), abs(float(data[7]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f'LEAK TRIP at B={float(data[1]):+.3f} T, TG={float(data[2]):+.4f} V, '
              f'BG={float(data[3]):+.4f} V: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A')
        station.interrupt_requested = True
s.register_run_after(fan_leak_guard, ())

result = s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt],
                          [Vtgs, Vbgs], slow_delay=0, fast_delay=3.0)
if result.metadata.get('interrupted'):
    print('fan interrupted; gates and field held. Read actual state before any next move.')
else:
    s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
    print(f'fan complete; B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V')
