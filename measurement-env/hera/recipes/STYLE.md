# Recipe style guide — epistemics for agent-executed science

*How to write recipes (especially `investigations/`) so that an agent
executing them literally is also executing them **calibratedly**. A recipe
is a program: an unstated validity condition is an unhandled branch, and
the agent will take it. Conservative rounding miscalibrates too — a rule
rounded toward caution makes the agent discard evidence it should weigh
(see burn log #1).*

## Rules

### 1. Rules carry their validity domain, inline

Never a bare binary ("X does not count", "X ⇒ Y"). The canonical form:

> **X alone is not evidence (because C); X together with Z is, weakening
> as W.**

The condition lives **at the rule**, in the same sentence or bullet — not
in a caveats appendix. Agents read locally; a caveat two sections away is
a caveat that doesn't execute.

### 2. Distinguish the three evidence axes

**Presence / pattern / magnitude.** Most miscalibration — in both
directions — comes from collapsing these:

- *presence*: the feature exists ("there are crossings")
- *pattern*: its structure matches a model ("a parallel-chain family
  co-locating with predicted ML×BL loci")
- *magnitude*: its size is in the predicted regime ("MΩ-insulating, not
  10 kΩ")

A rule about one axis must not be worded so it consumes the others
(burn log #1: a presence rule worded as a blanket rule discarded
pattern evidence).

### 3. Every discriminator names its confounds

For each "signal X ⇒ lean Y" rule, state what *else* produces X, next to
the rule. Standing examples in this corpus: series-path mosaic for
CNP-vs-D gap growth (any pair gaps if gappable domains span the channel);
two-domain beat fringes and grid aliasing for curved fan arcs. A
discriminator without a confounds list reads as stronger than it is.

### 4. Absence claims cite resolvability

"We did not see X" counts only with "and X was resolvable here because R"
— reference conditions (temperature, mobility/onset field, grid density)
against a stated benchmark. The resolution-ladder pattern
(`docs/papers/ncomms14518/paper.md#resolution-ladder`) is the house
implementation; replicate it for new investigations.

### 5. Provenance flags on factual claims

Mark each load-bearing claim as one of: **paper-data** (measured in the
cited reference), **citation** (claimed in the reference's citation
network, not its data), **our-measurement** (this lab, cite run ids),
**our-model** (this lab's validated forward model — cite the tool, and note
what gated it), **heuristic** (rule of thumb; state sample size — "n = 1
device" is common and fine, but say it). Unflagged claims read as paper-data.

### 6. Standardized strength vocabulary

Use exactly these words for evidence weight, and define calls with them:
**decisive · strong · weak · consistent-with · uninformative**. The
output contract should echo the same scale so calls are comparable
across sessions and recipes. "Supports", "suggests", "indicates" are
banned as load-bearing terms — they hide the weight.

### 7. Thresholds are labeled heuristics

Numeric triggers ("≥ 2 parallel chains", "rescale outside 0.8–1.2 is a
red flag") get a provenance flag (rule 5) and, where possible, the
failure mode they guard against. An unlabeled threshold gets treated as
physics.

### 8. "It depends" is a legal instruction

When a rule's condition is unmet, the recipe should say what *question*
to answer next, not force a branch. A decision ladder may bottom out in
"escalate to the operator with these specific alternatives" — that is an
outcome, not a gap.

### 9. Output contracts make hedging mandatory

Every investigation ends with a structured call: per-region/per-channel
verdicts, evidence list with coordinates and references, confidence with
named hedges, what-would-firm-it, and the explicit statement that a
reasoned "cannot tell" is success while an unevidenced confident call is
a protocol violation. (See `trilayer-stacking-id.md` step 5 for the
house form.)

### 10. Burn log — recipes are calibration instruments

When a rule misleads a live agent, fix the rule **and** record the burn
here, citing the session. Rules that have never been executed by an
agent are untested code.

### 11. Recipes are rig- and device-agnostic

Recipe steps contain **method** and **instrument-class conditionals**
("if the field source is ramp-rate-limited and the set call blocks,
then…") — never rig constants, driver names, or device numbers. The rig
prompt, device card, and session brief supply the parameters that
resolve the conditionals. Device- or rig-specific numbers are allowed
only in Examples, provenance-tagged (rule 5) — **except operating
setpoints** (gate operating points, screening voltages): those are
calibration data; Examples cite where the value is recorded
(`measurement_config`, notebook index, device card), never quote it.
An operational default quoted in an agent-visible file becomes an
inherited choice (burn log #5). Test: *could this recipe run on a
different fridge with only the device card and brief swapped?*

**Variant layer**: when instrument-class conditionals can't carry the
rig's reality — the rig changes the *procedure's shape*, not just its
parameters (e.g. a gate source with no leakage readback forces a
repatch workflow) — write a rig **variant** (`<base>-<rig>.md`, rule
13) instead of bloating the base with rig prose. Line test:
*parameters* change → conditional in the base; *procedure shape*
changes → variant file. Device-specific content (a particular flake's
numbers or wiring) never becomes a recipe at all — that lives in the
device card and `templates/<device>/`.

### 12. Feasibility-first: design-time guards beat post-hoc verification

**Feasibility-first** is the general tenet, and it governs *every*
measurement: before committing fridge time — especially to a long sweep —
work out **(1)** the **expected signature** (the specific feature:
frequency, gap, peak position, magnitude), **(2)** whether it is
**resolvable** on this apparatus (field / temperature / sensitivity
envelope), and **(3)** the **data density** needed to see it (field steps,
oscillation periods, 1/B record length, n-spacing). *Only then* spend the
time. Investigations **reference this rule** rather than restating it; where
the discriminator is a small signal, the feasibility pass is load-bearing,
not a formality (worked example: the FS-count Step 2,
`investigations/trilayer-stacking-fs-count.md`).

The sampling corner of this is mandatory and concrete:
Sampling/Nyquist checks (every swept axis), dynamic-range checks, and
the full cost model belong at **sweep-design time**. Verify-section
robustness tests confirm a sound design; they cannot rescue an
undersampled one — a fan that fails Nyquist in the claim window is
uninformative there, re-measure. Corollary: timing/overhead constants
are **calibrated from the session's own early sweeps**, not inherited;
an uncalibrated constant in a brief is a bug with false authority, and
the agent should treat it as a prior to check, not a fact.
**Extension to briefs**: every logistics number in a session brief
carries an honesty marker — `[measured: run N, date]` or `[assumed]` —
so the agent knows which figures are priors to re-derive (burn log #2).
**Settling floor**: a swept-point dwell has a floor near the
lock-in/filter time constant (`dwell ≳ k·τ`; k ≈ 5 at 6 dB/oct, 7–10 at
24 dB/oct) — below it the reading lags the true value. Derive the dwell
from the *measured* τ by default (read it before pricing; bring-up
records it so it lands in metadata) rather than a round number — the
same discipline as not inheriting a timing constant. The floor can be
bent judiciously — only when the lag is benign for the quantity
extracted: a uniform lag merely offsets a *read*-axis slope-fit's
intercept, and a smooth high-SNR signal tolerates some — but on a *fast*
axis feeding a per-column transform (a fan's FFT) it suppresses the
high-frequency tones. What's not OK is an *unexamined* round-number dwell
on an unknown τ. (burn log #6, #8)

### 13. Variants declare base, deltas, reasons, obsolescence

A rig variant opens by naming its **base recipe** and listing exactly
which steps it overrides, each with the **rig fact that forces the
override** ("DC205 has no leakage readback ⇒ step 2 becomes the
repatch workflow"). It never restates base content it doesn't change —
readers hold base + deltas, not two diverging copies. It ends with its
**obsolescence condition**: the hardware/driver change that would
delete it (e.g. a switch matrix obsoletes a repatch idiom) — variants
are workarounds with an expiry, not permanent forks. On their rig,
variants take precedence over their base (rig prompts encode this).

### 14. Extraction-sensitive claims are forks, not refinement targets

When a quantitative claim **flips under extraction-parameter changes**
(window, detrend order, fit range, threshold), stop refining and report
the **fork**: the robust finding, the parameter-dependent finding, and
the **deciding measurement** that would resolve it. A third extraction
scheme is not evidence — it's a third vote in an electorate you
invented. Separate what survives all reasonable parameter choices from
what doesn't, and price the measurement that settles it.

### 16. Load-bearing steps produce an output, not advice

An instruction an agent can satisfy by *acknowledging* it — "estimate the
cost", "consider the worst corner", "flag it to the operator" — is an escape
hatch, and under token pressure the agent takes it. A check that must hold:

- **Binding, not advisory** — demand a required artifact ("compute `N_B`,
  `N_n`, wall-clock; propose exactly one design"), not "estimate / consider /
  flag".
- **Computed, not eyeballed** — if a function yields the quantity, call it
  (`B_lo = sdh_onset(...)`); eyeballed quantities run biased and high-variance.
- **Forceful — keep the forcing** — the "do X, *not* Y, because Y fails"
  warning is the mechanism, not padding; trimming it to a bare formula re-opens
  the escape. (This rule fights the terse instinct: for a binding gate the
  forcing clause earns its tokens.)

Provenance [our-measurement, offline replay, n = 3 each]: the same fan cost
gate, phrased advisory → 13–35 h proposed sweeps; binding + computed + forceful
→ 3–7 h; trimming the forcing back out → 14–22 h.

### 17. Model windows clip claims, never sweeps

An interpretation-layer limit — a forward model's validity window, an
overlay's domain (e.g. one carrier sign only), an analysis tool's grid
edge — states where the *read* is quantitative, not what to *acquire*.
Acquisition design maximizes the measured record within hardware, safety,
and cost limits (rule 12 prices it); the model's window then bounds the
overlay, stated in the read. A sweep clamped to a model window pays
twice: the out-of-window record is lost outright, and — because record
quality (tone separation, δF, onset) improves with range — the
*in-window* claim degrades too. Cost is the legitimate cap ("range past
what the claim needs is just cost"); "the model can't interpret there"
is not. Test: would the extra range improve the measured record for the
in-window claim, at acceptable cost? Then take it, and flag the
overlay's domain in the read. (burn log #9)

## Burn log

1. **2026-06-11, QC0426 live session** (`trilayer-stacking-id`): the
   step-4 rule "crossings at finite D no longer count as ABA evidence"
   — written conservatively to prevent overconfidence — caused HERA to
   discard the chain hunt at D = +0.25 entirely ("this run informs gap
   physics, not the chain hunt"). The physics: crossing *presence* at
   finite D is indeed not ABA evidence (Lee et al.), but a chain
   *pattern* matching the ML×BL model loci still is, weakening with
   |D|. Fixed by restating per rules 1–2. Lesson: rounding a
   conditional rule toward caution miscalibrates exactly as badly as
   rounding it toward confidence.

2. **2026-06-10/11, QC0426 live session** (`landau-fan` +
   session brief): iteration-1 fan was B-axis aliased (0.25 T rows vs
   ~0.29 T in-window SdH period) — blocky texture, arc evidence
   discounted; recovered by the overnight 0.05 T fan. Failure chain
   spanned three documents: the brief carried a toploader-derived
   "~30 s/row" (measured: 278 s/row, ramp-limited on a blocking
   magnet), the agent sized a coarse-B fan to the mispriced budget, and
   no design-time Nyquist guard existed to catch it. Fixed by the
   landau-fan grid-design check + full cost model and rules 11–12.
   Lesson: a wrong constant with false authority plus a missing design
   guard compound; agnostic recipes with instrument-class conditionals
   force the agent to resolve parameters against the actual rig.

3. **2026-06-10, QC0426 live session** (run-5 SdH-FFT analysis): three
   successive f_low-extraction schemes gave conflicting slope signs
   before the agent stepped back and separated robust findings (two
   frequency scales, f₁+f₂=f_tot) from window-dependent ones (f_low's
   n-dependence). The agent self-diagnosed the spiral in its session
   notes; rule 14 canonizes its own lesson. Lesson: refinement loops on
   extraction-sensitive quantities consume session time and manufacture
   confidence — the fork report + deciding measurement is the correct
   terminal state.

4. **2026-06-10/11, QC0426 live session** (`trilayer-stacking-id`,
   post-mortem 06-12): run-4's vertical candidate came from a 4-row /
   0.25 T window — a dispersing minimum (true slope-ν ≈ 5.1 at fine
   rows) read as "non-dispersing". No rule barred a dispersion claim
   from a window that cannot resolve dispersion; the session
   adjudicated it correctly (anomaly, not evidence) but retiring the
   candidate cost a queued measurement. Fixed by the step-3 dispersion
   floor (≥ ~8 B-rows spanning ≥ 1.5 T, else "dispersion
   undetermined"). Lesson: a classifier without a stated resolution
   floor manufactures candidates from coarse data.

5. **2026-06-10, QC0426 live session** (round-2 device card + brief): an
   operating setpoint — Si = +50 V — quoted in an agent-visible file was
   inherited verbatim as the screening default rather than chosen or
   re-derived; the provenance trace shows it propagating as a choice the
   agent never made. Recurred 2026-06-14 in the same class — "round 2" /
   "replication" framing baked into the deployed templates built to fix
   this very leak (the campaign frame is itself an operational default).
   Fixed by rule 11's setpoint exception and the blinding conventions
   (`hera/blinding.md`). Lesson: operational defaults are information; an
   agent-visible file that quotes one makes the choice for the agent.

6. **2026-06-14, QC0426 live session** (`contact-survey-2t` + measure
   kit): the survey dwell was set to a round `SURVEY_DELAY = 0.5 s` to
   match the scout, not derived from the lock-in time constant; the
   SR830 τ was front-panel-set, unset by the kit, and stored `None` in
   run metadata, so the dwell-vs-τ relationship was implicit and
   unchecked (operator flagged it). Fixed by rule 12's settling floor +
   the VTI rig-card lock-in note + a bring-up τ-record step. Lesson:
   derive the dwell from the measured τ rather than a round number; the
   floor can be bent knowingly on a smooth signal, but an unexamined
   dwell on an unknown τ is a latent bias no later analysis can audit.

7. **2026-06-19, QC0426 .3 session** (`landau-fan` step 1): the electron
   fan's fixed sensitivity (1e-5) was sized for the metallic SdH region off
   the spot-check R-scale (n = 5e12, ≤ 171 Ω); the fan reached n = 1e12 where
   R ∝ 1/n × MR rails > 550 Ω, clipping 17% of the map — the n ≲ 2e12 high-B
   region, i.e. the bottom of the labeling band the fan exists to resolve.
   HERA predicted the clip and accepted it as an amplitude trade,
   mis-scoping the expendable region. Fixed by the step-1 worst-corner
   dynamic-range guard + the clipping-vs-streak Next item. Lesson: a
   fixed-sens 2D fan sizes to R(n_min, B_max), not the metallic region;
   clipping is FFT-distorting, and the design-time dynamic-range guard (rule
   12) is the sibling of the Nyquist guard (burn #2) — omitting it fails the
   same way.

8. **2026-06-19, QC0426 .3 session** (`landau-fan` fast_delay): the fan's
   fast-axis dwell was shaved as a benign "amplitude-for-time" trade, on the
   rule-12 license that a uniform lag only shifts an intercept. But the fast
   axis feeds a per-column FFT, where the lag suppresses the high-frequency
   tones — it gutted the stacking discriminator the fan existed to read, and
   only the full-settling spot checks carried it. Severity scaled with the
   coarse n-sampling, not the dwell alone. Fixed by rule-12's fast-axis
   carve-out + the step-7 note. Lesson: the intercept-only license is for 1D
   slope extraction; on a fan's fast axis under-settling costs the high-F
   tones, and density — not just dwell — buys it back.

9. **2026-07-14.2 → 16, QC0426 VTI sessions** (`trilayer-stacking-fs-count`
   + `landau-fan` + brief): the FS-count model's numerical clamp
   (|n| ≤ 3.5e12, electron-only) had been quoted onto agent-visible
   surfaces as "validity", and the agent designed *acquisition* to it —
   spot checks at the clamp, a hole-side fan stopped at −3.5e12 with the
   gate range reaching ±6.4e12 — halving the fan's usable record and
   leaving the top tone unresolved; the density/side choices also defeated
   the overlay the clamp belonged to. PI review traced four complaints to
   this one root. Fixed by the quote deletions + model extension
   (2026-07-18) and rule 17. Lesson: a tool limit written where the agent
   can read it becomes a design constraint; the window clips the claim,
   not the sweep.
