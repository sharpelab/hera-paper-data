# QC0426 Raman read — fresh-instance output contract (2026-07-25)

Fresh instance executing `recipes/investigations/raman-stacking-id.md` on
all three build-stage `.wip` files, corpus-allowlisted (recipe, STYLE,
tool + README, the three reference papers, device card, data dir) with no
sight of any transport result or prior session record. Contract as
returned; frictions and effort accounting are in the session record, not
here.

All data 532.34 nm (2.33 eV), WITec WS-3052, 100×/0.9 (spot ~0.7 µm);
maps on 600 g/mm (~8 cm⁻¹ class), spot spectra also at 1800 g/mm
(~2 cm⁻¹). N = 3 grower-stated (see hedges).

## Per-region / per-spot verdicts (strength scale, stage-stamped)

Coordinates are sample-stage µm per scan frame (flake map: x −35.8…+39.2,
y −22.3…+19.7; orientation anchored by spot1 registration — see hedges).

| Region / spot | Stage | Verdict |
|---|---|---|
| **R1** — central-left domain, x ≈ −22…+4, y ≈ −13…+8, plus upper-left patches; 51% of trilayer px (~899 µm²) | 04 flake (2026-04-28) | **ABA (strong)** |
| **R2** — right-of-center domain, x ≈ +4…+30, y ≈ −5…+12, plus interleaved 2–5 µm bands upper-left/lower-left; 49% of trilayer px (~854 µm²) | 04 flake | **ABC (strong)** — magnitude hedge: population split 5.2 cm⁻¹ below the ≳10 cm⁻¹ heuristic; the pattern axis (bimodal, coherent domains, sharp walls, screens passed) carries the grade |
| **spot1** (13.3, 0.9) — inside R2 | 04 flake | **ABC (strong)** — FWHM 64.5 (600 g/mm) / 63.9 (1800 g/mm), registration exact |
| **spot2** (−23.1, 5.1) — R1, ~1.5 µm from an R1/R2 wall | 04 flake | **ABA (strong)** — FWHM 58.7/58.5, matches R1 population per-spectrum, registration-independent |
| Flake-edge monolayer strips (FWHM ~29.6, 2D ctr 2676) | 04 flake | **uninformative** for trilayer stacking (N = 1) |
| p52 strips (FWHM 45–56 streaks; 330 px) | 04 flake | **uninformative** — thickness-ambiguous; 90% decompose (r² > 0.95) as in-map 1L+multilayer mixtures |
| Stack main gated body (Si-attenuated diagonal band; FWHM 62.9±1.8, 2D ctr 2703.6) | 05 stack (2026-05-05) | **consistent-with** at best for the buried channel — through-stack cap (graphite top+back gates in probe volume; +10 cm⁻¹ center shift vs flake body) |
| Stack off-gate periphery (FWHM 53.6±6.8, ctr 2696.1) | 05 stack | **weak** — heterogeneous, no clean split; not inconsistent with flake-stage assignments |
| Device map Scan LA--004, gated channel + finger gaps (FWHM 63.7±0.7, ctr 2703.8, uniform) | 06 device (2026-05-14/15) | **consistent-with** (either stacking) — through-stack cap; not evidence of conversion, not evidence against it |
| Device map Scan LA--002 | 06 device | **uninformative** — partial (2440/3721 px missing) and defocused (2D amp ~40–70× below Scan 004) |
| Device Spot1 (11.2, −4.3) | 06 device | **uninformative** — no G or 2D band; off-flake |

**Stage-stamp mapping to the finished device:** flake-stage call is "as
of 2026-04-28, bare exfoliated flake." Post-map steps by risk class:
stack assembly 04→05 (transfer/pickup — documented ABC→ABA converter
when hBN pickup runs along armchair) and device fabrication 05→06 (metal
deposition — documented µm-scale wall motion; lithography chemistry/bake
list **not supplied**). Direction ABC→ABA only: R2 (ABC) may be smaller,
moved, or absent in the finished device; R1 (ABA) remains ABA (sub-spot
slivers and unmapped areas excepted). Stages 05/06 can neither confirm
nor rule out R2's survival (through-stack cap).

## Evidence

- **Flake map (Scan LA--009, 75×42 µm, 0.75 µm step, 10 s/px, 2.43 mW
  in-fiber):** 3728/5757 credible graphene px. FWHM histogram
  multi-modal: 27 (1L), 52.5, 58.8, 64.0 cm⁻¹. After masking thickness
  populations, within-multilayer 2-means split: **58.75±0.84 (1585 px)
  vs 63.95±0.93 (1532 px), separation 5.2 cm⁻¹**, spatially coherent
  multi-µm domains, sharp walls (wall-mixture px ≈10% of body). Cluster
  mean spectra r² 0.991 / 0.986 (broad cluster more structured).
- **Reference panel:** Cong 2011 (532 nm, WITec, 600 g/mm; FWHM(2D)
  domain window 40–68 cm⁻¹, ABC broader) — populations inside it, ABC-
  candidate broader; lineshape family per Lui. (Matched against the
  papers' documented feature descriptions.)
- **2D-center microshift:** ABC-candidate 2693.0 vs ABA 2693.7 — ABA
  above ABC, matching Lui SI direction (weak, confirming).
- **G position:** ABC-candidate 1578.7 vs 1580.8 — ABC-redshifted,
  matching Cong direction (weak; doping-confounded).
- **Spot spectra (1800 g/mm):** spot1 63.9 / spot2 58.5 —
  grating-independent widths; both r² > 0.98.
- **Cross-checks:** G-width **conflicts** (broad-2D cluster has broader
  G, 12.6 vs 9.9, corr +0.84 — opposite Cong; d(2D)/d(G) slope 0.52 ⇒
  doping-dominated, not strain). M-band **conflicts/uninformative** —
  at 2.33 eV (inside the 2.1–2.4 eV crossing) directions invert vs
  Cong's table, as the crossing caveat predicts; weighted ~zero.
  Conflicts reported, not averaged; the call rests on the 2D-width
  channel.
- **Stack/device maps:** dominant populations 62.9±1.8 / 63.7±0.7 at ctr
  ~2703.7 (+10 cm⁻¹ vs flake body — gate-stack superposition); Si-520
  attenuation images the gated bar and contact fingers; hBN E2g
  (~1366 cm⁻¹) appears from stage 05 on.

## Confidence + named hedges

- **Sub-spot blindness** (structural, every verdict): domains < ~0.7 µm
  spot / 0.75 µm step invisible; walls localized to ~1 px.
- **Magnitude:** 5.2 cm⁻¹ split < the ≳10 heuristic; grade rides on
  pattern + screens.
- **Wavelength:** single excitation (2.33 eV); legitimate per Nguyen
  only because N is independently asserted — the (N, stacking) joint
  assignment is not Raman-confirmed.
- **Layer count:** N = 3 grower-stated, not independently verified (no
  bare-flake optical/AFM supplied). Fork inherited, not absorbed: equal
  2D amplitude across the R1/R2 wall (ratio 0.973) proves same N both
  sides — a stacking wall at whatever N; at N = 4 the family-level read
  stands with the ABCB blind-spot caveat.
- **Laser power:** in-fiber only (flake 2.43 / stack 8.0 / device
  4.1–6.0 mW); at-sample unknown. The load-bearing flake map was the
  lowest-power, earliest acquisition; any in-measurement conversion
  would only shrink ABC.
- **Registration:** orientation fixed empirically by spot1's exact FWHM
  match; spot2 sits ~1.5 µm from a wall, so the y-flip is not
  double-anchored. Region coordinates good to ~1–2 µm.
- **Coverage:** flake map 75×42 µm; device maps 20×20 µm each.
- **Si line saturated at flake stage** (65535 counts) — killed that
  terrace proxy; the terrace screen rests on the 2D-amplitude proxy.

## What would firm it

Second excitation (red — best lineshape contrast, M out of the
crossing); bare-flake optical/AFM thickness map (closes the N fork);
1800 g/mm map over an R1/R2 wall; near-field imaging (sub-spot walls,
post-fab survival); the transport FS-count on the finished device — the
only listed probe that settles whether R2's ABC survived fabrication.

## Protocol statement

A confident stacking call for the **finished device** is not supported
by this data: post-gate maps are through-stack superpositions and read
"cannot tell (consistent-with)" — the successful, evidence-limited
outcome for stages 05/06. The strong calls are flake-stage only and
carry their stage stamps.

## Verify screens (as run)

| Screen | Outcome |
|---|---|
| Tool gates (`validate.py`) | PASS 7/7 |
| Strain-mimic | PASS — bimodal + coherent domains + sharp walls; cluster ctr Δ −0.69 cm⁻¹; corr(FWHM, ctr) −0.25; map-wide shifts pattern as doping (d2D/dG 0.52) |
| Through-stack | TRIGGERED stages 05 + 06 — verdicts capped consistent-with; pre-gate map carries the call |
| Terrace | PASS on 2D-amp proxy (0.973 across the R1/R2 wall); Si-520 proxy unusable (saturated); 1L + p52 populations masked pre-split |
| Twist (history-triggered: stack-image wrinkles, p52 streaks) | no moiré; p52 = in-map 1L+multilayer mixtures (90% r² > 0.95) → boundary mixtures, no twist fork |
| Mixed-spectrum decomposition | 346 intermediate px: 65% at α ∈ (0.2, 0.8), median r² 0.998 → wall mixtures |
| Excitation-transfer ban | compliant — single wavelength; in-map/same-wavelength references only; skew/ratio non-discriminating (−0.049 vs −0.052) |
| Absence-claims | no "no-ABC" claim at 05/06; stated as "not resolved (through-stack)" with coverage + power |
