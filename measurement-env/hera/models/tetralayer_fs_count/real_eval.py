#!/usr/bin/env python3
"""
Real-data validation of the tetralayer stacking-ID stack against RPL_19 — the
device behind arXiv:2606.05356 (rmg19) — validation rung 2 of the tetralayer
readiness workstream.

Runs the *same* SdH-FFT pipeline and mechanical recipe logic used on the
synthetic fans (`synth_eval.py`, reused verbatim here) on real Landau fans from
the lab mirror, and scores the output against the paper's published ground
truth. The physics being validated:

  * high-density CQM  -> a single tone at n_SdH = n (g = 1, flavor-polarized
    quarter metal); in our g = 4 language that is a singleton at 4*F_L, which
    the degeneracy audit must catch (not read as a supra-F_L pocket).
  * the multitone region near the cCSC -> the pipeline must FAIL the Luttinger
    sum honestly (a reportable non-Onsager state), not force a stacking call.
  * flavor-tone regimes (S21) -> tone position reads the isospin degeneracy
    (f_nu = n_SdH/n = 1, 1/2, 1/4 -> g = 1, 2, 4).
  * the stacking read at the closest-to-operating-point data (highest |n|,
    lowest D, symmetric metal) -> what call the recipe mechanics produce.

KEY VALIDATION-DESIGN POINT: for a real device the lever arm is *known* from the
rmg19 gate calibration, so F_L is fixed and the degeneracy factor must NOT be
absorbed into a free scale fit. We therefore report BOTH:
  (a) the recipe's mechanical output run blind with a FREE scale
      (se.fit_scale / se.classify_column) — which, run on CQM data, lands at
      s ~ 4 (a 4x "scale error", far outside the 0.8-1.2 lever-arm prior); and
  (b) the calibration-fixed degeneracy audit (f_nu -> g) — which correctly
      reads g = 1. The gap between (a) and (b) IS the finding.

Run:
  cd hera/models/tetralayer_fs_count
  uv run --no-project --with numpy --with scipy [--with matplotlib] \
      python3 real_eval.py
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
_HERE = Path(__file__).resolve().parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, _HERE / f"{name}.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sf = _load("synth_fan")       # model helpers: F_L, orbits_for, template_curves
se = _load("synth_eval")      # pipeline + mechanical recipe logic (reused verbatim)
rl = _load("rpl19_load")      # RPL_19 lab-format loader

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAVE_MPL = True
except Exception:
    HAVE_MPL = False

OUT = Path("/data/sharpelab/hera-data/tetralayer-rpl19-validation")

# n_SdH [1e12 cm^-2] = (e/h) * f[T] / 1e16
NSDH_PER_T = (1.602176634e-19 / 6.62607015e-34) / 1e16   # 0.0241799

# ----------------------------------------------------------------------------
# Fan registry — the sweeps to run, with their regime and analysis field window.
# ----------------------------------------------------------------------------
FANS = [
    dict(id=1840, contact=2, D=1.0, blo=0.7, bhi=5.0,
         label="fig3 main fan (D=1): CQM + multitone",
         regime="cqm+multitone", primary=True),
    dict(id=1776, contact=2, D=1.0, blo=0.9, bhi=2.5,
         label="D=1 small fan: CQM cross-check", regime="cqm"),
    dict(id=1988, contact=2, D=0.2, blo=0.5, bhi=8.0,
         label="D=0.2 hole fan to n=-3 (8 T): operating-point stacking read",
         regime="sm_stacking", primary=True),
    dict(id=1638, contact=2, D=0.2, blo=0.5, bhi=1.5,
         label="D=0.2 electron fan (1.5 T): SM companion", regime="sm"),
    dict(id=2029, contact=2, D=0.5, blo=0.6, bhi=8.0,
         label="D=0.5 fan (8 T): half-metal degeneracy", regime="hm"),
]

# LK effective-mass temperature series at (n=1, D=1): the dense "Resuming
# effective mass" series (cells 147-166), all 1D field sweeps over the SAME
# 0.75-1.25 T window with the heater stepped 31 mK -> 1.19 K. (The earlier
# 1639-1642 set mixes field windows and T, so it is excluded.) 1648 is
# malformed (1-D data) and skipped by the loader guard.
LK_IDS = [1646, 1647, 1649, 1650, 1651, 1652, 1653, 1654, 1655, 1656,
          1657, 1658, 1659, 1660]


# ----------------------------------------------------------------------------
# Per-column tone extraction (reuses se pipeline) + degeneracy bookkeeping.
# ----------------------------------------------------------------------------
def clean_BR(B, R):
    """Return strictly-increasing B with R averaged over duplicate B values —
    real magnet-field records are not perfectly monotonic/unique, which the
    cubic 1/B interpolation in the pipeline requires."""
    m = np.isfinite(B) & np.isfinite(R)
    B, R = B[m], R[m]
    if B.size == 0:
        return B, R
    o = np.argsort(B)
    B, R = B[o], R[o]
    uB, idx = np.unique(B, return_inverse=True)
    if uB.size == B.size:
        return B, R
    uR = np.zeros_like(uB)
    cnt = np.zeros_like(uB)
    np.add.at(uR, idx, R)
    np.add.at(cnt, idx, 1.0)
    return uB, uR / cnt


def analyze_column(B, R, FLn, blo, bhi, cutoff=0.8, f_max_mult=8.0):
    """FFT one field-sweep column (se pipeline) and return the significant tones
    with degeneracy bookkeeping. f_max widened to f_max_mult*F_L so both the g=1
    tone at 4*F_L AND the multitone tones (n_SdH>n, i.e. f_nu>1 -> ratio up to
    ~6-8) are visible."""
    B, R = clean_BR(B, R)
    if B.size < 48 or FLn <= 0:
        return dict(peaks=[], tones=[], freq=None, psd=None, noise=np.nan)
    L = 1.0 / blo - 1.0 / bhi
    f_floor = 3.0 / L
    freq, psd = se.column_spectrum(B, R, blo, bhi, cutoff)
    peaks = se.pick_peaks(freq, psd, f_floor, f_max=f_max_mult * FLn, topk=8)
    peaks = se.merge_peaks(peaks, dfmerge=max(2.5 * f_floor, 0.06 * FLn))
    if peaks:
        mx = max(p for _, p in peaks)
        peaks = [(f, p) for f, p in peaks if p >= 0.02 * mx]
    return dict(peaks=peaks, freq=freq, psd=psd, noise=float(np.median(psd)),
                f_floor=f_floor)


def snap_g(f_nu):
    """Snap n/n_SdH = 1/f_nu to the nearest allowed isospin degeneracy {1,2,4}."""
    if f_nu <= 0 or not np.isfinite(f_nu):
        return None, np.inf
    g_est = 1.0 / f_nu
    cands = np.array([1, 2, 4])
    k = int(np.argmin(np.abs(cands - g_est)))
    g = int(cands[k])
    rel = abs(g_est - g) / g
    return g, rel


def tone_table(col, n):
    """Per-tone n_SdH / f_nu / degeneracy read for one column."""
    out = []
    FLn = sf.F_L(abs(n))
    for f, p in col["peaks"]:
        n_sdh = NSDH_PER_T * f
        f_nu = n_sdh / abs(n) if n != 0 else np.nan
        g, grel = snap_g(f_nu)
        out.append(dict(f=f, power=p, n_sdh=n_sdh, f_nu=f_nu,
                        ratio_FL=f / FLn, g=g, g_rel=grel))
    return out


# ----------------------------------------------------------------------------
# Fan-level evaluation.
# ----------------------------------------------------------------------------
def evaluate_fan(cfg):
    fan = rl.load_fan(cfg["id"], contact=cfg["contact"])
    B, Rxx, n, D = fan["B"], fan["Rxx"], fan["n"], fan["D"]
    blo, bhi = cfg["blo"], min(cfg["bhi"], float(np.nanmax(B)))
    sign = 1 if np.nanmedian(n) >= 0 else -1

    records, cols = [], []
    for j in range(n.size):
        nn = float(n[j])
        if abs(nn) < 0.12:                      # skip the CNP column (F_L->0)
            continue
        FLn = sf.F_L(abs(nn))
        col = analyze_column(B, Rxx[:, j], FLn, blo, bhi)
        tones = tone_table(col, nn)
        cols.append(dict(j=j, n=nn, D=float(D[j]), FLn=FLn, tones=tones,
                         peaks=col["peaks"], noise=col["noise"]))
        # build a record in se's shape for the mechanical (free-scale) recipe
        records.append(dict(j=j, n_nominal=nn, F_L_nom=FLn, freq=col["freq"],
                            psd=col["psd"], peaks=col["peaks"],
                            noise=col["noise"] if np.isfinite(col["noise"]) else 0.0))

    # --- (a) mechanical recipe, run BLIND with a free scale --------------------
    valid = [r for r in records if r["peaks"]]
    se.screen_harmonics(valid)
    s_fit = se.fit_scale(valid) if valid else float("nan")
    abab_pred, aba_pred = se.template_curves(sign)
    mech = []
    for r in valid:
        f_floor = 3.0 / (1.0 / blo - 1.0 / bhi)
        lab, _det = se.classify_column(r, s_fit, abab_pred, aba_pred, f_floor, blo, bhi)
        mech.append((r["n_nominal"], lab))

    # --- (b) calibration-fixed degeneracy audit -------------------------------
    for c in cols:
        dom = c["tones"][0] if c["tones"] else None
        c["dom"] = dom
        if dom is None:
            c["read"] = "no-tone"
            continue
        # multitone / non-Onsager: ANY significant tone whose single-pocket
        # density exceeds the gate density (f_nu > 1) cannot be a
        # simply-connected pocket in a g>=1 metal — the paper's multitone
        # signature (their high tones n_SdH ~ 0.89, 1.19 exceed n near the CSC).
        # "significant" = >= 15% of the dominant tone's power.
        pmax = dom["power"]
        big = [t for t in c["tones"] if t["power"] >= 0.15 * pmax]
        over = [t for t in big if t["f_nu"] > 1.15]
        if over:
            c["read"] = "non-onsager(f_nu>1)"
            c["over_tones"] = [(round(t["f"], 1), round(t["f_nu"], 2)) for t in over]
        elif dom["g"] is not None and dom["g_rel"] <= 0.18:
            c["read"] = f"g={dom['g']}"
        else:
            c["read"] = "unresolved-g"

    return dict(cfg=cfg, D_med=float(np.nanmedian(D)), n_range=(float(np.nanmin(n)), float(np.nanmax(n))),
                B_window=(blo, bhi), cols=cols, s_fit=s_fit, mech=mech, sign=sign, fan=fan)


# ----------------------------------------------------------------------------
# LK effective-mass fit.
# ----------------------------------------------------------------------------
def lk_effective_mass(ids=LK_IDS, contact=2):
    """Extract the CQM SdH amplitude vs T and fit the LK thermal damping
    R_T(T) = X/sinh(X), X = 2*pi^2*kB*T*m* / (hbar*e*B_eff), for m*."""
    kB, hbar, e, m_e = 1.380649e-23, 1.054571817e-34, 1.602176634e-19, 9.1093837015e-31
    sweeps = []
    for i in ids:
        try:
            s = rl.load_field_sweep(i, contact=contact)
        except Exception:
            continue
        sweeps.append(s)
    if len(sweeps) < 3:
        return None
    # fixed physical analysis window the series was designed for (0.75-1.25 T);
    # skip sweeps that don't cover it rather than clamping the window to the
    # shortest sweep. B_eff = mean-1/B field (SdH amplitude is high-B weighted).
    blo, bhi = 0.8, 1.2
    sweeps = [s for s in sweeps
              if np.nanmin(s["B"]) <= blo + 0.02 and np.nanmax(s["B"]) >= bhi - 0.02]
    if len(sweeps) < 3:
        return None
    B_eff = 1.0 / (0.5 * (1.0 / blo + 1.0 / bhi))     # mid-window field
    # CQM at (n=1, D=1): single tone at n_SdH = n -> f = n/NSDH_PER_T
    F_target = 1.0 / NSDH_PER_T                        # ~41.3 T for n=1
    def raw_amplitude(B, R, band_lo, band_hi):
        """Absolute (UN-normalized) FFT amplitude in a frequency band. se's
        column_spectrum normalizes by psd.max(), which erases the thermal
        damping we are trying to measure — so run the same primitives here and
        keep the raw magnitude."""
        o = np.argsort(B)
        B, R = B[o], R[o]
        m = (B >= blo) & (B <= bhi)
        B, R = B[m], R[m]
        if B.size < 48:
            return np.nan
        R = se.detrend_poly_B(B, R, degree=5)
        invB, Ri = se.interp_to_invB(B, R, nx=1000)
        Ri = se.detrend_butter_invB(invB, Ri, cutoff=0.8)
        freq, psd = se.fft_psd(invB, Ri, padding=8)
        band = (freq > band_lo) & (freq < band_hi)
        return float(np.sqrt(psd[band].max())) if band.any() else np.nan

    amps, temps = [], []
    for s in sweeps:
        Bc, Rc = clean_BR(s["B"], s["Rxx"])
        if Bc.size < 48:
            continue
        A = raw_amplitude(Bc, Rc, 0.85 * F_target, 1.15 * F_target)
        if not np.isfinite(A):
            continue
        amps.append(A)
        temps.append(s["T"])
    amps, temps = np.array(amps), np.array(temps)
    if amps.size < 3:
        return None

    def R_T(T, mstar):
        X = 2 * np.pi**2 * kB * T * mstar * m_e / (hbar * e * B_eff)
        return X / np.sinh(X)

    # normalized amplitude fit: A(T)/A0 = R_T(T)/R_T(T0)
    order = np.argsort(temps)
    temps, amps = temps[order], amps[order]
    from scipy.optimize import curve_fit
    T0 = temps[0]

    def model(T, mstar, A0):
        return A0 * R_T(T, mstar) / R_T(T0, mstar)
    try:
        popt, pcov = curve_fit(model, temps, amps, p0=[0.4, amps[0]],
                               bounds=([0.05, 0], [3.0, 10 * amps.max()]))
        mstar, _A0 = popt
        merr = float(np.sqrt(pcov[0, 0]))
    except Exception:
        return dict(temps=temps.tolist(), amps=amps.tolist(), B_eff=B_eff,
                    mstar=None, fit_ok=False)
    return dict(temps=temps.tolist(), amps=amps.tolist(), B_eff=B_eff,
                F_target=F_target, mstar=float(mstar), mstar_err=merr,
                fit_ok=True, n_pts=int(amps.size))


# ----------------------------------------------------------------------------
# Diagnostics + reporting.
# ----------------------------------------------------------------------------
def fan_png(res):
    if not HAVE_MPL:
        return
    cols = [c for c in res["cols"] if c["peaks"]]
    if not cols:
        return
    pick = cols[:: max(1, len(cols) // 6)][:6]
    fig, axes = plt.subplots(len(pick), 1, figsize=(6, 9), sharex=False)
    for ax, c in zip(np.atleast_1d(axes), pick):
        f, p = c_freqpsd(res, c)
        if f is None:
            continue
        FLn = c["FLn"]
        ax.plot(f, p, lw=0.8)
        for mult, col_ in ((1, "C2"), (2, "C1"), (4, "C3")):
            ax.axvline(mult * FLn, color=col_, ls="--", lw=0.7)
        for t in c["tones"][:4]:
            ax.plot(t["f"], t["power"], "o", ms=4, color="k")
        ax.set_xlim(0, 5.2 * FLn)
        ax.set_ylabel(f"n={c['n']:.2f}", fontsize=7)
    axes[0].set_title(f"{res['cfg']['id']} {res['cfg']['label']}\n"
                      "dash: F_L (g4,green) 2F_L (g2,orange) 4F_L (g1,red)", fontsize=7)
    axes[-1].set_xlabel("F (T)")
    fig.tight_layout()
    d = OUT / str(res["cfg"]["id"])
    d.mkdir(parents=True, exist_ok=True)
    fig.savefig(d / "spectra.png", dpi=90)
    plt.close(fig)


def c_freqpsd(res, c):
    # recompute the spectrum for the picked column (freq/psd not stored per col)
    fan = res["fan"]
    blo, bhi = res["B_window"]
    B, R = clean_BR(fan["B"], fan["Rxx"][:, c["j"]])
    if B.size < 48:
        return None, None
    return se.column_spectrum(B, R, blo, bhi, 0.8)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results = [evaluate_fan(cfg) for cfg in FANS]
    lk = lk_effective_mass()
    for res in results:
        fan_png(res)
    payload = summarize(results, lk)
    (OUT / "results.json").write_text(json.dumps(payload, indent=2, default=float))
    print(payload["console"])
    return results, lk


def summarize(results, lk):
    lines = []
    lines.append("=" * 78)
    lines.append("RPL_19 (rmg19) real-data validation — tetralayer FS-count stack")
    lines.append("=" * 78)
    for res in results:
        cfg = res["cfg"]
        reads = {}
        for c in res["cols"]:
            reads[c.get("read", "?")] = reads.get(c.get("read", "?"), 0) + 1
        mech = {}
        for _, lab in res["mech"]:
            mech[lab] = mech.get(lab, 0) + 1
        lines.append(f"\n[{cfg['id']}] {cfg['label']}")
        lines.append(f"  D≈{res['D_med']:.2f}  n∈[{res['n_range'][0]:.2f},{res['n_range'][1]:.2f}]  "
                     f"B∈{res['B_window']}  cols={len(res['cols'])}")
        lines.append(f"  (a) free-scale recipe: s_fit={res['s_fit']:.2f}  "
                     f"labels={mech}")
        lines.append(f"  (b) degeneracy audit: {reads}")
        # sample a few columns
        for c in res["cols"][:: max(1, len(res["cols"]) // 4)][:4]:
            if not c["tones"]:
                continue
            t = c["tones"][0]
            lines.append(f"      n={c['n']:+.2f}: dom f={t['f']:.1f}T "
                         f"n_SdH={t['n_sdh']:.2f} f_ν={t['f_nu']:.2f} "
                         f"(F_L={c['FLn']:.1f}, ratio={t['ratio_FL']:.2f}) -> {c['read']}")
    if lk and lk.get("fit_ok"):
        lines.append(f"\n[LK] effective mass at (n=1,D=1): m*={lk['mstar']:.3f}±"
                     f"{lk['mstar_err']:.3f} m_e (B_eff={lk['B_eff']:.2f}T, "
                     f"{lk['n_pts']} T-points {min(lk['temps'])*1e3:.0f}-{max(lk['temps'])*1e3:.0f}mK)")
        lines.append("     paper Fig 3g: m* = 0.39 -> 0.7 m_e (rising as n->n_c)")
    elif lk:
        lines.append(f"\n[LK] fit failed; T-points={len(lk.get('temps',[]))}")
    console = "\n".join(lines)
    return dict(console=console,
                fans=[dict(id=r["cfg"]["id"], label=r["cfg"]["label"],
                           D=r["D_med"], s_fit=r["s_fit"],
                           reads={c["j"]: dict(n=c["n"], read=c.get("read"),
                                               dom=c["tones"][0] if c["tones"] else None)
                                  for c in r["cols"]}) for r in results],
                lk=lk)


if __name__ == "__main__":
    main()
