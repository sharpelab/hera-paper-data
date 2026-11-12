# QC0426 fusion — fresh-instance output contract (2026-07-25)

Fresh instance executing
`recipes/investigations/stacking-raman-transport-fusion.md` on the two
locked contracts (transport 2026-07-16, Raman 2026-07-25
`raman-read-contract.md`), corpus-allowlisted, no sight of any prior
fusion attempt. Registration figures archived at
`$HERA_DATA/raman-qc0426-fusion-2026-07-25/` (binding artifact:
`channel_on_04.png` — channel footprints on the 04 stacking map under
all three registration variants).

## Step 1 — admissibility

Both contracts fusible (strength scale, coordinates, hedges).
**Independence PASS**: transport locked 2026-07-16, nine days before the
Raman read existed, citing only magnetotransport; the Raman contract's
provenance states no sight of transport results.

## Step 4 — fusion table

| Channel | Transport | Raman (stage) | Fused (device) | Mechanism class |
|---|---|---|---|---|
| sr1 (T3–T4) | ABA **strong** | ABA **strong** on 74–100% of footprint, ABC **strong** on 0–26% (variant-dependent); stage 04; coverage **partial** (share registration-limited) | **ABA strong** | **Concordant** on the majority share. Minority ABC share: reconciled-by-conversion (named steps: hBN pickup with *measured* non-rigid strain; finger metallization on-segment) or reconciled-by-geometry (2–5 µm bands at registration+spot scale) — indistinguishable, both legal, direction ABC→ABA only |
| sr2 (B4–B5) | ABA **strong** | mixed: R1 fraction 37–100% across registration variants; coverage **partial** | **ABA strong** (transport-dominant; Raman leg **weak**) | **Registration-limited** — stress audit flips the share; reported, not classified |
| sr3 (T5–B6 Hall) | uninformative for stacking (density scale only) | ABA **strong**; R1 = 100% under all variants; corroborated by exact-registered spot2 inside the mesa | **ABA strong** (flake-stage, propagates forward — ABA cannot have converted away) | **Raman-only** — no recipe class fits a transport-uninformative row (friction) |

**Per-device: QC0426 probed device = ABA (Bernal), strong** — all
covered channels concur. **Headline mechanism is geometric**: the
fabricated mesa sits in the flake's upper-left interleaved R1/R2 zone;
the coherent ABC core (R2, containing spot1) maps ~25 µm right of the
mesa in GDS frame — never fabricated into the device. "Flake ~49% ABC"
and "device measures pure ABA" reconcile mostly by geometry, conversion
as the allowed fallback for in-channel minority bands; transport's
no-mosaic finding independently disfavors surviving in-channel ABC at
its sensitivity.

## Registration chain

| Link | Method | Uncertainty |
|---|---|---|
| L1: 04 scan ↔ 04 stage | WITec per-pixel position grids (witio direct) | <0.01 µm |
| L2: 04 → 05 (across pickup) | ICP on two spectrally-verified stable features (no-graphene gap edge; 1L-strip boundary); the features are rigidly incompatible by 4–5 µm over the 50 µm window — genuine non-rigid pickup strain; handled as three anchor-weighting variants, θ ∈ [−3.1°, +1.7°] | **±2–3 µm at the device footprint — dominant chain error** |
| L3: 05 → GDS | edge-NCC of 05 video vs marker-referenced 50x image in GDS frame | ±0.5 µm |
| L3b: 50x jpg → GDS | 4 etched markers, 100 µm pitch, similarity fit ("0,0" glyphs fix identity and exclude mirror) | 0.02 µm residual |
| L4: GDS → 06 stage | etch-layer raster vs 06 map 2D-amp bar pattern (validation only) | ±0.4–0.7 µm |
| L5: GDS → contact labels | lead census forced by gate-lead identification (TG strip on L10 edge, BG tail on L9); alternative assignment excluded (9 bottom contacts for 8 labels); Hall pair near-opposite ✓ | ±0.3 µm |

Channel footprints land at 04-frame ≈ (−25…−10, −2…+8) — the
interleaved band zone, 1–3 µm from walls. Map coverage of every channel
is 100%; "partial" grades come from registration σ ≳ local band scale.

## Verify audits

1. **Independence — PASS.**
2. **Registration stress — executed as anchor-variant spread** (σ is a
   variant spread, not a scalar). sr3 stable (R1 = 1.00 all variants);
   sr1 majority stable, minority share 0→26% registration-limited;
   sr2 flips (0.37→1.00) — reported registration-limited, not
   classified.
3. **Directionality — PASS.** Conversion invoked only ABC(04)→ABA(now)
   with named risky steps; unreconciled class correctly empty.
4. **No-averaging — PASS.** No fused strength exceeds its strongest
   input; per-device verdict issued only because all covered regions
   concur.

## Frictions (recipe follow-ups; see session record)

Non-rigid registration procedure absent (Step 2 presumes one scalar σ);
no vocabulary for covered-but-share-unresolved; Step 4 row format
assumes one Raman verdict per channel; no class for a
transport-uninformative channel (needs single-modality +
directionality-propagation); Step 3 differencing must be restricted to
like-conditioned maps (through-stack ~8 cm⁻¹ apparatus shift would
manufacture "wall motion"); GDS lead census can be ±1-ambiguous when
gate leads are geometrically ordinary; locked contracts should ship
region masks, not prose ranges (re-derivation reproduced geography and
spot memberships but not boundary pixels).

## Effort

Link L2 (cross-pickup, non-rigid) ≈ half the session (six
failed/partial approaches before ICP variants); GDS forensics ≈ a
quarter; marker fit / GDS→06 / 05→jpg were one-shot after the
marker-referenced 50x image — the pivotal supplied bridge.
