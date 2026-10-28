"""Run 5 (sdh-downsweep): the definitive Fermi-pocket count.

100 field points 6 -> 0.5 T uniform in 1/B at 5 fixed densities on the D = 0 line.
Resolution 0.55 T, Nyquist 27.3 T — comfortably above every Onsager frequency in play,
unlike the fan (Nyquist 17.3 T, which aliased the top densities).

The test, stated so it needs no calibration: TWO Fermi pockets produce TWO SdH tones,
BOTH proportional to n, whose frequencies sum to the full Onsager value. ONE pocket
produces one tone carrying all of it. Counting tones that scale with n is independent
of the absolute density scale.
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.constants as cst

from hera.analysis import (open_run, fan_grids, resistance_grids, sdh_fft,
                           sdh_onset, SdhOnsetError, GateCalibration, luttinger_frequency)

here = Path(__file__).resolve().parent.parent
r = open_run(here / "data" / "5")
fan = fan_grids(r)
rg = resistance_grids(fan)
Rxx = np.abs(rg.R["sr1"])
nB, nD = Rxx.shape
_bi = [i for i, c in enumerate(fan.cols) if c == "magnet_field"]
B = fan.data[:, _bi[-1]].reshape(nB, nD).mean(axis=1)     # MEASURED, not setpoint
Vtg = fan.grid("k_2400_tg_volt")[0]
RATIO = 1.2737
cal_g = GateCalibration.from_thicknesses(9.5e-9, 11e-9, 0.0)
cal_s = GateCalibration(c_tg=cal_g.c_tg, c_bg=cal_g.c_tg / RATIO)
n_ass = cal_s.density(Vtg, RATIO * Vtg)
print(f"run 5: {nB} field rows x {nD} densities | B {B.min():.3f}..{B.max():.3f} T "
      f"(measured; setpoint offset {np.mean(B - fan.slow)*1e3:+.1f} mT)")
print(f"densities (assumed scale): {np.round(n_ass*1e-16, 2)} e12 cm^-2")
print(f"Rxx {np.nanmin(Rxx):.1f} .. {np.nanmax(Rxx):.1f} ohm")

span = (1 / B).max() - (1 / B).min()
F_RES, F_NYQ = 1 / span, nB / (2 * span)
print(f"1/B span {span:.3f} /T -> resolution {F_RES:.2f} T, Nyquist {F_NYQ:.1f} T")

freqs, spec = sdh_fft(Rxx, B, bg_degree=5, log=True)
print(f"\n{'n_ass':>7} {'f_full':>8} | tones above 25% of the max, freq (T) x amplitude")
tab = []
for j in range(nD):
    fo = luttinger_frequency(abs(n_ass[j]))
    m = (freqs > 1.2) & (freqs < F_NYQ)
    fi, si = freqs[m], spec[j][m]
    si = si / si.max()
    loc = [k for k in range(1, len(si) - 1) if si[k] > si[k-1] and si[k] >= si[k+1]
           and si[k] > 0.25]
    loc.sort(key=lambda k: -si[k])
    keep = []
    for k in loc:
        if all(abs(fi[k] - fi[q]) > F_RES for q in keep):
            keep.append(k)
    keep = keep[:4]
    s_ = "  ".join(f"{fi[k]:5.2f}x{si[k]:.2f}" for k in keep)
    tab.append((n_ass[j] * 1e-16, fo, [fi[k] for k in keep], [si[k] for k in keep]))
    print(f"{n_ass[j]*1e-16:7.2f} {fo:8.1f} | {s_}")

# --- which tones scale linearly with n? --------------------------------------
print("\ndoes each tone scale with density? (a real pocket must)")
ns = np.array([t[0] for t in tab])
prim = np.array([t[2][0] if t[2] else np.nan for t in tab])
ok = np.isfinite(prim) & (np.abs(ns) > 0.3)
if ok.sum() >= 3:
    sl = np.sum(ns[ok] * prim[ok]) / np.sum(ns[ok] ** 2)
    rr = np.corrcoef(np.abs(ns[ok]), prim[ok])[0, 1]
    full_slope = cst.h / (4 * cst.e) * 1e16
    print(f"  dominant tone: slope {sl:.2f} T per e12 cm^-2, |r| = {abs(rr):.4f}")
    print(f"  full-Onsager slope would be {full_slope:.2f} T per e12 -> "
          f"ratio {abs(sl)/full_slope:.3f}  (= 1/alpha for a single 4-fold pocket)")
    print(f"  a TWO-pocket split would put the dominant tone well below this and add a "
          f"second tone at the complement")

# --- per-trace onset (independent of the FFT) --------------------------------
print("\nsdh_onset per density trace (independent tone finder):")
for j in range(nD):
    try:
        o = sdh_onset(Rxx[:, j], B, r_full_scale=1e-3 / 10e-9)
        tones = ", ".join(f"{t.freq:.2f} T (contrast {t.contrast:.2f}"
                          f"{', marginal' if t.marginal else ''}"
                          f"{', harmonic' if t.harmonic_of else ''})" for t in o.tones[:4])
        print(f"  n={n_ass[j]*1e-16:+.2f}: onset {o.onset_b:.2f} T | tones: {tones}")
    except SdhOnsetError as e:
        print(f"  n={n_ass[j]*1e-16:+.2f}: no trackable tone ({e})")
    except Exception as e:
        print(f"  n={n_ass[j]*1e-16:+.2f}: {e!r}")

fig, ax = plt.subplots(1, 3, figsize=(17, 4.8))
for j in range(nD):
    ax[0].plot(1 / B, Rxx[:, j], lw=1.0, label=f"n={n_ass[j]*1e-16:+.2f}")
ax[0].set_xlabel("1/B (1/T)"); ax[0].set_ylabel("Rxx (ohm)"); ax[0].set_yscale("log")
ax[0].set_title("run 5 — SdH traces, D = 0, T = base"); ax[0].legend(fontsize=7)

for j in range(nD):
    ax[1].plot(freqs, spec[j] / spec[j].max() + j * 1.1, lw=1.0,
               label=f"n={n_ass[j]*1e-16:+.2f}")
    fo = luttinger_frequency(abs(n_ass[j]))
    ax[1].plot([fo], [j * 1.1], "kv", ms=7)
ax[1].set_xlim(0, F_NYQ); ax[1].set_xlabel("SdH frequency (T)")
ax[1].set_ylabel("normalised |FFT| (offset)")
ax[1].set_title("spectra (triangles = full Onsager, assumed n)"); ax[1].legend(fontsize=7)

ax[2].plot(np.abs(ns), prim, "o", ms=7, label="dominant tone")
xx = np.linspace(0, np.abs(ns).max() * 1.1, 10)
ax[2].plot(xx, cst.h / (4 * cst.e) * 1e16 * xx, "k--", lw=1.0, label="full Onsager")
ax[2].plot(xx, cst.h / (4 * cst.e) * 1e16 * xx / 2, "c:", lw=1.0, label="half (2 pockets)")
ax[2].set_xlabel("|n| assumed (1e12 cm^-2)"); ax[2].set_ylabel("tone frequency (T)")
ax[2].set_title("one tone, proportional to n"); ax[2].legend(fontsize=8); ax[2].grid(alpha=0.3)
fig.tight_layout()
out = here / "hera_scratch" / "a8_downsweep.png"
fig.savefig(out, dpi=110)
print(f"\nwrote {out}")
