"""Landau-fan design (investigation Step 4 / landau-fan step 1) — binding computations.

1. B_lo: sdh_onset on run 6, honest about the undersampled sub-1 T segment.
2. Dynamic range: R along the D=0 line at B=0 (run 5) x measured MR factor.
3. Model tone table over the candidate n-window; dual overlay ABAB / ABCA / trilayer.
4. Nyquist both axes; dF; partner-tone period count.
5. Cost model calibrated on this session's runs 5/6/7. One design.
"""
import sys, json, numpy as np, importlib.util as iu


def _load(name, path):
    spec = iu.spec_from_file_location(name, path)
    m = iu.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


fc = _load("tet_fs", "/home/hera/measurement_env/hera/models/tetralayer_fs_count/fs_count_b0.py")
trimod = _load("tri_fs", "/home/hera/measurement_env/hera/models/trilayer_fs_count/fs_count_b0.py")
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN, TG_MAX = -0.3, 1.0
BG_MIN, BG_MAX = -1.3, 2.0
I_BIAS = 1.0 / 100e6
R_FS = 50e-6 / I_BIAS

print("#" * 74)
print("# 1. B_lo — sdh_onset on run 6, and the sub-1 T sampling honesty check")
print("#" * 74)
r6 = open_run("data/6")
B6 = np.asarray(r6.col("magnet_field"), float)
R6 = np.asarray(r6.col("sr1_X"), float) / I_BIAS
o = np.argsort(B6); B6, R6 = B6[o], R6[o]
# what is d(1/B) actually delivered vs the Nyquist need at n=3.2e12?
F_L32 = float(luttinger_frequency(3.2e16))
need = 1.0 / (2 * F_L32)
for lo, hi in ((0.3, 1.0), (1.0, 2.0), (2.0, 5.0), (5.0, 10.0)):
    m = (B6 >= lo) & (B6 <= hi)
    d = np.abs(np.diff(1.0 / B6[m]))
    print(f"  run 6, B {lo:4.1f}-{hi:4.1f} T: max d(1/B) = {d.max():.4f} 1/T  "
          f"vs Nyquist need {need:.4f}  -> {'OK' if d.max() <= need else 'UNDERSAMPLED'}")
for blo in (0.3, 0.8, 1.0, 1.2):
    on = sdh_onset(R6, B6, b_lo=blo, r_full_scale=R_FS)
    tn = ", ".join(f"{t.freq:.1f}{'*' if getattr(t,'censored',False) else ''}" for t in on.tones[:5])
    print(f"  sdh_onset(b_lo={blo}): onset_b = {on.onset_b:.3f} T   tones: {tn}  (*=censored@edge)")

print()
print("#" * 74)
print("# 2. Dynamic range — worst corner (low n x high B), fixed sensitivity")
print("#" * 74)
r5 = open_run("data/5")
vtg5 = np.asarray(r5.col("k_2400_tg_volt"), float)
vbg5 = np.asarray(r5.col("k_2400_bg_volt"), float)
R5 = np.asarray(r5.col("sr1_X"), float) / I_BIAS
n5, D5 = calc_nD(vtg5, vbg5, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
sel = np.abs(D5) < 0.02
for ntarg in (2.0, 2.4, 2.8, 3.2):
    k = sel & (np.abs(n5 - ntarg) < 0.08)
    if k.any():
        print(f"  run 5 (B=0): R(n={ntarg:+.1f}e12, |D|<0.02) = {np.median(R5[k]):6.1f} Ohm  (N={k.sum()})")
# measured MR factor from run 6 at n=3.2
r0_6 = np.median(R6[B6 < 0.1])
print(f"  run 6 (n=+3.2e12): R(B~0) = {r0_6:.1f}, R_max = {R6.max():.1f} Ohm at B = {B6[np.argmax(R6)]:.2f} T"
      f"  -> MR factor {R6.max()/r0_6:.1f}x")
r7 = open_run("data/7")
B7 = np.asarray(r7.col("magnet_field"), float); R7 = np.asarray(r7.col("sr1_X"), float) / I_BIAS
print(f"  run 7 (n=-1.2e12): R(0.3 T) = {R7[np.argmin(abs(B7-0.3))]:.1f}, R_max = {R7.max():.1f} Ohm"
      f"  -> MR factor {R7.max()/R7[np.argmin(abs(B7-0.3))]:.1f}x")

print()
print("#" * 74)
print("# 3. Model tone table over the candidate window (u_D = 0)")
print("#" * 74)
print("  n[e12]  F_L    ABAB F (light,heavy)     partition      ABAB m*        ABCA F   ABA(3L) F      ABA part")
for n in (1.2, 1.6, 2.0, 2.4, 2.8, 3.2):
    FL = float(luttinger_frequency(n * 1e16))
    _, orb = fc.abab_fs(n * 1e16)
    abab = sorted(f for f, _ in orb)
    ms = [m for _, m in fc.abab_mstar(n * 1e16)]
    _, topo, ncomp, nfreq, Ftot = fc.abca_fs(n * 1e16)
    try:
        _, torb = trimod.aba_fs(n * 1e16)
        tf = sorted(x[0] for x in torb)
        tpart = [round(x / sum(tf), 3) for x in tf]
    except Exception as e:
        tf, tpart = [], str(e)[:30]
    print(f"  {n:+.2f}  {FL:6.2f}  {['%.2f'%f for f in abab]!s:24s} "
          f"{[round(f/sum(abab),3) for f in abab]!s:15s} {['%.3f'%m for m in ms]!s:14s} "
          f"{Ftot:6.2f}   {['%.2f'%x for x in tf]!s:14s} {tpart}")

print()
print("#" * 74)
print("# 4. Sampling / resolution design (electron side, D = 0)")
print("#" * 74)
N_MIN, N_MAX = 2.0, 3.2
for nn in (N_MIN, N_MAX):
    vt, vb = calc_gate_voltages(nn, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
    print(f"  n = {nn:+.2f}e12, D = 0 -> (Vtg, Vbg) = ({vt:+.4f}, {vb:+.4f}) V  "
          f"[TG margin {TG_MAX-vt:+.4f} / {vt-TG_MIN:+.4f}; BG margin {BG_MAX-vb:+.4f} / {vb-BG_MIN:+.4f}]")
# also the n at the TG ceiling
print(f"  n at Vtg = +1.000 (D=0): {calc_nD(1.0, calc_gate_voltages(3.2,0.0,CAL['c_tg'],CAL['c_bg'],CAL['n_offset'],CAL['D_offset'])[1], CAL['c_tg'],CAL['c_bg'],CAL['n_offset'],CAL['D_offset'])}")

FL_max = float(luttinger_frequency(N_MAX * 1e16))
d_invB_nyq = 1.0 / (2 * FL_max)
d_invB_pref = 1.0 / (3 * FL_max)
print(f"\n  Nyquist on B: F_L(n_max={N_MAX}) = {FL_max:.2f} T -> d(1/B) <= {d_invB_nyq:.5f} "
      f"(prefer {d_invB_pref:.5f}) 1/T")
E_H = 2.417989e14  # e/h, per T per m^2
for B_LO in (0.5, 0.6, 0.7, 0.8, 1.0):
    B_MAX = 10.0
    span = 1 / B_LO - 1 / B_MAX
    N_B = int(np.ceil(span / d_invB_pref)) + 1
    dF = 1 / span
    dn_ray = 4 * E_H * B_LO / 1e16          # in 1e12 cm^-2
    N_n = int(np.ceil((N_MAX - N_MIN) / (dn_ray / 2))) + 1
    # partner-tone periods at the low-n edge
    _, orb = fc.abab_fs(N_MIN * 1e16)
    f_part = min(f for f, _ in orb)
    f_heavy = max(f for f, _ in orb)
    FL_lo = float(luttinger_frequency(N_MIN * 1e16))
    print(f"  B_lo={B_LO:.1f}: 1/B span {span:.3f} | N_B={N_B:3d} | dF={dF:.2f} T | "
          f"partner({f_part:.1f} T)@n_min: {span*f_part:.1f} periods (need>=5) | "
          f"heavy-vs-F_L@n_min sep {FL_lo-f_heavy:.2f} T = {(FL_lo-f_heavy)/dF:.1f} dF (need>=2) | "
          f"n-ray dn={dn_ray:.4f} -> N_n>={N_n}")

print()
print("#" * 74)
print("# 5. Cost model — calibrated on this session")
print("#" * 74)
m5 = json.load(open("data/5/metadata.json"))
t5 = m5["end_time"] - m5["start_time"]
print(f"  run 5 (gatemap, fast_delay=1.0, NPLC=1): 63 rows x 66 pts = {t5:.0f} s"
      f"  -> t_pt = 1.098 s measured (delay+0.098 s readback overhead)")
m6 = json.load(open("data/6/metadata.json"))
t6 = m6["end_time"] - m6["start_time"]
print(f"  run 6 (field sweep, 921 pts, 10 T): {t6:.0f} s; bare traverse {10/0.137*60:.0f} s"
      f"  -> per-point field overhead {(t6-10/0.137*60)/921:.2f} s/pt")
print(f"  run 7: {json.load(open('data/7/metadata.json'))['end_time']-json.load(open('data/7/metadata.json'))['start_time']:.0f} s"
      f" (486 pts, 9.7 T) -> {( (json.load(open('data/7/metadata.json'))['end_time']-json.load(open('data/7/metadata.json'))['start_time']) - 9.7/0.137*60)/486:.2f} s/pt")

TAU, K = 0.3, 7
fast_delay = round(K * TAU, 2)
t_pt = fast_delay + 0.098
B_LO, B_MAX = 0.7, 10.0
span = 1 / B_LO - 1 / B_MAX
N_B = int(np.ceil(span / d_invB_pref)) + 1
dn_ray = 4 * E_H * B_LO / 1e16
N_n = int(np.ceil((N_MAX - N_MIN) / (dn_ray / 2))) + 1
vt_lo, vb_lo = calc_gate_voltages(N_MIN, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
vt_hi, vb_hi = calc_gate_voltages(N_MAX, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
flyback = (abs(vt_hi - vt_lo) / 0.005 + abs(vb_hi - vb_lo) / 0.005) * 0.006
slow_delay = 3.0
traverse = (B_MAX - B_LO) / 0.137 * 60
meas = N_B * N_n * t_pt
fixed = N_B * (slow_delay + flyback)
print(f"\n  DESIGN: n {N_MIN}->{N_MAX}e12 at D=0, N_n={N_n}; B {B_LO}->{B_MAX} T uniform-1/B, N_B={N_B}")
print(f"          fast_delay = {fast_delay} s (= {K} tau at tau={TAU} s / 24 dB), t_pt = {t_pt:.3f} s")
print(f"          d(1/B) = {span/(N_B-1):.5f} 1/T (need <= {d_invB_nyq:.5f}, prefer {d_invB_pref:.5f})")
print(f"          dn = {(N_MAX-N_MIN)/(N_n-1):.4f}e12 (ray floor {dn_ray/2:.4f}e12)")
print(f"          gate flyback/row = {flyback:.2f} s, slow_delay = {slow_delay} s")
print(f"  COST:   traverse {traverse/3600:.2f} h + grid {meas/3600:.2f} h + row fixed {fixed/3600:.2f} h"
      f"  = {(traverse+meas+fixed)/3600:.2f} h")
print(f"          + 10% contingency -> {(traverse+meas+fixed)*1.10/3600:.2f} h")
print(f"          total points {N_B*N_n}")
