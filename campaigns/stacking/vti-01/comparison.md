# vti-01 — comparison

**SCORER / SUPPORT-SIDE ⚠️ — not for agent view.** Prereg §5 step 4. The
three locked verdicts side by side; nothing upstream changes after this.

## Locks

| Artifact | Commit | Produced |
|---|---|---|
| `transport-call.md` | `39e57bb` 2026-08-20 21:56 EDT | E1 HERA tactical, VTI, 2026-08-18→20; corpus `d8e1337` (= `arm1-freeze`) |
| `raman.md` (raw, hash-verified) | `911c706` 2026-08-21 | `vti-01.wip`, sealed 2026-08-19, unsealed after the transport lock |
| `raman-contract.md` | `df4089c` 2026-08-21 | fresh instance, `raman-stacking-id.md`, no sight of transport |
| `fusion-verdict.md` | `0a93b8d` 2026-08-21 | fresh instance, `stacking-raman-transport-fusion.md`, staged inputs only |
| `adjudication.md` | `5a7379b` 2026-08-21 | Aaron's `vti-01-fused_call.md`, sealed 2026-08-19 (hash `d95f48…`), before the transport call existed; fuses the Raman with the owner's own transport (see `../deviations.md`, 2026-08-19) |

## Per channel — stacking at measurement time

| Channel | Transport (HERA) | Fusion (HERA) | Adjudication (Aaron) | Concordance |
|---|---|---|---|---|
| sr1 (B_SD–L4) | ABA, strong (two-branch) | ABA, strong — reconciled-by-conversion | Bernal, strong (all pairs) | **concordant** |
| sr3 (L3–L2) | ABA, consistent-with | ABA, consistent-with — reconciled-by-conversion | Bernal, strong (all pairs) | concordant on verdict; strength differs (consistent-with vs strong) |
| sr2 (L4–L1) | uninformative | no measurement-time verdict — single-modality (Raman, as of S1) | Bernal, strong (all pairs) | **divergent on coverage**: HERA reads the pair as uninformative on its own data; Aaron's read rests on the owner's transport, a different dataset |
| per device | none | none (not all covered regions concur at measurement time) | homogeneously Bernal, strong | divergent on generalization, not on any measured channel |

## Raman leg and mechanism

| | Fusion (HERA; Raman contract) | Adjudication (Aaron) | Concordance |
|---|---|---|---|
| Raman at pre-stacking stage | ABC, strong, S1 = 2026-05-28 post-first-cut, pre-transfer; device rectangle 0.976 ABC / 0.000 ABA at S1 | isolated rhombohedral domain prior to stacking, strong; survived the cutting | **concordant** (incl. survival of the cut — HERA's S1 map is post-cut) |
| Mechanism | ABC→ABA conversion, consistent-with not observed; risky steps named by construction (hBN pickup/encapsulation, contact metallization), undated | conversion during stacking, complete | **concordant** on mechanism and direction; HERA hedges completeness (sr2 uncovered at measurement time, sub-spectral-weight ABC not excludable), Aaron calls it complete |

## Evidence divergences, traced

- **sr2.** HERA's transport: weak short pair, signals near floor throughout, contact-limited session (T_SD ≈ 109 MΩ). Aaron's transport: the owner's run, pairs of "different clarity" but all Bernal. Not a disagreement about physics — a coverage difference between two transport datasets. What would settle it is in both documents: restore the pair (HERA) / the owner's fan on that pair, if it exists.
- **Strength on sr3 and per-device.** HERA's scale is per-channel and withholds a device headline when a covered channel lacks a measurement-time read; Aaron's is a device-level read over the owner's full pair set. Same evidence class, different granularity.
- **Adjudication labels L3–L2 as `sr4`**; the intake config and every HERA artifact name it `sr3`. Typo, no consequence.

## Run metrics

Definitions per `hera-paper/notes/trial-metrics.md`; the open items there
are ruled here (Zack, 2026-08-21): wall-clock runs grant → final handoff,
any stretch HERA is idle waiting on a human is standby; the
operator-requested extension counts because the locked call includes its
addendum; tokens are reported for all three instances. Times PDT (rig).

| Metric | Value |
|---|---|
| Bring-up (excluded) | brief 2026-08-18 23:11 → E1 grant 23:16 |
| Wall-clock, gross | grant 23:16 → final handoff 2026-08-20 17:22 = **42.1 h** |
| Standby (idle on a human) | 16.6 h — E0 stop-and-report 08-19 00:05 → rulings + re-grant 11:28 (11.4 h); close-out handoff 08-20 03:40 → extension request 08:57 (5.3 h) |
| Wall-clock, active | **25.5 h** (monitor waits on running sweeps are active) |
| Interventions (operator messages after bring-up, both channels, liberal) | **2**, both chat: 08-19 11:28 — TG-range + Si rulings + E1 re-grant, answering the agent's safety stop; 08-20 08:57 — request for a higher-quality fan (runs 19–20). No operator notebook input after bring-up (gates A/B were operator-run at bring-up). |
| Agent-initiated stops | **1** — E0 drop at gate C (TG leak turn-on inside card limits), resumed on explicit re-grant |
| Interrupted runs | **0** of 21 sweeps (runs 0–20) aborted; 2 nb-collab client timeouts with the kernel unaffected |
| Tokens — tactical session | 536 API turns; 747k output; 5.18M cache-write; 163M cache-read; ~1k uncached input |
| Tokens — Raman read (fresh instance) | 213k (harness-reported) |
| Tokens — fusion (fresh instance) | 160k (harness-reported) |

Not captured: `hera-session` init tokens (shared project dir, not archived).

## Summary

Transport-time stacking: concordant on every channel both sides read (sr1 strong, sr3). Pre-stacking Raman: concordant (rhombohedral, strong). Mechanism: concordant (conversion during assembly). The divergences are coverage (sr2) and headline granularity (per-device), not evidence.
