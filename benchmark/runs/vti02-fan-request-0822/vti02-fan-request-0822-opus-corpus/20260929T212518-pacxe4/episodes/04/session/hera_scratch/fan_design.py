"""Landau-fan design arithmetic for the stacking call: onset re-read on the well-sampled
part of run 6, model F(n) design table, Nyquist/resolution/cost model, dynamic-range anchor."""
import json, numpy as np, sys
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M
from hera.analysis import open_run, sdh_onset, sdh_fft, fan_grids, resistance_grids
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

h, e = 6.62607015e-34, 1.602176634e-19
FL = lambda n12: h / (4 * e) * abs(n12) * 1e16
CAL = json.load(open("hera_scratch/cal_run5.json"))
ct, cb, n0, D0 = CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]

print("=" * 78)
print("A. onset re-read on the ADEQUATELY SAMPLED part of run 6 (electron, n=+3.2e12)")
print("   run 6 grid: 50 mT below 1 T, 10 mT above -> Nyquist F = B^2/(2*dB):")
for B in (0.4, 0.6, 0.85, 1.0, 1.0, 2.0):
    dB = 0.05 if B < 1.0 else 0.01
    print(f"     B={B:.2f} T, dB={dB*1e3:.0f} mT -> d(1/B)={dB/B**2:.4f} 1/T, Nyquist F={B**2/(2*dB):5.1f} T")
run = open_run("data/6")
B = run.col("magnet_field"); R = (run.col("sr1_X") / 1.0) / (run.col("sr0_X") / -1e6)
o = np.argsort(B); B, R = B[o], R[o]
I_bias = float(np.nanmedian(np.abs(run.col("sr0_X") / -1e6)))
for blo in (0.85, 1.0):
    print(f"\n  --- sdh_onset(b_lo={blo}) ---")
    on = sdh_onset(R, B, b_lo=blo, r_full_scale=50e-6 / I_bias)
    print("   " + on.summary().replace("\n", "\n   "))

print("\n" + "=" * 78)
print("B. design table from the forward model (electron side, u_D = 0)")
print(f"  {'n12':>5} {'F_L':>6} {'ABAB f_part':>11} {'ABAB f_heavy':>12} {'part frac':>9} "
      f"{'dF<=f_p/5':>9} {'ABCA F':>7} {'m* l/h':>13}")
tab = {}
for n in [1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.8, 3.2]:
    _, orbs = M.abab_fs(n * 1e16); ms = M.abab_mstar(n * 1e16)
    fp, fh = orbs[0][0], orbs[1][0]
    Fa, _ = M.abca_mstar(n * 1e16)
    tab[n] = (fp, fh)
    print(f"  {n:5.2f} {FL(n):6.2f} {fp:11.2f} {fh:12.2f} {fp/FL(n):9.3f} {fp/5:9.3f} {Fa:7.2f} "
          f"{ms[0][1]:6.4f}/{ms[1][1]:6.4f}")

print("\n" + "=" * 78)
print("C. fan cost / resolution model.  dF = 1/(1/B_lo - 1/B_max);  partner needs dF <= f_p/5")
GE_H = 4 * e / h * 1e-4 / 1e12   # e12 cm^-2 per Tesla of ray spacing (g=4)
print(f"  ray spacing per Tesla: g*e/h = {GE_H:.4f} e12 cm^-2 / T")
dinvB = 1 / (3 * FL(3.2))        # Nyquist(x3) on F_L at n_max
print(f"  d(1/B) = 1/(3*F_L(3.2e12)) = {dinvB:.5f} 1/T  (Nyquist freq {1/(2*dinvB):.0f} T)")
T_PT = 1.15      # fast_delay 1.0 s (10 tau at tau=0.1) + 0.15 s reads/gate writes; run-5 calib: 1.10 s at fd=1.0
FLYBACK, SLOW_D, SETTLE = 1.6, 1.0, 3.0

def price(B_lo, B_max, n_lo, n_hi, n_pts=None, dinv=dinvB, verbose=True):
    dF = 1 / (1 / B_lo - 1 / B_max)
    dn_nyq = GE_H * B_lo / 2
    N_n = n_pts or int(np.ceil((n_hi - n_lo) / dn_nyq)) + 1
    dn = (n_hi - n_lo) / (N_n - 1)
    N_B = int(np.ceil((1 / B_lo - 1 / B_max) / dinv)) + 1
    trav = (B_max - B_lo) / 0.137 * 60
    row = SETTLE + FLYBACK + SLOW_D + N_n * T_PT
    tot = trav + N_B * row
    # lowest density at which the ABAB partner clears 5 periods
    nmin_ok = min([n for n in tab if tab[n][0] / 5 >= dF], default=None)
    if verbose:
        print(f"  B[{B_lo:.2f},{B_max:.1f}] n[{n_lo:.1f},{n_hi:.1f}] -> dF={dF:5.3f} T | "
              f"N_B={N_B:4d} N_n={N_n:4d} (dn={dn:.4f}, {dn_nyq/dn:.2f} pts/ray@B_lo) | "
              f"pts={N_B*N_n:6d} | {tot/3600:5.2f} h (x1.1 = {tot*1.1/3600:5.2f} h) | "
              f"partner>=5 periods for n>={nmin_ok}")
    return tot, N_B, N_n, dF

for blo in (0.3, 0.4, 0.5, 0.6, 0.7, 0.85, 1.0):
    for bmax in (6.0, 10.0):
        price(blo, bmax, 1.2, 3.2)
    print()
print("  -- trimmed n-window variants (floor the claim, keep the Nyquist) --")
for blo in (0.3, 0.4, 0.5):
    price(blo, 6.0, 2.0, 3.2)
    price(blo, 6.0, 2.4, 3.2)

print("\n" + "=" * 78)
print("D. dynamic range: R at D=0 along the electron n-line (run 5, B=0) x MR from runs 6/7")
g = fan_grids("data/5"); rg = resistance_grids(g)
Rm = np.abs(rg.R["sr1"]); Vbg = g.slow
fs = g.meta["fast_setpoints"]; Vtg = np.asarray(fs[0] if isinstance(fs[0], list) else fs)
N, D = calc_nD(Vtg[None, :], Vbg[:, None], ct, cb, n_offset=n0, D_offset=D0)
for nq in (1.2, 1.6, 2.0, 2.4, 2.8, 3.2):
    d = np.abs(N - nq) + 3 * np.abs(D)
    i, j = np.unravel_index(np.argmin(d), d.shape)
    print(f"  n={nq:+.2f}e12, D={D[i,j]:+.3f}: R(B=0) = {Rm[i,j]:6.1f} Ohm   (Vtg {Vtg[j]:+.3f}, Vbg {Vbg[i]:+.3f})")
for rid, lbl in ((6, "electron n=+3.2"), (7, "hole n=-1.2")):
    r = open_run(f"data/{rid}")
    b = r.col("magnet_field"); rr = (r.col("sr1_X") / 1.0) / (r.col("sr0_X") / -1e6)
    lo = np.nanmedian(rr[np.abs(b) < 0.15]) if (np.abs(b) < 0.15).any() else np.nanmedian(rr[b < 0.4])
    for bt in (6.0, 10.0):
        m = np.abs(b - bt) < 0.15
        if m.any(): print(f"  run {rid} ({lbl}): R(B~{bt:.0f} T) = {np.nanmedian(rr[m]):6.1f} Ohm, "
                          f"R(low B) = {lo:5.1f} -> MR x{np.nanmedian(rr[m])/lo:.2f}")

print("\n" + "=" * 78)
print("E. gate voltages on the fan n-line (D = 0) vs validators [-0.3,1.0] / [-1.3,2.0]")
for nq in (1.2, 2.0, 2.4, 3.2):
    vt, vb = calc_gate_voltages(nq, 0.0, ct, cb, n0, D0)
    print(f"  n={nq:+.2f}e12 -> Vtg {vt:+.4f}, Vbg {vb:+.4f}  "
          f"{'OK' if -0.3 <= vt <= 1.0 and -1.3 <= vb <= 2.0 else 'VIOLATION'}")
print(f"  I_bias = {I_bias*1e9:.3f} nA; 50 uV FS = {50e-6/I_bias:.0f} Ohm; 20 uV FS = {20e-6/I_bias:.0f} Ohm")

print("\n" + "=" * 78)
print("F. low-field extension (uniform 1/B, 0.3 -> 1.0 T at n=+3.2e12, tau 0.3 s / 3 s settle)")
for bext in (0.25, 0.3, 0.35):
    Nx = int(np.ceil((1 / bext - 1 / 1.0) / dinvB)) + 1
    dB_lo = dinvB * bext**2
    cost = Nx * 3.15 + (1.0 - bext) / 0.137 * 60 + (bext - 0.003) / 0.137 * 60
    print(f"  B_lo={bext:.2f}: N={Nx:4d} pts, dB at low edge {dB_lo*1e3:5.2f} mT ({dB_lo/0.137*1e3:.1f} mA), "
          f"~{cost/60:4.1f} min (x1.1 = {cost*1.1/60:4.1f}) | combined with run 6: "
          f"dF = {1/(1/bext - 1/10.0):.3f} T")
