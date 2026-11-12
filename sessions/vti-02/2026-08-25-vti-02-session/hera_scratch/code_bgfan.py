# HERA — back-gate calibration fan, measured on the way DOWN from 6 T.
# recipe: measurements/landau-fan-vti.md
# V_bg fast at fixed V_tg; B slow, DESCENDING 6 -> 1 T so the traverse home is
# measured rather than wasted (rig card: never re-traverse without a reason).
import numpy as np

# --- preconditions this cell assumes but does not set ---
_vsi = dc205.voltage()
_B0, _Ts = magnet.field(), T_sample()
print(f"preconditions: V_tg={k_tg.volt():+.4f} V  V_bg={k_bg.volt():+.4f} V  V_si={_vsi:+.4f} V  "
      f"B={_B0:+.4f} T  T_sample={_Ts:.3f} K")
assert abs(_vsi) < 0.01, "V_si not at 0"
assert 5.8 <= _B0 <= 6.2, f"expected to start at 6 T, found {_B0:.4f} T"
assert 1.0 <= _Ts <= 1.4, "sample not at base"
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert np.isclose(sr1.time_constant(), 0.1) and abs(sr1.filter_slope() - 24) < 1, \
    "sr1 not at the committed tau/slope"
assert magnet.persistent_switch_on() and magnet.output_enabled(), "magnet not ready"

# CNP measured from run 5's ray convergence: V_tg = +0.0216 V at V_bg = 0.
# Fixing V_tg there puts the CNP at V_bg = 0, centring the fast axis on it.
V_TG_FIXED = 0.0216
B_V = np.array([6.0, 5.0, 4.0, 3.0, 2.0, 1.0])      # descending: rides the magnet home
BG_V = np.linspace(BG_MIN, BG_MAX, 301)             # 11 mV steps over the full window

assert B_V.max() <= B_SESSION_CAP, "B vector exceeds committed session cap"
assert TG_MIN <= V_TG_FIXED <= TG_MAX, "V_tg outside validator"
assert BG_V.min() >= BG_MIN and BG_V.max() <= BG_MAX, "BG vector outside validator"

print(f"grid: B {B_V[0]:.1f} -> {B_V[-1]:.1f} T x{len(B_V)} rows (descending)  [slow]")
print(f"      V_bg {BG_V[0]:+.3f} -> {BG_V[-1]:+.3f} V x{len(BG_V)} "
      f"({np.diff(BG_V)[0]*1e3:.1f} mV) at V_tg = {V_TG_FIXED:+.4f} V  [fast]")
print(f"      {len(B_V)*len(BG_V)} points; descent {5.0/0.137:.0f} min + "
      f"grid {len(B_V)*len(BG_V)*0.87/60:.0f} min")
# predicted LL spacing on the back gate, using c_bg = 0.864 * c_tg(measured)
_c_tg_meas = 2.5152e-3
_c_bg_guess = 0.864 * _c_tg_meas
_a_bg = cst.e**2 / (cst.h * _c_bg_guess)
print(f"      predicted dV_bg per dnu=4 at 6 T: {4*_a_bg*6.0:.3f} V "
      f"-> {3.3/(4*_a_bg*6.0):.1f} periods across the window, "
      f"{4*_a_bg*6.0/np.diff(BG_V)[0]:.0f} pts/period")

meas_config["comments"] = ("back-gate calibration fan on the descent from 6 T: absolute c_bg "
                           "from LL spacing + CNP line slope; both carrier signs")
meas_config["Si (V)"] = dc205.voltage()
meas_config["sample_temperature:"] = T_sample()

s = sweep.AsyncStation(meas_config)
s.add_comment('landau-fan-vti')
s.add_comment('CALIBRATION fan #2 (back-gate lever arm), measured on the descent from 6 T')
s.add_comment(f'B slow {B_V[0]:g}..{B_V[-1]:g} T x{len(B_V)} DESCENDING; '
              f'V_bg fast {BG_V[0]:+g}..{BG_V[-1]:+g} V x{len(BG_V)} at V_tg = {V_TG_FIXED:+g} V')
s.add_comment('V_tg fixed at run 5 measured CNP (+0.0216 V at V_bg=0), so the CNP sits at V_bg=0')
s.add_comment('run 5 gave c_tg = 2.515e-3 F/m^2 (dn/dV_tg = 1.570e12 cm^-2/V) from 7 LL '
              'ray slopes in ratio 4:8:12:16:20:24, slope/nu consistent to 1.4%')
s.add_comment(f'I_bias = {I_BIAS:.4e} A, drive {sr1.amplitude()} V @ {sr1.frequency()} Hz')
s.add_comment(f'sr1 tau={sr1.time_constant()} s slope={sr1.filter_slope()} dB/oct, '
              f'fast_delay={DWELL:.2f} s, sens {sr1.sensitivity():.1e} (CNP clips, by design)')
s.add_comment('NOTE: Rxx carries a small R_xy admixture (negative R at deep minima, '
              'consistent with ~0.5% of h/8e^2) - single field polarity, not symmetrised')
s.add_comment('contacts hardwired: source T_0, drain B_3 (sr0), Rxx B_1-B_2 (sr1); sr2/sr3 n.c.')

s.ramp(k_tg.volt, V_TG_FIXED)
s.ramp(k_bg.volt, BG_V[0])
interruptible_sleep(10)
print(f"positioned: V_tg={k_tg.volt():+.4f}, V_bg={k_bg.volt():+.4f}, B={magnet.field():+.4f} T")

s.fp(k_tg.curr).fp(k_bg.curr)
s.fp(T_sample).fp(T_vaporizer)
for _lia in (sr0, sr1, sr2, sr3):
    s.fp(_lia.X).fp(_lia.P)
    s.plot(k_bg.volt, _lia.X)
s.plot(k_bg.volt, k_tg.curr)
s.plot(k_bg.volt, k_bg.curr)

try:
    s.megasweep(magnet.field, B_V, k_bg.volt, BG_V, slow_delay=2.0, fast_delay=DWELL)
finally:
    print(f"sweep exited at B={magnet.field():+.4f} T, V_bg={k_bg.volt():+.4f} V")
    s.ramp(k_bg.volt, 0)
    s.ramp(k_tg.volt, 0)
    print(f"parked gates: V_tg={k_tg.volt():+.4f} V, V_bg={k_bg.volt():+.4f} V "
          f"(field left at {magnet.field():+.4f} T for the next step)")

print(f"\nBGFAN: done.  B={magnet.field():+.4f} T, T={T_sample():.3f} K")
