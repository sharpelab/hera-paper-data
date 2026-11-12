You are looking at the finished data of a pre-registered experiment and reporting what you see. Read-only: write nothing except your notes file. Budget: the ChatGPT week is at 95%, so stay compact — under ~40 tool calls, no long exploratory loops, no web search.

## What the experiment is
A replay benchmark for an AI measurement agent (HERA) on a condensed-matter transport rig. Each episode: a fresh agent picks up a frozen session state (device vti-02, 2026-08-22, after two Shubnikov-de Haas spot checks) and is asked, in the brief, to design and land a Landau fan for a "stacking call" (which tetralayer-graphene stacking the device is, from the SdH tones F_L and F_heavy). Two arms: `corpus` (the agent has the lab's method recipes and prior-measurement corpus) and `none` (no corpus). Six models × two arms, N = 20 fans per cell (one cell capped at 19), 300 episodes in all. Four pre-registered metrics, each corpus − none, permutation-tested within model with Holm correction: P(call) within 8 h, tracked span in FFT bins, rows per F_L period at the top density, and Pareto dominance on (P(call), hours). All four came out strongly positive.

## Files (absolute paths)
- /home/zack/sharpelab/measurement-env/hera/campaigns/vti02-fan-design/prereg.md — the design and metric definitions (read §3–§5 and §7–§9).
- /data/sharpelab/hera-data/vti02-fan-scoring-v2/final/analysis.md — the registered analysis output: per-cell table, registered results, sensitivities, one row per fan with field axis, hours, P(call), spans, rows/F_L, the censored list.
- /data/sharpelab/hera-data/vti02-fan-scoring-v2/final/analysis.json — the same, machine-readable (`episodes`, `cells`, `results`, `sensitivities`).
- /data/sharpelab/hera-data/vti02-fan-scoring-v2/final/episodes.json — one record per episode (300): model, arm, ending (fan / spot_check / nothing_landed), episode cost and wall, hours, p_call, p_light, p_split, span, rows_fl, and for fans the parsed field axis: spacing (invB / stitched / B), B_min, B_max, n_B rows, nmin/nmax density in 1e12 cm^-2, ncols.
- Per-episode detail if you need it (transcripts, appended notebook cells, grader extraction output.json with `notes`): /data/sharpelab/hera-data/replay/runs/vti02-fan-request-0822-<model>-<arm>/<stamp>/episodes/<NN>/ — sample sparingly, these are large.

## Already known (do not re-derive at length; go past it)
- The arm gap sits in the F_L/F_heavy split part of P(call), not the light tone (0.90 vs 0.51 against 0.91 vs 0.87).
- No-corpus agents often pick a field grid uniform in B (38 of 120 fans, mean P(call) 0.13); corpus agents use 1/B-uniform grids (106 of 119).
- Corpus agents defer the fan for a low-field spot check 59 times in 178 episodes (none arm: 1 in 122); those are censored and the result survives scoring them 0.
- No-corpus fans cover the hole side (112 of 120) and spend points on density columns; corpus fans are electron-only with more field rows.
- Corpus fans with B_min ≤ 0.5 T run ~11 h and blow the 8 h budget; the 8 h budget drives Fable 5's per-model number.

## What I want from you
Things a careful physicist-analyst would notice that the list above misses. Ideas, not obligations: model-specific design signatures (grid shapes, density windows, lock-in choices) and whether they are stable across episodes; whether the metrics can be gamed or where they disagree with what a physicist would call a good fan; the relationship between rig hours and quality within an arm; anything odd in the fan table (duplicates, identical designs across episodes of one model, suspicious extraction values); what the censoring sensitivity does and does not cover; what a follow-up experiment should change. Where you compute something, say exactly how. Distinguish what you measured from what you infer. Numbers over adjectives.

Write your notes to /data/sharpelab/hera-data/vti02-fan-scoring-v2/final/astra-notes.md (create it; that is the only file you write), then end with a five-line summary in the terminal.
