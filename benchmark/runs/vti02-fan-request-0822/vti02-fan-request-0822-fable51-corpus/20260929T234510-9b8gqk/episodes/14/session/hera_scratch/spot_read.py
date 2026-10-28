"""Spot-check read (runs 6 electron n=+3.2, 7 hole n=-1.2): raw R(B), dR vs 1/B, FFT windows, tones vs F_L/model;
run-5 R(n) along D=0 for fan sensitivity sizing; run-5 gate-axis timing."""
import numpy as np, json, sys, warnings
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_fft, sdh_onset, luttinger_frequency, fan_grids, resistance_grids
from sharpelab_nb.gates import calc_nD, calc_gate_voltages
sys.path.insert(0, '/home/hera/measurement_env/hera/models/tetralayer_fs_count'); import fs_count_b0 as M
CAL = json.load(open('hera_scratch/cal_run5.json')); c_tg, c_bg, n_off, D_off = CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset']
I_BIAS = 1e-8

def load(rid):
    r = open_run(f'data/{rid}'); B = r.col('magnet_field'); R = r.col('sr1_X') / I_BIAS
    o = np.argsort(B); return B[o], R[o], r

def spectrum(B, R, lo, hi, deg=5, nfft=4096):
    f, s = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=deg, log=False, nfft=nfft)
    return f, s[0]

def peaks(f, s, fmax=60, rel=0.04):
    m = f <= fmax; f, s = f[m], s[m]
    pk, pr = find_peaks(s, prominence=rel * s.max())
    return sorted(zip(f[pk], s[pk]), key=lambda t: -t[1])[:10]

fig, axs = plt.subplots(2, 3, figsize=(17, 8))
for row, (rid, n) in enumerate([(6, 3.2), (7, -1.2)]):
    B, R, r = load(rid); FL = luttinger_frequency(n * 1e16)
    ax = axs[row, 0]; ax.plot(B, R, lw=0.6); ax.set_xlabel('B (T)'); ax.set_ylabel('Rxx sr1 (Ohm)'); ax.set_title(f'run {rid}: n = {n:+.1f}e12, D = 0 — raw')
    # background-subtracted vs 1/B above 1 T
    m = B >= 1.0; cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    ax = axs[row, 1]; ax.plot(1 / B[m], dR, lw=0.6); ax.set_xlabel('1/B (1/T)'); ax.set_ylabel('dRxx (Ohm), deg-5 bg in B'); ax.set_title(f'run {rid}: dR vs 1/B (B > 1 T)')
    ax = axs[row, 2]
    wins = [(1.0, 10.0), (1.0, 3.5), (3.5, 10.0), (1.6, 10.0)] if rid == 6 else [(1.0, 10.0), (1.0, 3.5), (3.5, 10.0), (2.0, 10.0)]
    print(f"\n=== run {rid}: n = {n:+.1f}e12, F_L = {FL:.1f} T; R range {R.min():.0f}..{R.max():.0f} Ohm; R(B<0.5) med {np.median(R[B<0.5]):.0f}, R(B>9.5) med {np.median(R[B>9.5]):.0f} max {R[B>9.5].max():.0f}")
    print("  model ABAB", [(round(F, 2), round(mm, 3)) for F, mm in M.abab_mstar(n * 1e16)], " ABCA F", round(M.abca_fs(n * 1e16)[4], 2))
    nB = n - 0.426 if n > 0 else n - 0.426
    print(f"  region B (n_A - 0.43): n_B = {nB:+.2f} -> F_L,B = {luttinger_frequency(abs(nB)*1e16):.1f} T; ABAB_B", [round(F, 2) for F, _ in M.abab_mstar(nB * 1e16)])
    for (lo, hi) in wins:
        f, s = spectrum(B, R, lo, hi); dF = 1 / (1 / lo - 1 / hi)
        ax.plot(f, s / s[f > 2].max() + 0.0, lw=0.8, label=f'[{lo},{hi}] T, dF={dF:.2f}')
        pk = peaks(f, s)
        print(f"  window [{lo},{hi}] dF={dF:.2f} T: peaks " + ", ".join(f"{ff:.1f}T({ss/ s[f>2].max():.2f})" for ff, ss in pk if ff > 1.5))
    for k in range(1, 6): ax.axvline(7.1 * k if rid == 6 else 6.6 * k, color='0.7', ls=':', lw=0.7)
    ax.axvline(FL, color='r', ls='--', lw=1, label=f'F_L={FL:.1f}')
    for F, _ in M.abab_mstar(n * 1e16): ax.axvline(F, color='g', ls='-.', lw=0.8)
    ax.set_xlim(0, 60); ax.set_xlabel('F (T)'); ax.set_ylabel('FFT amp (norm)'); ax.legend(fontsize=7); ax.set_title(f'run {rid}: SdH FFT, windows (red F_L, green ABAB model, dotted k x f1)')
fig.tight_layout(); fig.savefig('hera_scratch/spot_read.png', dpi=110)

# --- run 5: R(n) along the D = 0 line (fan fast axis) for sensitivity sizing; timing
g = fan_grids('data/5'); rg = resistance_grids(g); R5 = np.abs(rg.R['sr1']); Vbg = g.slow
fs = g.meta['fast_setpoints']; Vtg = np.asarray(fs[0] if isinstance(fs[0], list) else fs)
ns = np.linspace(-1.2, 3.2, 45); Vt, Vb = calc_gate_voltages(ns, np.zeros_like(ns), c_tg, c_bg, n_off, D_off)
from scipy.interpolate import RegularGridInterpolator
itp = RegularGridInterpolator((Vbg, Vtg), R5, bounds_error=False, fill_value=np.nan)
Rn = itp(np.c_[Vb, Vt])
print("\nrun 5 R(n) along D=0 (B=0):", ", ".join(f"{a:+.1f}:{b:.0f}" for a, b in zip(ns[::4], Rn[::4])))
r5 = open_run('data/5'); t = r5.col('time'); print(f"run 5 timing: {len(t)} pts, {(t[-1]-t[0])/(len(t)-1):.3f} s/pt incl. row turnaround; fast_delay 1.0, slow_delay 3.0; total {(t[-1]-t[0])/60:.1f} min")
# per-point within a row: median dt between consecutive points
dt = np.diff(t); print(f"  median in-row dt {np.median(dt):.3f} s; row turnaround (95th pct) {np.percentile(dt, 98):.1f} s")
# fan fast axis voltages
for nn in (1.0, 3.2):
    print(f"  n={nn}: (Vtg, Vbg) = {calc_gate_voltages(nn, 0.0, c_tg, c_bg, n_off, D_off)}")
# model F(n) table for the fan window
print("\nmodel F(n) electron side (ABAB light/heavy, ABCA, F_L):")
for nn in np.arange(1.0, 3.21, 0.2):
    ab = [round(F, 2) for F, _ in M.abab_mstar(nn * 1e16)]
    print(f"  n={nn:.1f}: ABAB {ab}  ABCA {M.abca_fs(nn*1e16)[4]:.2f}  F_L {luttinger_frequency(nn*1e16):.2f}")
