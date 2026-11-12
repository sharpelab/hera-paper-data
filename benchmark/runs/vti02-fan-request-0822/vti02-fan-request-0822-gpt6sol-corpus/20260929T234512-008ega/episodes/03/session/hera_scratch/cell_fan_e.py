# === Tetralayer FS-count electron fan: run-5 region-A calibration, D = 0 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# Preconditions: inherited state only. The cell sets its own sensitivity, gates, and B.
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _Tv0, _B0 = T_sample(), T_vaporizer(), magnet.field()
_Vtg0, _Vbg0, _Vsi0 = k_tg.volt(), k_bg.volt(), k_si()
_amp, _tau, _slope = sr1.amplitude(), sr1.time_constant(), sr1.filter_slope()
print(f"preconditions: T_sample={_T0:.3f} K (1.0..1.5), T_vaporizer={_Tv0:.3f} K (<1.5); B={_B0:+.4f} T (|B|<0.05); "
      f"TG/BG/Si=({_Vtg0:+.4f},{_Vbg0:+.4f},{_Vsi0:+.4f}) V (all 0); PS={magnet.persistent_switch_on()}, output={magnet.output_enabled()}; "
      f"drive={_amp:.3f} V (1.0), SR1 tau={_tau:.3f} s (0.3), slope={_slope} dB/oct (24)")
assert 1.0 <= _T0 <= 1.5 and 0.5 <= _Tv0 <= 1.5
assert abs(_B0) < 0.05 and abs(_Vtg0) < 0.01 and abs(_Vbg0) < 0.01 and abs(_Vsi0) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert abs(_amp - 1.0) < 0.01 and abs(_tau - 0.3) < 0.01 and _slope == 24
assert k_tg.nplci() == 1 and k_bg.nplci() == 1

CAL_FAN = dict(c_tg=2.7960593093052633e-3, c_bg=2.160696465377614e-3,
               n_offset=-0.08937933224099137, D_offset=-0.013)
N_FAST, N_B = 31, 74
ns_fan = np.linspace(3.2, 1.8, N_FAST)  # high n first; low n is the worst high-B corner
Ds_fan = np.zeros(N_FAST)
Vtgs, Vbgs = calc_gate_voltages(ns_fan, Ds_fan, **CAL_FAN)
B_vec = field_invB(1.2, 10.0, N_B)
assert np.all(np.isfinite(Vtgs)) and np.all(np.isfinite(Vbgs))
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX
assert np.all(np.diff(B_vec) > 0) and B_vec.max() <= B_SESSION_CAP
_ncheck, _Dcheck = calc_nD(Vtgs, Vbgs, **CAL_FAN)
assert np.max(np.abs(_ncheck - ns_fan)) < 1e-5 and np.max(np.abs(_Dcheck)) < 1e-5
print(f"grid: {N_B} B rows {B_vec[0]:.3f}->{B_vec[-1]:.3f} T, d(1/B)={abs(1/B_vec[1]-1/B_vec[0]):.5f} T^-1; "
      f"{N_FAST} n points {ns_fan[0]:+.3f}->{ns_fan[-1]:+.3f}e12, dn={abs(ns_fan[1]-ns_fan[0]):.4f}e12; "
      f"TG [{Vtgs.min():+.4f},{Vtgs.max():+.4f}] BG [{Vbgs.min():+.4f},{Vbgs.max():+.4f}] V")

sr1.sensitivity(50e-6)  # 5 kOhm at 10 nA; fixed through the fan
print(f"SR1 sensitivity={sr1.sensitivity():.2e} V (expect 50 uV)")
assert abs(sr1.sensitivity() - 50e-6) < 1e-9

mc = dict(meas_config); mc["Si (V)"] = _Vsi0; mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan-vti electron region A: run-5 cal, D=0; n +3.2 to +1.8e12 cm^-2 (31), "
                  "B 1.2 to 10 T (74 uniform 1/B), Si=0, SR1=50uV, fast_delay=3s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('region A B1-B2 Rxx; D=0 V/nm; n=+3.2..+1.8e12 cm^-2 (31); B=1.2..10.0 T (74 uniform 1/B); '
              'calibration run 5; spots runs 6-7; SR1 50uV, tau 0.3s/24dB, fast_delay 3s; Si 0V')

s.ramp(k_bg.volt, float(Vbgs[0])); s.ramp(k_tg.volt, float(Vtgs[0]))
interruptible_sleep(5)
magnet.field(float(B_vec[0]))  # blocking 0 -> 1.2 T, ~9 min; driver includes settle
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_Tstart, _Bstart = T_sample(), magnet.field()
print(f"fan start: T_sample={_Tstart:.3f} K (1.0..1.5), B={_Bstart:.4f} T (1.2), TG/BG=({k_tg.volt():+.4f},{k_bg.volt():+.4f}) V")
assert 1.0 <= _Tstart <= 1.5 and abs(_Bstart - 1.2) < 0.03
assert abs(k_tg.volt() - Vtgs[0]) < 0.01 and abs(k_bg.volt() - Vbgs[0]) < 0.01

# Row layout: time, B, TG, BG, T_sample, I_TG, I_BG, sr0.X/P, sr1.X/P.
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot('time', T_sample)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', sr0.X); s.plot('time', sr0.P)
s.plot(k_tg.volt, sr1.X); s.plot('time', sr1.P)

I_TRIP = 1e-9
def fan_guard(station, data):
    temp, i_tg, i_bg = float(data[4]), abs(float(data[5])), abs(float(data[6]))
    if not (1.0 <= temp <= 1.5) or i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"FAN TRIP: B={float(data[1]):.3f} T, T={temp:.3f} K, |I_TG|={i_tg:.3e}, |I_BG|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=1.0, fast_delay=3.0)
finally:
    s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
print(f"fan ended: B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V")
