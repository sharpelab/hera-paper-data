---
slug: after-qo-discovery
user: aaron
cut_index: 54
latest_fileid: 159
included:
  data: [132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159]
  images: []
leak_terms:
  - "Temperature dependence"
  - "s.ramp(heater.volt"
  - "heater.curr"
forward_scan: "kept region (cells 0-54) greped for forward references (temperature dependence / heater ramp / heater.curr / Tc / transition). 'temperature' appears only as the s.fp(temperature) readout fastparam and the read_temperature def (cell 12) — i.e. the always-present T column, not a forward reference to the T-dependence experiment. 'heater' appears only in cells 9-10 (instrument instantiation + validator = setup). No s.ramp(heater.volt), no heater.curr, no Tc/transition pre-cut. Clean."
---

# Frontier — cut at end of `# Quantum oscillations discovery journey`

*Defines the decision boundary at which this fixture freezes the RPL_10 QO run
for offline replay. The YAML frontmatter above is the machine-readable contract
the `hera-replay` driver reads; the prose below is for humans. This is a
**CONTESTED** frontier — at the cut, several legitimate next experiments compete
(see `../ground_truth/after-qo-discovery/next_move.md` judging buckets).*

## The frontmatter contract

- **`cut_index` (54)** — fixture-relative, 0-based, inclusive. The agent sees
  cells `0..54`; everything after is the answer key. Index 54 is the last cell
  of `# Quantum oscillations discovery journey`; index 55 is the
  `# Temperature dependence` markdown header — the first cell of the *next*
  experiment, which is the thing HERA is asked to predict.
- **`latest_fileid` (159)** — the freshest *executed* sweep at the cut (cell 53);
  the agent is pointed here as "the most recent result." See
  `../ground_truth/after-qo-discovery/reading.md`.
- **`included.data`** — the **allowlist** of pre-cut data dirs the driver
  hardlinks into the working copy: `[132 … 159]`, the full file_id span of THIS
  notebook up to and including the cut. Authoritative; adding a post-cut id
  (160+, the temperature-dependence sweeps) would be the leak.
- **`leak_terms`** — post-cut-only tripwires (verified below).
- **`forward_scan`** — human attestation that kept markdown/comments carry no
  forward reference (the one vector cropping can't catch).

## Cut

- **Cut index 54** sits on a **section boundary**. Index 54 is itself a **raw
  (unexecuted) cell** — a draft of one more QO fan (`D = 0.25 V/nm`,
  `n = -2.75 to -0.35`) that Aaron staged but never ran (raw cell, no outputs, no
  data dir). The last *executed* QO sweep is cell 53 → `data/159/`. Index 55 is
  the `# Temperature dependence` header.
- **No mid-section header leak.** Truncating at 54 keeps the
  `# Quantum oscillations discovery journey` header (44) and its two
  sub-headers (`## Gate maps in field` 45, `## D = 0.31 V/nm up to B = 1 T` 49)
  and drops `# Temperature dependence`. No lookahead headers survive.

## Leak-term verification

- **`"Temperature dependence"`** — the next section header (cell 55 only).
- **`"s.ramp(heater.volt"`** — the heater-ramp *call* that starts the T-dependence
  work; first appears at cell 57 (verified all matches > 54). The bare token
  `heater.volt` appears pre-cut in cells 9–10 (`heater.volt.step`,
  `heater.volt.add_validator`) — that's instrument *setup* (capability, legit),
  which is why the tripwire is the `s.ramp(heater.volt` *call*, not `heater.volt`.
- **`"heater.curr"`** — the heater current readout (`s.read(heater.curr)`); first
  appears at cell 57 (verified all matches > 54).

`mag.field` is deliberately **not** a leak term: unlike the b1c2 SC fixture, the
magnet IS the QO measurement axis here — it's swept ±1 T throughout the kept
region (cells 23–53). The magnet is established capability, not the answer.

## What's live at the cut

The run has, in order:
1. `# Taking gate maps in field` (B = ±100 mT) and a multiferroism Hall check
   around the "bubble" (cells 21–33) → `data/132–138`.
2. `# High res gate map` + `# Perusing Idc` (DC-bias × density linecuts at a few
   D) (cells 34–43) → `data/139–152`.
3. `# Quantum oscillations discovery journey` (cells 44–54) → `data/153–159`:
   B = ±1 T field gatemaps (153–155), then **n-vs-B Landau fans at D = 0.31 V/nm**
   (156–159) confirming oscillatory behavior.

**Latest landed sweep: `data/159/`** (cell 53) — a B (1→0 T, 351 pts) × (n: −2.9
to −2.1 at D = 0.31, 251 pts) fan. State at the cut: gates parked to 0,
`V_si = −20 V`, magnet ramped back, **base temperature** (heater never driven).

## Why this is a CONTESTED frontier

Oscillations have just been discovered/confirmed. "What next?" has several
defensible answers, and a competent operator could pick any:
- **Temperature dependence** (what Aaron actually did) — heat the sample and
  watch the oscillations / SC features evolve (effective mass from QO T-damping;
  Tc of the SC state).
- **More / finer QO mapping** — other D values (he did D = 0.28, 0.25 later),
  higher-resolution fans, extend n-range, push to higher B — to nail the
  Landau-fan slopes and Fermi-surface degeneracy cleanly first.
- **Fraunhofer / SC-dome characterization** — the device hosts SC1/SC1'; map the
  supercurrent's field response or sit on the dome.
- **(n, D) gate maps** — re-survey the phase diagram at B = 0 to place the QO
  region in context.

All four are reasonable; the choice is a genuine **strategic** branch, not a
mechanical retune. The judging buckets in `next_move.md` reflect this — "different
but reasonable" is a populated bucket here, not an empty one.

## Caveats carried into the cut

- **Long calendar span.** This single notebook session ran 2024-12-30 → 2025-01-07
  (`data/132` is Dec 30; `data/159` finishes Jan 7). The file_ids are contiguous
  and chronological; the wide date range is real (a multi-day campaign), not a
  fixture bug.
- **Degraded input (v0).** No live kernel, no operator screen observations, and
  deliberately **no `live_notes.md`**: the next decision class does not hinge on
  an unrecorded live fact. The plots are raw multi-trace overlays (see
  `reading.md`) — the QO/fan structure is not directly legible as a 2D colormap
  from the embedded PNGs; that's an honest input limitation, not leakage.
