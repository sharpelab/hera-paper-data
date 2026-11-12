# Pass B — collaborator debrief

**DRAFT until Aaron locks it.** Aaron: practice on `CAL2.html` (the Pass A calibration run, already burned — its
export is shakedown data, not a score) and edit the tool, pages, and `ANALYSIS-PLAN.md` as you see fit. When
satisfied, regenerate the six tier-1 pages if the tool changed, **commit the final state and tag it
(`passb-locked`) before opening any tier-1 page** — that commit is the instrument lock. Then grade in the
randomized order `T1E → T1C → T1F → T1D → T1B → T1A` (`random.Random(20260830).shuffle`), exporting each
`<key>.passb.json` into `passb/` and committing. `hera_passb_ingest.py` turns exports into `scores/passb.*.csv`;
`passb/<key>.map.json` carries the card→unit map for the concordance analysis. One known gap: `T1F-052` is
anchored to a transcript line, not a notebook cell, so it cannot appear in any dossier panel (the dossier is the
notebook pair by ruling).

Pass A grades extracted claims one at a time, blind. Pass B is the other read: the expert opens the whole session
dossier and grades it as an advisor grades a collaborator's work.

    python3 hera_passb.py <run_key> <archive_dir>     # -> passb/<run_key>.html

Stdlib only. Needs `*_measure.ipynb`, `*_ana.ipynb`, `data/<N>/`; Pass A claims come from `cards/<run_key>.cards.jsonl`
if present (`items` joined in from the other card files by exact claim text). One self-contained file, figures inlined as
base64, opened from `file://`. Reading order: skim (prior belief, THE CALL, ana figure gallery, initial reaction) → "Begin
full read" → one widget per unit (`1`/`2`/`3`/`4` = sound/shaky/wrong/n-a, `j`/`k` move, `n` note) → final debrief,
unlocked once every unit is ruled. Autosaves to localStorage under `hera-passb-<run_key>`; Import restores an export.

**Units.** A markdown header cell plus the cells under it. Measure units run in notebook order; each ana unit renders
inline under the last measure unit it shares a data id with (produced sweep ids, from the run-id log line), the rest
trail as standalone. Everything before the first `#`-marked HERA cell folds into one "Session bring-up (operator-run)"
unit. Protocol and template units are then marked **context** — not rendered at all, export-only — on three signals:
that bring-up fold; a session-start / kernel-probe / VERIFY title before the first acquisition; every markdown cell
recurring in 3+ sibling `*-session` archives (post-scrub, whitespace-normalized). Rails: a unit with data ids, and
the final-call unit, are always graded. A card belongs to the unit whose `cell_range` (or attached `inline[]` span)
holds its `verbatim` anchor (`[measure 33]` / `[ana 23]`), else the last unit sharing a `data_ids` entry — the rule
behind the "What Pass A extracted here" panel; a card landing in a context unit folds into the next graded unit's
panel, prefixed "(from excluded context)".

## Export JSON — `<run_key>.passb.json`: `run_key`, `exported`, `phase`, plus
- `units[]` — graded and (unrendered) context alike: `{unit_id, notebook, cell_range, title, inline[], data_ids,
  context, context_reason, ruling, note, ts}`; `ruling` is `sound|shaky|wrong|na|null`, always null when `context`.
- `skim` / `final` — every field always present, `""` when blank: `know_text`, `know_adjudicated`,
  `skim_disposition`, `skim_supervision`, `skim_impression`, `ts`, `began_ts`; and `final_disposition`,
  `reanalysis`, `remeasure`, `final_supervision`, `overall_read`, `omission`, `biggest_right`,
  `biggest_wrong`, `ts`.
- `events[]` — `{ts, kind, target, value}` for every action, for effort analysis.
