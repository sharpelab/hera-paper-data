#!/usr/bin/env python3
"""
Synthetic Landau-fan generator on the validated tetralayer band model.

Builds Rxx(n, B) fans by dressing the B=0 Onsager frequencies F_j(n) and
cyclotron masses m*_j(n) from fs_count_b0 with Lifshitz-Kosevich thermal /
Dingle damping, a 2nd harmonic, a smooth non-oscillatory background, Gaussian
noise, and (optionally) a lever-arm scale error, a magnetic-breakdown sum-tone,
or a two-stacking mixed-domain superposition. Each fan is written as an .npz
plus a truth.json that records the generating ground truth.

Physics per Onsager orbit j at density n:
  dR_j = A_j * R_T(m*_j,T,B) * R_D(m*_j,T_D,B) * cos(2*pi*F_j/B + phi_j)
  R_T = X/sinh(X),  X = alpha*m*T/B,  alpha = 2*pi^2 k_B m_e/(hbar e) ~ 14.69 T/K
  R_D = exp(-alpha*m* T_D/B)
Second harmonic: 0.15*A_j*R_T(2X)*R_D(2*..)*cos(4*pi*F_j/B + phi2_j).

Run:
  uv run --no-project --with numpy --with scipy [--with matplotlib] \
      python3 synth_fan.py --all
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

# ---- import the validated forward model by path ----
_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("fs_count_b0", _HERE / "fs_count_b0.py")
assert _spec is not None and _spec.loader is not None
fb = importlib.util.module_from_spec(_spec)
sys.dont_write_bytecode = True
_spec.loader.exec_module(fb)

DATA_DIR = Path("/data/sharpelab/hera-data/tetralayer-synth-validation")

# LK constant: alpha = 2 pi^2 k_B m_e / (hbar e)  [T/K], m* in units of m_e
ALPHA = 2 * np.pi**2 * 1.380649e-23 * fb.ME / (fb.HBAR * fb.E)  # ~14.69

H_OVER_4E = fb.HBAR * 2 * np.pi / (4 * fb.E)  # F_L = (h/4e)|n| ; n in m^-2


def F_L(n12):
    """Luttinger frequency (T) for |n| in 1e12 cm^-2 units (g=4)."""
    return H_OVER_4E * abs(n12) * 1e16


# ---------------- table-reusing orbit extraction ----------------
# The model rebuilds its density table on every public call (seconds for the
# 2D ABCA solve). We build each table once and interpolate across columns.

def _bernal_table(seq, p, ud=0.0):
    kg, Eb, EFs, nvals = fb._radial_table(seq, p, ud, 6e8, 7000, 0.3, 12001)
    return dict(kind="bernal", kg=kg, Eb=Eb, EFs=EFs, nvals=nvals)


def _bernal_orbits(tab, n_m2):
    """[(F, m*/m_e), ...] at signed density n_m2 (m^-2), sorted by F."""
    EF = fb._interp_domain_checked(n_m2, tab["nvals"], tab["EFs"], "bernal")
    out = []
    for F, kF, b, c in fb._radial_orbits(tab["kg"], tab["Eb"], EF):
        dEdk = abs(tab["Eb"][b, c + 1] - tab["Eb"][b, c]) / (
            tab["kg"][c + 1] - tab["kg"][c]) * fb.E
        out.append((F, fb.HBAR**2 * kF / dEdk / fb.ME))
    return sorted(out)


def _rhombo_table(seq, p, ud, band):
    Egrid, dk, EFs, nvals = fb._rhombo_table(seq, p, ud, band, 6.5e8, 601, 6000)
    return dict(kind="rhombo", Egrid=Egrid, dk=dk, EFs=EFs, nvals=nvals, band=band)


def _rhombo_orbits(tab, n_m2, fit_mev=0.6):
    """[(F_total, m*/m_e)] single tone at signed density n_m2 (m^-2)."""
    EF = fb._interp_domain_checked(n_m2, tab["nvals"], tab["EFs"], "rhombo")
    occ = (tab["Egrid"] < EF) if tab["band"] > 0 else (tab["Egrid"] > EF)
    F = fb.F_from_area(occ.sum() * tab["dk"] * tab["dk"])
    win = np.abs(tab["EFs"] - EF) <= fit_mev * 1e-3
    if win.sum() < 10:
        raise ValueError("m* window off the solved table")
    slope = np.polyfit(tab["EFs"][win], tab["nvals"][win], 1)[0] / fb.E
    return [(F, np.pi / 2 * fb.HBAR**2 * abs(slope) / fb.ME)]


def orbits_for(stacking, sign, ud=0.0):
    """Return a callable n12 -> [(F, m*, label), ...] for a stacking + sign."""
    if stacking == "ABAB":
        tab = _bernal_table("ABAB", fb.ABAB, ud)

        def f(n12):
            os = _bernal_orbits(tab, sign * n12 * 1e16)
            labels = _label_pair(os)
            return [(F, m, lab) for (F, m), lab in zip(os, labels)]
        return f
    if stacking == "ABCA":
        band = 1 if sign > 0 else -1
        tab = _rhombo_table("ABCA", fb.ABCA, ud, band)

        def f(n12):
            os = _rhombo_orbits(tab, sign * n12 * 1e16)
            return [(os[0][0], os[0][1], "singleton")]
        return f
    if stacking == "ABA":  # trilayer, for the mislabeled-N case
        tab = _bernal_table("ABA", fb.ABA_TRI, ud)

        def f(n12):
            os = _bernal_orbits(tab, sign * n12 * 1e16)
            labels = _label_pair(os)
            return [(F, m, lab) for (F, m), lab in zip(os, labels)]
        return f
    raise ValueError(stacking)


def _label_pair(orbits):
    """Name the two dominant orbits light/heavy; extras get orbit_k."""
    if len(orbits) == 1:
        return ["heavy"]
    labs = [None] * len(orbits)
    # smallest F = light, largest F = heavy
    fi = np.argsort([F for F, _ in orbits])
    labs[fi[0]] = "light"
    labs[fi[-1]] = "heavy"
    k = 0
    for i in range(len(orbits)):
        if labs[i] is None:
            labs[i] = f"orbit_{k}"
            k += 1
    return labs


# ---------------- LK reduction factors ----------------

def R_T(mstar, T, B, harmonic=1):
    X = harmonic * ALPHA * mstar * T / B
    return np.where(X < 1e-9, 1.0, X / np.sinh(np.clip(X, 0, 700)))


def R_D(mstar, T_D, B, harmonic=1):
    return np.exp(-harmonic * ALPHA * mstar * T_D / B)


# ---------------- fan generation ----------------

def generate_fan(*, case, stacking, sign, s=1.0,
                 n_lo=0.8, n_hi=6.0, n_cols=40,
                 B_lo=0.35, B_hi=3.0, n_B=900,
                 T=1.4, T_D=1.5, osc_frac=0.20, noise_frac=0.004,
                 breakdown=None, mixed=None, seed=0,
                 nominal_material="4LGr", true_material=None):
    """
    Build one Rxx(n,B) fan and its truth record.

    breakdown : None or dict(B0=..., weight=...) — sum-tone at F_sum=Sum F_j.
    mixed     : None or dict(stacking=..., weight=(w0,w1)) — superpose a second
                stacking's dR on the same grid (weights sum to 1).
    """
    rng = np.random.default_rng(seed)
    invB = np.linspace(1.0 / B_hi, 1.0 / B_lo, n_B)  # uniform in 1/B
    B = 1.0 / invB                                    # descending 3.0 -> 0.35
    n12 = np.linspace(n_lo, n_hi, n_cols)             # magnitude, 1e12 cm^-2
    n_nominal = sign * n12                            # reported density axis

    orbfn = orbits_for(stacking, sign)
    orbfn2 = orbits_for(mixed["stacking"], sign) if mixed else None

    Rxx = np.zeros((n_B, n_cols))
    truth_cols = []

    for j, nn in enumerate(n_nominal):
        n_true = s * nn                 # true density that sets the physics
        R0 = 800.0 / (1.0 + abs(n_true))  # few hundred ohms, falling with |n|
        c1, c2 = 0.03, -0.004
        bg = R0 * (1.0 + c1 * B + c2 * B**2)

        col_truth: dict = dict(i=int(j), n_nominal=float(nn), n_true=float(n_true),
                         R0=float(R0), F_L_nominal=float(F_L(nn)),
                         F_L_true=float(F_L(n_true)), fundamentals=[])

        def add_stacking(orbf, weight, tag, record):
            dR = np.zeros(n_B)
            Fs = []
            for (F, mstar, lab) in orbf(abs(n_true)):
                A = weight * osc_frac * R0
                phi = rng.uniform(0, 2 * np.pi)
                dR += A * R_T(mstar, T, B) * R_D(mstar, T_D, B) * np.cos(
                    2 * np.pi * F / B + phi)
                # 2nd harmonic ~15%, extra Dingle (squared damping)
                phi2 = rng.uniform(0, 2 * np.pi)
                dR += 0.15 * A * R_T(mstar, T, B, 2) * R_D(mstar, T_D, B, 2) * \
                    np.cos(4 * np.pi * F / B + phi2)
                Fs.append(F)
                if record:
                    col_truth["fundamentals"].append(
                        dict(stacking=tag, label=lab, F=float(F),
                             mstar=float(mstar), A=float(A)))
            return dR, Fs

        if mixed:
            w0, w1 = mixed["weight"]
            dR0, Fs0 = add_stacking(orbfn, w0, stacking, True)
            dR1, _Fs1 = add_stacking(orbfn2, w1, mixed["stacking"], True)
            osc = dR0 + dR1  # mixed-domain: primary truth keeps Fs0
            Fs = Fs0
        else:
            osc, Fs = add_stacking(orbfn, 1.0, stacking, True)

        # magnetic-breakdown sum-tone at F_sum = sum of the primary tones
        col_truth["breakdown"] = None
        if breakdown:
            F_sum = float(np.sum(Fs))
            B0 = breakdown["B0"]
            w = breakdown["weight"]
            phi = rng.uniform(0, 2 * np.pi)
            osc = osc + w * osc_frac * R0 * np.exp(-B0 / B) * np.cos(
                2 * np.pi * F_sum / B + phi)
            col_truth["breakdown"] = dict(F=F_sum, B0=float(B0), weight=float(w))

        noise = rng.normal(0.0, noise_frac * R0, n_B)
        Rxx[:, j] = bg + osc + noise
        truth_cols.append(col_truth)

    truth = dict(
        case=case, stacking_true=stacking, sign=int(sign), s=float(s),
        nominal_material=nominal_material,
        true_material=true_material or f"{stacking}-4L",
        T=float(T), T_D=float(T_D), osc_frac=float(osc_frac),
        noise_frac=float(noise_frac),
        B_lo=float(B_lo), B_hi=float(B_hi), n_B=int(n_B),
        n_lo=float(n_lo), n_hi=float(n_hi), n_cols=int(n_cols),
        breakdown=breakdown, mixed=mixed, seed=int(seed),
        columns=truth_cols)

    out = DATA_DIR / case
    out.mkdir(parents=True, exist_ok=True)
    np.savez(out / "fan.npz", Rxx=Rxx, B=B, n=n_nominal)
    with open(out / "truth.json", "w") as fh:
        json.dump(truth, fh, indent=2)
    print(f"[{case}] wrote {out/'fan.npz'}  Rxx{Rxx.shape}  "
          f"n=[{n_nominal[0]:.2f}..{n_nominal[-1]:.2f}]  stacking={stacking} s={s}")
    return out


# ---------------- the six cases ----------------

CASES = {
    "abab_hole": dict(stacking="ABAB", sign=-1, s=1.0, seed=1),
    "abab_electron_trap": dict(stacking="ABAB", sign=+1, s=1.0, seed=2),
    "abca_clean": dict(stacking="ABCA", sign=-1, s=1.0, seed=3),
    "abab_breakdown": dict(stacking="ABAB", sign=-1, s=1.0, seed=4,
                           breakdown=dict(B0=3.0, weight=3.0)),
    "abca_scale": dict(stacking="ABCA", sign=-1, s=1.12, seed=5),
    "mislabeled_N": dict(stacking="ABA", sign=-1, s=1.0, seed=6,
                         nominal_material="4LGr", true_material="ABA-3L"),
}


def generate_case(name):
    cfg = dict(CASES[name])
    return generate_fan(case=name, **cfg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--case", choices=list(CASES))
    args = ap.parse_args()
    if args.all:
        for name in CASES:
            generate_case(name)
    elif args.case:
        generate_case(args.case)
    else:
        ap.error("pass --all or --case NAME")


if __name__ == "__main__":
    main()
