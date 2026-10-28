"""Fan design numbers: timing calibration (runs 5, 6), onset on the fully-sampled (>=1 T) spot-check record,
R0(n) along D = 0 (run 5) for the dynamic-range corner, grid + price."""
import sys, json
import numpy as np
from pathlib import Path
from hera.analysis import (open_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency, fan_grids,
                           resistance_grids, field_invB, SdhOnsetError)
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
import fs_count_b0 as fs

D = Path(__file__).resolve().parents[1] / "data"
cal = json.load(open(Path(__file__).with_name("cal_run5.json")))
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)   # as used in runs 6/7

# --- timing, run 5 (gatemap, fast_delay 1.0, slow_delay 3)
r5 = open_run(D / "5"); t = r5.col("time"); nf = 66
dt = np.diff(t); intra = dt[np.arange(1, len(t)) % nf != 0]; inter = dt[np.arange(1, len(t)) % nf == 0]
print(f"run 5: intra-row dt median {np.median(intra):.3f} s (fast_delay 1.0 -> overhead {np.median(intra)-1.0:.3f} s/pt); "
      f"row turnaround median {np.median(inter):.2f} s (incl slow_delay 3)")
r6 = open_run(D / "6"); t6 = r6.col("time"); B6 = r6.col("magnet_field")
dt6 = np.diff(t6); dB6 = np.abs(np.diff(B6))
m = (B6[1:] > 1.05)
cf = np.polyfit(dB6[m], dt6[m], 1)
print(f"run 6 magnet set: dt = {cf[1]:.2f} s + {cf[0]:.1f} s/T * dB  (bare 1/0.137*60 = {60/0.137:.0f} s/T)")
t_set0, s_per_T = cf[1], cf[0]

# --- onset on the >=1 T (10 mT) portion of run 6 and run 7 (>=0.71 fully 20 mT anyway)
for rid, n, blo, sens in ((6, 3.2, 1.0, 50e-6), (7, -1.2, 0.3, 50e-6)):
    r = open_run(D / str(rid)); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); R = (r.col("sr1_X") / ch["sr1"].gain) / (r.col("sr0_X") / ch["sr0"].gain)
    o = np.argsort(B); B, R = B[o], R[o]
    try:
        on = sdh_onset(R, B, b_lo=blo, r_full_scale=sens / 10e-9)
        print(f"\nrun {rid} (n={n:+}) b_lo={blo}:"); print(on.summary())
    except SdhOnsetError as e:
        print(rid, "SdhOnsetError", e)
    for w in ((1.0, 10.0), (1.0, 8.0), (1.0, 6.0), (1.0, 4.0), (1.3, 8.0), (2.0, 8.0)):
        if rid == 7: continue
        f, sp = sdh_fft(R[:, None], B, b_range=w, bg_degree=5, log=False, nfft=4096)
        s = sp[0]; k = (f > 4) & (f < 45)
        from scipy.signal import find_peaks
        pk, _ = find_peaks(s[k], prominence=0.1 * s[k].max()); ff, ss = f[k], s[k]
        pk = pk[np.argsort(ss[pk])[::-1]][:6]
        print(f"  run6 FFT {w}: dF {1/(1/w[0]-1/w[1]):.2f} T: " + ", ".join(f"{ff[p]:.1f}({ss[p]/ss.max():.2f})" for p in sorted(pk)))

# --- R0(n) along D = 0 from run 5 (B = 0), for the dynamic-range corner
g = fan_grids(str(D / "5")); rg = resistance_grids(g); R5 = np.abs(rg.R["sr1"])
fsp = g.meta["fast_setpoints"]; Vtg5 = np.asarray(fsp[0] if isinstance(fsp[0], list) else fsp); Vbg5 = g.slow
from scipy.interpolate import RegularGridInterpolator
itp = RegularGridInterpolator((Vbg5, Vtg5), R5, bounds_error=False)
for n in (0.6, 0.8, 1.0, 1.2, 1.5, 2.0, 2.5, 3.0, 3.2):
    vt, vb = calc_gate_voltages(n, 0.0, **CAL)
    print(f"  R0 at n={n:+.1f}e12, D=0: (Vtg,Vbg)=({vt:+.3f},{vb:+.3f}) R={float(itp((vb, vt))):.0f} Ohm")

# --- model table across the window (scale 1)
print("\nmodel (scale 1): n, F_L, ABAB (light, heavy), ABCA F, m*")
for n in (1.0, 1.5, 2.0, 2.5, 3.0, 3.2):
    FL = float(luttinger_frequency(n * 1e16)); _, orbs = fs.abab_fs(n * 1e16); ms = fs.abab_mstar(n * 1e16)
    print(f"  {n:+.1f}: F_L {FL:5.1f} | ABAB " + ", ".join(f"{f:.1f}T/{mm:.3f}" for (f, _), (_, mm) in zip(orbs, ms)) +
          f" | ABCA {fs.abca_mstar(n*1e16)[0]:.1f}T/{fs.abca_mstar(n*1e16)[1]:.3f}")

# --- grid + price
n_hi, n_lo, N_n = 3.2, 1.0, 51
B_lo, B_hi = 1.0, 8.0
FLmax = float(luttinger_frequency(n_hi * 1e16))
dinv = 1 / (4 * FLmax)
N_B = int(np.ceil((1 / B_lo - 1 / B_hi) / dinv)) + 1
Bv = field_invB(B_lo, B_hi, N_B)
dinv_real = (1 / B_lo - 1 / B_hi) / (N_B - 1)
ns = np.linspace(n_hi, n_lo, N_n); Vt, Vb = calc_gate_voltages(ns, np.zeros_like(ns), **CAL)
ray = 4 * 2.417989e14 * B_lo / 1e16
print(f"\nGRID: N_B {N_B} (field_invB {B_lo}->{B_hi}), d(1/B) {dinv_real:.5f} -> F_Nyq {1/(2*dinv_real):.1f} T (F_L,max {FLmax:.1f}; {1/(dinv_real*FLmax):.2f} pts/period); "
      f"dB at B_lo {Bv[1]-Bv[0]:.4f} T, at B_hi {Bv[-1]-Bv[-2]:.3f} T")
print(f"      N_n {N_n}, dn {abs(ns[1]-ns[0]):.4f}e12 vs ray spacing at B_lo {ray:.4f}e12 -> {ray/abs(ns[1]-ns[0]):.2f} pts/ray")
print(f"      Vtg {Vt.min():+.4f}..{Vt.max():+.4f}, Vbg {Vb.min():+.4f}..{Vb.max():+.4f}; dF(record) {1/(1/B_lo-1/B_hi):.2f} T")
for fd in (1.8, 2.1):
    t_pt = fd + (np.median(intra) - 1.0)
    row = N_n * t_pt + 3.0 + 1.5   # slow_delay 3 + flyback
    ramp = s_per_T * (B_hi - B_lo) + t_set0 * N_B + s_per_T * B_lo + 60
    tot = N_B * row + ramp
    print(f"  fast_delay {fd}: t_pt {t_pt:.2f} s, row {row:.0f} s, magnet {ramp/60:.0f} min -> total {tot/3600:.2f} h (x1.07 = {1.07*tot/3600:.2f} h)")
