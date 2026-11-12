# HERA — calibration Landau fan. recipe: measurements/landau-fan-vti.md
# B slow (magnet ramps once per row), V_tg fast at fixed V_bg = 0.
# Purpose: absolute lever arm from LL spacing + unambiguous CNP location +
# the one-fan-or-two test. NOT the FS-count fan (B rows are far too coarse
# for a 1/B FFT -- see the markdown).
import numpy as np

# --- preconditions this cell assumes but does not set ---
_vsi = dc205.voltage()
_B0, _Ts = magnet.field(), T_sample()
print(f"preconditions: V_tg={k_tg.volt():+.4f} V  V_bg={k_bg.volt():+.4f} V  V_si={_vsi:+.4f} V  "
      f"B={_B0:+.4f} T  T_sample={_Ts:.3f} K")
assert abs(_vsi) < 0.01, "V_si not at 0"
assert abs(_B0) < 0.05, "field not near zero -- fan assumes it starts at 0 T"
assert 1.0 <= _Ts <= 1.4, "sample not at base"
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert np.isclose(sr1.time_constant(), 0.1) and abs(sr1.filter_slope() - 24) < 1, \
    "sr1 not at the committed tau/slope"
assert magnet.persistent_switch_on() and magnet.output_enabled(), "magnet not ready"

B_MAX = 6.0
B_V = np.arange(0.0, B_MAX + 1e-9, 0.5)          # 13 rows, magnet ramps per row
TG_V = np.linspace(TG_MIN, TG_MAX, 201)          # 6.5 mV steps
V_BG_FIXED = 0.0

assert B_V.max() <= B_SESSION_CAP, "B vector exceeds the committed session cap"
assert TG_V.min() >= TG_MIN and TG_V.max() <= TG_MAX, "TG vector outside validator"
assert BG_MIN <= V_BG_FIXED <= BG_MAX, "V_bg outside validator"

print(f"grid: B {B_V[0]:.2f} -> {B_V[-1]:.2f} T x{len(B_V)} rows ({np.diff(B_V)[0]:.2f} T)  [slow]")
print(f"      V_tg {TG_V[0]:+.3f} -> {TG_V[-1]:+.3f} V x{len(TG_V)} "
      f"({np.diff(TG_V)[0]*1e3:.1f} mV) at V_bg = {V_BG_FIXED:+.2f} V  [fast]")
print(f"      {len(B_V)*len(TG_V)} points; traverse {B_MAX/0.137:.0f} min + "
      f"grid {len(B_V)*len(TG_V)*0.87/60:.0f} min")
# Landau-level spacing in V_tg at the top field, on the geometry prior --
# this is what has to be resolvable for the lever-arm read.
_dn_per_nu = cst.e * B_MAX / cst.h * 1e-4        # cm^-2 per filling factor
_dvtg = _dn_per_nu / (2.7960593112e-3 / cst.e * 1e-4)
print(f"      at {B_MAX:.0f} T: dn per filling factor = {_dn_per_nu*1e-12:.3f}e12 cm^-2 "
      f"-> dV_tg = {_dvtg*1e3:.0f} mV = {_dvtg/np.diff(TG_V)[0]:.1f} fast-axis points")

meas_config["comments"] = ("calibration Landau fan at V_bg = 0: absolute lever arm from LL "
                           "spacing, CNP location, and the one-fan-or-two domain test")
meas_config["Si (V)"] = dc205.voltage()
meas_config["sample_temperature:"] = T_sample()

s = sweep.AsyncStation(meas_config)
s.add_comment('landau-fan-vti')
s.add_comment('CALIBRATION fan (lever arm + CNP identification), not the FS-count fan')
s.add_comment(f'B slow {B_V[0]:g}..{B_V[-1]:g} T x{len(B_V)}; '
              f'V_tg fast {TG_V[0]:+g}..{TG_V[-1]:+g} V x{len(TG_V)} at V_bg = {V_BG_FIXED:+g} V')
s.add_comment('B rows 0.5 T are deliberately coarse: this fan is read as LL structure vs gate '
              'at each field, NOT by 1/B FFT (that needs the sdh-spot-check grid)')
s.add_comment(f'I_bias = {I_BIAS:.4e} A, drive {sr1.amplitude()} V @ {sr1.frequency()} Hz')
s.add_comment(f'sr1 tau={sr1.time_constant()} s slope={sr1.filter_slope()} dB/oct, '
              f'fast_delay={DWELL:.2f} s; sr1 sens {sr1.sensitivity():.1e} '
              f'(R ceiling ~{sr1.sensitivity()/abs(I_BIAS)/1e3:.0f} kohm, CNP may rail at high B)')
s.add_comment('crosses BOTH gate-map ridges: B at V_tg=+0.113, A at V_tg=-0.203 (run 4)')
s.add_comment('contacts hardwired: source T_0, drain B_3 (sr0), Rxx B_1-B_2 (sr1); sr2/sr3 n.c.')

s.ramp(k_bg.volt, V_BG_FIXED)
s.ramp(k_tg.volt, TG_V[0])
interruptible_sleep(10)
print(f"positioned: V_tg={k_tg.volt():+.4f}, V_bg={k_bg.volt():+.4f}, B={magnet.field():+.4f} T")

s.fp(k_tg.curr).fp(k_bg.curr)
s.fp(T_sample).fp(T_vaporizer)
for _lia in (sr0, sr1, sr2, sr3):
    s.fp(_lia.X).fp(_lia.P)
    s.plot(k_tg.volt, _lia.X)
s.plot(k_tg.volt, k_tg.curr)
s.plot(k_tg.volt, k_bg.curr)

try:
    s.megasweep(magnet.field, B_V, k_tg.volt, TG_V, slow_delay=2.0, fast_delay=DWELL)
finally:
    print(f"sweep exited at B={magnet.field():+.4f} T, V_tg={k_tg.volt():+.4f} V")
    s.ramp(k_tg.volt, 0)
    print(f"parked V_tg -> {k_tg.volt():+.4f} V (field left where the sweep ended, "
          f"by design -- next step decides the endpoint)")

print(f"\nCALFAN: done.  B={magnet.field():+.4f} T, V_tg={k_tg.volt():+.4f} V, "
      f"V_bg={k_bg.volt():+.4f} V, T={T_sample():.3f} K")
