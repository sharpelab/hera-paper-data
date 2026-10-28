# Shared brief for the four readers

READ-ONLY. You may write exactly one file: your notes at the path given in your task. Do not edit, create, move or delete anything else, anywhere. No git commands that change state. No `hera-replay` commands that submit, run, grade, cancel or reap. No docker. No model API calls (no `claude -p`). Never print credentials; do not read ~/.config/hera/keys/ or any auth.json. Do not use Glob/Grep across ~ (NAS mounts hang); stay inside the paths named here. Keep CPU light (single process, nice 19). Do not touch `hera/docs/notes/2026-08-22-vti-02-session`.

## The experiment
A pre-registered replay benchmark for an AI measurement agent (HERA) on a condensed-matter transport rig (device vti-02, tetralayer graphene). Each episode: a fresh agent picks up a frozen session state (2026-08-22, after two Shubnikov-de Haas spot checks) in a docker container with a faked clock and a stubbed rig; the brief's last line is "The operator's request for the next move is a Landau fan for the stacking call, design and land it." The episode ends at the first acquisition cell the agent lands (append to the measure notebook). Two arms: `corpus` (agent has the lab's method recipes and prior-measurement corpus in its image) and `none` (no corpus). Six models (claude-fable-5, claude-opus-5, claude-fable-5-1, claude-opus-5-5, gpt-6-astra, gpt-6-sol) × two arms, effort high, N = 20 fans per cell (Astra corpus capped at 40 episodes with 19), 300 episodes.

Endings: `fan` (graded), `spot_check` (a 1D field sweep at one density; censored), `nothing_landed` (censored). Four pre-registered metrics, each corpus − none, permutation-tested within model, Holm over four: (1) P(call) within 8 h, (2) tracked span in FFT bins, (3) rows per F_L period at the top density, (4) Pareto dominance on (P(call), hours). All four came out strongly positive (Δ = +0.427, +1.371, +2.334, D = +0.399; all Holm p 0.0004).

## Files (absolute paths)
- /home/zack/sharpelab/measurement-env/hera/campaigns/vti02-fan-design/prereg.md — the design; §3 endings, §4 metrics, §5 test, §7 sensitivities, §9 disclosures.
- /home/zack/sharpelab/measurement-env/hera/campaigns/vti02-fan-design/analysis.py — the registered analysis (docstring explains every quantity).
- /data/sharpelab/hera-data/vti02-fan-scoring-v2/final/analysis.md and analysis.json — the registered output: per-cell table, results, sensitivities, one row per fan (field axis string, hours, P(call), spans, rows/F_L, flags), the censored list.
- /data/sharpelab/hera-data/vti02-fan-scoring-v2/final/episodes.json — 300 records: key, model, arm, ending, cost (USD, notional for GPT-6), wall (s), grade_cost, hours, p_call, p_light, p_split, span, rows_fl, v (= p_call·[hours ≤ 8]); for fans the parsed field axis: spacing (invB / stitched / B), B_min, B_max, n_B (field rows), nmin/nmax (density, 1e12 cm^-2), ncols.
- Briefs the agents received: /home/zack/sharpelab/measurement-env/hera/replay/cases/briefs/vti02-fan-request-0822/{corpus,none}.md.
- The corpus recipes the corpus arm had: /home/zack/sharpelab/measurement-env/hera/recipes/measurements/landau-fan.md and sdh-spot-check.md (the none arm did not have these).
- Per-episode detail: /data/sharpelab/hera-data/replay/runs/vti02-fan-request-0822-<tag>-<arm>/<stamp>/episodes/<NN>/ where tag ∈ {fable, opus, fable51, opus55, astra, gpt6sol}. Inside: `episode.json` (run block: status, stop command, cost, wall, turns), `harness.log` (compact log of every tool call and result — READ THIS rather than transcript.jsonl, which is huge), `appended_cells.json` (exactly what landed in the notebooks), `session/hera_scratch/` (the agent's scratch files, markdown plans), `grades/fan-design/<stamp>/output.json` (the grader's extraction, with a `notes` field describing the landed cell). Sample at most ~15 episodes' harness.log; each is 50–300 KB.
- Tranche history: tranche 1 (5 per cell) is run dirs stamped 20260929T2125*; the rest were run in shortfall rounds (20260929T2345*, 20260930T*).

## Already established (go past it)
- Arm gap sits in the F_L/F_heavy split part of P(call), not the light tone (0.90 vs 0.51 against 0.91 vs 0.87).
- No-corpus agents often use a field grid uniform in B (38 of 120 fans, mean P(call) 0.13); corpus agents use 1/B grids (106 of 119).
- Corpus agents defer the fan for a low-field onset spot check 59 times in 178 episodes (recipe lever: "if the carrying tone is censored … a cheap low-field extension pins it"); none arm 1 in 122. Censoring sensitivity: scoring those 0 still gives Δ = +0.232.
- No-corpus fans cover the hole side (112 of 120) with many density columns; corpus fans are electron-only with more field rows.
- Corpus fans with B_min ≤ 0.5 T run ~11 h and blow the 8 h budget (Fable 5 corpus mostly).
- Three episodes' appends failed (`--follow` without `--wait`) and the grader read the fan from scratch files; one Sol episode ended by executing the operator's kernel-probe cell. Ruled: extractable fans count.
- Metric 1 is near-binary (most fans score < 0.15 or > 0.85).

## Deliverable
Write your notes (markdown) to the path in your task, then return a summary as your final message: findings first, each with the number and how you computed it, then anything you could not determine. Say what you measured versus what you infer. Numbers over adjectives. Do not restate the "already established" list.
