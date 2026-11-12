# === Electron-side D=0 Landau fan; run-5 calibration, runs 6/7 spot checks ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
import numpy as np

CAL_FAN = dict(c_tg=0.0027960593093052633, c_bg=0.002160696465377614,
               n_offset=-0.08937933224099137, D_offset=-0.013)
ns_fan = np.linspace(3.20, 2.65, 19)      # 1e12 cm^-2, high -> low density
ds_fan = np.zeros_like(ns_fan)             # V/nm, D = 0 throughout
vtgs_fan, vbgs_fan = calc_gate_voltages(ns_fan, ds_fan, **CAL_FAN)
assert np.all((TG_MIN <= vtgs_fan) & (vtgs_fan <= TG_MAX))
assert np.all((BG_MIN <= vbgs_fan) & (vbgs_fan <= BG_MAX))
nr, dr = calc_nD(vtgs_fan, vbgs_fan, **CAL_FAN)
assert np.max(np.abs(nr-ns_fan)) < 1e-9 and np.max(np.abs(dr)) < 1e-9
B_fan = 1 / np.linspace(1/1.0, 1/10.0, 97)  # uniform inverse field, rising B
FL_max = 10.339 * max(ns_fan)
assert max(np.abs(np.diff(1/B_fan))) <= 1/(3*FL_max)
assert np.max(B_fan) <= B_SESSION_CAP
print(f'plan: n {ns_fan[0]:+.3f}->{ns_fan[-1]:+.3f}e12, D max error {np.max(np.abs(dr)):.2e} V/nm; '
      f'TG {min(vtgs_fan):+.4f}..{max(vtgs_fan):+.4f}, BG {min(vbgs_fan):+.4f}..{max(vbgs_fan):+.4f} V; '
      f'B {B_fan[0]:.2f}->{B_fan[-1]:.2f} T, 97x19, d(1/B)={abs(1/B_fan[1]-1/B_fan[0]):.5f} 1/T')

# Preconditions: these are inherited, not set by the fan. The handoff parked the rig.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
t0, tv0, b0 = T_sample(), T_vaporizer(), magnet.field()
vsi0, vtg0, vbg0 = k_si(), k_tg.volt(), k_bg.volt()
drive0, tau0, slope0 = sr1.amplitude(), sr1.time_constant(), sr1.filter_slope()
print(f'preconditions: T_sample {t0:.3f} K (1.0..1.5), T_vaporizer {tv0:.3f} K (<1.5); '
      f'B {b0:+.4f} T (0±0.05), Si {vsi0:+.4f} V, TG {vtg0:+.4f} V, BG {vbg0:+.4f} V (all 0±0.01); '
      f'PS {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, '
      f'drive {drive0:.3f} V (1), tau {tau0:.3f} s (0.3), slope {slope0} dB/oct (24)')
assert 1.0 <= t0 <= 1.5 and tv0 < 1.5 and abs(b0) < 0.05
assert abs(vsi0) < 0.01 and abs(vtg0) < 0.01 and abs(vbg0) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert abs(drive0-1.0) < 0.02 and abs(tau0-.3) < 1e-3 and slope0 == 24

# Explicit position, fixed sensitivity and start point. The field call blocks (~7.3 min).
sr1.sensitivity(50e-6)
magnet.field(float(B_fan[0]))
k_bg.volt(float(vbgs_fan[0])); k_tg.volt(float(vtgs_fan[0]))
interruptible_sleep(10)
print(f'positioned: B {magnet.field():+.4f} T, TG {k_tg.volt():+.4f} V, BG {k_bg.volt():+.4f} V, sr1 sens {sr1.sensitivity():.2e} V')

mc = dict(meas_config)
mc['Si (V)'] = vsi0
mc['sample_temperature:'] = t0
mc['comments'] = ('landau-fan-vti electron D=0; n +3.20 to +2.65e12 cm^-2; '
                  'B 1 to 10 T, 97 uniform-1/B rows x 19 paired-gate points; '
                  'run-5 c-ratio calibration, absolute scale geometry-prior; sr1 50uV, tau 0.3s')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('electron, D=0 V/nm; n +3.20->+2.65e12 cm^-2; B +1.0->+10.0 T; '
              '97 uniform-1/B rows x 19 n; TG +0.826..+0.984 V, BG +0.962..+1.166 V; '
              'fast_delay 2.1s, slow_delay 1s; cal from run 5, sr1 50uV')

# Layout: time, B, TG, BG, T_sample, TG_current, BG_current, sr0 X/P, sr1 X/P.
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
for ch in (T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P):
    s.plot('time', ch)
s.plot(k_tg.volt, sr1.X)

def fan_leak_guard(station, data):
    itg, ibg = abs(float(data[5])), abs(float(data[6]))
    if itg > 1e-9 or ibg > 1e-9:
        print(f'LEAK TRIP B={float(data[1]):.3f} T n-line TG={float(data[2]):+.4f} V: '
              f'|I_tg|={itg:.3e}, |I_bg|={ibg:.3e} A')
        station.interrupt_requested = True
s.register_run_after(fan_leak_guard, ())

s.multimegasweep([magnet.field], [B_fan], [k_tg.volt, k_bg.volt],
                 [vtgs_fan, vbgs_fan], slow_delay=1, fast_delay=2.1)
print(f'fan ended: measured B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V')
