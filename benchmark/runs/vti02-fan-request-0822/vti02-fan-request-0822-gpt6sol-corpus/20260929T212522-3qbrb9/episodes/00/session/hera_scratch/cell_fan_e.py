# === Electron D=0 Landau fan (`landau-fan-vti`), region-A calibration from run 5 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Preconditions: state inherited from operator handoff, not set by this cell.
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
assert_thermometry_live("T_vaporizer", VTI.temp_logfile_candidates["T_vaporizer"], max_age=15, max_period=12)
_T0, _Tv0, _B0 = T_sample(), T_vaporizer(), magnet.field()
_Vtg0, _Vbg0, _Vsi0 = k_tg.volt(), k_bg.volt(), k_si()
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
_amp, _tau, _slope = sr1.amplitude(), sr1.time_constant(), sr1.filter_slope()
print(f"precondition: T_sample={_T0:.3f} K (1.0..1.5), T_vaporizer={_Tv0:.3f} K (0.7..1.5); "
      f"B={_B0:+.4f} T (|B|<0.05); TG={_Vtg0:+.4f}, BG={_Vbg0:+.4f}, Si={_Vsi0:+.4f} V (all 0); "
      f"PS_on={_ps}, output={_out}; drive={_amp:.3f} V (1), sr1 tau={_tau:.3f} s (0.3), slope={_slope} dB/oct (24)")
assert 1.0 <= _T0 <= 1.5 and 0.7 <= _Tv0 <= 1.5 and abs(_B0) < 0.05
assert abs(_Vtg0) < 0.01 and abs(_Vbg0) < 0.01 and abs(_Vsi0) < 0.01
assert _ps and _out and abs(_amp - 1.0) < 0.01 and abs(_tau - 0.3) < 0.001 and _slope == 24
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0
assert (TG_MIN, TG_MAX, BG_MIN, BG_MAX, SI_MIN, SI_MAX) == (-0.3, 1.0, -1.3, 2.0, -25.0, 25.0)
assert k_tg.nplci() == 1 and k_bg.nplci() == 1

CAL = dict(c_tg=2.796e-3, c_bg=2.161e-3, n_offset=-0.0894, D_offset=-0.013)
ns = np.linspace(3.2, 2.2, 46)                         # 1e12 cm^-2, high n first
Ds = np.zeros_like(ns)                                  # V/nm, calibrated physical D=0
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, **CAL)
n_check, D_check = calc_nD(Vtgs, Vbgs, **CAL)
assert np.allclose(n_check, ns, atol=1e-10) and np.max(np.abs(D_check)) < 1e-10
assert min(Vtgs) >= TG_MIN and max(Vtgs) <= TG_MAX and min(Vbgs) >= BG_MIN and max(Vbgs) <= BG_MAX
B_vec = 1 / np.linspace(1/0.70, 1/10.0, 134)           # uniform in 1/B; 0.70 -> 10 T
assert np.all(np.diff(B_vec) > 0) and B_vec[-1] <= B_SESSION_CAP
F_L_max = 33.09
ray_at_Blo = 0.09672 * B_vec[0]                         # 1e12 cm^-2 for g=4
dinvB = abs(1/B_vec[1] - 1/B_vec[0])
dn = abs(ns[1] - ns[0])
assert dinvB <= 1/(3*F_L_max) and dn <= ray_at_Blo/3
print(f"fan: B {B_vec[0]:.2f}->{B_vec[-1]:.2f} T, {len(B_vec)} rows, d(1/B)={dinvB:.5f} T^-1; "
      f"n {ns[0]:+.2f}->{ns[-1]:+.2f}e12, {len(ns)} points/row, dn={dn:.4f}e12; "
      f"TG {Vtgs.min():+.4f}..{Vtgs.max():+.4f}, BG {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V")

FAST_DELAY, SLOW_DELAY = 2.4, 1.0                 # 8 tau at 24 dB/oct; slow row dwell after blocking B set
I_TRIP, V_RAIL = 1e-9, 0.85 * 50e-6
sr1.sensitivity(50e-6)                            # 5 kOhm FS at 1 V / 100 MOhm = 10 nA
print(f"sr1 sensitivity={sr1.sensitivity():.2e} V, full-scale R={sr1.sensitivity()/(_amp/100e6):.0f} Ohm; "
      f"fast delay={FAST_DELAY:.1f} s = {FAST_DELAY/_tau:.1f} tau")

# One 5-min bare position from the verified 0 T handoff; driver blocks through settle.
magnet.field(float(B_vec[0]))
s = sweep.AsyncStation(dict(meas_config,
    **{"Si (V)": _Vsi0, "sample_temperature:": _T0,
       "comments": "landau-fan-vti electron: region-A run-5 calibration; D=0 V/nm, n=+3.2..+2.2e12 cm^-2 (46), B=0.70..10.0 T (134 uniform 1/B), TG/BG paired, Si=0, sr1 50uV, fast_delay=2.4s"}))
s.add_comment('landau-fan-vti')
s.add_comment('electron D=0; n +3.2 to +2.2e12 cm^-2, 46 pts; B 0.70 to 10.0 T, 134 rows uniform 1/B; run-5 cal ratio 0.773, n_offset -0.0894e12, D_offset -0.013 V/nm; Si 0 V; sr1 50 uV, fast delay 2.4 s')
s.ramp(k_bg.volt, float(Vbgs[0])); s.ramp(k_tg.volt, float(Vtgs[0]))
interruptible_sleep(10)

# multimegasweep row: [time, B, Vtg, Vbg, T_sample, I_tg, I_bg, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot('time', T_sample); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)

def fan_guard(station, data):
    i_tg, i_bg, v_rxx = abs(float(data[5])), abs(float(data[6])), abs(float(data[9]))
    if i_tg > I_TRIP or i_bg > I_TRIP or v_rxx > V_RAIL:
        print(f"FAN TRIP B={float(data[1]):.3f} T, TG={float(data[2]):+.4f} V: "
              f"|I_tg|={i_tg:.3e} A, |I_bg|={i_bg:.3e} A, |sr1.X|={v_rxx:.3e} V")
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
print(f"fan ended: B={magnet.field():+.3f} T, TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V; "
      "field and gates held for disk-first analysis")
