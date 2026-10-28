"""sdh-spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12): raw R(B), onset, FFT, model overlay."""
import sys, json, warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
import fs_count_b0 as m

HERE = Path(__file__).parent
DATA = HERE.parent / "data"
I_BIAS = 1.0 / 100e6  # 1 V / 100 MOhm

def load(i):
    r = open_run(DATA / str(i))
    B = r.col("magnet_field"); I = r.col("sr0_X") / -1e6; V = r.col("sr1_X") / 1.0
    R = V / I
    o = np.argsort(B)
    return B[o], R[o], I[o], r

out = {}
fig, axes = plt.subplots(3, 2, figsize=(14, 12))
for col, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    B, R, I, r = load(rid)
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"\n===== run {rid}: n = {n12:+.2f}e12, F_L = {FL:.1f} T; R range {R.min():.1f}..{R.max():.1f} Ohm; I {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA =====")
    # model
    try:
        EF, orbs = m.abab_fs(n12 * 1e16)
        ms = m.abab_mstar(n12 * 1e16)
        print("  model ABAB orbits (F [T], m*/me):", [(round(F, 2), round(mm, 3)) for (F, _), (_, mm) in zip(orbs, ms)])
    except Exception as e:
        print("  ABAB model:", e)
    try:
        EF, topo, ncomp, nfreq, Ft = m.abca_fs(n12 * 1e16)
        Ft2, mm = m.abca_mstar(n12 * 1e16)
        print(f"  model ABCA: topo {topo}, ncomp {ncomp}, F_total {Ft:.2f} T, m* {mm:.3f}")
    except Exception as e:
        print("  ABCA model:", e)
    # raw
    ax = axes[0, col]; ax.plot(B, R, lw=0.7); ax.set_title(f"run {rid} raw Rxx  n={n12:+.1f}e12  (F_L={FL:.1f} T)"); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    # onset
    rfs = 50e-6 / I_BIAS
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            on = sdh_onset(R, B, r_full_scale=rfs)
            for ww in w: print("  warn:", ww.message)
        print(on.summary())
        out[rid] = dict(onset_b=float(on.onset_b), onset_freq=float(on.onset_freq), clip_high_b=float(on.clip_high_b),
                        tones=[dict(freq=float(t.freq), onset_b=float(t.onset_b), censored=t.censored, marginal=t.marginal,
                                    harmonic_of=t.harmonic_of, n_periods=float(t.n_periods)) for t in on.tones])
        onset_b = on.onset_b
    except SdhOnsetError as e:
        print("  SdhOnsetError:", e); out[rid] = dict(error=str(e)); onset_b = None
    # background-subtracted trace (deg 5 in B) above 1 T
    sel = B >= 1.0
    p = np.polyfit(B[sel], R[sel], 5); dR = R[sel] - np.polyval(p, B[sel])
    ax = axes[1, col]; ax.plot(1 / B[sel], dR, lw=0.7); ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm), deg-5 bg in B, B>=1 T")
    if onset_b: ax.axvline(1 / onset_b, color="r", ls="--", label=f"onset {onset_b:.2f} T"); ax.legend()
    # FFT stability sweep
    ax = axes[2, col]
    Bmax = B.max()
    for cut, deg, win, c in [(max(1.0, onset_b or 1.0), 5, "hann", "k"), (2.0, 5, "hann", "C0"), (3.0, 5, "hann", "C1"), (2.0, 3, "hann", "C2"), (2.0, 7, "hann", "C3"), (2.0, 5, None, "C4")]:
        if cut >= Bmax - 1: continue
        f, s = sdh_fft(R[:, None], B, b_range=(cut, Bmax), bg_degree=deg, window=win, log=False, nfft=4096)
        s = s[0]; mfreq = f < 3 * FL
        ax.plot(f[mfreq], s[mfreq] / s[mfreq][f[mfreq] > 2].max(), lw=0.8, color=c, label=f"cut {cut:.1f} deg{deg} {win}")
        if deg == 5 and win == "hann":
            fm = f[mfreq]; sm = s[mfreq]
            from scipy.signal import find_peaks
            pk, pr = find_peaks(sm, prominence=0.1 * sm[fm > 2].max())
            pk = [q for q in pk if fm[q] > 2]
            print(f"  FFT cut {cut:.1f} T deg{deg}: dF = {1/(1/cut - 1/Bmax):.2f} T; peaks (T, rel amp): " +
                  ", ".join(f"{fm[q]:.1f} ({sm[q]/sm[pk].max():.2f})" for q in sorted(pk, key=lambda q: -sm[q])[:8]))
    ax.axvline(FL, color="m", ls=":", label="F_L"); ax.axvline(0.72 * FL, color="g", ls=":", label="0.72 F_L"); ax.axvline(0.28 * FL, color="g", ls="-.", label="0.28 F_L")
    ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm)"); ax.set_xlim(0, 2.2 * FL); ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig(HERE / "spot_read.png", dpi=110)
json.dump(out, open(HERE / "spot_read.json", "w"), indent=1, default=str)

# model F(n) table over the candidate fan windows
print("\n===== model F(n) table (T) =====")
print(f"{'n(e12)':>8} {'F_L':>6} | ABAB orbits (F, m*) | ABCA F, m*")
for n12 in [-1.27, -1.0, -0.8, -0.6, 1.0, 1.5, 2.0, 2.5, 3.0, 3.27]:
    FL = luttinger_frequency(abs(n12) * 1e16)
    try:
        _, orbs = m.abab_fs(n12 * 1e16); ms = m.abab_mstar(n12 * 1e16)
        ab = " ".join(f"{F:5.1f}({mm:.3f})" for (F, _), (_, mm) in zip(orbs, ms))
    except Exception as e: ab = f"err {e}"
    try:
        *_, Ft = m.abca_fs(n12 * 1e16); _, mm = m.abca_mstar(n12 * 1e16); ac = f"{Ft:5.1f}({mm:.3f})"
    except Exception as e: ac = f"err {str(e)[:40]}"
    print(f"{n12:+8.2f} {FL:6.1f} | {ab} | {ac}")
