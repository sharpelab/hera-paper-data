**SCORER / SUPPORT-SIDE ⚠️ — not for agent view.** Campaign lock (clean-environment rerun, 2026-08-18 session, fusion stage — SCORED, chained per the prereg chain ruling). Verbatim `fusion-verdict.md` (brief: `hera/docs/brief-vti-01-20260818-fusion-rerun.md`; run dir `$HERA_DATA/raman-vti-01-20260818-fusion/`). DISCREPANT-IN-PART with the locked original (`vti-01/fusion-verdict.md`): all stacking verdicts and strengths identical; mechanism class diverged (original: sr1/sr3 reconciled-by-conversion; this run: all channels uncovered → single-modality). Ruled 2026-08-27: promoted to the main text per the prereg disclosure rule; the pinned diagnostic (`fusion-verdict-pinned.md`) attributes the divergence to upstream-contract representation, not the launch frame. Locked as produced; not edited.

# vti-01 — fused Raman×transport stacking verdict (fusion run 2026-08-27)

Recipe: `hera/recipes/investigations/stacking-raman-transport-fusion.md`,
consuming the locked transport contract (`inputs/transport-call.md`,
`trilayer-stacking-fs-count.md` route — trilayer per device card) and the
locked stage-stamped Raman contract (`inputs/raman-contract.md` +
`inputs/raman-provenance.md` + `inputs/regions.npz`).

## Step 1 — admissibility + independence (gate: PASSED)

Both contracts admissible: weight words, evidence lists, coordinates
(transport: named contact pairs sr1 = B_SD–L4, sr2 = L4–L1, sr3 = L3–L2;
Raman: region raster `regions.npz` in stage µm + stage stamps S0/S1).
Independence confirmed — **fusion is evidential, not a consistency
narrative**: the transport call (landed 2026-08-20, ana cells 33/38)
contains zero Raman/WITec references (parsed-JSON sweep of all 39 notebook
cells, plus session notes, device card, and the call text: 0 matches); the
Raman read (executed 2026-08-27 from the 2026-08-18 brief) states in its
provenance that no transport result, prior Raman read, or third-party view
was seen. Machine-checked: `s1_admissibility_independence.py` →
`audit_step1.txt` (13/13 PASS).

## Step 2 — spatial registration (artifact: `fig_registration.png`)

Frame bridges actually supplied: the three stage-registered video images
inside `vti-01.wip` (exact per-pixel stage grids, 0.5° rotation kept), the
region raster in the same stage frame, and the device card's contact map —
which is **topological only** (Hall-bar roles and pad numbers, no
coordinates, no image). Not supplied: optical image of the finished
device, GDS, build-step list, pickup→device testimony. The ana notebook
carries no device geometry beyond gate-stack thicknesses.

- **Within the stage frame**: raster vs map A's true grid deviates ≤ 0.99 µm
  (mean 0.72 µm; the neglected 0.5° scan rotation + center convention) —
  registration uncertainty **±1 µm class**, map-step dominated
  (`registration_numbers.txt`).
- **Stage frame → finished device**: **zero anchors — uncertainty
  unbounded**, exceeding the 2–5 µm domain scale by construction. Two
  disjoint candidate device stocks are visible in-file (pickup 1 ≈ flake
  minus the leftover rectangle, spanning R1 ABA + R2 ABC + R3 mixed;
  pickup 2 = the leftover's upper part, ABC at S1), and which — if
  either — became vti-01 is unknown, as is channel placement within it.
  Even the flake↔device association itself rests only on the file being
  supplied as `vti-01.wip` (owner filename testimony).

**Coverage classification (binding): sr1 UNCOVERED, sr2 UNCOVERED, sr3
UNCOVERED.** Uncovered stays uncovered — no interpolation, and no
share sub-rows can be formed.

## Step 3 — temporal registration

Raman stage stamps (imagery-inferred, hedged — QC0426 lesson): S0 = intact
flake on SiO₂/Si (map A, 2026-05-28 19:57 UTC); S1 = after first pickup
(map B, 20:20 UTC). Transport: finished dual-gated hBN-encapsulated device,
measured in-situ 2026-08-18/20 — a ~12-week stage gap. Intervening steps,
by conversion-risk class (conversion runs ABC→ABA only):

| Step (map → measurement) | Evidence | Risk class |
|---|---|---|
| Pickup 1 (~20:10–20:19 UTC, removed most of flake) | in-file videos 002→004 | transfer/pickup |
| Pickup 2 (by 20:29 UTC, removed leftover's upper part) | videos 004→007 | transfer/pickup |
| Stack assembly: hBN encapsulation, graphite BG pickup | device card (steps themselves unsupplied) | transfer/pickup |
| Contact metal deposition + lithography chemistry/bake | device card implies; unsupplied | **metal deposition** (highest) + chemical+bake |
| Cooldown/thermal cycling | session notes | clean thermal |

Multi-stage differencing (like-conditioned: both maps bare-flake,
gate-clean per imagery): map A vs map B — the leftover part of R2 was
**still ABC after pickup 1** (63.5 vs 62.3 cm⁻¹ in-footprint, unimodal).
Direct evidence that pickup 1 did not convert the material *left behind*;
it says nothing about the picked-up material. All later steps carry
unquantified risk-class inference only.

## Step 4 — per-channel fusion table

| Channel | Transport verdict (strength) | Raman verdict (strength, stage) | Fused verdict (strength) | Mechanism class |
|---|---|---|---|---|
| **sr1** (B_SD–L4) | ABA / Bernal (**strong, two-branch**: f_BL+f_ML Luttinger pair at λ=1.14, LK mass 0.049(2) mₑ, breakdown excluded) | **uncovered** (no stage→device bridge; flake-level S0 facts: R1 ABA strong / R2 ABC strong / R3 mixed strong-as-mixture — none assignable to this footprint) | **ABA / Bernal (strong, two-branch)** — transport leg only, at measurement time 2026-08-18/20; no fused upgrade | **Single-modality (transport)** |
| **sr2** (L4–L1) | uninformative (weak short pair, signals at floor) | **uncovered** | **cannot tell (uninformative)** — no informative leg | **Single-modality (degenerate — neither leg informative)** |
| **sr3** (L3–L2) | ABA (**consistent-with**: agrees with sr1 on all frequency content incl. run-19 ML corroboration at lower SNR; no independent mass/tracking) | **uncovered** | **ABA (consistent-with)** — transport leg only, at measurement time | **Single-modality (transport)** |

**No per-device fused verdict is issued** (no covered region; the
no-averaging rule forbids a headline). No concordant,
reconciled-by-conversion, reconciled-by-geometry, or unreconciled rows
exist — there is no same-region pair to reconcile.

**Consistency observation (explicitly not a mechanism class, carries no
strength):** the transport-ABA picture is *compatible* with the Raman
flake picture under every bridge hypothesis — vti-01 built from R1 ABA
material (no conversion needed), from R2/R3 ABC material (ABC→ABA
conversion via the named risky steps, direction allowed), or from other
material entirely. Compatible-but-nondiagnostic; invoking
reconciled-by-conversion here would be a free pass the recipe forbids
(no named step ties any channel to a mapped ABC region). Conversely,
nothing in the Raman read conflicts with transport: an unreconcilable
Raman-Bernal vs transport-rhombohedral pattern does not occur.

## Step 5 — the call

- **sr1: ABA / Bernal (strong, two-branch)** — single-modality
  (transport, in-situ, measurement time). The flake-stage Raman read
  cannot upgrade or contest it: uncovered.
- **sr3: ABA (consistent-with)** — single-modality (transport).
- **sr2: cannot tell** — uninformative on both legs.
- The Raman contract's own verdicts stand unchanged as **flake-stage
  facts** (R1 ABA strong, R2 ABC strong, R3 mixed strong-as-mixture, at
  S0; leftover-rectangle ABC re-confirmed at S1) — stage-stamped, not
  propagated to the device. Per conversion directionality, R1's ABA would
  propagate to measurement time *if* a bridge tied it to a channel; no
  bridge exists, so nothing propagates.

This is a fused "cannot tell at the fusion level" outcome by design: the
two modalities never probed a common, registrable region, so the fusion
adds no strength to either contract — and says so rather than forcing
concordance.

### Registration artifact

`fig_registration.png` (+ `registration_numbers.txt`), regenerated by
`s2_registration.py`. Coverage: sr1/sr2/sr3 all UNCOVERED. Registration
uncertainty: ±1 µm within the stage frame; unbounded stage→device (zero
anchors) against a 2–5 µm domain scale.

### Named hedges

1. **Piece-to-device bridge absent** (the dominating hedge): no optical
   image, GDS, or build testimony links stage frame to device; the
   flake↔device association itself is filename testimony. All coverage
   labels and the single-modality classifications follow from this.
2. **Stage gap ~12 weeks** with the full fab sequence (2 pickups observed
   in-file; encapsulation, graphite-gate pickup, metal deposition,
   chemistry+bake unsupplied) — every documented ABC→ABA converter class
   intervenes, unquantified.
3. **Raman stage stamps are imagery-inferred**, not testimony (QC0426
   lesson); through-stack cleanliness of maps A/B likewise
   imagery-inferred.
4. Inherited transport hedges: λ = 1.14 pending the QH lever-arm check;
   ML mass unmeasured; sr3 has no independent tracking; whole campaign
   contact-limited through one ~109 MΩ source contact; T_e ≈ 8 K;
   sub-spectral-weight ABC slivers not excluded.
5. Inherited Raman hedges: N = 3 rests on owner testimony (single
   wavelength → two-wavelength rule leans on it; ABCB caveat if N were 4);
   2D split 4.96 cm⁻¹ below the ≳10 cm⁻¹ heuristic (pattern carries the
   grade); sub-spot blindness; at-sample power unknown.

### What-would-settle

No unreconciled rows exist; the following would convert the uncovered
rows and firm the calls:

- **sr1/sr3 (and the fusion as a whole): supply the piece-to-device
  bridge** — build-step list + which pickup became vti-01, plus an
  optical image or GDS registrable to the stage frame. This alone would
  re-run Step 2 to covered/partial and could produce a concordant (R1→
  channel) or reconciled-by-conversion (R2/R3→channel, metal/pickup
  steps named) row — either a genuine strength upgrade for sr1 or a
  worked conversion case.
- Post-fab Raman re-map of the finished device (through-stack screen
  applies through the encapsulant/gates — cap consistent-with) or
  **near-field s-SNOM** of the channel regions — the in-place check.
- **sr2**: operator rewiring/contact repair at the breakout; no analysis
  can inform this row.
- Transport firming (from the base contract): ML mass at low B, Streda
  step-6 complement at 10 T+, QH lever-arm scale upgrade.

## Audit outcomes (Verify)

1. **Independence audit: PASS** — neither call cites the other's evidence
   (13/13 machine checks, `audit_step1.txt`); fusion is evidential.
2. **Registration stress: PASS (trivially stable)** — coverage is
   uncovered under every registration variant (stage→device uncertainty
   is unbounded; no shift can create coverage), and no fused row consumes
   in-frame geometry, so the ±1 µm in-frame uncertainty flips nothing.
   All three rows are **registration-limited by absence of a bridge** and
   are classified only as single-modality, the one class that survives
   any registration.
3. **Directionality audit: PASS** — zero reconciled-by-conversion rows
   (none invoked; no named step ties a channel to a mapped ABC region —
   conversion explicitly *not* used as a free pass); zero
   Raman-Bernal/transport-rhombohedral rows exist to force into
   unreconciled.
4. **No-averaging audit: PASS** — every fused strength equals its
   strongest (only) input: sr1 strong = transport strong; sr3
   consistent-with = transport; sr2 uninformative. No concordant upgrades
   claimed; no per-device verdict issued (no covered regions).

## File map (this run)

- `fusion-verdict.md` — this contract.
- `s1_admissibility_independence.py` → `audit_step1.txt` (Step 1 + audit 1).
- `s2_registration.py` → `fig_registration.png`,
  `registration_numbers.txt` (Step 2 binding artifact + audit 2 numbers).

## Provenance line

Received: the complete input set named in the brief —
`inputs/transport-call.md`, `inputs/raman-contract.md`,
`inputs/raman-provenance.md`, `inputs/regions.npz` / `inputs/regions.png`,
`inputs/vti-01.wip` (read via witio for imagery/transforms only),
`inputs/20260818_ana.ipynb` (parsed as JSON, not executed),
`inputs/session_notes.md`, `inputs/device_card.md`. Corpus used: the
fusion recipe, `trilayer-stacking-fs-count.md`, `raman-stacking-id.md`.
No frame bridges beyond the in-file video images were supplied or used.
I saw **no prior fusion attempt, draft, or verdict for this device, and
no third-party read, lean, or reaction to either modality's call**. No
sibling directories under `/data/sharpelab/hera-data/` were listed or
read. Harness-injected environment context (platform, user identity, a
memory-directory pointer, generic agent/skill listings) contained no
repository/git information and no information about this device beyond
the run-directory path; none of it was used.
