"""Fan design numbers: model F(n)/m*(n) electron side, D=0 window inside validators,
run-6 onset on the Nyquist-valid record, global scale from the run-6 peak set."""
import sys, json
import numpy as np
from pathlib import Path
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency

sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
import fs_count_b0 as M
HERE = Path(__file__).resolve().parent.parent
CAL = json.load(open(HERE / "hera_scratch/cal_run5.json"))
c_tg, c_bg, n0, D0 = CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]

# --- D = 0 electron window inside validators
ns = np.arange(0.0, 4.0, 0.01)
V = np.array([calc_gate_voltages(n, 0.0, c_tg, c_bg, n0, D0) for n in ns])
ok = (V[:, 0] >= -0.3) & (V[:, 0] <= 1.0) & (V[:, 1] >= -1.3) & (V[:, 1] <= 2.0)
print(f"D=0 electron window inside validators: n <= {ns[ok].max():.2f}e12; at n=3.3: V={calc_gate_voltages(3.3,0,c_tg,c_bg,n0,D0)}")
for n in (1.0, 1.5, 2.0, 3.25, 3.3):
    print(f"  n={n}: (Vtg,Vbg)={np.round(calc_gate_voltages(n,0,c_tg,c_bg,n0,D0),4)}")

# --- model table
print("\nn    F_L   ABAB orbits (F, m*)                 ABCA (F, m*)")
for n in (1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 3.2, 3.3):
    nm = n * 1e16
    ab = M.abab_fs(nm)[1]; am = M.abab_mstar(nm); ca = M.abca_mstar(nm)
    print(f"{n:4.2f} {float(luttinger_frequency(nm)):5.1f}  " + "  ".join(f"({f:.2f},{m:.3f})" for f, m in am) + f"   ({ca[0]:.1f},{ca[1]:.3f})")

# --- run 6 onset on the Nyquist-valid record (10 mT above 1 T; 50 mT valid for F<=7 T only above 0.85 T)
r = open_run(HERE / "data/6"); B = r.col("magnet_field"); R = np.abs(r.col("sr1_X") / (r.col("sr0_X") / -1e6))
o = np.argsort(B); B, R = B[o], R[o]
for blo in (0.85, 1.0):
    on = sdh_onset(R, B, b_lo=blo, r_full_scale=50e-6 / 9.9e-9)
    print(f"\n--- run 6 sdh_onset b_lo={blo}"); print(on.summary())
r7 = open_run(HERE / "data/7"); B7 = r7.col("magnet_field"); R7 = np.abs(r7.col("sr1_X") / (r7.col("sr0_X") / -1e6))
o = np.argsort(B7); B7, R7 = B7[o], R7[o]

# --- B-window split, wide windows, run 6
print("\nrun 6 FFT window ladder (deg 5):")
for bl, bh in ((1.0, 10), (1.3, 10), (1.0, 4.0), (1.5, 5.0), (2.0, 10), (3.0, 10)):
    f, S = sdh_fft(R[:, None], B, b_range=(bl, bh), bg_degree=5, nfft=8192); s = S[0]
    pk = [(f[i], s[i]) for i in range(1, len(s) - 1) if s[i] > s[i-1] and s[i] > s[i+1] and 3 < f[i] < 60]
    top = s[(f > 3) & (f < 60)].max()
    pk = [p for p in pk if p[1] > 0.12 * top]
    print(f"  [{bl},{bh}] dF={1/(1/bl-1/bh):.2f}: " + ", ".join(f"{a:.1f}({b/top:.2f})" for a, b in pk))
print("\nrun 7 FFT window ladder (deg 5):")
for bl, bh in ((0.6, 10), (1.0, 10), (0.6, 3.0), (1.5, 10)):
    f, S = sdh_fft(R7[:, None], B7, b_range=(bl, bh), bg_degree=5, nfft=8192); s = S[0]
    pk = [(f[i], s[i]) for i in range(1, len(s) - 1) if s[i] > s[i-1] and s[i] > s[i+1] and 2 < f[i] < 40]
    top = s[(f > 2) & (f < 40)].max()
    pk = [p for p in pk if p[1] > 0.12 * top]
    print(f"  [{bl},{bh}] dF={1/(1/bl-1/bh):.2f}: " + ", ".join(f"{a:.1f}({b/top:.2f})" for a, b in pk))

# --- global scale from run 6 pair: f1+f2 = s*F_L
FL6 = float(luttinger_frequency(3.2e16))
for f1, f2 in ((7.1, 22.2),):
    s = (f1 + f2) / FL6
    ab = [f for f, _ in M.abab_fs(3.2e16 * s)[1]]
    print(f"\nrun 6 pair {f1}+{f2} = {f1+f2:.1f} T = {s:.3f} F_L(3.2) -> n_eff {3.2*s:.2f}e12; model ABAB at n_eff: {np.round(ab,2)}; "
          f"partition {f1/(f1+f2):.3f}/{f2/(f1+f2):.3f}")
# resistance headroom: run 6/7 maxima
print(f"\nR max run 6 {R.max():.0f} Ohm (B={B[np.argmax(R)]:.2f}); run 7 {R7.max():.0f} Ohm; R(B<0.1) run6 {R[B<0.1].mean():.0f}")
