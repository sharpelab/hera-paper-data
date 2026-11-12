# Grading synthesis — Pass A beside Pass B

Human-readable pages and a joined machine-readable artifact that put the two expert
gradings of each tier-1 HERA run side by side: **Pass A** (per-claim, blind, item-scored;
`scores/T1.*`) and **Pass B** (whole-session collaborator debrief, unit-scored;
`passb/<KEY>.passb.json`). Everything here is generated; regenerate after any change to
the inputs:

    python3 dossiers/hera_synth.py

Stdlib only, read-only on the rest of the repo, deterministic (no timestamps or git state
in the output), so the generated files are committed beside the scores they derive from.

## Pages

- `index.html` — overview across the six runs: headline table (Pass A metrics beside the
  Pass B letters, stratified unit tally, propagation pair, active scorer minutes), the unit
  sequence of every run as ruling chips, every debrief field verbatim in a six-column grid,
  regex themes over the notes corpus, and the artifact list.
- `<KEY>.html` — one run: header per rater (Pass A tiles, Pass B skim → final decoded,
  stratified tally, propagation, effort, debrief fields), then every unit in grading order
  with its ruling, the rater's note, and the Pass A cards mapped to it (type, value, claim,
  card note, item verdicts, divergence marker). Context units and hidden cards are present
  but compressed so the counts reconcile.

Rules the pages follow (from `PREREG.md` and `passb/ANALYSIS-PLAN.md`): Pass A and Pass B
quantities are shown as pairs, never combined; the unit tally is only ever shown stratified
(conclusion-bearing = the unit holds ≥1 Pass A inference or verdict card, routine = the
rest); a rater's words are verbatim, italic on a tinted block labelled with their name, and
nothing on the page interprets them.

## Tables

All long-form: **rater is a column**, so a new rater adds rows, never columns.

| file | grain | carries |
|---|---|---|
| `runs.csv` | run × rater | identity and arm; Pass A metrics (blank if the rater did not score Pass A); Pass B letters, decoded text, skim→final deltas, stratified tally `cb_*` / `ro_*`, propagation `prop_*`, effort minutes, every debrief text field (blank if no Pass B) |
| `units.csv` | Pass B unit × rater | ruling, note, stratum, context flag and reason, cell range, number of cards by type |
| `cards.csv` | pooled Pass A card × rater | original id, type, hidden flag, verdict, value, item counts, note, verbatim anchor, mapped unit and its stratum, claim text |
| `concordance.csv` | card × Pass A rater × Pass B rater | value beside the unit ruling; `divergence` = `down` (value 1.0 in a shaky/wrong unit), `up` (value < 0.5 in a sound unit), `none`, or `ineligible:<reason>` |
| `propagation.csv` | run × rater pair, plus `ALL` | pre-declared analysis #3 counts and rates |
| `notes.jsonl` | one free-text field | `run rater pass level field ref orig_id unit_id type value hidden ruling text` — the grep corpus |

The card→unit join is the exact chain pooled id → `blind-map.yaml` `pool_T1` → run key +
original claim id → `passb/<KEY>.map.json` → unit id → export ruling. No fuzzy matching.
`T1F-052` (transcript-anchored) maps to no unit and is also a hidden card.

Example questions the tables answer directly:

    # Pass A cards ruled 1.0 that sit in a shaky or wrong Pass B unit
    awk -F, '$13=="down"' dossiers/concordance.csv
    # everything Aaron wrote that mentions the double peak
    grep -i 'double\|series resist\|second region' dossiers/notes.jsonl

## Raters

Discovery is by filename; nothing is hardcoded to Aaron beyond the bare-filename default.

- Pass B: `passb/<KEY>.passb.json` is Aaron; `passb/<KEY>.<rater>.passb.json` is `<rater>`
  (the convention `passb/RATER-JORDAN.md` prescribes). CAL* exports are ignored.
- Pass A: `scores/T1.cards.csv` + `T1.items.csv` + `T1.runs.csv` are Aaron;
  `scores/T1.<rater>.cards.csv` (+ `.items` / `.runs`) is `<rater>`.

Display names live in `RATERS` in `synth_common.py`. A rater who did one pass only gets a
`runs.csv` row with the other pass's columns blank; the concordance and propagation tables
form every Pass A rater × Pass B rater pair.

## Files

- `hera_synth.py` — loader, join, tables, entry point
- `synth_common.py` — identities, letter decode, theme lexicon, HTML helpers, CSS
- `synth_render_run.py` / `synth_render_index.py` — the two page renderers
