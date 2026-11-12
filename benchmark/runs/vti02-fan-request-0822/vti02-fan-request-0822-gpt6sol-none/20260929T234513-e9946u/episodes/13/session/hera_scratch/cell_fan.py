# === Step 4: calibrated D=0 Landau fan, field slow 0 -> 10 T ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.7960593093052633e-3, c_bg=2.160696465377614e-3,
           n_offset=-0.08937933224099137, D_offset=-0.013)
n_vec = np.linspace(-1.2, 3.2, 89)     # 1e12 cm^-2; 0.05 step
D_vec = np.zeros_like(n_vec)            # calibrated D=0 V/nm
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, D_vec, **CAL)
B_vec = np.linspace(0.0, 10.0, 41)     # 0.25 T row spacing; one upward traverse
assert np.all((Vtg_vec >= TG_MIN) & (Vtg_vec <= TG_MAX))
assert np.all((Vbg_vec >= BG_MIN) & (Vbg_vec <= BG_MAX))
assert np.all(np.abs(B_vec) <= B_SESSION_CAP)
_nr, _Dr = calc_nD(Vtg_vec, Vbg_vec, **CAL)
assert np.max(np.abs(_nr - n_vec)) < 1e-6 and np.max(np.abs(_Dr)) < 1e-6
print(f'fan axes: B {B_vec[0]:.2f}->{B_vec[-1]:.2f} T, {len(B_vec)} rows; '
      f'n {n_vec[0]:+.2f}->{n_vec[-1]:+.2f}e12, {len(n_vec)} points/row; '
      f'TG {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f}, BG {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V')

# Read every state this cell assumes and does not set. Gates themselves are set by the fast axis.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_Ts, _Tv, _B, _Si = T_sample(), T_vaporizer(), magnet.field(), k_si()
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
_hs, _hv = heater.sample_range(), heater.vaporizer_range()
_drive, _tau, _slope = sr1.amplitude(), sr1.time_constant(), sr1.filter_slope()
print(f'preconditions: T_sample={_Ts:.3f} K (1.0..1.5), T_vaporizer={_Tv:.3f} K (<1.6); '
      f'B={_B:+.4f} T (|B|<0.05), Si={_Si:+.4f} V (0); '
      f'PS={_ps}, output={_out}, heater ranges=({_hs},{_hv}); '
      f'drive={_drive:.3f} V (1.0), tau={_tau:.3f} s (0.3), slope={_slope} dB/oct (24)')
assert 1.0 <= _Ts <= 1.5 and _Tv < 1.6 and abs(_Tv - _Ts) < 0.6
assert abs(_B) < 0.05 and abs(_Si) < 0.01 and _ps and _out
assert (_hs, _hv) == (0, 0)
assert abs(_drive - 1.0) < 0.01 and abs(_tau - 0.3) < 1e-6 and _slope == 24
assert k_tg.volt.vals._min_value == -0.3 and k_tg.volt.vals._max_value == 1.0
assert k_bg.volt.vals._min_value == -1.3 and k_bg.volt.vals._max_value == 2.0
assert magnet.field.vals._min_value == -10.0 and magnet.field.vals._max_value == 10.0

SENS = 500e-6
I_TRIP = 1e-9
sr1.sensitivity(SENS)
print(f'sr1 sensitivity={sr1.sensitivity():.6g} V; R nominal full scale={SENS/(_drive/100e6):.0f} Ohm; '
      f'fast dwell=3.0 s (=10 tau)')

mc = dict(meas_config)
mc['Si (V)'] = _Si
mc['sample_temperature:'] = _Ts
mc['comments'] = ('landau-fan D=0, n -1.2..+3.2e12 cm^-2 step 0.05e12, '
                  'B 0..10 T step 0.25, 3 s point dwell, sr1 sensitivity 500 uV; '
                  'calibration from run 5')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'B slow 0..10 T in 0.25 T steps; D=0; n fast -1.2..+3.2e12 cm^-2 in 0.05e12 steps; '
              f'TG {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} V, BG {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V; '
              f'Si=0 V; cal data/5 c_bg/c_tg={CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n_offset={CAL["n_offset"]:+.4f}e12, D_offset={CAL["D_offset"]:+.3f} V/nm; '
              f'3 s dwell, sr1 sensitivity 500 uV, source T_0, drain B_3, Rxx B_1-B_2')
s.fp(T_sample).fp(T_vaporizer).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
for _p in (T_sample, T_vaporizer, k_tg.curr, k_bg.curr,
           sr0.X, sr0.P, sr1.X, sr1.P):
    s.plot('time', _p)

# Row layout: time, B, TG setpoint, BG setpoint, T_sample, T_vaporizer,
#             I_TG, I_BG, sr0.X, sr0.P, sr1.X, sr1.P.
def fan_guard(station, data):
    _it, _ib, _vx = abs(float(data[6])), abs(float(data[7])), abs(float(data[10]))
    if _it > I_TRIP or _ib > I_TRIP or _vx > 0.90 * SENS:
        print(f'FAN TRIP: B={float(data[1]):.3f} T, TG={float(data[2]):+.4f} V; '
              f'|I_TG|={_it:.3e}, |I_BG|={_ib:.3e} A, |sr1.X|={_vx:.3e} V')
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

result = s.multimegasweep([magnet.field], [B_vec],
                          [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                          slow_delay=0, fast_delay=3.0)
print(f'fan run id={result.id}, interrupted={result.metadata.get("interrupted")}; '
      f'actual B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V')
