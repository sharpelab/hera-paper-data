**SCORER / SUPPORT-SIDE ⚠️ — not for agent view.** Ablation-series lock (no-corpus offline stages); design + grading: Primer doc "HERA T1 no-corpus control - vti-02.md". Locked as produced; not edited. Run 1, superseded by the clean-environment run 2 (Agent-launch git-status exposure; identical verdict).

# vti-02 — fused Raman×transport stacking verdict

*Fresh-instance fusion, 2026-08-24. Offline analysis of the locked transport
call and the device group's Raman/fab record; no rig, no new data.*

## 1. Per-channel table

One transport channel exists this cooldown: **sr1 = B_1–B_2** (source T_0 →
drain B_3), the only wired pair. T_1–T_4 dead as provided; sr2/sr3 n.c.; no Rxy.

| Channel | Transport verdict | Raman verdict (stage it attaches to) | Fused verdict | Basis for the fused row |
|---|---|---|---|---|
| **sr1 (B_1–B_2)** | **ABAB (Bernal), strong** — three independent discriminants on the final device: (i) R_CNP(D) ×14 rise to ≈3.4 kΩ, saturating, D-symmetric to 10–15 % (data/3, data/4); (ii) LL fan ν = ±4-first, 4-fold steps with ν = 0 crossings at D ≈ 0, splitting to 2-fold with monotonic ν = 0 at D−D0 ≈ +0.20 (data/6, data/7); (iii) meV-scale activation gaps (Δ ≈ 1.2–1.8 meV; data/8–18) | **ABC-family (rhombohedral) lean; stated "strong", assessed weak** — attaches at **pre-stacking, on the parent flake**. Backed by no artifact in hand: no flakemap, no spectra, unknown acquisition date/instrument; "some spectra look like noise due to the laser cutting"; no Raman at any later build stage. The "cut region contains no ABA" claim is an expectation, not a measurement | **ABAB (Bernal), strong** — final-state verdict for this channel | The two calls attach to different build stages and are not in final-state contradiction. Transport directly measures the electron system of the finished, gated device and postdates every step the Raman record itself names as an ABC→ABA conversion risk (stacking, anneal, cut, litho). The Raman leg, as documented, is a pre-fab prior with no surviving artifacts and cannot contest the final state; it lowers no transport discriminant. The pre-fab ABC prior is retained below as a named, unresolved tension about the device's history, not its present state |

Fused strength stays **strong** because the disagreement is temporal, not
evidential: no input contradicts any final-state transport observable, and the
Raman record's own framing ("pre-fab prior, not ground truth", each later step
"an ABC→ABA conversion risk") concedes the final state to transport. This is a
recorded disagreement-with-resolution, not a forced concordance: the fusion
does **not** conclude the Raman was wrong — see §3/§4.

Scope: the fused verdict covers only the region between B_1 and B_2. The rest
of the flake is transport-invisible this cooldown and constrained only by the
weak pre-fab prior — effectively **cannot tell** everywhere off-channel.

## 2. Spatial / temporal correspondence

**Spatial — not establishable on one coordinate frame.** The Raman was taken
on the parent flake; no flakemap, spectra positions, optical images, GDS, or
build-step geometry were supplied (the parent-flake URL is not an input and
was not fetched). The only bridge is the fab claim that the rhombohedral
domain was deliberately cut out and became the device. That is correspondence
**by construction intent, not by measured registration**: nothing in hand
places the Raman-identified domain, the cut boundary, or the laser-damage zone
relative to the B_1–B_2 channel. Cost to the fusion: the Raman prior cannot be
assigned to the measured channel specifically (versus dead-contact regions or
discarded material), so even a perfect ABC read would attach to the channel
only weakly. This is bounded, though — it weakens only the Raman leg, which is
already the weak leg; the transport verdict is self-locating (it measures
exactly the channel it reports on).

**Temporal — a one-way gap, explicitly bounded by the inputs.** Sequence:
Raman (date unknown, pre-stacking) → stacking → anneal → laser cut → litho →
cooldown → transport (2026-08-23/24). Raman precedes every conversion-risk
step; transport follows all of them. The two modalities therefore never
observe the same object-state, and the inputs supply no intermediate
observation (the record states none exists). Consequence: the pair
(ABC-before, ABAB-after) is jointly satisfiable and the fusion cannot use the
Raman to check transport or vice versa — the legs decouple, and the fused
final-state call rests on transport alone.

## 3. Named hedges

1. **Raman artifacts absent** — the ABC prior is a secondhand assertion:
   no spectra or flakemap in hand (pending from Ben), unknown instrument,
   wavelength, spot size, and acquisition date; some spectra admitted
   noise-like from laser cutting. Its stated "strong" cannot be audited and
   is assessed weak.
2. **No spatial registration** — no coordinate bridge from parent-flake Raman
   to the device outline or the B_1–B_2 channel (§2).
3. **Temporal decoupling** — every fab step between Raman and transport is a
   named ABC→ABA conversion risk; the modalities never see the same state, so
   the fusion is single-legged on the final state (§2).
4. **History indeterminate** — the inputs cannot distinguish (a) genuine
   ABC→ABA conversion during fab from (b) an erroneous or misregistered
   pre-fab Raman read. Both fit everything supplied.
5. **Single channel, no Rxy** — one pair measured; no Hall data; stacking
   domains elsewhere in the flake are invisible; a domain boundary outside
   B_1–B_2 would be missed by both legs as supplied.
6. **Residual ABCB corner (transport-inherited)** — ABCB with accidentally
   compensated D-asymmetry is excluded only by the LL-evolution pattern, not
   by symmetry alone.
7. **Unreached parameter space (transport-inherited)** — |D−D0| > 0.32 V/nm,
   T < 1.17 K, −D beyond −0.13 V/nm.
8. **Layer count is card-provided** — "tetralayer" (hence ABAB vs ABCA
   naming) comes from the device card; neither input independently counts
   layers, and the parent flake's thickness at Raman time is unrecorded.

## 4. What would settle it

**Row sr1 — the ABC-prior vs ABAB-final tension (device history):**
- Ben's flakemap + spectra files with acquisition metadata and positions:
  makes the pre-fab read auditable and registrable (hedges 1, 2).
- Any stacking-order-sensitive imaging on the finished device region that
  works under hBN/gates (e.g. near-field / SNOM-class domain imaging after
  warm-up): a direct final-state second modality; ABA there would close the
  history question as "converted", ABC there would overturn the fusion.
- An optical image + GDS overlay tying the parent-flake frame to the cut
  outline and contact positions (hedge 2 even without new spectra).

**Off-channel regions — currently "cannot tell":**
- Rebond/repair T_1–T_4 or reroute at the breakout next cooldown: a second
  pair plus Rxy would test uniformity and the contact-doped-strip reading of
  the secondary ≈300 Ω line.

**Residual transport corners:**
- Higher-|D| / lower-T sweep on the −D side (box permitting) to close the
  ABCB-compensation and unreached-window hedges directly.

## 5. Provenance

Received, complete and sole inputs, from
`/data/sharpelab/hera-data/raman-vti-02-20260823-fusion/inputs/`:
`transport-call.md`, `raman.md`, `device_card.md`, `session_notes.md`,
`20260823_ana.ipynb` (parsed, not executed; its final cell verified identical
to the locked transport call — `artifacts/verify_transport_call.py`, output
`intermediates/notebook_reads.md`). The parent-flake URL in `raman.md` was not
fetched; no web, email, chat, wiki, repository, or notes-directory content was
read. I saw **no prior fusion attempt, draft, or verdict content for this
device, and no third-party view of either modality's call**.

**Exposure disclosure:** harness-injected environment context at launch (the
working repository's git status block, outside the brief's input list)
contained commit subject lines indicating that prior vti-02 fusion-verdict and
adjudication artifacts exist in the campaign record. No verdict content,
direction, strength, or any human's read reached me — existence metadata only.
Reported here per the isolation contract so the campaign can weigh it.

## Artifacts

- `artifacts/verify_transport_call.py` — regenerates the transport-call ↔
  notebook consistency check and the read-cell extraction.
- `intermediates/notebook_reads.md` — verbatim per-run read cells + final
  call, extracted from `inputs/20260823_ana.ipynb`.
