# Registration record — vti-02 Raman × transport fusion (Step 2)

Figure: `artifacts/registration-vti-02.png` (regenerate:
`uv run --no-project --with matplotlib python scripts/registration.py`).

## Frame bridges actually supplied

| Bridge | Source | Nature |
|---|---|---|
| Contact map (pad labels, liveness, roles) | `inputs/device_card.md` | Label order only ("T = top arc L→R, B = left side then bottom L→R"); **no coordinates, no GDS, no optical image** |
| "We cut out the rhombohedral domain and expect the cut region to contain no ABA" | `inputs/raman.md` | Author attestation; no map, no domain boundary, no scale |
| Ana notebook geometry | `inputs/20260821_ana.ipynb` (parsed) | Electrical only (gate-stack thicknesses, lever arms); no spatial frame. Seven embedded PNGs are all analysis plots — no device imagery (`artifacts/ana_inventory.md`) |

No optical images, GDS, or build-step list were supplied (brief: "none").
The parent-flake URL in `raman.md` is not an input and was not fetched.

## Registration chain (all links topological)

parent flake (Raman stage) → [laser cut] → cut region *(claimed ⊂ ABC
domain — attestation)* → [hBN pickup / stack, anneal, litho] → device
vti-02 → contact frame {T_0, B_1, B_2, B_3 alive} → channel **sr1 =
B_1–B_2** (source T_0, drain B_3).

- **Metric anchors: 0.** No shared coordinate frame exists at any link;
  no transform can be fit, so no anchor-variant spread can be computed —
  the stress audit runs over the two limiting topological variants
  instead (sr1 inside vs. outside the attested ABC domain).
- **Registration uncertainty: unbounded.** Domain scale: unknown (no
  Raman map in hand). Uncertainty ≳ domain scale at every link.

## Coverage classification (per named transport channel)

| Channel | Raman coverage | Basis |
|---|---|---|
| sr1 (B_1–B_2) | **at best partial** — recorded as *attested-covered, metrically unverifiable* | Whole-device ⊂ ABC-domain attestation only; per recipe, uncertainty ≳ domain scale caps coverage at partial. Domain *composition* under the footprint also unresolved (sub-spot / sub-domain structure unknowable without the map) |
| sr2, sr3 | n.c. — no transport leg | Transport-uncovered regions; Raman attestation covers them with the same caveat |

No interpolation performed; uncovered stays uncovered.
