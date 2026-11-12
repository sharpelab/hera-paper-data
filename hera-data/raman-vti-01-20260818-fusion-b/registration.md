# vti-01 fusion — Step 2 registration artifact (binding)

Produced by `s1_registration.py` (this dir); figure
`figures/f_registration.png`; numbers `intermediates/registration_coverage.json`.
Coordinate frame: **WITec stage µm of `inputs/vti-01.wip`** (sample `73474_`,
2026-05-28) — the Raman contract's frame, carried by `inputs/regions.npz`
(`x_edges`/`y_edges`, 1 µm pitch).

## Frame bridges used (the complete set supplied)

1. **In-file stage-registered video images** 002 (12:55, pre-cut), 004
   (13:19, post-first-cut), 007 (13:29, post-1064 nm top pass) — extracted
   with `witio`, per-pixel stage-µm position grids from the in-file space
   transformations. These tie video ↔ both Raman maps exactly (metadata-level).
2. **Device card contact map** — topology only: Hall bar, `T_SD` and `B_SD`
   at the two ends, `L1…L4` voltage probes in order down one side, `R1/R2`
   dead. Channels: sr1 = B_SD–L4, sr2 = L4–L1, sr3 = L3–L2. **No physical
   pad geometry** (pad numbers are breakout wiring, not positions).
3. **Ana notebook geometry** — parsed (JSON); contains only gate-stack
   thicknesses. **No channel dimensions or probe spacings.**

Not supplied: GDS, post-fab optical image, build-step list. The
flake-frame → finished-device link therefore rests on **one inferred anchor**:
the device rectangle x −12045.5…−12034, y 1274…1287 µm (11.5 × 13 µm), the
only Hall-bar-shaped remnant after the cuts (Raman contract Step 0 inference,
carried verbatim in `regions.npz:device_rect` — not testimony).

## Channel placement model

Contact positions inside the rectangle are unregistered. Model: SD contacts
at the two ends of the bar axis, L1…L4 evenly spaced between (fractions
1/5…4/5); segment bands at full transverse width. **36 variants** = bar axis
along y or x × both orientations × rectangle jitter on a ±1 µm grid (the
stated in-frame uncertainty). A ±2 µm grid is run as stress margin.

## Registration uncertainty vs domain scale

| link | uncertainty | basis |
|---|---|---|
| map 22 ↔ map 27 ↔ video | ≤ 1 µm | in-file transforms; S0↔S1 best integer shift (0,0) µm, label agreement 92% (Raman contract) |
| map pixel ↔ true stage (wall positions) | ±1 µm | 1 µm step, 0.7 µm spot; scan rotation 0.5° ≲ 0.15 µm across the rect |
| rectangle edges ↔ piece (imagery) | ±1 µm | video pixel 49 nm; cut-kerf edge reading |
| **combined in-frame** | **±1 µm (stress ±2 µm)** | — |
| contact positions inside rect | unconstrained | handled as the 36 placement variants, not a µm number |
| **flake frame ↔ finished device (piece identity)** | **not a µm number — an inference** | anchor-variant B below |

Domain scale: the ABC lobe (region B) main component is ~25 × 30 µm, walls
1–2 µm; the rectangle interior is a **single 238-px connected ABC component**
at S1. In-frame uncertainty (±1 µm) ≪ domain scale, so coverage labels are
stable against it — the binding uncertainty is the piece-identity anchor,
which is all-or-nothing, and the sub-spot/sub-µm blindness inherited from
the Raman contract.

## Coverage classification (S1 = map 27, the last pre-processing view)

Whole rectangle: S0 149/156 classified px ABC (96%); S1 **123/127 ABC (97%)**,
1 ABA px, 3 wall px. The only coherent ABA structure (18-px strip at the
slanted top, y 1290–1295) lies **outside** the rectangle, inside the 13:27
cut footprint, and is gone from the final piece.

| channel | coverage | ABC share of classified px (36 variants, ±1 µm) | notes |
|---|---|---|---|
| sr1 (B_SD–L4) | **partial** (registration-limited) | 88–100% where covered; **3/36 variants: no classified coverage** (bar-along-x placements put the end segment on map-27's partial-spot right-edge column) | end-segment band also abuts the rectangle's bottom edge = 13:30 1064 nm pass margin (post-S1, unobserved) |
| sr2 (L4–L1) | **covered** | 96–100% (69–91 px in every variant) | |
| sr3 (L3–L2) | **covered** | 92–100% (26–33 px in every variant) | |

±2 µm stress margin: sr1 88–100% (3/36 no-coverage), sr2 95–100%, sr3
92–100% — no label changes beyond sr1's existing partial status.

**Anchor-variant B (piece identity fails):** if the rectangle is not the
piece that became vti-01, all three channels are **uncovered** — no
interpolation; each row degrades to single-modality (transport). Recorded in
the stress audit; there is no second in-frame anchor to fit against, so this
is a discrete variant, not a spread.

All coverage is **as of S1 (2026-05-28 13:20)** — contact metal deposition
moves stacking walls by µm (base-recipe converter list), so even "covered"
does not pin the *measurement-time* domain composition; that is the Step 3
temporal gap, not a registration defect.
