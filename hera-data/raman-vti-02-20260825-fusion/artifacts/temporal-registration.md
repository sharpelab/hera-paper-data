# Temporal registration artifact — vti-02 (fusion recipe Step 3)

Build steps between the Raman stage stamp and the transport measurement,
tagged by the recipe's conversion-risk classes (metal deposition on/near
the region > transfer/pickup > chemical+bake > clean thermal).

**Stage S (Raman):** pre-stacking, on the parent flake. Acquisition date
**unknown** (`raman.md`: "Raman acquisition date: unknown"), so the stage
gap is fixed only *ordinally* — S precedes every step below — never in
elapsed time.

**Measurement time (transport):** 2026-08-24 17:03 → 2026-08-25 05:00
rig-local, runs 5–8, channel B_1–B_2 (`transport-call.md` provenance).

**Maps at multiple build stages: none.** `raman.md` records exactly one
read and states "no Raman at any later stage (no exposed device layer
after gating)". Differencing is therefore unavailable and risk-class
inference is the only instrument Step 3 has here.

**Through-stack status:** the one map is on a bare parent flake before
stacking — **gate-clean and stack-clean**. The through-stack screen
(`raman-stacking-id.md` Verify; the QC0426 burn) does **not** trigger.
This is the Raman leg's one methodological strength, and it is the
mirror image of its weakness: the gate-clean stage is also the stage
furthest from the finished device, four risky steps upstream.

| # | Step (post-map, pre-measurement) | Risk class | Grade | Basis |
|---|---|---|---|---|
| 1 | **Laser cut** isolating the rhombohedral domain from the parent flake | laser heating | **high, perimeter-certain** | Laser heating at the ~10 mW scale (~430 K local) is a documented ABC→ABA converter; mapping at ≤ 1 mW is safe by an order of magnitude [citation, Zhang LSA 9 174, via `raman-stacking-id.md`]. Cutting is a material-removal power scale, orders above the safe-mapping level, applied along the whole perimeter of the retained piece. `raman.md` itself reports "some spectra look like noise due to the laser cutting" — direct testimony that the cut perturbed the Raman response. Radial extent of the affected zone: undocumented. |
| 2 | **Stacking** — hBN pickup / stack assembly | transfer/pickup | **high** | hBN pickup along armchair converts; zigzag preserves [citation, Yang NL 19 8526, via `raman-stacking-id.md`]. The pickup crystallographic alignment for this stack is not documented, so the risk cannot be retired. |
| 3 | **Anneal** | chemical + bake | **moderate–high** | Adsorbate chemistry plus a modest bake is a documented converter [citation, Zhang NC 4 2074, via `raman-stacking-id.md`]. Temperature, atmosphere and duration are undocumented, so the risk cannot be sized, let alone retired. |
| 4 | **Litho + metal contact deposition** (contacts, incl. B_1 and B_2; plus the graphite back gate and hBN dielectrics of the card's gate stack) | metal deposition **on** the region | **highest, and spatially coincident with the measured channel** | Anisotropic strain from metal-contact deposition moves domain walls by µm [citation, Geisenhof AANM 2 6067, via `raman-stacking-id.md`]. This is the top of the recipe's ladder, and here the metal is deposited at the ends of the very channel the transport leg measures — the strain source is *on* the region, not merely near it. |
| 5 | Cooldown to ≈ 1.2 K, gating within the card's committed windows | clean thermal / electrostatic | **low** | No documented conversion pathway at cryogenic temperature and these fields/gate ranges. |

**Ordering ambiguity in the Raman contract (hedge).** The header of
`raman.md` lists the post-read steps as "Stacking, anneal, cut, and
litho", while its body reads as cut-then-stack ("a domain of
rhombohedral that was subsequently isolated"; "we cut out the
rhombohedral domain"). Whether the cut acted on bare graphene or on an
encapsulated stack changes the thermal boundary condition of step 1, not
the risk inventory. Recorded, not resolved.

**Unsupported survival claim (hedge).** `raman.md` states "the
rhombohedral domain survived the cutting process" while also stating
"no further Raman was performed during device assembly". No post-cut
read exists in the input set, so the survival claim has no evidence
behind it in this document.

**Directionality (the recipe's one hard rule).** Conversion runs
rhombohedral→Bernal only. A Raman-rhombohedral region legitimately
measuring Bernal later is permitted; the reverse is not. The vti-02
pairing (Raman rhombohedral at stage S, transport Bernal now) is in the
**permitted** direction, so nothing here is a physics conflict. What it
is not, is evidence: the permitted direction plus four unretired risky
steps means the Raman leg constrains the finished device **not at all**
on this axis — a rhombohedral verdict does not propagate forward in
time (`stacking-raman-transport-fusion.md`, Step 4, single-modality
clause).
