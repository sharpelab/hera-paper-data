# HERA — electron-side Landau fan at D = 0, uniform in 1/B, tau = 300 ms.
# recipe: measurements/landau-fan-vti.md (investigation Step 4/5)
# Operator-directed: tau=300ms, B 1-8 T sampled in 1/B, much finer B, 4-6 h.
import numpy as np

# --- preconditions this cell assumes but does not set ---
_vsi = dc205.voltage()
_B0, _Ts = magnet.field(), T_sample()
print(f"preconditions: V_tg={k_tg.volt():+.4f} V  V_bg={k_bg.volt():+.4f} V  V_si={_vsi:+.4f} V  "
      f"B={_B0:+.4f} T  T_sample={_Ts:.3f} K  T_vap={T_vaporizer():.3f} K")
assert abs(_vsi) < 0.01, "V_si not at 0"
assert abs(_B0) <= 8.5, "unexpected field"   # close-out was interrupted mid-ramp;
# the supply is still heading for 0 (rig card: interrupt != stop). We redirect below.
assert 1.0 <= _Ts <= 1.4, "sample not at base"
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert magnet.persistent_switch_on() and magnet.output_enabled(), "magnet not ready"
assert int(heater.sample_range()) == 0 and int(heater.vaporizer_range()) == 0, "heaters not off"

# --- acquisition config: close-out restored bring-up values, so re-establish ---
# tau = 300 ms is the operator's call and it is the right one: at 5 V drive the
# measured point-to-point scatter was 0.14% of R_xx at tau=0.3 vs 0.35% at
# tau=0.1 (cell 39/41), i.e. 2.5x better SNR -- aimed squarely at the partner
# tones that reproduced in only 3-9 of 18 extraction choices in run 7.
sr1.amplitude(5.0)                 # I_bias = 5.0 V / 100 Mohm ~ 49.2 nA (linearity verified cell 41)
for _s in (sr0, sr1):
    _s.time_constant(0.3)
    _s.filter_slope(24)
sr0.sensitivity(0.2)               # 49 nA x 1e6 V/A = 49 mV -> 0.25 of full scale
sr1.sensitivity(1e-4)              # R ceiling ~2 kohm; electron flank runs 10-400 ohm
interruptible_sleep(5.0)
DWELL_FAN = 7 * sr1.time_constant()          # 24 dB/oct settling floor = 2.1 s
_I = sr0.X() / meas_config["sr0_gain"]
print(f"acquisition: drive={sr1.amplitude()} V @ {sr1.frequency()} Hz -> I={_I:.4e} A; "
      f"tau={sr1.time_constant()} s, slope={sr1.filter_slope()} dB/oct, dwell={DWELL_FAN:.2f} s")
print(f"             sr0 sens={sr0.sensitivity():.2e} (load {abs(sr0.X())/sr0.sensitivity():.3f}), "
      f"sr1 sens={sr1.sensitivity():.2e} (R ceiling {sr1.sensitivity()/abs(_I)/1e3:.2f} kohm)")

# --- calibration measured this session (runs 5, 6) ---
DN_DVTG, DN_DVBG, V_TG_CNP = 1.570e12, 1.307e12, 0.0203
RATIO = DN_DVBG / DN_DVTG                     # c_bg/c_tg = 0.8324
# D = 0 (D_offset = 0 -- still an UNEXAMINED assumption): V_bg = V_tg / RATIO
N_LO, N_HI, N_COLS = 1.20, 3.05, 57           # 1e12 cm^-2, electron side
NS = np.linspace(N_LO, N_HI, N_COLS)
V_TGS = (NS * 1e12 + DN_DVTG * V_TG_CNP) / (DN_DVTG + DN_DVBG / RATIO)
V_BGS = V_TGS / RATIO
assert V_TGS.min() >= TG_MIN and V_TGS.max() <= TG_MAX, "V_tg vector outside validator"
assert V_BGS.min() >= BG_MIN and V_BGS.max() <= BG_MAX, "V_bg vector outside validator"

# --- field axis: uniform in 1/B (operator-directed; field_invB is the helper) ---
B_LO, B_HI, N_B = 1.0, 8.0, 101
# DESCENDING (operator): start high, sweep down, so the fan ends near zero and the
# traverse home is the measurement. field_invB(high, low, N) sets the direction.
B_V = field_invB(B_HI, B_LO, N_B)            # descending, uniform in 1/B
assert B_V.max() <= B_SESSION_CAP, "B vector exceeds the committed session cap"
_ib = 1.0 / B_V
_dib = abs(np.diff(_ib)[0])
_FL_hi = cst.h / (4 * cst.e) * NS.max() * 1e16
_dF = 1.0 / (_ib[0] - _ib[-1])
print(f"\ngrid: B {B_V[0]:.2f} -> {B_V[-1]:.2f} T x{N_B} rows, UNIFORM IN 1/B "
      f"(d(1/B) = {_dib:.6f} 1/T)  [slow]")
print(f"      dB = {abs(B_V[1]-B_V[0]):.4f} T at the low end, "
      f"{abs(B_V[-1]-B_V[-2]):.4f} T at the high end")
print(f"      n {NS[0]:.2f} -> {NS[-1]:.2f} e12 cm^-2 x{N_COLS} cols (dn = {np.diff(NS)[0]:.4f}e12), "
      f"D = 0  [fast]")
print(f"      V_tg {V_TGS[0]:.4f} -> {V_TGS[-1]:.4f} V; V_bg {V_BGS[0]:.4f} -> {V_BGS[-1]:.4f} V")
print(f"sampling: F_L(n_max) = {_FL_hi:.2f} T; Nyquist needs d(1/B) <= {1/(2*_FL_hi):.5f}, "
      f"prefer {1/(3*_FL_hi):.5f}; have {_dib:.5f}  -> {1/(2*_dib):.1f} T resolvable "
      f"({1/(2*_dib)/_FL_hi:.2f} x F_L)")
print(f"resolution: dF = {_dF:.3f} T   (run 7 spot check had 2.00 T)")
_half = 0.5 * (_ib[0] + _ib[-1])
print(f"B-window split at B = {1/_half:.3f} T: halves have EQUAL d(1/B) span -> "
      f"dF_half = {1/(_ib[0]-_half):.2f} T each; the ABAB pair separation (17.7 T at n=3e12) "
      f"is {17.7/(1/(_ib[0]-_half)):.1f}x that, so BOTH tones resolve in BOTH halves")
print(f"partner tone gets {(_ib[0]-_ib[-1])*6.67:.1f} periods in the record (recipe wants >= 5)")
_rampin = abs(B_V[0] - magnet.field())/0.137*60
print(f"points: {N_B*N_COLS}; estimated {(_rampin + (B_HI-B_LO)/0.137*60 + N_B*3 + N_B*N_COLS*2.25 + N_B*4.1)/3600:.2f} h "
      f"(ramp-in {_rampin/60:.0f}m + traverse {(B_HI-B_LO)/0.137:.0f}m + grid {N_B*N_COLS*2.25/60:.0f}m)")

meas_config["comments"] = ("electron-side Landau fan at D=0, uniform in 1/B, tau=300ms; "
                           "investigation Step 4/5 -- per-column FFT, Luttinger partition, F(n)")
meas_config["Si (V)"] = dc205.voltage()
meas_config["sample_temperature:"] = T_sample()

s = sweep.AsyncStation(meas_config)
s.add_comment('landau-fan-vti')
s.add_comment('FS-COUNT fan (investigation Step 4/5), electron side, D = 0')
s.add_comment(f'B slow {B_V[0]:g}..{B_V[-1]:g} T x{N_B} DESCENDING, UNIFORM IN 1/B (d(1/B)={_dib:.6f}); '
              f'n fast {NS[0]:g}..{NS[-1]:g} e12 cm^-2 x{N_COLS} at D=0')
s.add_comment(f'resolution dF = {_dF:.3f} T; Nyquist {1/(2*_dib):.1f} T = '
              f'{1/(2*_dib)/_FL_hi:.2f}x F_L(n_max)')
s.add_comment(f'calibration THIS SESSION: dn/dV_tg={DN_DVTG:.3e}, dn/dV_bg={DN_DVBG:.3e} cm^-2/V, '
              f'c_bg/c_tg={RATIO:.4f}, CNP at V_tg={V_TG_CNP:+.4f} V (V_bg=0), from LL rays runs 5/6')
s.add_comment('D_offset = 0 remains an UNEXAMINED assumption')
s.add_comment(f'tau={sr1.time_constant()} s slope={sr1.filter_slope()} dB/oct, '
              f'fast_delay={DWELL_FAN:.2f} s (7*tau); I_bias={_I:.4e} A; sr1 sens={sr1.sensitivity():.1e}')
s.add_comment('purpose: firm the run-7 ABAB(consistent-with) read -- partner-tone reproducibility, '
              'Luttinger sum across density, and the F_L-tone origin B-window split')
s.add_comment('Rxx carries ~1% R_xy admixture; SINGLE field polarity, not symmetrised. '
              'R_xy is periodic in 1/B at the same fundamental, so it distorts harmonic content '
              'but does NOT create new fundamental frequencies')
s.add_comment('contacts hardwired: source T_0, drain B_3 (sr0), Rxx B_1-B_2 (sr1); sr2/sr3 n.c.')

s.ramp(k_tg.volt, float(V_TGS[0]))
s.ramp(k_bg.volt, float(V_BGS[0]))
interruptible_sleep(10)
print(f"\npositioned gates: V_tg={k_tg.volt():+.4f}, V_bg={k_bg.volt():+.4f}")

# Redirect the magnet. It is still ramping toward 0 from the interrupted close-out
# -- on this rig an interrupt does NOT stop the supply, and the only recovery is a
# fresh blocking set with a new target (rig card, Magnet). This is that set.
_bnow = magnet.field()
print(f"field now {_bnow:+.4f} T, commanded {magnet.commanded_field} -> redirecting to "
      f"{B_V[0]:.2f} T (~{abs(B_V[0]-_bnow)/0.137:.0f} min blocking ramp)")
magnet.field(float(B_V[0]))
interruptible_sleep(10)
print(f"at field: B={magnet.field():+.4f} T, T_sample={T_sample():.3f} K, "
      f"T_vap={T_vaporizer():.3f} K; starting the descent")

s.fp(k_tg.curr).fp(k_bg.curr)
s.fp(T_sample).fp(T_vaporizer)
for _lia in (sr0, sr1, sr2, sr3):
    s.fp(_lia.X).fp(_lia.P)
    s.plot(k_tg.volt, _lia.X)
s.plot(k_tg.volt, k_tg.curr)
s.plot(k_tg.volt, k_bg.curr)

try:
    s.multimegasweep([magnet.field], [B_V], [k_tg.volt, k_bg.volt], [V_TGS, V_BGS],
                     slow_delay=2.5, fast_delay=DWELL_FAN)
finally:
    print(f"sweep exited at B={magnet.field():+.4f} T")
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)
    print(f"parked gates: V_tg={k_tg.volt():+.4f} V, V_bg={k_bg.volt():+.4f} V; "
          f"field left at {magnet.field():+.4f} T")

print(f"\nBIGFAN: done.  B={magnet.field():+.4f} T, T={T_sample():.3f} K")
