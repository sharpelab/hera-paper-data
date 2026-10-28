"""Runs 6 + 7 — sdh-spot-check read (electron n=+3.2e12, hole n=-1.2e12; D = 0, run-5 cal): raw R(B), background-
subtracted 1/B record, sdh_onset per run, FFT stability sweep, forward-model F(n) (tetralayer_fs_count) at each spot."""
import sys, warnings
from pathlib import Path
from scipy.signal import find_peaks
import hera
from hera.analysis import sdh_onset, SdhOnsetError, sdh_fft, luttinger_frequency
_MODEL_DIR = Path(hera.__file__).resolve().parents[2] / "hera" / "models" / "tetralayer_fs_count"   # <repo>/hera/models/... via the installed package, OS-agnostic
assert _MODEL_DIR.is_dir(), _MODEL_DIR
sys.path.insert(0, str(_MODEL_DIR))
import fs_count_b0 as fsm

def trace(i):
    r = run(i); B = r.col("magnet_field"); R = (r.col("sr1_X") / 1.0) / (r.col("sr0_X") / -1e6)
    o = np.argsort(B); return B[o], R[o], r

spots = [(6, 3.2, 1.0), (7, -1.2, 0.5)]        # (run, n [1e12], b_lo for the onset read: run 6's 0-1 T leg is 50 mT-stepped -> Nyquist-blind, excluded)
fig, axes = plt.subplots(3, 2, figsize=(14, 12))
for col, (rid, n12, blo) in enumerate(spots):
    B, R, r = trace(rid); FL = luttinger_frequency(abs(n12) * 1e16); Bmax = B.max()
    _, orbs = fsm.abab_fs(n12 * 1e16); ms = fsm.abab_mstar(n12 * 1e16); *_, Fabca = fsm.abca_fs(n12 * 1e16); _, mabca = fsm.abca_mstar(n12 * 1e16)
    print(f"\n=== run {rid}: n = {n12:+.2f}e12, F_L = {FL:.1f} T | model ABAB " + ", ".join(f"{F:.1f} T (m* {mm:.3f})" for (F, _), (_, mm) in zip(orbs, ms))
          + f" | ABCA {Fabca:.1f} T (m* {mabca:.3f}) | R {R.min():.0f}..{R.max():.0f} Ohm")
    ax = axes[0, col]; ax.plot(B, R, lw=0.7, color="k"); ax.set_title(f"run {rid} raw Rxx (sr1/sr0), n = {n12:+.1f}e12, D = 0"); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    sel = B >= blo - 1e-6
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            on = sdh_onset(R[sel], B[sel], r_full_scale=50e-6 / 10e-9); onset_b = on.onset_b
            for ww in w: print("  warn:", ww.message)
            print(on.summary())
        except SdhOnsetError as e:
            print("  SdhOnsetError:", e); onset_b = None
    p = np.polyfit(B[sel], R[sel], 5); dR = R[sel] - np.polyval(p, B[sel])
    ax = axes[1, col]; ax.plot(1 / B[sel], dR, lw=0.7); ax.set_xlabel("1/B (1/T)"); ax.set_ylabel(f"dRxx (Ohm), deg-5 bg in B, B >= {blo} T")
    if onset_b: ax.axvline(1 / onset_b, color="r", ls="--", label=f"sdh_onset {onset_b:.2f} T"); ax.legend()
    ax = axes[2, col]
    for cut, deg, win, c in [(blo, 5, "hann", "k"), (2.0, 5, "hann", "C0"), (3.0, 5, "hann", "C1"), (2.0, 3, "hann", "C2"), (2.0, 7, "hann", "C3"), (2.0, 5, None, "C4")]:
        f, s = sdh_fft(R[:, None], B, b_range=(cut, Bmax), bg_degree=deg, window=win, log=False, nfft=4096)
        s = s[0]; mf = (f > 1.5) & (f < 2.2 * FL); ax.plot(f[mf], s[mf] / s[mf].max(), lw=0.8, color=c, label=f"cut {cut:.1f} T, deg {deg}, {win}")
        if deg == 5 and win == "hann":
            pk, _ = find_peaks(s[mf], prominence=0.1 * s[mf].max())
            print(f"  FFT [{cut:.1f}, {Bmax:.0f}] T (dF {1/(1/cut-1/Bmax):.2f} T): " + ", ".join(f"{f[mf][q]:.1f} T ({s[mf][q]/s[mf][pk].max():.2f})" for q in sorted(pk, key=lambda q: -s[mf][q])[:6]))
    for x, lab, ls in ((FL, "F_L", ":"), (orbs[-1][0], "ABAB heavy (model)", "--"), (orbs[0][0], "ABAB light (model)", "-.")):
        ax.axvline(x, color="m" if lab == "F_L" else "g", ls=ls, label=lab)
    ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm)"); ax.set_xlim(0, 2.2 * FL); ax.legend(fontsize=7)
fig.tight_layout(); plt.show()
