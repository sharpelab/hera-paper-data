---
slug: after-sc-gatemap
user: aaron
cut_index: 83
latest_fileid: 145
included:
  data: [130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145]
  images: []
leak_terms:
  - "Fraunhofer"
  - "fraunhofer"
  - "megasweep(mag.field"
  - "determining Ic"
  - "Ic at zero"
forward_scan: "kept region (cells 0-83) greped for forward references (fraunhofer / Ic / 'determining Ic' / megasweep(mag.field) / 'next'). No forward reference to the field x bias Fraunhofer move found. Pre-cut 'field' mentions are all legitimate setup (AMI430 driver def at cell 41, magnet init at cells 9/11/42/43/47) or the SC-gatemap section's own small-field line-cuts (cells 70/77/83 ramp or 1D-sweep mag.field over 0-20 mT while mapping the dome) — capability/context, not the post-cut decision. The cut sits on the `# Fraunhofer` boundary (header at cell 84, dropped). Clean."
---

# Frontier — cut at end of `# Gatemap of SC`

*Defines the decision boundary at which this fixture freezes the RPL_19
2025-11-03 campaign for offline replay. The YAML frontmatter above is the
machine-readable contract the `hera-replay` driver reads; the prose below is for
humans. This is the fixture's single (CONTESTED-type) frontier — it carries the
full 2x2 autonomy x length brief grid (depth held = deep). Added 2026-06-01.*

## The frontmatter contract

- **`cut_index`** — fixture-relative, 0-based, inclusive. The agent sees cells
  `0..cut_index`; everything after is the answer key. Fixture indices == source
  indices (the notebook was cropped from cell 0).
- **`latest_fileid`** — the freshest sweep at the cut; the agent is pointed here
  as "the most recent result." See `../ground_truth/after-sc-gatemap/reading.md`.
- **`included.data`** — the **allowlist** of pre-cut data dirs the driver
  hardlinks into the working copy. Authoritative; the driver copies *only* these,
  so adding a post-cut sweep id (146+) here would be the leak. Derived from the
  cell↔file_id map (`../cell-to-fileid.md`) for cells ≤ 83.
- **`included.images`** — empty. Every sweep cell in this notebook embeds only
  one PNG output: the live gate-leakage monitor (`k_*_curr` vs time/Vbg), *not* a
  transport heatmap. The transport data lives in the TSVs. So there is no useful
  cell plot to extract; the agent reads `data/<id>/plot.png` (also the leakage
  monitor) and the TSVs directly. See `reading.md`.
- **`leak_terms`** — post-cut-only tripwires, each verified with
  `nb grep <notebook> -i <term>`:
  - `Fraunhofer` / `fraunhofer` — only cells 84 (header) and 97. Both > 83.
  - `megasweep(mag.field` — the field × DC-bias Fraunhofer sweep *call*; earliest
    occurrence cell 100. The SC-gatemap section sweeps the magnet too, but only as
    `s.ramp(mag.field, 0)`, `s.sweep(mag.field, ...)` (1D) and
    `multimegasweep([mag.field], ...)` (gate-line × small field) — never the
    `megasweep(mag.field, ..., dc205_1.volt, ...)` field × bias map. So the
    literal `megasweep(mag.field` token is post-cut-only.
  - `determining Ic` / `Ic at zero` — the Fraunhofer comment strings (cells 86/87
    and following). Both > 83.
- **`forward_scan`** — the human attestation that the kept markdown/comments were
  checked for forward references. Clean (see frontmatter).

## Cut

- **Cut index 83** sits on a **section boundary**: cell 84 is the `# Fraunhofer`
  markdown header (the first cell of the next experiment, which HERA must
  predict). Cell 63 is the `# Gatemap of SC` header; the SC-gatemap section runs
  63→83.
- Cell 83 is the section's last sweep: `s.multimegasweep([mag.field],
  [np.linspace(0, 0.020, 201)], [k_tg.volt, k_bg.volt], [ys, xs], ...)` — a
  gate-line cut through the SC dome (a line in (Vbg, Vtg) through (-5.2, 0.47),
  slope 0.3) versus a small perpendicular field 0→20 mT. → `data/145/`.
- **No mid-section header leak.** Truncating at 83 keeps `# Gatemap of SC` (cell
  63) and `# Configs` / `# Gate checks` and drops `# Fraunhofer` (84) and
  everything after.

## What's live at the cut

The 2025-11-03 cooldown (a mature cooldown: `measurebot` alerts wired, fast
setup) has, in order:

1. `# Configs` (cell 46) + `# Gate checks` (cells 50–62) — top-gate (16 nm) and
   back-gate (25.5 nm) responsiveness checks at V_Si = −48 V. → `data/130–133`.
2. `# Gatemap of SC` (cells 63–83) — a finer (Vtg, Vbg) gate map of the SC dome
   at V_Si = −48 V (`data/134`), then a sequence of maps/line-cuts of the dome,
   including some that ramp or sweep the magnet over small fields (0–20 mT) to
   look at the dome's low-field behavior. → `data/134–145`.

**Latest landed sweep: `data/145/`** (cell 83). State at the cut: a candidate
SC dome has been located and mapped near (TG ≈ 0.47, BG ≈ −5.2) at V_Si = −48 V,
base T ≈ 45–60 mK; AC excitation ~0.5 nA at 7.78 Hz; current channel on sr830_4
(`I_{6-22}`), voltage channels on sr830_3 (`25-24`) and sr830_5 (`13-14`).

## Why this frontier is CONTESTED

Unlike the b1c2 `after-idc-vs-n` frontier (where good context made the field test
the obvious move), the SC dome here has been *mapped* but not yet *interrogated*,
and several legitimate next experiments compete. Aaron went to **Fraunhofer**
(Ic vs perpendicular field at the fixed dome optimum), but a strong analyst could
equally argue for: temperature dependence across the dome (Ic→0 at Tc), looking
for oscillations / quantum-oscillation structure, or a zero-effective-field
gatemap to pin the dome center before field work. The 2x2 brief grid tests
whether autonomy (open vs directive) and length (short vs long) steer the agent
toward Aaron's actual move — this is exactly the kind of frontier where those
levers should discriminate. See `../ground_truth/after-sc-gatemap/next_move.md`
for the judging buckets.

## Caveats carried into the cut

- **Plots show leakage, not transport.** Every sweep's embedded/disk PNG is the
  registered live-monitor (`s.plot(k_bg.volt, k_bg.curr)` etc.) — gate leakage
  currents, all ~1e−11–1e−10 A (healthy, no leakage). The SC physics is only in
  the TSV columns (`sr830_*_X`). An agent relying on `plot.png` alone will see
  nothing; the correct read requires the TSVs. This is a real property of the
  source notebook, not a fixture defect.
- **Latest sweep was interrupted.** `data/145` stops at B ≈ 11.6 mT of its
  planned 0→20 mT (23,490 of ~40k rows). The gate-line × field intent is legible
  from `metadata.json`'s `slow_setpoints` regardless.
- **Degraded input (v0).** No live kernel, no operator screen observations, and
  deliberately **no `live_notes.md`**: the contested decision is a genuine
  strategic branch, not one that hinges on an unrecorded live fact. Per the
  locked principle, live_notes is added only when the decision *class* flips
  without it.
