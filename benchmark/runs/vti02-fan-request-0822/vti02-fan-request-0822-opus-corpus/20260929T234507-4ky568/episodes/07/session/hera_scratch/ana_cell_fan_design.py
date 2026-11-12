"""Fan design (investigation Step 4) — both-axis Nyquist, resolution, dynamic range,
wall-clock. Every lever at its floor; this IS the proposal (landau-fan step 1)."""
import scipy.constants as cst
from hera.analysis import field_invB
from sharpelab_nb.gates import calc_gate_voltages

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)  # run 5
TAU = 0.30                                   # sr1 time constant, 24 dB/oct (read at bring-up)
B_LO, B_HI, N_B = 1.00, 10.0, 91             # B_lo = run-6 onset lower bound; B_hi = session cap
n_hi, n_lo, N_n = 3.20, 0.80, 61
FAST_DELAY, SLOW_DELAY = 6 * TAU, 1.0
T_READ = 0.098                               # per-point read overhead, calibrated on run 5

B_vec = field_invB(B_LO, B_HI, N_B)
ns = np.linspace(n_hi, n_lo, N_n)
Vtgs, Vbgs = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"],
                                CAL["n_offset"], CAL["D_offset"])
F_L = luttinger_frequency(np.abs(ns) * 1e12 * 1e4)
d_invB = abs(np.median(np.diff(1 / B_vec)))
dn = abs(ns[1] - ns[0])
dn_ray = 4 * cst.e / cst.h / 1e4 / 1e12 * B_LO         # ray spacing at the lowest B read, 1e12 cm^-2
dF = 1 / (1 / B_LO - 1 / B_HI)

print("B AXIS — uniform in 1/B (per-column SdH-FFT fan)")
print(f"  {N_B} rows, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T ; d(1/B) = {d_invB:.5f} 1/T")
print(f"  samples/period at F_L(n_max) = {F_L[0]:.1f} T : {1/(d_invB*F_L[0]):.2f}   [Nyquist floor 2, target 3]")
print(f"  dB: {B_vec[1]-B_vec[0]*1:.4f} T at the bottom row -> {B_vec[-1]-B_vec[-2]:.3f} T at the top")
print(f"  resolution dF = 1/(1/B_lo - 1/B_hi) = {dF:.2f} T")
print(f"    ABAB heavy (25.9) vs 3rd harmonic of the light tone (21.9): "
      f"{(25.9-21.9)/dF:.1f} x dF  [need > 2]")
print(f"    ABCA singleton (33.1) vs ABAB heavy (25.9):                 {(33.1-25.9)/dF:.1f} x dF")
print(f"  B-window-split halves (F_L-tone origin Verify): dF_half ~ "
      f"{1/(1/B_LO-1/np.sqrt(B_LO*B_HI)):.2f} T — marginal for the 21.9/25.9 pair; the")
print( "    n-dependence screen, not the split, is the primary harmonic discriminator here.")

print("\nn AXIS — ray Nyquist at the lowest B read")
print(f"  {N_n} pts, n {n_hi} -> {n_lo} e12 cm^-2 at D = 0 ; step {dn:.4f}e12")
print(f"  ray spacing g(e/h)B_lo = {dn_ray:.4f}e12 -> {dn_ray/dn:.2f} pts/ray "
      f"[floor 2; still {dn_ray/dn/1.15:.2f} under a 15% lever-arm scale error]")
print(f"  V_tg {Vtgs.min():+.4f} .. {Vtgs.max():+.4f} V  (limit [{-0.3:+.1f}, {1.0:+.1f}], "
      f"{1.0-Vtgs.max():.3f} V margin)")
print(f"  V_bg {Vbgs.min():+.4f} .. {Vbgs.max():+.4f} V  (limit [{-1.3:+.1f}, {2.0:+.1f}])")
print(f"  F_L across the fan: {F_L[-1]:.2f} -> {F_L[0]:.2f} T ; "
      f"periods in the 1/B record at the low-n edge: {F_L[-1]*(1/B_LO-1/B_HI):.1f}")

print("\nDYNAMIC RANGE — worst corner is low n x high B")
print("  anchors: run-5 gatemap R(n=+0.8e12, D=0, B=0) = 145 Ohm ; R(n=+3.2e12) = 56 Ohm")
print("           run 6 (n=+3.2e12) peaked at 523 Ohm at 8.8 T -> MR x9.3")
print("           run 7 (n=-1.2e12, R_B=0 = 144 Ohm - the matched low-|n| anchor) peaked 576 Ohm -> MR x4")
print("  -> worst corner projects to 600-1350 Ohm = 0.12-0.27 of the 5 kOhm FS at 50 uV.")
print("     Keep sr1 at 50 uV (the spot check's validated setting): 3.7x headroom at the")
print("     pessimistic projection, and the high-n/low-B corner still fills ~1% of range,")
print("     which delivered SNR 96 tones on run 6.")

t_pt = FAST_DELAY + T_READ
n_pts = N_B * N_n
retrace = max(np.ptp(Vtgs), np.ptp(Vbgs)) / 0.005 * 0.006
traverse = (B_HI - B_LO) / 0.137 * 60
turn = retrace + SLOW_DELAY + 3.0
tot = n_pts * t_pt + traverse + N_B * turn
print("\nWALL CLOCK  (measurement-dominated regime — landau-fan-vti cost model)")
print(f"  fast_delay {FAST_DELAY:.2f} s (6 tau, n-axis carries the extracted signal) "
      f"+ {T_READ:.3f} s reads (run-5 calibrated) = {t_pt:.3f} s/pt")
print(f"  grid {N_B} x {N_n} = {n_pts} pts          -> {n_pts*t_pt/3600:.2f} h")
print(f"  field traverse {B_HI-B_LO:.0f} T / 0.137 T/min -> {traverse/3600:.2f} h")
print(f"  row turnaround {turn:.1f} s x {N_B}        -> {N_B*turn/3600:.2f} h")
print(f"  TOTAL {tot/3600:.2f} h ; realistic with the session's 10% overrun = {tot*1.1/3600:.2f} h")
print(f"  + positioning 0 -> {B_LO:.1f} T bare ramp = {B_LO/0.137:.0f} min. Ends at 10 T.")
