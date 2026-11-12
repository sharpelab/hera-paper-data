"""Runs 6/7 — sdh-spot-check read for the ana notebook: raw R(B) (gain-divided), background-subtracted dR vs 1/B,
sdh_onset tone table, prominence-based FFT peaks vs F_L and the model's ABAB pair / ABCA singleton (both signs).
Standalone (paths via file_path when run in ana; falls back to ./data)."""
import sys, warnings, numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

_model = Path.home() / "measurement_env/hera/models/tetralayer_fs_count"
sys.path.insert(0, str(_model))
from fs_count_b0 import abab_fs, abca_fs

DATA = Path(globals().get("file_path", "data"))
I_BIAS = 1.0 / 100e6; R_FS = 50e-6 / I_BIAS      # 10 nA; sr1 50 uV -> 5 kOhm FS on both spot checks
SPOTS = {6: ("electron", +3.2e16), 7: ("hole", -1.2e16)}


def spot_trace(rid):
    r = open_run(DATA / str(rid))
    B = r.col("magnet_field"); R = (r.col("sr1_X") / 1.0) / (r.col("sr0_X") / -1e6)
    o = np.argsort(B)
    return r, B[o], R[o], r.col("T_sample")[o]


def fft_peaks(R, B, lo, hi, FL, nfft=8192):
    f, spec = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, log=False, nfft=nfft)
    sp = spec[0]; dF = 1 / (1 / lo - 1 / hi)
    sel = (f >= 1.5) & (f <= 2.2 * FL)
    ff, ss = f[sel], sp[sel]
    pk, prop = find_peaks(ss, prominence=0.08 * ss.max(), distance=max(1, int(0.8 * dF / (ff[1] - ff[0]))))
    order = np.argsort(prop["prominences"])[::-1]
    return ff, ss, [(float(ff[i]), float(ss[i] / ss.max())) for i in pk[order]], dF


fig, ax = plt.subplots(3, 2, figsize=(14, 12))
for j, (rid, (side, n_si)) in enumerate(SPOTS.items()):
    r, B, R, T = spot_trace(rid)
    FL = float(luttinger_frequency(n_si)); n12 = n_si * 1e-16
    abab = [f for f, k in abab_fs(n_si)[1]]; abca = abca_fs(n_si)[4]
    print(f"\n===== run {rid} ({side}, n = {n12:+.2f}e12, D = 0) — {len(B)} pts, B {B.min():.2f}-{B.max():.2f} T, T {T.min():.3f}-{T.max():.3f} K, "
          f"R {R.min():.0f}..{R.max():.0f} Ohm (max {R.max()/R_FS:.2f} FS) =====")
    print(f"F_L = {FL:.1f} T | model ABAB pair {np.round(abab, 1)} T (sum {sum(abab):.1f}) | ABCA singleton {abca:.1f} T")
    ax[0, j].plot(B, R, lw=0.7, color="k"); ax[0, j].set(title=f"run {rid} {side}: n = {n12:+.2f}e12, D = 0 — raw Rxx(B) (sr1/sr0, 50 uV)", xlabel="B (T)", ylabel="Rxx (Ohm)")
    # onset (per-tone) — the fan's B_lo contract
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always"); on = sdh_onset(R, B, r_full_scale=R_FS)
        for ww in w: print("  warn:", ww.message)
        print(on.summary()); onset = float(on.onset_b)
    except SdhOnsetError as e:
        print("  SdhOnsetError:", e); onset = 1.0
    lo = max(1.0, onset)   # 1.0 T: the 10 mT-sampled edge of run 6 / valid for both records
    m = B >= lo; cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    ax[1, j].plot(1 / B[m], dR, lw=0.6, color="k"); ax[1, j].set(title=f"deg-5 background (in B) removed, B >= {lo:.1f} T", xlabel="1/B (1/T)", ylabel="dRxx (Ohm)")
    # FFT peak sets over two windows (stability): full record above lo, and above 1.5 T
    for k, (wlo, col) in enumerate([(lo, "C0"), (1.5, "C1")]):
        ff, ss, pks, dF = fft_peaks(R, B, wlo, B.max(), FL)
        print(f"  FFT [{wlo:.1f}, {B.max():.0f}] T, dF {dF:.2f} T — peaks (F, rel. amp): " + ", ".join(f"{f:.1f} ({a:.2f})" for f, a in pks[:8]))
        ax[2, j].plot(ff, ss / ss.max(), color=col, lw=0.9, label=f"B >= {wlo:.1f} T (dF {dF:.1f} T)")
        for f, a in pks[:6]: ax[2, j].annotate(f"{f:.1f}", (f, a), fontsize=7, color=col, xytext=(0, 3), textcoords="offset points", ha="center")
    ax[2, j].axvline(FL, color="k", ls="--", lw=1, label=f"F_L = {FL:.1f} T")
    for i, t in enumerate(abab): ax[2, j].axvline(t, color="r", ls=":", lw=1, label="model ABAB pair" if i == 0 else None)
    ax[2, j].set(xlim=(0, 2.2 * FL), xlabel="F (T)", ylabel="FFT amp (norm.)", title="1/B FFT vs F_L and the ABAB template"); ax[2, j].legend(fontsize=7)
fig.tight_layout()
