# Pre-registration — vti-02 fan-design replay matrix

Declared 2026-09-29 by the commit that adds this file, before any production episode ran.
Rulings: Zack; reviewed by Aaron.

## 1. What is pre-registered

Four metrics of a fan's design, each compared between the corpus and no-corpus arms with
the same test (§ 5). They are a family: each is reported and discussed on its own, and no
verdict combines them. Everything else is exploratory (§ 8).

## 2. Matrix

- **Episode:** a fresh agent picks up the frozen vti-02 state (the 08-22 session after both
  spot checks are acquired, before the fan is designed). Its brief closes on the operator's
  request: "The operator's request for the next move is a Landau fan for the stacking call,
  design and land it."
- **Frontier:** `vti02-fan-request-0822`.
- **Arms:** corpus (live deploy `13b07e9`), none (live no-corpus deploy `039b0f5`). The none
  deploy drops the recipes, crops, `hera/models` and the method docs.
- **Models, effort high:** Fable 5, Opus 5, Fable 5.1, Opus 5.5, GPT-6 Astra, GPT-6 Sol.
  Twelve cells.
- **Labels:** by `run.model.observed`.

## 3. Endings and the analysis set

Each episode gets one ending, read mechanically from `episode.json`, `summary.csv` and the
extraction.

| Ending | Rule | Treatment |
|---|---|---|
| Fan | the grader's fan tier: a 2D sweep, a continuous ramp, or a column series with a declared ladder; a `landed_unexecuted` fan included | graded |
| Spot check | a field sweep at one density | censored |
| B = 0 cell | a landed cell with no field axis | censored |
| Nothing landed | the episode ended (stop, stall, timeout, turn cap) with no measure cell appended | censored |
| Harness failure | status interrupted, quota or error; a prep-cell handoff; observed model ≠ pinned; pinned model or effort ≠ the case file's; the image's corpus condition ≠ the arm | excluded, listed |

- Censored episodes are counted per cell and not graded.
- A fan whose extraction fails, or leaves τ or the drive untraced, is re-extracted once. If
  it fails again the fan scores 0 on metrics 1–3 and sits at P(call) 0, unbounded hours,
  for metric 4.
- An episode with several extractions takes the latest.
- Selection is by case name, not by cut: other frontiers share the cut.

The analysis set is every episode of the twelve `vti02-fan-request-0822-*` cases launched
after this declaration, with cut digest `f7f808fe…`. Every development and smoke episode is
excluded.

## 4. The metrics

| # | Metric | What it says |
|---|---|---|
| 1 | P(call) within 8 h | the probability that the fan supports the stacking call, 0 past 8 h |
| 2 | Tracked span, in FFT bins | how far along the light tone the fan follows it |
| 3 | Rows per F_L period at the top density | whether the field grid samples F_L (Aaron grades at 3) |
| 4 | Pareto dominance on (P(call), hours) | how often a fan is both better and cheaper |

1. **P(call):** per part (the light tone; the F_L / F_heavy split), k independent detected
   columns support the call with probability 0, 0.16, 0.50, 0.84, 1 for k = 0 … 4 or more.
   Columns are independent when their light tones sit half a bin apart. The fan takes the
   lesser of its two parts. Per fan v = P(call) · [hours ≤ 8].
2. **Tracked span:** a column speaks for a stretch of the light-tone axis half a bin wide,
   centred on its own model tone: the column spacing of metric 1. The span is the weighted
   length of the union over columns, in bins of the part's own window. The fan takes the
   lesser of its two parts. No pass mark.
3. **Rows per F_L period:** at the fan's top electron-side density, over its coarsest row
   interval above 1.0 T. A fan with no electron-side column scores 0.
4. **Pareto dominance:** fan a dominates fan b when it is no worse on P(call) and on hours
   and better on one.

Metrics 2 and 3 read the field and density axes; the lock-in settings enter through
metric 1, and a clipped column carries no weight in metrics 1 and 2.

Hours are the rig cost model's, the fan's own measurement time. Definitions of record:
`hera/docs/fan-design-grader.md`, `hera/graders/fan-design/box.py` and `analysis.py` beside
this file, at the frozen commit.

## 5. The test

- Metrics 1–3: per cell S = the mean over its fans; Δ = the mean over models of
  S(corpus) − S(none).
- Metric 4: per model D = P(a corpus fan dominates a none fan) − P(the reverse); D_pool =
  the mean over models.
- Each: a two-sided permutation of the arm labels within each model, 10 000 permutations,
  seed 20260929. Reported with the raw p and the Holm-adjusted p over the four.
- A model with no fan in either cell drops out and is listed.

## 6. Stopping

- Each cell runs to N = 20 fans, capped at 40 episodes. Fixed before launch.
- Tranche 1 is 5 episodes per cell. The rest follow whatever tranche 1 shows. Every episode
  submitted counts.
- No data-dependent extension. No grader, prompt, image or case change between tranches.
- On the development set, N = 20 detects Δ ≥ 0.13 on metric 1 at 80 % power (95 %
  half-width 0.09); N = 5 detects Δ ≥ 0.23.

## 7. Registered sensitivities (reported, never decision inputs)

| Axis | Levels |
|---|---|
| Budget (metric 1) | 6 h, 12 h, none |
| Column spacing (metrics 1 and 2, one number) | a quarter bin; one bin |
| P(call) curve | a step at four points; linear |
| P(call) combination | the parts averaged; their product |
| Censoring | censored episodes scored 0 (share of episodes) |

All are computed from the saved extractions; none needs a re-extraction.

## 8. Exploratory, not pre-registered

- The free-choice frontier `vti02-pre-fan-0822`: the same state with no request in the
  brief. What each cell does next (fan, spot check, B = 0 cell, nothing) is its result.
- Box quality, the six-item checklist, tracked-span P, Aaron's resolved fraction.
- Per-model Δ and model contrasts; ending counts with Wilson intervals.
- The 08-24 cut; the live fans placed beside their offline cells.

The metrics grade the fan's design. They make no claim to predict a session's call: of the
five live sessions, P(call) of the session's fan matches the call in two.

## 9. Disclosures

- The grader was developed on every episode to date: the period ramp on three measured
  fans, the acquisition factor on two.
- The four metrics were chosen on 2026-09-29 from about twenty candidates, by how well each
  separates the arms on 27 development fans and 5 live fans. Record length, the lowest field
  and box quality were among those set aside.
- The development fans came from free-choice briefs, and 15 of their 19 corpus fans from
  stand-in models (Sonnet 5, Haiku 4.5, GPT-5.6).
- P(call) took its present form on 2026-09-28, after the development set had been scored
  with a step at four points and the parts averaged. The change moves the development-set
  Δ(8 h) from +0.22 to +0.44.
- The request was smoked on six episodes before this declaration (GPT-6 Astra and GPT-6 Sol
  with corpus, Fable 5 and Opus 5.5 without, and two stand-ins). All six landed a fan; both
  no-corpus matrix-model fans scored above 0.9 on P(call).
- The 08-22 state carries 3.6 h of corpus-prompted spot checks that the metrics do not
  count. Every arm starts with F_L in hand, so the offline gap is a lower bound on the live
  one.
- P(call) treats column failures as independent; it runs optimistic at 10 nA.
- Claude episodes bill the Anthropic AI for Science award through the API; Codex episodes
  bill a ChatGPT plan.

## 10. Freeze record

| Surface | Sha / id |
|---|---|
| Repo commit | the commit that adds this file |
| Grader `hera/graders/fan-design` | `box.py` `b1242820`, `grade.py` `32d39e00`, `cases.toml` `53511fba`, `prompt.md` `152661ec` |
| Harness | `src/hera/replay` tree `2f9d7b08`, code hash `168ca185…` |
| Stubs | tree `a5728e13` |
| Mask | `masks/vti02-pre-fan-0822.yaml` `78697e7a` |
| Briefs | `briefs/vti02-fan-request-0822/corpus.md` `12c39aed`, `none.md` `b359dc74` |
| Case files | the twelve `vti02-fan-request-0822-*.yaml` at the repo commit |
| Images | corpus `sha256:194d62c195b5…`, none `sha256:f1eac925261e…` |
| Cut digest | `f7f808fe749b9bf8…`, both arms, checked before each tranche |
| Models | `claude-fable-5`, `claude-opus-5`, `claude-fable-5-1`, `claude-opus-5-5`, `gpt-6-astra`, `gpt-6-sol` |
| Effort, CLIs | high; Claude Code 2.1.283, Codex 0.157.1 |
| Analysis script | `analysis.py` beside this file, at the repo commit |

## 11. Deviations

Logged in `deviations.md` beside this file, dated, before the affected result is read.
