# Step 2 — registration artifact (vti-02 fusion, 2026-08-22)

Figure: `registration_chain.png` (regenerate with
`uv run --no-project --with matplotlib python make_registration_figure.py`).

## Frame bridges actually supplied

| Bridge | Supplied? | Content |
|---|---|---|
| Raman spot/region coordinates in flake frame | **No** | `raman.md` gives no positions, no raster, no map — prose only ("a domain of rhombohedral") |
| Parent-flake image | **No** | The flake-database URL in `raman.md` is declared not-an-input by the brief; not fetched |
| Cut outline (flake → cut piece) | **No** | "We cut out the rhombohedral domain" — prose, no geometry |
| Stack imagery (cut piece → stack) | **No** | None supplied |
| Device optical image / GDS | **No** | None supplied |
| Device contact map | **Yes** | Device card: pads by label/position class only (T = top arc L→R, B = left side then bottom L→R); B_1 = pad 12 (left side), B_2 = pad 04 (bottom); sr1 = B_1−B_2 straddles a flake corner (session notes) |
| Ana-notebook geometry | Vertical only | Gate-stack thicknesses (9.5 / 11 nm hBN) — no lateral geometry |
| In-channel region structure | **Yes (transport-side)** | Run 5 gatemap: two CNP ridges → regions A + B in series in the B_1−B_2 channel; B electron-doped by +0.43×10¹² cm⁻², weak weight |

## Registration statement

No common coordinate frame between the Raman frame (parent flake) and the
transport frame (finished device) can be constructed: **zero anchors exist
on the Raman side** (no positions of any kind) and the transport side has
contact labels without an image or GDS. Three transfer/processing
boundaries (cut, stack+anneal, litho) intervene, each of which the fusion
recipe warns against bridging even with anchors under one rigid transform;
here there are no anchors at all.

- **Registration uncertainty: not quantifiable** (no anchors, no frames to
  relate). Against the domain scale: the domain scale is itself unknown
  (no map, no spot size); the uncertainty therefore cannot be shown to be
  below it.
- **Coverage classification, channel sr1 (B_1−B_2): UNCOVERED.** The only
  linkage — "the cut region ⊂ the rhombohedral domain" — is uncoordinated
  testimony and cannot establish coverage per Step 2. No interpolation.
- **Coverage, region A and region B separately: UNCOVERED** (a fortiori —
  `raman.md` does not resolve any sub-device region).
- The transport-side registration (which pads bound which channel, the
  corner-straddling footprint, the A+B series structure) is well-defined
  and carried into the Step 4 table; it is the Raman→device link that is
  absent.

## Consequence for Step 2's stress audit

With no quantitative registration, there is no shift to apply; the audit
degenerates safely: every row is already at the coverage floor
(uncovered → single-modality), so no perturbation of the registration can
change any row's mechanism class, coverage label, or domain share. No row
is classified *by virtue of* registration; none is registration-limited in
the flip sense — the limitation is total and already priced in as
"uncovered".
