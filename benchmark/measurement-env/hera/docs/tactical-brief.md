# The tactical brief — the strategic→tactical contract

*The brief is what the strategic layer (Tier-3) hands the tactical layer
(Tier-2) to execute. This doc defines its shape, the two design axes we're
sweeping, why the brief is high-leverage, and how it plugs into the offline
benchmark. Drafted 2026-06-01, out of the b1c2 fixture-design review. Companion:
`hera/docs/strategic-layer.md` (the Tier-3 work this interfaces with) and
`hera/docs/benchmark-plan.md` (the eval harness). The reference brief shape is
`hera/test-cases/2026-05-06-b1c2-sc-characterization/briefs/after-idc-vs-n/directive-long.md`.*

## Why this exists

`hera-v0` ships the **Tier-2 (tactical)** agent and explicitly defers **Tier-3
(strategic)** (`hera-v0.md`). But today's tactical prompt (`hera_tactical.md`)
is fed a *campaign-level* goal ("characterize this device") and told to "decide
what to measure next… commit to an arc." So it currently does strategic and
tactical reasoning **jointly**.

The fixture review made the cost of that visible. Replaying the b1c2
`after-idc-vs-n` cut three times at campaign-goal altitude produced three
*different* next experiments — not because execution was noisy, but because the
agent was making an open **strategic** choice (test SC-ness now vs. map the dome
first vs. widen the density scan), each then executed competently. That variance
is strategic, and it was leaking into what we wanted to be a *tactical* eval.

**The prompt sets the altitude.** A campaign goal makes the agent reason
strategically; a brief makes it reason tactically. The brief is the knob. Get it
right and Tier-2 reliably executes while still exercising real judgment (ranges,
operating point, catching problems, escalating). Get it wrong and you either
re-introduce strategic variance (too open) or reduce Tier-2 to a sweep-typist
that stops noticing when the brief itself is wrong (too directive). Because the
brief governs that trade-off for *every* tactical run, it is one of the
highest-leverage design surfaces in the system.

## The contract — five fields

A brief specifies **what to find out and where**, and deliberately leaves **how
to sweep it** to Tier-2. The reference shape:

1. **Objective / hypothesis** — the specific question this run answers
   ("confirm the zero-bias feature is a supercurrent"). One run, one question.
2. **Target observable** — what to measure to address it, and what the answer
   looks like ("dV/dI vs (Idc, B⊥); suppression toward a Bc ⇒ SC").
3. **Operating point / scope** — where in parameter space to sit; what's fixed.
4. **Success / escalate criteria** — when the brief is *done*, and when to stop
   and **send back up** to strategic (anomaly, hypothesis looks wrong, can't
   proceed). This is the return edge of the loop — Tier-2 "runs until completion
   *or* something worth sending up."
5. **Depth / rigor** — *how thoroughly*. Usually a qualitative level, not a
   clock (exact hour deadlines exist but are the exception):
   - **quick exploration** — the fastest pass that answers "is there anything
     here worth a real measurement?" Coarse, sparse, single-shot; optimize for
     speed, accept low SNR.
   - **deep investigation** — characterize the feature well enough to support a
     defensible physics conclusion. Sensible resolution, range, and averaging.
     The default working mode.
   - **bulletproof / paper-grade** — publication-quality data and argument:
     high SNR, repeats, controls, reproducibility — survives referee scrutiny.
   The level directly sets tactical execution: point counts, averaging time,
   repeats, control sweeps, coverage. For the tactical layer it's plausibly the
   *highest-signal* field — it changes what "good execution" even means.
6. **Constraints** — validators / safe ranges; safety; what not to touch; an
   occasional hard time or resource cap when one genuinely applies.

What a brief does **not** contain: the exact sweep call. Picking ranges, step
counts, the operating-point refinement, and handling rig quirks (e.g. the
rotator's Beff=0 offset) is Tier-2's job. If the brief writes the sweep, there's
no tactical layer left to evaluate.

A brief is also a vehicle for **live/rig context** the strategic layer holds and
a frozen fixture can't show — e.g. "respect the rotator's calibrated Beff=0
setpoint." This is legitimately how Tier-3 would pass down what it knows; it is
not benchmark leakage (it's input, not the answer key).

## The dimensions we're sweeping

The brief lives in a design space whose dimensions are not the same thing:

- **Autonomy** (how *prescriptive*): from **open** (hypothesis only — Tier-2
  chooses the experiment) to **directive** (experiment named — Tier-2 only
  executes). This controls how much strategic reasoning Tier-2 must still do.
- **Length** (how much *context*): from **short** (one line) to **long** (full
  framing — what's known, what's at stake, what would be convincing). This
  controls how much the agent has to reconstruct vs. is handed.
- **Depth / rigor** (field 5): **quick exploration** → **deep investigation** →
  **bulletproof / paper-grade**. This controls *how thoroughly* Tier-2 executes
  — and likely moves execution more than the other two combined.

Autonomy and length are orthogonal: a brief can be *directive + short* ("run
B vs Idc at the SC point") or *open + long* (pages of context ending in "decide
the best SC test"). We author the **2×2 corners** per frontier so the benchmark
can attribute effects to each axis independently, not just the diagonal — with
**depth held constant** (at *deep investigation*) across all four so it doesn't
confound the grid.

Depth is then **probed separately** on a single anchor (`directive-short`) at all
three levels, rather than exploded into a full 2×2×3. This isolates the rigor
effect cheaply: same experiment, same framing, only the depth level changes.

Reference variants (b1c2 `after-idc-vs-n/briefs/`):
- 2×2 (autonomy × length, depth = deep): `open-short`, `open-long`,
  `directive-short`, `directive-long`.
- depth probe (on `directive-short`): `directive-short-quick`,
  `directive-short` (= deep, the shared anchor), `directive-short-paper`.

### Results — first faithful sweep (2026-06-01, after-idc-vs-n, recipes-ON, N=3)
See `notes/2026-06-01-after-idc-vs-n-lever-sweep.md`. Headlines, which partly
overturned the pre-recipe expectations below:
- **Strategic variance collapsed (21/21 → field sweep).** With production-parity
  context the agent picks the decisive move from *any* altitude, including the
  bare campaign goal. The earlier high variance was a recipes-OFF artifact, so
  **autonomy/length barely discriminated here** — test them on *contested*
  frontiers, not ones good context makes obvious.
- **Depth is the real signal**, and it swung execution exactly as hoped (points
  ~20×, runtime ~30–60×; quick=screen → deep=characterize → paper=lobe-resolved),
  and deeper levels even surfaced a cooldown-drift verify-first check on their own.

### Hypotheses the sweep tests
- **Directive collapses strategic variance.** `directive-*` should converge on
  Isaac's actual move (the field sweep) with low run-to-run spread; `open-*`
  should retain the strategic spread we saw at campaign-goal altitude.
- **Length alone is weaker than autonomy.** `open-long` (rich context, no
  prescription) probably does *not* collapse variance as much as
  `directive-short` — i.e. telling it *what* matters more than telling it *more*.
- **Over-direction has a cost.** Watch whether `directive-long` makes the agent
  *stop catching* the things the open variants caught for free (the magnet
  offset, the trace-overlay plotting limitation, the cooldown drift). If a
  tightly-specified brief suppresses problem-detection, that's the price of low
  autonomy — and a key input to where the sweet spot sits.
- **Depth moves execution most.** Across `directive-short-{quick,deep,paper}`,
  expect the sweep parameters to swing hard — point counts, averaging, range,
  repeats/controls — while the *experiment* stays fixed. If depth barely changes
  the proposed sweep, that's a finding too (the agent isn't internalizing the
  rigor signal, which a real tactical layer must). Observed (early-characterization
  cold start): depth swung the gate-map grid from ~500 to ~11k points context-free,
  and from ~5k (71², ~45 min) to ~40k (201², ~3.5 h) *with* recipe access.
- **Recipe access sets the depth *scale*.** The depth label is relative; what
  "quick" and "deep" cash out to in absolute points/delay/time is anchored by the
  recipe defaults (lever #3 in `benchmark-plan.md`). Run the depth probe with
  recipes ON (the faithful baseline) so the levels mean what they mean in the lab
  — a context-free "quick" is an unrealistic 2-min toy; a recipe-grounded one is
  the real ~45-min gatemap.

## How it plugs into the benchmark

- **Brief as a goal-framing lever.** `hera-replay` will take `--brief <variant>`
  and inject the brief body in place of the campaign-goal framing in the prompt
  (driver change still to wire). Same fixture, same cut, swap the brief → measure
  the altitude effect across N samples.
- **Fixtures are dual-use.** A section-boundary frontier *is* a strategic
  decision point. Hide the next section → "what next?" = **strategic** eval (what
  we built). Reveal the next brief → "execute this" = **tactical** eval. One
  corpus, both layers, depending only on whether the brief is shown.
- **Judging shifts with altitude.** Under an **open** brief, the eval still
  includes *did it choose the right test* (closer to strategic). Under a
  **directive** brief, the eval is *execution quality*: did it land the right
  sweep with sensible parameters, refine the operating point, catch rig issues,
  and escalate when appropriate. The existing
  `ground_truth/<slug>/next_move.md` (the expert's actual sweep + judging
  buckets) serves the directive case directly; open briefs lean more on the
  strategic-match read.

## Authoring briefs in the extract

Cheap, because the campaign already contains them. Each notebook **section
header is a proto-brief** the expert wrote to themselves; the section's sweeps
are the execution. To author a frontier's briefs: take the next section's intent
as the objective, the sweeps Isaac ran as the (hidden) execution ground truth,
and write the 2×2 around it. Put them under `briefs/<slug>/<variant>.md`,
parallel to `ground_truth/<slug>/`.
