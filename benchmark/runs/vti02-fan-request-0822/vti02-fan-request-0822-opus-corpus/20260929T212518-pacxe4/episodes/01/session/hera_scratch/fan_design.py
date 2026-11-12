"""Fan design numbers: R anchors along D=0 (run 5 gatemap, B=0), run-6 MR + phase check,
Nyquist/resolution/cost arithmetic. Prints the whole design table."""
import json
from pathlib import Path
import numpy as np
from hera.analysis import open_run, fan_grids, resistance_grids, luttinger_frequency
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

HERE = Path("/home/hera/measurements/zack/20260822-vti-02")
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN, TG_MAX, BG_MIN, BG_MAX = -0.3, 1.0, -1.3, 2.0

print("=== D=0 line: gate voltages and validator headroom ===")
for n in [0.8, 1.0, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2, 3.27]:
    vt, vb = calc_gate_voltages(n, 0.0, **CAL)
    nn, dd = calc_nD(vt, vb, **CAL)
    print(f"  n={n:+.2f}e12 -> Vtg={vt:+.4f} Vbg={vb:+.4f}  (roundtrip n={nn:+.3f} D={dd:+.4f})"
          f"{'  <-- TG over limit' if vt > TG_MAX else ''}")

# ---- R anchors at B = 0 from run 5 gatemap, along the D = 0 line
g = fan_grids(str(HERE / "data" / "5")); rg = resistance_grids(g)
R = np.abs(rg.R["sr1"]); Vbg = g.slow
fs = g.meta["fast_setpoints"]; Vtg = np.asarray(fs[0] if isinstance(fs[0], list) else fs)
print("\n=== B = 0 R(n) along D = 0 (run 5 gatemap, nearest grid point) ===")
anchors = {}
for n in [1.2, 1.6, 2.0, 2.4, 2.8, 3.2]:
    vt, vb = calc_gate_voltages(n, 0.0, **CAL)
    i = int(np.argmin(np.abs(Vbg - vb))); j = int(np.argmin(np.abs(Vtg - vt)))
    anchors[n] = float(R[i, j])
    print(f"  n={n:+.2f}e12  (Vtg {vt:+.3f}/{Vtg[j]:+.3f}, Vbg {vb:+.3f}/{Vbg[i]:+.3f})  R = {R[i,j]:7.1f} Ohm")
# hole-side anchor for comparison
vt, vb = calc_gate_voltages(-1.2, 0.0, **CAL)
i = int(np.argmin(np.abs(Vbg - vb))); j = int(np.argmin(np.abs(Vtg - vt)))
print(f"  n=-1.20e12 (hole, run-7 spot)                           R = {R[i,j]:7.1f} Ohm  [run 7 measured 130 Ohm @0.3 T]")

# ---- run 6 phase check: is X the whole signal?
r6 = open_run(HERE / "data" / "6")
B6 = r6.col("magnet_field"); X6 = np.abs(r6.col("sr1_X")); P6 = r6.col("sr1_P")
I6 = 10e-9
print("\n=== run 6: phase and |R| = |X|/cos(theta) ===")
for lo, hi in [(0.5, 2), (2, 5), (5, 7.4), (7.6, 10)]:
    m = (B6 >= lo) & (B6 < hi)
    Rx = X6[m] / I6; Rm = X6[m] / np.cos(np.deg2rad(P6[m])) / I6
    print(f"  B {lo}-{hi} T: phase med {np.median(P6[m]):+6.1f} deg (ptp {np.ptp(P6[m]):.0f});"
          f" R_from_X med {np.median(Rx):7.1f}  |R| med {np.median(np.abs(Rm)):7.1f} Ohm")
mr = {}
for lo, hi in [(0.0, 0.3), (9.5, 10.0)]:
    m = (B6 >= lo) & (B6 <= hi); mr[lo] = float(np.median(X6[m] / I6))
print(f"  run 6 MR factor n=+3.2e12: R(0 T)={mr[0.0]:.1f} -> R(10 T)={mr[9.5]:.1f}  = x{mr[9.5]/max(mr[0.0],1e-9):.1f}")
r7 = open_run(HERE / "data" / "7")
B7 = r7.col("magnet_field"); X7 = np.abs(r7.col("sr1_X"))
m_lo = B7 < 0.5; m_hi = B7 > 9.5
print(f"  run 7 MR factor n=-1.2e12: R(0.3 T)={np.median(X7[m_lo])/I6:.1f} -> R(10 T)={np.median(X7[m_hi])/I6:.1f}"
      f"  = x{np.median(X7[m_hi])/np.median(X7[m_lo]):.1f}")

# ---- design arithmetic
print("\n" + "=" * 72)
n_lo, n_hi = 1.20, 3.20
B_lo, B_hi = 1.0, 10.0
FL_hi = luttinger_frequency(n_hi * 1e16)   # n in 1e12 cm^-2 -> m^-2 = n*1e16
FL_lo = luttinger_frequency(n_lo * 1e16)
print(f"F_L(n_max={n_hi}e12) = {FL_hi:.2f} T ;  F_L(n_min={n_lo}e12) = {FL_lo:.2f} T")
dinvB_max = 1 / (3 * FL_hi)
print(f"Nyquist x3 on F_L(n_max): d(1/B) <= {dinvB_max:.5f} 1/T")
for N_B in [81, 91, 101]:
    d = (1 / B_lo - 1 / B_hi) / (N_B - 1)
    print(f"  N_B={N_B}: d(1/B)={d:.5f} -> Nyquist factor on F_L(n_max) = {1/(d*FL_hi):.2f}"
          f" ; dB at B_lo = {d*B_lo**2*1e3:.1f} mT, at B_hi = {d*B_hi**2*1e3:.0f} mT")
dn_ray = 4 * 1.602176634e-19 / 6.62607015e-34 * B_lo * 1e-16   # 1e12 cm^-2 per ray at B_lo
print(f"\nn-axis: LL ray spacing at B_lo={B_lo} T is dn = {dn_ray:.4f}e12 cm^-2")
for N_n in [51, 65, 81]:
    dn = (n_hi - n_lo) / (N_n - 1)
    print(f"  N_n={N_n}: dn={dn:.4f}e12 -> {dn_ray/dn:.2f} pts per ray"
          f" {'(>=3 OK)' if dn_ray/dn >= 3 else '(>=2 only)' if dn_ray/dn >= 2 else '(FAILS)'}")
dF = 1 / (1 / B_lo - 1 / B_hi)
print(f"\nresolution dF = 1/(1/{B_lo} - 1/{B_hi}) = {dF:.2f} T")
print(f"  ABAB-heavy vs ABCA-singleton separation at n_max: 0.28*F_L = {0.28*FL_hi:.1f} T  (need > 2dF = {2*dF:.1f} T)"
      f" -> {'OK' if 0.28*FL_hi > 2*dF else 'FAIL'}")
print("  >=5-period partner criterion (1/B_lo - 1/B_hi) >= 5/f_partner:")
for n in [1.2, 1.6, 1.9, 2.0, 2.4, 2.8, 3.2]:
    fp_ = 0.28 * luttinger_frequency(n * 1e16)
    need = 5 / fp_
    print(f"    n={n:+.2f}e12: f_partner~{fp_:5.2f} T, need span {need:.3f} (have {1/B_lo-1/B_hi:.3f})"
          f" -> {'OK' if need <= (1/B_lo-1/B_hi) else 'partner not claimable'}")

# ---- cost
N_B, N_n = 91, 65
fast_delay = 1.8
overhead = 0.101   # s/pt, measured: run 5 gatemap 4158 pts / 81.1 min minus row turnaround, nplci=1
vt_lo, vb_lo = calc_gate_voltages(n_lo, 0.0, **CAL); vt_hi, vb_hi = calc_gate_voltages(n_hi, 0.0, **CAL)
flyback = abs(vt_hi - vt_lo) / 5e-3 * 6e-3
ramp = (B_hi - B_lo) / 0.137 * 60
pts = N_B * N_n
t_pts = pts * (fast_delay + overhead)
t_rows = N_B * (flyback + 1.0 + 3.0)
print(f"\n=== cost: {N_B} B rows x {N_n} n points = {pts} pts ===")
print(f"  Vtg span {vt_lo:+.4f} -> {vt_hi:+.4f} ({abs(vt_hi-vt_lo)*1e3:.0f} mV), Vbg {vb_lo:+.4f} -> {vb_hi:+.4f}")
print(f"  per-point {fast_delay}+{overhead} = {fast_delay+overhead:.2f} s -> {t_pts/3600:.2f} h")
print(f"  row overhead {N_B} x (flyback {flyback:.2f} + slow_delay 1 + magnet settle 3) = {t_rows/60:.1f} min")
print(f"  field traverse {B_hi-B_lo:.1f} T at 0.137 T/min = {ramp/60:.1f} min")
print(f"  TOTAL = {(t_pts+t_rows+ramp)/3600:.2f} h   (+10% margin = {(t_pts+t_rows+ramp)*1.1/3600:.2f} h)")
