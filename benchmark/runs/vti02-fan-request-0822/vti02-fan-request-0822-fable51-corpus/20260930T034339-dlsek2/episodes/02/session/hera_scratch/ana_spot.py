"""Runs 6/7 — sdh-spot-check at D = 0: raw Rxx(B) first, then onset + windowed 1/B FFTs against F_L and the
tetralayer FS-count model (ABAB pair vs ABCA singleton), and the Luttinger sum / global density scale."""
import sys, warnings
from scipy.signal import find_peaks
from hera.analysis import sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M

SENS = 50e-6
def spot(rid):
    r = open_run(str(Path(file_path) / str(rid)))
    B = r.col("magnet_field"); I = r.col("sr0_X") / -1e6; R = r.col("sr1_X") / I
    o = np.argsort(B); return r, B[o], R[o], float(np.median(I))

runs = {6: (+3.2, 1.0, [(1.0, 3.0), (1.5, 6.0), (2.0, 10.0)]), 7: (-1.2, 0.3, [(0.7, 2.5), (1.0, 5.0), (2.0, 10.0)])}
fig, ax = plt.subplots(1, 2, figsize=(14, 4.2))
peaks = {}
for k, (rid, (n12, blo, wins)) in enumerate(runs.items()):
    r, B, R, I = spot(rid)
    FL = luttinger_frequency(abs(n12) * 1e16)
    ax[k].plot(B, R, lw=0.7); ax[k].set_xlabel("B (T)"); ax[k].set_ylabel("Rxx = sr1_X / (sr0_X/-1e6)  (Ohm)")
    ax[k].set_title(f"run {rid} raw — {'electron' if n12 > 0 else 'hole'} side n = {n12:+.1f}e12, D = 0, sr1 {SENS*1e6:.0f} uV, I = {I*1e9:.2f} nA")
    print(f"===== run {rid}: n = {n12:+.2f}e12, F_L = (h/4e)|n| = {FL:.1f} T; T_sample {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K; R {R.min():.0f}..{R.max():.0f} Ohm =====")
    ab = M.abab_fs(n12 * 1e16)[1]; mm = M.abab_mstar(n12 * 1e16); ac = M.abca_fs(n12 * 1e16)
    print(f"  model: ABAB pair F = {[round(f,1) for f,_ in ab]} T (m* {[round(m,3) for _,m in mm]}); ABCA singleton F = {ac[4]:.1f} T ({ac[1]})")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            on = sdh_onset(R, B, b_lo=blo, r_full_scale=SENS / I); print("  " + on.summary().replace("\n", "\n  "))
        except SdhOnsetError as e: print("  SdhOnsetError:", e)
    peaks[rid] = []
    for a, b in wins:
        f, sp = sdh_fft(R[:, None], B, b_range=(a, b), bg_degree=5, log=False); sp = sp[0]; m = (f > 1) & (f < 60)
        pk, pr = find_peaks(sp[m], prominence=0.05 * sp[m].max())
        top = sorted(zip(pr["prominences"], f[m][pk]), reverse=True)[:5]
        peaks[rid].append((a, b, f[m], sp[m] / sp[m].max(), [ff for _, ff in top]))
        print(f"  FFT {a}-{b} T (dF = {1/(1/a-1/b):.2f} T): F = " + ", ".join(f"{ff:.1f} ({ff/FL:.2f} F_L)" for _, ff in top))
fig.tight_layout(); plt.show()

fig, ax = plt.subplots(2, 3, figsize=(15, 7))
for k, rid in enumerate(runs):
    n12 = runs[rid][0]; FL = luttinger_frequency(abs(n12) * 1e16)
    ab = [f for f, _ in M.abab_fs(n12 * 1e16)[1]]
    for j, (a, b, f, sp, top) in enumerate(peaks[rid]):
        a_ = ax[k, j]; a_.plot(f, sp, lw=1)
        a_.axvline(FL, color="r", ls="--", lw=0.8, label=f"F_L {FL:.1f}")
        for q, fa in enumerate(ab): a_.axvline(fa, color="g", ls=":", lw=0.8, label="model ABAB pair" if q == 0 else None)
        for ff in top[:4]: a_.annotate(f"{ff:.1f}", (ff, np.interp(ff, f, sp)), fontsize=8)
        a_.set_title(f"run {rid}: FFT in 1/B, {a}-{b} T"); a_.set_xlabel("F (T)"); a_.set_xlim(0, 50); a_.legend(fontsize=7)
fig.tight_layout(); plt.show()

# Luttinger sum / global scale from the resolved pairs (frequencies from the 1.0-3.0 T (e) and 0.7-2.5 T (h) windows + onset tracks)
for rid, (f1, f2) in {6: (7.5, 22.5), 7: (4.7, 6.6)}.items():
    FL = luttinger_frequency(abs(runs[rid][0]) * 1e16)
    print(f"run {rid}: f1 + f2 = {f1 + f2:.1f} T = {(f1+f2)/FL:.2f} F_L -> density scale {(f1+f2)/FL:.2f}; partition {f1/(f1+f2):.2f}/{f2/(f1+f2):.2f}")
