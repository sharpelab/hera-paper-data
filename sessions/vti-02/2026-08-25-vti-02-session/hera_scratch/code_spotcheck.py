# HERA — SdH spot check on the measured D = 0 line.
# recipe: measurements/sdh-spot-check.md (+ field-sweep-1d call surface)
# B slow (magnet ramps once per row), 5 fixed (n, D=0) gate points fast, so all
# five densities ride the SAME traverse.
import numpy as np

# --- preconditions this cell assumes but does not set ---
_vsi = dc205.voltage()
_B0, _Ts = magnet.field(), T_sample()
print(f"preconditions: V_tg={k_tg.volt():+.4f} V  V_bg={k_bg.volt():+.4f} V  V_si={_vsi:+.4f} V  "
      f"B={_B0:+.4f} T  T_sample={_Ts:.3f} K")
assert abs(_vsi) < 0.01, "V_si not at 0"
assert 0.8 <= _B0 <= 1.2, f"expected to start near 1 T (end of run 6), found {_B0:.4f} T"
assert 1.0 <= _Ts <= 1.4, "sample not at base"
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert magnet.persistent_switch_on() and magnet.output_enabled(), "magnet not ready"

# ---- calibration, measured this session (runs 5 and 6) ----
DN_DVTG = 1.570e12      # cm^-2 / V   (run 5, 7 LL ray slopes, 1.4% scatter)
DN_DVBG = 1.307e12      # cm^-2 / V   (run 6, 7 LL ray slopes, 6% scatter)
V_TG_CNP, V_BG_CNP = 0.0203, 0.0      # run 5 ray convergence, +/- 0.0076 V
RATIO = DN_DVBG / DN_DVTG             # c_bg/c_tg = 0.832 measured
# D = 0 (assuming D_offset = 0 -- an UNEXAMINED assumption, stated per recipe):
#   c_tg*V_tg = c_bg*V_bg  ->  V_bg = V_tg / RATIO
N_TARGETS = np.array([-0.9, 1.8, 2.2, 2.6, 3.0])      # 1e12 cm^-2
V_TGS = (N_TARGETS * 1e12 + DN_DVTG * V_TG_CNP) / (DN_DVTG + DN_DVBG / RATIO)
V_BGS = V_TGS / RATIO

print("\n(n, D=0) targets on the measured calibration:")
for n_, vt, vb in zip(N_TARGETS, V_TGS, V_BGS):
    n_chk = (DN_DVTG * (vt - V_TG_CNP) + DN_DVBG * (vb - V_BG_CNP)) / 1e12
    print(f"  n = {n_:+5.2f}e12  ->  V_tg = {vt:+.4f} V, V_bg = {vb:+.4f} V   "
          f"(closure check: n = {n_chk:+.3f}e12)")
assert V_TGS.min() >= TG_MIN and V_TGS.max() <= TG_MAX, "V_tg targets outside validator"
assert V_BGS.min() >= BG_MIN and V_BGS.max() <= BG_MAX, "V_bg targets outside validator"

# ---- field grid: uniform in B with dB = d(1/B)*B_lo^2 (blocking magnet) ----
B_LO, B_HI = 1.5, 6.0
F_L_MAX = cst.h / (4 * cst.e) * np.abs(N_TARGETS).max() * 1e16      # Tesla
D_INVB = 1.0 / (3 * F_L_MAX)                                        # Nyquist x3 on F_L
DB = D_INVB * B_LO ** 2
B_V = np.arange(B_LO, B_HI + 1e-9, DB)
assert B_V.max() <= B_SESSION_CAP, "B vector exceeds committed session cap"
print(f"\nsampling: F_L(max |n|) = {F_L_MAX:.1f} T -> d(1/B) = {D_INVB:.5f} 1/T "
      f"(Nyquist x3) -> dB = {DB:.4f} T")
print(f"  B {B_LO} -> {B_HI} T, {len(B_V)} rows; d(1/B) at B_lo = {DB/B_LO**2:.5f}, "
      f"at B_hi = {DB/B_HI**2:.5f} 1/T")
print(f"  usable-record resolution dF = 1/(1/B_lo - 1/B_hi) = "
      f"{1/(1/B_LO - 1/B_HI):.2f} T")
print(f"  cost: traverse {(B_HI-B_LO)/0.137:.0f} min + {len(B_V)} settles x3 s "
      f"= {len(B_V)*3/60:.0f} min + grid {len(B_V)*len(V_TGS)*0.87/60:.0f} min")

# ---- lock-in range: sens ~ I_bias * R_target, NOT the wide CNP range ----
# recipe: "a signal at a few % of range is coarse-ADC digitized (grainy-FFT)".
# Away from the CNP R_xx runs ~50-300 ohm; 1e-4 puts full scale at ~2 kohm.
sr1.sensitivity(1e-4)
interruptible_sleep(2.0)
print(f"\nsr1 re-ranged to {sr1.sensitivity():.1e} V (R ceiling "
      f"{sr1.sensitivity()/abs(I_BIAS)/1e3:.2f} kohm); tau={sr1.time_constant()} s, "
      f"slope={sr1.filter_slope()} dB/oct, dwell={DWELL:.2f} s")

meas_config["comments"] = ("SdH spot check on the measured D=0 line, 5 densities "
                           "(-0.9, 1.8, 2.2, 2.6, 3.0 e12 cm^-2), B 1.5-6 T uniform-B")
meas_config["Si (V)"] = dc205.voltage()
meas_config["sample_temperature:"] = T_sample()

s = sweep.AsyncStation(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment('5 fixed (n, D=0) points share one traverse; B slow so the magnet ramps per row')
s.add_comment(f'n targets (1e12 cm^-2): {N_TARGETS.tolist()}')
s.add_comment(f'V_tg: {[round(v,4) for v in V_TGS]}')
s.add_comment(f'V_bg: {[round(v,4) for v in V_BGS]}')
s.add_comment(f'calibration THIS SESSION: dn/dV_tg={DN_DVTG:.3e}, dn/dV_bg={DN_DVBG:.3e} cm^-2/V, '
              f'c_bg/c_tg={RATIO:.4f}, CNP at V_tg={V_TG_CNP:+.4f} V (V_bg=0) '
              '-- from LL ray slopes/convergence, runs 5 and 6')
s.add_comment('D_offset = 0 is an UNEXAMINED assumption (no feature yet locates D=0 physically)')
s.add_comment(f'B {B_LO}..{B_HI} T uniform-B, dB={DB:.4f} T = d(1/B)*B_lo^2, '
              f'{len(B_V)} rows; Nyquist x3 on F_L={F_L_MAX:.1f} T')
s.add_comment(f'I_bias = {I_BIAS:.4e} A; sr1 sens {sr1.sensitivity():.1e} sized to R_target '
              f'(not the wide CNP range) per the recipe grainy-FFT warning')
s.add_comment('Rxx carries ~1% R_xy admixture; single field polarity, NOT symmetrised')
s.add_comment('contacts hardwired: source T_0, drain B_3 (sr0), Rxx B_1-B_2 (sr1); sr2/sr3 n.c.')

s.ramp(k_tg.volt, float(V_TGS[0]))
s.ramp(k_bg.volt, float(V_BGS[0]))
interruptible_sleep(10)
print(f"positioned: V_tg={k_tg.volt():+.4f}, V_bg={k_bg.volt():+.4f}, B={magnet.field():+.4f} T")

s.fp(k_tg.curr).fp(k_bg.curr)
s.fp(T_sample).fp(T_vaporizer)
for _lia in (sr0, sr1, sr2, sr3):
    s.fp(_lia.X).fp(_lia.P)
    s.plot(magnet.field, _lia.X)
s.plot(magnet.field, k_tg.curr)
s.plot(magnet.field, k_bg.curr)

try:
    s.multimegasweep([magnet.field], [B_V], [k_tg.volt, k_bg.volt], [V_TGS, V_BGS],
                     slow_delay=1.0, fast_delay=DWELL)
finally:
    print(f"sweep exited at B={magnet.field():+.4f} T")
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)
    print(f"parked gates: V_tg={k_tg.volt():+.4f} V, V_bg={k_bg.volt():+.4f} V")

print(f"\nSPOTCHECK: done.  B={magnet.field():+.4f} T, T={T_sample():.3f} K")
