"""SdH spot checks, runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12), D=0 (run-5 cal).
Raw R(B) -> sdh_onset -> sdh_fft (window stability) -> model F(n) table at the spot densities."""
import sys, json, warnings
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
import fs_count_b0 as M

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
SPOTS = {6: 3.2, 7: -1.2}      # 1e12 cm^-2
SENS = {6: 50e-6, 7: 50e-6}


def load(rid):
    run = open_run(DATA / str(rid))
    mc = run.meta["measurement_config"]
    B = run.col("magnet_field"); I = run.col("sr0_X") / mc["sr0_gain"]
    R = (run.col("sr1_X") / mc.get("sr1_gain", 1.0)) / I
    o = np.argsort(B)
    return B[o], R[o], np.median(np.abs(I))


out = {}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, rid in enumerate((6, 7)):
    n = SPOTS[rid]; B, R, I = load(rid)
    FL = float(luttinger_frequency(n * 1e16))
    efs = M.abab_fs(n * 1e16)[1]; ems = M.abab_mstar(n * 1e16)
    Fa, ma = M.abca_mstar(n * 1e16)
    print(f"\n=== run {rid}: n = {n:+.2f}e12, F_L = {FL:.2f} T, I = {I*1e9:.2f} nA, R {R.min():.1f}..{R.max():.1f} Ohm")
    print(f"  model ABAB orbits F[T] (m*): " + ", ".join(f"{F:.2f} ({m:.3f})" for (F, _), (_, m) in zip(efs, ems)))
    print(f"  model ABCA F = {Fa:.2f} T, m* = {ma:.3f}")
    rfs = SENS[rid] / I
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            on = sdh_onset(R, B, r_full_scale=rfs, b_lo=0.3)
            for ww in w: print("  warn:", ww.message)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print("  SdhOnsetError:", e); on = None; onset = np.nan
    out[rid] = dict(n=n, FL=FL, onset=float(onset),
                    tones=[dict(f=float(t.freq), onset=float(t.onset_b), censored=bool(t.censored),
                                marginal=bool(t.marginal), harmonic_of=t.harmonic_of) for t in (on.tones if on else [])],
                    abab=[float(F) for F, _ in efs], abca=float(Fa))
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("Rxx (Ohm)")
    ax[0, j].set_title(f"run {rid} raw — n = {n:+.1f}e12, D = 0")
    if np.isfinite(onset): ax[0, j].axvline(onset, color="r", ls="--", lw=0.8, label=f"onset {onset:.2f} T"); ax[0, j].legend()
    # FFT window-stability sweep
    bmax = B.max()
    lo_list = [max(onset, 0.5) if np.isfinite(onset) else 1.0]
    lo_list += [lo_list[0] * 1.3, lo_list[0] * 1.7]
    for lo in lo_list:
        for deg in (3, 5):
            fq, sp = sdh_fft(R[:, None], B, b_range=(lo, bmax), bg_degree=deg, nfft=4096)
            s = sp[0]; msk = fq > 2
            ax[1 + (deg == 5), j].plot(fq[msk], s[msk] / s[msk].max(), lw=0.8, label=f"[{lo:.2f},{bmax:.1f}] T")
            from scipy.signal import find_peaks
            pk, _ = find_peaks(s * msk, prominence=0.08 * s[msk].max())
            pk = sorted(pk, key=lambda p: -s[p])[:6]
            print(f"  FFT win [{lo:.2f},{bmax:.2f}] deg {deg}: peaks " + ", ".join(f"{fq[p]:.2f}T({s[p]/s[msk].max():.2f})" for p in sorted(pk)))
    for r_ in (1, 2):
        a = ax[r_, j]; a.axvline(FL, color="k", ls="--", lw=1, label=f"F_L {FL:.1f}")
        for F, _ in efs:
            if F > 0.5: a.axvline(F, color="b", ls=":", lw=1)
        a.axvline(Fa, color="m", ls="-.", lw=0.8)
        a.set_xlim(0, 2.2 * FL); a.set_xlabel("F (T)"); a.set_title(f"run {rid} FFT bg_deg {3 if r_ == 1 else 5} (blue: ABAB model; k--: F_L; m: ABCA)")
        a.legend(fontsize=7)
fig.tight_layout(); fig.savefig(HERE / "spot_runs6_7.png", dpi=110)
json.dump(out, open(HERE / "spot_runs6_7.json", "w"), indent=1, default=str)
