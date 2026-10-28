# vti-02 — comparison

**SCORER / SUPPORT-SIDE ⚠️ — not for agent view.** Prereg §5 step 4. The
three locked verdicts side by side; nothing upstream changes after this.

## Locks

| Artifact | Commit | Produced |
|---|---|---|
| `transport-call.md` | `b6f3a32` 2026-08-22 15:27 EDT | E1 HERA tactical, VTI, 2026-08-21 20:16 → 08-22 09:37 PDT; corpus `13b07e9` (= `vti-02-deploy` = `arm1-freeze` + kit) |
| `raman.md` | `969e667` 2026-08-22 | Aaron's `vti-02-raman.md`, sealed 2026-08-22T02:36Z, unsealed after the transport lock; a pre-fab prior on the parent flake — no positions, date, or spectra (raw map unretrievable, `../deviations.md`) |
| `fusion-verdict.md` | `1d5fb24` 2026-08-22 | fresh instance, `stacking-raman-transport-fusion.md`, staged inputs only; no HERA Raman read exists for this device |
| `adjudication.md` | `f6cdcb1` 2026-08-22 | Aaron's `vti-02-fused_call.md`, sealed 2026-08-22T02:36Z — before the HERA session began (03:16Z); fuses the Raman document with the shield's own transport; held unread until the fusion lock |

## Per channel — stacking at measurement time

| Channel | Transport (HERA) | Fusion (HERA) | Adjudication (Aaron) | Concordance |
|---|---|---|---|---|
| sr1 (B_1–B_2) | ABAB / Bernal, strong | ABAB, strong — single-modality (Raman leg inadmissible; no upgrade, no downgrade) | Bernal, strong ("the only measurable contact pair") | **concordant**, strength included |
| per device | none (one region; flake may host other domains) | none | homogeneously Bernal, strong | divergent on generalization, not on any measured channel — the vti-01 pattern; by Aaron's vti-01 reconciliation, homogeneity claims are semantic, not spatial |

## Raman leg and mechanism

| | Fusion (HERA) | Adjudication (Aaron) | Concordance |
|---|---|---|---|
| Raman at pre-stacking stage | document inadmissible as evidence (no spectra, map, positions, wavelength, date); its ABC-strong lean carried at face value only, not weighed | isolated rhombohedral domain prior to stacking, strong; survived the cut | **not scorable** — both columns are the same document (`raman.md` ≡ the Raman section of the fused call, near-verbatim); there is no independent Raman read to concord with |
| Mechanism | at face value: reconciled-by-conversion, allowed direction, named steps (contact metallization top tier; pickup, anneal, laser cut); conversion **not asserted** — narrative only | conversion during stacking, complete | concordant on direction conditional on the Raman; HERA withholds the assertion because the premise is unevidenced, Aaron asserts it and its completeness |

## Evidence divergences, traced

- **The Raman leg has one source.** Aaron's document and Aaron's fused
  call carry the same Raman read; HERA's fusion could only assess it, not
  test it. Every item the fusion names as settling (Ben's spectra and map
  with metadata, the parent-flake image with the cut outline, stage
  testimony on map-vs-cut order) is absent from both. The fusion's
  single-modality downgrade is the correct reading of that absence, not a
  disagreement with Aaron about the flake.
- **Stage fork.** `raman.md` says the Raman predates stacking on the
  parent flake; the fused call says the domain "survived the cutting
  process" — one read, two stage descriptions. Neither document dates it.
- **Transport datasets differ, verdict doesn't.** Aaron's transport
  column is his own fan from before the session (the call was sealed
  before HERA ran); HERA's is the 16-run session. Same pair, same
  verdict, same strength.
- **Per-device headline.** As on vti-01: HERA withholds a device verdict
  with one region read; Aaron generalizes. Already ruled semantic in
  `../vti-01/reconciliation.md`; no new evidence either way.

## Run metrics

Definitions per `hera-paper/notes/trial-metrics.md` with the vti-01
rulings (wall-clock grant → final handoff; idle-on-a-human is standby;
tokens for every instance). Times PDT (rig).

| Metric | Value |
|---|---|
| Bring-up (excluded) | brief 2026-08-21 20:05 → E1 grant 20:21 |
| Wall-clock, gross | grant 20:21 → final handoff 2026-08-22 09:37 = **13.3 h** |
| Standby (idle on a human) | **0 h** — the He-budget asks (20:08, 21:00, 01:20) went unanswered; the agent proceeded on the standing grant |
| Wall-clock, active | **13.3 h** |
| Interventions (operator messages after bring-up, both channels, liberal) | **0**. The grant ("go for autonomy", 20:21:07, queued while VERIFY ran) is the only human message in the transcript. No notebook input after bring-up. |
| Agent-initiated stops | **0** |
| Interrupted runs | **1** of 16 (run 9: LS335 `HTR?` timeout under `fp` at ladder point 6; heaters-off `finally` ran; self-corrected, re-landed as runs 10–15) |
| Tokens — tactical session | 358 API turns; 201 tool calls; 582k output; 5.43M cache-write; 97.9M cache-read; 77k uncached input |
| Tokens — Raman read (fresh instance) | — (no raw data; step not run) |
| Tokens — fusion (fresh instance) | 153k (harness-reported) |

Not captured: `hera-session` init tokens (shared project dir, not archived).

## Summary

Transport-time stacking on the one wired pair: concordant across all three
verdicts at strong. The Raman leg cannot be scored — there is a single
human read and no data behind it, and HERA's fusion correctly declines to
weigh it. Mechanism: concordant on direction if the Raman is taken as
given; HERA does not take it as given. The only divergence is the
per-device headline, the same one as vti-01. Operationally the session was
fully autonomous: one grant, zero interventions, zero stops, 13.3 h.
