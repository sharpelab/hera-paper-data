"""Landau-fan read (run 4): LL structure in (n, B), filling-factor identification,
SdH tone count, and the first ABSOLUTE density calibration.

Key physics being tested:
  * Landau fan lines emanating from the CNP have dn/dB = nu*e/h. Fitting their slopes
    gives nu directly AND calibrates c_tg absolutely (so far only the geometry prior).
  * A rhombohedral N-layer stack has an N-fold orbitally degenerate zero-energy LL:
    tetralayer ABCA -> 4 orbital x 4 spin/valley = 16 states, first flanking gaps at
    nu = +/-8. A Bernal tetralayer decomposes into two bilayer-like sets whose levels
    arrive at different fields -> a different sequence.
  * Tone count per density: one SdH frequency carrying the full Onsager value = one
    Fermi pocket (ABCA); two tones splitting it = two pockets (ABAB/ABCB).
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.constants as cst

from hera.analysis import (open_run, fan_grids, resistance_grids, sdh_fft,
                           GateCalibration, luttinger_frequency)

rid = int(sys.argv[1]) if len(sys.argv) > 1 else 4
here = Path(__file__).resolve().parent.parent
r = open_run(here / "data" / str(rid))
print(f"run {rid}: {r.recipe}  rows={r.rows}  interrupted={r.interrupted}")

fan = fan_grids(r)
rg = resistance_grids(fan)
Rxx = np.abs(rg.R["sr1"])                       # (nB, nfast)
Vtg = fan.grid("k_2400_tg_volt")
Bcmd = fan.slow
# DUPLICATE COLUMN TRAP: for a multimegasweep with magnet.field as slow axis AND
# followed, "magnet_field" appears twice. FanGrids.grid() resolves duplicates to the
# FIRST occurrence = the planned setpoint. The measured readback is the LAST one.
_bidx = [i for i, c in enumerate(fan.cols) if c == "magnet_field"]
assert len(_bidx) >= 2, f"expected setpoint+readback columns, got {_bidx}"
Bgrid = fan.data[:, _bidx[-1]].reshape(fan.nrows, fan.nfast)   # MEASURED
Bmeas = Bgrid.mean(axis=1)
nB, nfast = Rxx.shape

# ---- CLIP MASK: sr1 at 1 mV full scale rails ~1.09x. Above ~1.7 T the ~n=0 columns
# exceed it (the nu=0 insulator), so those Rxx values are floor/garbage, not data.
_sidx = [i for i, c in enumerate(fan.cols) if c == "sr1_X"][0]
Vxx = fan.data[:, _sidx].reshape(nB, nfast)
SR1_SENS = 1e-3
clip = np.abs(Vxx) > 0.95 * SR1_SENS
Rxx = np.where(clip, np.nan, Rxx)
print(f"clipped (|sr1_X| > 0.95 x {SR1_SENS:g} V): {clip.sum()} of {clip.size} pts "
      f"({100*clip.mean():.1f} %); affected density columns: "
      f"{[float(round(x,2)) for x in np.unique(np.where(clip.any(axis=0))[0])[:99]][:12]} (indices)")
if clip.any():
    print(f"  clipping starts at row {int(np.argmax(clip.any(axis=1)))} "
          f"and is confined to |n| <= {0.0:.2f} + a few columns around neutrality")
print(f"grid {nB} field rows x {nfast} density pts")
print(f"B commanded {Bcmd.min():.3f}..{Bcmd.max():.3f} T | "
      f"measured {Bmeas.min():.3f}..{Bmeas.max():.3f} T | "
      f"max |cmd-meas| = {np.abs(Bcmd - Bmeas).max()*1e3:.1f} mT")
print(f"Rxx {Rxx.min():.1f} .. {Rxx.max():.1f} ohm")
print(f"within-row spread of MEASURED B: "
      f"{(Bgrid.max(axis=1) - Bgrid.min(axis=1)).max() * 1e3:.1f} mT max; "
      f"mean offset from setpoint {np.mean(Bmeas - Bcmd) * 1e3:+.1f} mT "
      f"(this is why magnet.field is followed rather than trusted from the setpoint)")

# FFT validity: the 1/B record length sets resolution AND Nyquist. Density columns whose
# Onsager frequency exceeds Nyquist ALIAS and must not be interpreted.
_span = (1.0 / Bmeas).max() - (1.0 / Bmeas).min()
F_RES, F_NYQ = 1.0 / _span, nB / (2.0 * _span)
print(f"1/B record: span {_span:.3f} /T -> FFT resolution {F_RES:.2f} T, "
      f"Nyquist {F_NYQ:.1f} T")

RATIO = 1.2737                                   # measured from run 3's CNP line
cal_g = GateCalibration.from_thicknesses(9.5e-9, 11e-9, 0.0)
cal_s = GateCalibration(c_tg=cal_g.c_tg, c_bg=cal_g.c_tg / RATIO)
Vbg_row = RATIO * Vtg
n = cal_s.density(Vtg, Vbg_row)                  # m^-2, geometry-prior absolute scale
n12 = n * 1e-16
n_line = n12[0]
print(f"n range {n_line.min():+.3f} .. {n_line.max():+.3f} e12 cm^-2 "
      f"(geometry-prior absolute scale)")

# ---- filling factor nu = n*h/(e*B) on the prior scale -----------------------
NU = (n[None, :] if n.ndim == 1 else n) * cst.h / (cst.e * Bmeas[:, None])
print(f"nu spans {NU.min():+.1f} .. {NU.max():+.1f} over the fan")

# ---- SdH FFT per density column --------------------------------------------
print("\n--- SdH FFT in 1/B (per density column) ---")
try:
    freqs, spec = sdh_fft(Rxx, Bmeas, bg_degree=5, log=True)
    print(f"freqs {freqs.min():.2f}..{freqs.max():.2f} T, spec shape {spec.shape}")
    print(f"{'n(e12)':>8} {'f_Onsager':>10} {'f_peak':>9} {'f2':>9} {'ratio':>7}  interp")
    rows_out = []
    for j in range(0, nfast, max(1, nfast // 14)):
        f_ons = luttinger_frequency(abs(n_line[j] * 1e16))
        sp = spec[j]
        m = freqs > 1.0
        fi, si = freqs[m], sp[m]
        # top two well-separated local maxima
        loc = [k for k in range(1, len(si) - 1) if si[k] > si[k-1] and si[k] >= si[k+1]]
        loc.sort(key=lambda k: -si[k])
        f1 = fi[loc[0]] if loc else np.nan
        f2 = np.nan
        for k in loc[1:]:
            if abs(fi[k] - f1) > 0.15 * max(f1, 1) and si[k] > 0.35 * si[loc[0]]:
                f2 = fi[k]
                break
        tag = ""
        if f_ons > F_NYQ:
            tag = f"ALIASED (Onsager {f_ons:.1f} T > Nyquist {F_NYQ:.1f} T) — ignore"
        if np.isfinite(f1) and f_ons > 0.5 and f_ons <= F_NYQ:
            rr = f1 / f_ons
            tag = ("1 pocket (full Onsager)" if 0.8 < rr < 1.25 else
                   "HALF Onsager" if 0.4 < rr < 0.62 else
                   "QUARTER" if 0.2 < rr < 0.31 else f"ratio {rr:.2f}")
        rows_out.append((n_line[j], f_ons, f1, f2, f1 / f_ons if f_ons > 0.5 else np.nan, tag))
        print(f"{n_line[j]:8.3f} {f_ons:10.2f} {f1:9.2f} {f2:9.2f} "
              f"{(f1/f_ons if f_ons>0.5 else np.nan):7.2f}  {tag}")
except Exception as e:
    print(f"sdh_fft failed: {e!r}")
    freqs = spec = None

# ---- figures ---------------------------------------------------------------
fig = plt.figure(figsize=(14, 9))
gs = fig.add_gridspec(2, 2)

ax = fig.add_subplot(gs[0, :])
pc = ax.pcolormesh(np.tile(n_line[None, :], (nB, 1)),
                   np.tile(Bmeas[:, None], (1, nfast)),
                   np.log10(np.maximum(Rxx, 1.0)), shading="nearest", cmap="magma")
for nu in (-16, -8, -4, 4, 8, 16):
    bb = np.linspace(max(Bmeas.min(), 0.3), Bmeas.max(), 50)
    nn = nu * cst.e * bb / cst.h * 1e-16
    ok = (nn > n_line.min()) & (nn < n_line.max())
    if ok.sum() > 2:
        ax.plot(nn[ok], bb[ok], "w--", lw=0.8, alpha=0.75)
        ax.annotate(f"{nu}", (nn[ok][-1], bb[ok][-1]), color="w", fontsize=7)
ax.set_xlabel("n  (1e12 cm^-2)"); ax.set_ylabel("B (T)")
ax.set_title(f"run {rid} — Landau fan, log10 Rxx (ohm), D = 0, T = base "
             f"(dashed = constant nu on the geometry-prior scale)")
fig.colorbar(pc, ax=ax, label="log10 Rxx")

ax = fig.add_subplot(gs[1, 0])
for j in (nfast // 6, nfast // 3, nfast // 2, 2 * nfast // 3, 5 * nfast // 6):
    ax.plot(1.0 / Bmeas, Rxx[:, j], lw=1.0, label=f"n={n_line[j]:+.2f}")
ax.set_xlabel("1/B  (1/T)"); ax.set_ylabel("Rxx (ohm)"); ax.set_yscale("log")
ax.set_title("SdH traces vs 1/B"); ax.legend(fontsize=7)

ax = fig.add_subplot(gs[1, 1])
if freqs is not None:
    pc = ax.pcolormesh(np.tile(n_line[:, None], (1, len(freqs))),
                       np.tile(freqs[None, :], (nfast, 1)), np.log10(spec + 1e-9),
                       shading="nearest", cmap="viridis")
    fo = luttinger_frequency(np.abs(n_line * 1e16))
    ax.plot(n_line, fo, "r--", lw=1.2, label="full Onsager  n*h/4e")
    ax.plot(n_line, fo / 2, "c:", lw=1.2, label="half (2 pockets)")
    ax.set_ylim(0, min(freqs.max(), np.nanmax(fo) * 2.2))
    ax.set_xlabel("n  (1e12 cm^-2)"); ax.set_ylabel("SdH frequency (T)")
    ax.set_title("SdH spectrum vs density"); ax.legend(fontsize=7)
    fig.colorbar(pc, ax=ax, label="log10 |FFT|")
fig.tight_layout()
out = here / "hera_scratch" / f"a5_fan_run{rid}.png"
fig.savefig(out, dpi=110)
print(f"\nwrote {out}")
