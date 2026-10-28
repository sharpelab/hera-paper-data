# ABAB light-tone prior from the literature (agent, 2026-09-23)

## Headline

Two independent routes reproduce the vti-02 light fraction F_light/F_L to within ±0.01 over
n 1.5–3.0 (10¹² cm⁻²), with nothing fitted to vti-02:
- **(A)** published Bernal-tetralayer sets: **Halder_ABAB** (arXiv 2607.25757, ABAB SdH) and
  **Shi_ABAB** (PRL 120 096802, ABAB LL crossings), with no added screening. Both reach
  rms 0.005–0.006.
- **(B)** corpus or graphite parameters plus self-consistent D = 0 Hartree screening, which the
  corpus model omits.

The corpus model runs about 0.033 low. Two things are wrong with it: its effective γ2 is too
strong for ABAB, and it omits D = 0 screening. Either one alone closes the gap, so vti-02 can't
tell them apart. γ3 = 0 is not the cause: it moves the fraction by only +0.002 to +0.004. A
residual |D| ≲ 0.02–0.03 V/nm pushes the fraction the wrong way, by at most −0.003 to −0.01.

Halder check on a different device: Halder's own finite-D point (n 1.5, D/ε0 0.15 V/nm)
reproduces as 13.73 / 1.78 T against the measured 13.84 / 1.81 T (1–2 %).

## Observed reference

Density frame pinned by the F_L tone: 0825 ×0.951, 0822 ×1.018 on top of the fixture frame.

| n | 1.56 | 1.85 | 2.15 | 2.45 | 2.75 |
|---|---|---|---|---|---|
| light fraction | 0.178 | 0.192 | 0.213 | 0.224 | 0.238 |

- Below n 1.5 the light tone has fewer than 2 periods, so those columns are unreliable.
- The brief's "8–29 % low" figure includes those columns. On clean columns the gap is a
  near-constant −0.03.

## Sets vs vti-02 (none fitted to it)

| Set | screening | fraction at n 1.5 / 2.0 / 2.5 / 3.0 | rms | mean residual |
|---|---|---|---|---|
| corpus_KM | none | 0.132 / 0.172 / 0.197 / 0.215 | 0.033 | −0.033 |
| **Shi_ABAB** | none | 0.165 / 0.207 / 0.232 / 0.250 | 0.005 | +0.002 |
| **Halder_ABAB** | none | 0.164 / 0.206 / 0.233 / 0.252 | 0.006 | +0.002 |
| Campos_ABA | none | 0.166 / 0.201 / 0.222 / 0.238 | 0.005 | −0.005 |
| Zibrov_ABA | none | 0.173 / 0.210 / 0.234 / 0.251 | 0.006 | +0.005 |
| graphite_DD | none | 0.154 / 0.189 / 0.212 / 0.228 | 0.016 | −0.016 |
| graphite_DD | ε 5.7, Fermi sea only | 0.174 / 0.211 / 0.234 / 0.252 | 0.006 | +0.006 |
| corpus_KM | ε 4, with valence | 0.156 / 0.197 / 0.224 / 0.243 | 0.009 | −0.007 |
| Shi / Halder | ε 5.7 | ~0.184 / 0.227 / 0.255 / 0.274 | 0.023 | +0.022 |
| trilayer γ2 sets (Taychat, Wu, Stepanov, Yagi2018) | none | 0.075–0.108 at n 1.5 | 0.05–0.07 | −0.05 to −0.07 |

Adding screening on top of Shi or Halder overshoots: their fits already absorb it.

## Recommendation (the prior)

**Halder_ABAB** at D = 0, with no added screening and γ3 on (2D grid solve). Shi_ABAB is its
twin. The parameters are γ0 3.0, γ1 0.39, γ2 −0.020, γ3 0.3, γ4 0.04, γ5 0.04 and Δ′ 0.0303,
with middle-pair couplings Γ1/Γ3/Γ4 = 0.32/0.25/0.032. The middle-pair values are quoted
secondhand from Klanurak 2024, because the Shi supplement is paywalled.

| n | 1.0 | 1.25 | 1.5 | 1.75 | 2.0 | 2.5 | 3.0 | 3.5 |
|---|---|---|---|---|---|---|---|---|
| fraction | 0.082 | 0.131 | 0.164 | 0.188 | 0.206 | 0.233 | 0.252 | 0.265 |
| F_light (T) | 0.85 | 1.69 | 2.54 | 3.40 | 4.27 | 6.02 | 7.80 | 9.60 |

- Masses (light / heavy): 0.027 / 0.053 at n 1.5, 0.030 / 0.057 at n 3.0.
- The ratio heavy/light ≈ 1.9–2.0, against a measured 1.2–1.5 (model-fit).

**Band:** the spread across the independent routes is ±0.01 in fraction at n ≥ 1.5, which is
≤ 0.3 T and much smaller than δF of about 1.1 T. At n 1.0–1.25 it is ±0.03. The light-pocket
onset lands at n ≈ 0.75–0.85. Hole side: not studied.

## Knob sensitivities (vs corpus; `scan1d.csv`, `hartree_scan.csv`)

- **γ2** −0.032 → 0: fraction moves −0.095 → +0.157 at n 1.5, about 7.8 per eV at n 1.5 and
  3.9 per eV at n 3.
- **γ0** 2.6 → 3.16: −0.050 → +0.015.
- **γ1** 0.36 → 0.42: +0.017 → −0.009.
- **γ4** 0 → 0.14: −0.010 → +0.022.
- **γ5** 0 → 0.06: −0.015 → +0.007.
- **Δ′**: ≤ 0.008.
- **γ3** 0 → 0.3: +0.002 to +0.004.
- **Hartree** ε_z 5.7 → 2.0: +0.021 to +0.049. This is a bracket, not a derivation: the result
  depends on the valence k cutoff.

## Files

- Main output: `curves_recommended.csv` (n 0.8–3.5, six variants).
- All sets: `litsets_curves.csv` (17 sets × 4 screening variants).
- Scans: `scan1d.csv`, `hartree_scan.csv`.
- Reference: `observed_fraction.csv`.
- Code: `abab_lib.py` (read-only corpus `build_h` plus a layer potential, a middle-pair
  override, the 2D grid solve and Hartree), `litsets_defs.py`, `litsets.py`, `scan1d.py`,
  `hartree_scan.py`, `curves.py`, `observed.py`.
