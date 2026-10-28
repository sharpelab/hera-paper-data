#!/usr/bin/env python3
"""
Validation gates for the raman_stacking tool, run against labeled public data.

Data (see hera/docs/raman-public-data.md):
  $HERA_DATA/raman-public-data/zenodo-20374368-pku    (CC-BY 4.0)
  $HERA_DATA/raman-public-data/zenodo-10931524-nemes  (CC-BY-SA 4.0)

Gates:
  A  PKU labeled spectra (Fig 4A/4B: per-layer ABC vs AB, includes trilayer;
     Fig 2C1/2C2 single pair): our FWHM must separate the stackings in the
     ABC-broader direction at every layer number.
     [Assumption, flagged: 4A/2C1 = ABC, 4B/2C2 = AB -- inferred from the
     dataset's ABC-first column convention + lineshapes; paper not yet
     indexed to confirm.]
  B  Nemes FLG_38 labeled single pair (hexa vs rhomb): direction check.
  C  Nemes per-layer ABC spectra (multiple excitations): ABC signature
     consistency across wavelengths. ABC-only (no paired ABA) ->
     sensitivity-side evidence, not specificity. The deposit's 3/5/6-layer
     spectra cover only the ERS region (~3200-6600 cm^-1, their flat-band
     identification method) with no 2D band -- trilayer 2D-band ground
     truth in public data comes from Gate A (PKU) alone.
  E  Mixed-spectrum decomposition: recover known synthetic mixing fractions
     of gate D's cluster means (±0.1 at 2% noise); report real wall-pixel α.
  D  Nemes FLG_37 hyperspectral map (488 nm, 48x45 px): two-population FWHM
     segmentation; cluster mean spectra matched against the deposit's
     labeled region-average spectra (7/8-layer hexa/rhomb). The deposit has
     region-average spectra, NOT per-pixel masks -- so this gate scores
     population-level agreement, not pixel accuracy. Flake is 7/8-layer:
     validates the pipeline, not trilayer specifically.

Run: uv run --no-project --with numpy --with scipy --with matplotlib \
       python3 validate.py
"""
import re
import sys
from pathlib import Path

import numpy as np

from raman_io import (data_root, load_pku_pairs, load_spectrum, load_witec,
                      map_shape, witec_excitation_nm)
from metrics import decompose_mixed, metrics_2d
from map_tools import (cluster_mean_spectrum, per_pixel_metrics, to_image,
                       two_population_split)

OUT = Path(__file__).resolve().parent
RESULTS = []


def report(gate, ok, msg):
    RESULTS.append((gate, ok, msg))
    print(f"[{'PASS' if ok else 'FAIL'}] {gate}: {msg}")


def gate_a_pku():
    d = data_root() / "zenodo-20374368-pku"
    abc = load_pku_pairs(d / "Figure4A.csv")
    ab = load_pku_pairs(d / "Figure4B.csv")

    def by_layer(traces):
        out = {}
        for lab, wn, ii in traces:
            m = re.search(r"\((\d+)\s*layers?\)", lab)
            if m:
                mm = metrics_2d(wn, ii)
                if mm:
                    out[int(m.group(1))] = mm
        return out

    m_abc, m_ab = by_layer(abc), by_layer(ab)
    shared = sorted(set(m_abc) & set(m_ab))
    rows, ok_all = [], True
    for n in shared:
        a, b = m_abc[n], m_ab[n]
        ok = a["fwhm"] > b["fwhm"]
        ok_all &= ok
        rows.append((n, a["fwhm"], b["fwhm"], a["skew"], b["skew"],
                     a["ratio_lh"], b["ratio_lh"], ok))
    print("  N   FWHM(ABC)  FWHM(AB)   skew(ABC)  skew(AB)  r_lh(ABC)  r_lh(AB)")
    for r in rows:
        print(f"  {r[0]:>3}  {r[1]:8.1f}  {r[2]:8.1f}   {r[3]:8.2f}  {r[4]:8.2f}"
              f"  {r[5]:8.2f}  {r[6]:8.2f}  {'ok' if r[7] else 'X'}")
    report("A.pku-fig4", ok_all and 3 in m_abc,
           f"FWHM(ABC)>FWHM(AB) at all shared N={shared} (trilayer included: {3 in shared})")

    pair = []
    for f in ("Figure2C1.csv", "Figure2C2.csv"):
        (_, wn, ii), = load_pku_pairs(d / f)
        pair.append(metrics_2d(wn, ii))
    report("A.pku-fig2c", pair[0]["fwhm"] > pair[1]["fwhm"],
           f"2C1 (ABC-labeled) FWHM {pair[0]['fwhm']:.1f} vs 2C2 {pair[1]['fwhm']:.1f}")
    return {n: (m_abc[n], m_ab[n]) for n in shared}


def gate_b_nemes_pair():
    d = data_root() / "zenodo-10931524-nemes" / "Figure 2"
    wn_h, i_h = load_spectrum(d / "FLG_38--Spectrum--045--Spec.Data 1_ss_hexa.txt")
    wn_r, i_r = load_spectrum(d / "FLG_38--Spectrum--046--Spec.Data 1_ss_rhomb.txt")
    mh, mr = metrics_2d(wn_h, i_h), metrics_2d(wn_r, i_r)
    report("B.nemes-pair", mr["fwhm"] > mh["fwhm"],
           f"rhomb FWHM {mr['fwhm']:.1f} / skew {mr['skew']:.2f} vs "
           f"hexa {mh['fwhm']:.1f} / {mh['skew']:.2f}")
    return mh, mr


def gate_c_nemes_layers():
    d = data_root() / "zenodo-10931524-nemes" / "Figure 3 and 4" / "data"
    rows, ers_only = [], []
    for sub in sorted(d.iterdir()):
        if not sub.is_dir() or "layer" not in sub.name:
            continue
        nm = None
        for info in sub.glob("*Information.txt"):
            nm = witec_excitation_nm(info)
            if nm:
                break
        if nm is None:
            m = re.search(r"_(\d{3})$", sub.name)
            nm = float(m.group(1)) if m else np.nan
        for f in sorted(sub.glob("*.txt")):
            if "Information" in f.name:
                continue
            try:
                wn, ii = load_spectrum(f)
            except Exception:
                continue
            mm = metrics_2d(wn, ii)
            if mm:
                rows.append((sub.name, f.name[:40], nm, mm))
            else:
                ers_only.append((sub.name, wn.min(), wn.max()))
    print("  dir              file                                      nm     FWHM   skew")
    for name, fn, nm, mm in rows:
        print(f"  {name:<16} {fn:<40} {nm:6.0f} {mm['fwhm']:7.1f} {mm['skew']:6.2f}")
    for name, lo, hi in ers_only:
        print(f"  {name:<16} [ERS-region export, {lo:.0f}-{hi:.0f} cm^-1, no 2D band]")
    wavelengths = {round(nm) for _, _, nm, _ in rows if np.isfinite(nm)}
    fwhms = np.array([mm["fwhm"] for _, _, _, mm in rows])
    skews = np.array([mm["skew"] for _, _, _, mm in rows])
    ok = len(rows) >= 10 and len(wavelengths) >= 2
    report("C.nemes-abc-layers", ok,
           f"{len(rows)} labeled-ABC 2D spectra at {sorted(wavelengths)} nm, "
           f"FWHM {fwhms.min():.0f}-{fwhms.max():.0f}, median skew {np.median(skews):.2f}; "
           f"{len(ers_only)} ERS-only exports (incl. all trilayer -- 2D-band "
           f"trilayer truth is Gate A)")
    return rows


def gate_d_map():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    base = data_root() / "zenodo-10931524-nemes"
    wn, ii, hdr = load_witec(
        base / "Figure 2" /
        "FLG_37--Scan Piezo--013--Spec.Data 1 (Sub BG) (CRR)_2D only_anal90.txt")
    sx, sy = map_shape(hdr)
    px = per_pixel_metrics(wn, ii)
    labels, centers = two_population_split(px["fwhm"])
    n0, n1 = (labels == 0).sum(), (labels == 1).sum()
    print(f"  map {sx}x{sy}: {np.isfinite(px['fwhm']).sum()} graphene px, "
          f"clusters {n0} @ {centers[0]:.1f} / {n1} @ {centers[1]:.1f} cm^-1")

    # labeled region-average spectra from the deposit (7/8-layer hexa/rhomb)
    refs = {}
    rdir = base / "Figure 3 and 4"
    for f in rdir.glob("*mask_Draw Image*"):
        tag = ("rhomb" if "rhom" in f.name else "hexa") + \
              ("-7L" if f.name.startswith("7") else "-8L")
        rwn, rii = load_spectrum(f)
        refs[tag] = (rwn, rii, metrics_2d(rwn, rii))
    for tag, (_, _, m) in sorted(refs.items()):
        print(f"  ref {tag:<9} FWHM {m['fwhm']:6.1f}  skew {m['skew']:5.2f}")
    ok_refs = all(refs[f"rhomb-{n}"][2]["fwhm"] > refs[f"hexa-{n}"][2]["fwhm"]
                  for n in ("7L", "8L"))
    report("D.map-refs", ok_refs,
           "labeled region averages: rhomb FWHM > hexa at 7L and 8L")

    # Match each cluster to the labeled averages by the discriminating
    # metric itself (FWHM of the cluster-mean spectrum): waveform
    # correlation is dominated by overall band presence and cannot
    # separate 61 vs 78 cm^-1 populations.
    match, ok_match = {}, True
    for k, want in ((0, "hexa"), (1, "rhomb")):
        spec = cluster_mean_spectrum(ii, labels, k)
        mm = metrics_2d(wn, spec)
        best = min(refs, key=lambda t: abs(refs[t][2]["fwhm"] - mm["fwhm"]))
        match[k] = (best, mm["fwhm"])
        ok_match &= best.startswith(want)
        print(f"  cluster {k} ({'low' if k == 0 else 'high'}-FWHM) mean-spectrum "
              f"FWHM {mm['fwhm']:.1f} -> nearest ref {best} "
              f"({refs[best][2]['fwhm']:.1f})")
    report("D.map-clusters", ok_match,
           f"low-FWHM cluster -> {match[0][0]}, high-FWHM cluster -> {match[1][0]}")

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    im0 = axes[0].imshow(to_image(px["fwhm"], sx, sy), origin="lower", cmap="viridis")
    axes[0].set_title("2D FWHM (cm$^{-1}$)")
    fig.colorbar(im0, ax=axes[0], shrink=0.8)
    axes[1].imshow(to_image(labels, sx, sy), origin="lower", cmap="coolwarm",
                   vmin=-1, vmax=1)
    axes[1].set_title(f"segmentation (red=broad, {centers[1]:.0f} cm$^{{-1}}$)")
    for k, color in ((0, "C0"), (1, "C3")):
        spec = cluster_mean_spectrum(ii, labels, k)
        axes[2].plot(wn, spec / spec.max(), color,
                     label=f"cluster {k} ({'narrow' if k == 0 else 'broad'})")
    for tag, sty in (("hexa-7L", "C0--"), ("rhomb-7L", "C3--")):
        rwn, rii, _ = refs[tag]
        rn = rii - np.median(rii[:50])
        axes[2].plot(rwn, rn / rn.max(), sty, alpha=0.6, label=f"ref {tag}")
    axes[2].set_xlim(2550, 2850)
    axes[2].set_xlabel("Raman shift (cm$^{-1}$)")
    axes[2].legend(fontsize=7)
    axes[2].set_title("cluster means vs labeled averages")
    fig.tight_layout()
    fig.savefig(OUT / "flg37_map_validation.png", dpi=140)
    print(f"  wrote {OUT / 'flg37_map_validation.png'}")
    return wn, ii, px, labels


def gate_e_decompose(wn, ii, px, labels):
    """Mixed-spectrum decomposition: recover known synthetic mixing
    fractions of the map's own cluster means (small noise added), and
    report the α distribution of the real intermediate-FWHM pixels."""
    a = cluster_mean_spectrum(ii, labels, 0)  # narrow / hexa
    b = cluster_mean_spectrum(ii, labels, 1)  # broad / rhomb
    rng = np.random.default_rng(20260717)
    noise = 0.02 * b.max()
    ok, rows = True, []
    for alpha_true in (0.0, 0.25, 0.5, 0.75, 1.0):
        s = alpha_true * a + (1 - alpha_true) * b + rng.normal(0, noise, a.shape)
        d = decompose_mixed(wn, s, a, b)
        rows.append((alpha_true, d["alpha"], d["r2"]))
        ok &= abs(d["alpha"] - alpha_true) < 0.1
    for at, af, r2 in rows:
        print(f"  synthetic α={at:.2f} -> recovered {af:.3f} (r2 {r2:.3f})")
    inter = np.where((px["fwhm"] > 65) & (px["fwhm"] < 73))[0]
    alphas = [decompose_mixed(wn, ii[:, j], a, b)["alpha"] for j in inter]
    frac_mid = np.mean([(0.2 < al < 0.8) for al in alphas]) if alphas else 0.0
    print(f"  {len(inter)} intermediate-FWHM map pixels: "
          f"{100*frac_mid:.0f}% decompose at α ∈ (0.2, 0.8)")
    report("E.decompose", ok,
           f"synthetic mixtures recovered within ±0.1 at 2% noise "
           f"(real wall pixels: {100*frac_mid:.0f}% mid-α)")


def main():
    gate_a_pku()
    gate_b_nemes_pair()
    gate_c_nemes_layers()
    gate_e_decompose(*gate_d_map())
    print()
    fails = [r for r in RESULTS if not r[1]]
    print(f"{len(RESULTS) - len(fails)}/{len(RESULTS)} gates passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
