# Gate range finding

*Base recipe, rig-agnostic (STYLE rule 11): method and instrument-class
conditionals only — the rig prompt, rig variant, device card, and session
brief supply the sweep stack, driver names, and numbers. Rig variants
(`gate-range-finding-<rig>.md`, STYLE rule 13) take precedence on their
rig. Relation to `gate-current-sanity-check`: that recipe is the same
core activity in toploader-native form and remains the reference
implementation there (it carries the live-tested failure-mode catalog);
this base exists so rigs whose hardware changes the procedure's *shape*
can hang variants off it, and adds the four-corners stress check the
toploader recipe predates.*

## What
Establish the safe voltage range of every active gate for the cooldown,
by iterative endpoint-walking sweeps a human refines between runs, then
verify the combined-gate *box* at its corners, then commit the observed
ranges as hard validators. Three outputs: (1) confirmed device liveness
on the transport channels, (2) a leakage-onset (or stress-tested ceiling)
per gate per polarity, (3) committed validators mirrored to the device
card — the durable record that gates every subsequent recipe.

## When
Once per cooldown, after instrument init and the measurement-config
block, before any survey map or science measurement. Again after thermal
cycling or physical intervention (reseating contacts, swapping a gate
source, repatching).

**Precondition — device ungrounded.** A device tied to ground at any
contact gives flat-nonzero, all-channels-identical lock-in readouts that
mimic signal (see the failure-mode catalog in
`gate-current-sanity-check` — it applies to this recipe wholesale).
Confirm before the first sweep.

**Precondition — measurement_config tells the truth.** Before any
range-finding run, `measurement_config` must record which physical
instrument drives which gate *for this run*. Channel labels follow
instruments, not gates: any repatch or re-cable makes every
`<label>.volt` column a lie unless the config (comments and channel
entries) is updated in the same cell that uses the new wiring. The rule
is universal, not a repatch corner case: **a channel label alone is not
evidence of what it drove (labels persist across rewiring); the per-run
`measurement_config` is the truth surface, and it is only the truth if
this recipe's discipline keeps it so.** The war story is in Examples.

## Why
A device that doesn't pass current with gates parked at zero, or a gate
that leaks at small voltage, will not give a clean survey map — find
that in minutes, save hours. Beyond liveness, this is where cooldown-wide
validators get **set from observed behavior** rather than guessed from
geometry, and validators set this way are the only durable "I confirmed
this range is safe": they bound every later sweep, and the device-card
mirror survives kernel resets and session handoffs. The four-corners
step exists because per-gate sweeps hold the other gates at zero — the
corner combinations maximize total field across shared dielectrics and
cross-gate paths, and a box blessed on its axes alone can still break
down at its corners.

## Recipe

Wall-clock: each iteration is a 1D sweep of 51–101 points at ~1 s/point
*(heuristic, both rigs to date; calibrate from this session's first
sweep rather than inheriting — STYLE rule 12)* — one to two minutes.
The whole procedure, both polarities of two or three gates plus
corners, is tens of minutes. Price it that way and never let it be
skipped to save time; it protects the hours-scale maps that follow.

### Step 1 — per-gate, per-polarity endpoint walk

For each active gate, one polarity at a time, all other gates parked
at 0:

1. Build the station per the rig's sweep stack;
   `s.add_comment('gate-range-finding')` (or the rig variant's slug)
   first, then a structured comment naming the gate and the leg
   (`'gate: <name>, leg: 0 -> +1.0 V'`).
2. Set the leakage-readback channel to its highest-SNR integration mode
   for the duration of the search (reset in step 3). Which channel that
   is depends on instrument class:
   - **Gate source with pA-capable current readback** (the common case:
     a source-measure unit driving the gate): read the source's own
     current at high integration. The toploader implementation of
     exactly this branch is `gate-current-sanity-check`.
   - **Gate source without usable current readback** (a pure voltage
     source, or an SMU whose current floor is too noisy at pA): the
     procedure's shape changes — see the rig variant. Do not substitute
     "watch the transport channels and hope": transport responds to
     gating whether or not the dielectric is leaking.
3. Record per point: temperature, every gate's voltage and (where it
   exists) current, every lock-in channel. Live-plot the swept gate's
   leakage current and at least one transport channel.
4. Sweep from 0 to a modest endpoint (a volt-scale first leg, 51–101
   points, ~1 s delay). Wrap the sweep so an interrupt still parks the
   gate (`try/finally` ramp-to-zero).
5. Read the live plot: transport channels alive and smoothly varying;
   swept gate's leakage at the readback floor; parked gates' leakage
   flat (a parked gate tracking the swept gate is a cross-gate path —
   stop and run `gate-leakage-survey`).
6. Iterate by copying the cell — one cell per run, so the history of
   the search stays in the notebook — and walking the endpoint outward
   until either:
   - **leakage onset**: the gate current rolls off the floor toward nA.
     Optionally bracket it with a fine-stepped short sweep just below
     the onset (a 0.1 V window at 51 points localizes it cheaply), then
     back the endpoint off to a value safely below; that is the safe
     limit for this polarity. Or
   - **geometry ceiling**: ≈ ±0.5 V/nm × dielectric thickness for
     metal gates (heuristic, multi-device toploader experience; guards
     against a masked readback silently passing breakdown) — do not
     walk past it even if the leakage channel stays quiet, and treat
     "quiet all the way to the ceiling" as the ceiling being the limit,
     not as evidence of a larger safe range.
7. **Operator fast-path — watch-and-interrupt** *(our-practice, Isaac's
   toploader idiom)*: an experienced operator may replace the
   endpoint walk with one long leg watched live, interrupting the
   kernel at the first sign of leakage onset / nonlinearity. The
   recipe supports this: the step-4 `try/finally` parks the gate on
   interrupt, the partial run lands on disk readable
   (`interrupted: true`), and the follow-up is the same fine
   bracketing sweep below the observed onset. Trade-offs: one sweep
   instead of N, but onset localization inherits human reaction
   latency — back the limit off accordingly — and the leg demands
   unbroken attention. Under an agent-driven session this is natural
   division of labor: the agent proposes the guarded long leg,
   early interruption is the operator's prerogative (never the
   agent's to request mid-cell), and the agent brackets from the
   partial data.
8. Repeat for the other polarity, then the next gate.

### Step 2 — four-corners stress check

After every gate has a chosen range, verify the box. The hazard is the
inter-gate voltage across the shared dielectric, so the corners split by
polarity, not by per-gate onset:

1. The two **like-polarity** corners (+/+, −/−) are **safe** (small
   inter-gate difference); the two **opposite-polarity** corners (+/−,
   −/+) are **dangerous** (max voltage across the shared dielectric).
2. Park **both** gates at a safe (like-polarity) corner; settle long
   enough for the slower of the two sources.
3. Sweep one gate from the safe corner **toward** a dangerous corner — a
   monotonic approach into the suspect corner, watching the same channels
   as step 1 and now also the *parked* gate's leakage (it carries the
   cross-gate signal); abort on onset.
4. Repeat for the **other** dangerous corner: from the **same safe
   corner**, sweep the other gate toward it — same monotonic approach,
   watching both channels' leakage (incl. the parked gate's); abort on
   onset. Four corners, a handful of cheap 1D sweeps, minutes total.
5. Read: any corner showing leakage onset that the axis sweeps didn't
   show shrinks the box (back off the endpoint that participates in
   that corner) — or, if the onset moves substantially as the parked
   gate steps, the safe region is a polygon, not a box: run
   `gate-leakage-survey` and inscribe the validators inside its result.
   For devices with more than two active gates, corner the two
   strongest-coupled gates and spot-check the third at its extremes —
   the full 2^N corner set is rarely worth it (heuristic; n = small,
   from dual-gate-plus-Si devices where the Si couples weakly). Decide
   coupling strength from the gate-stack geometry in the device card
   (shared dielectric, overlap area, dielectric thickness); if the
   card doesn't settle it, ask the operator rather than guessing.

A readback-quality caveat travels with this step: the corner check is
**onset-grade only where the parked and swept gates both have pA-capable
readback**; with a noisy channel in the loop it degrades to a
gross-breakdown check, and the pA-grade confidence for the box interior
comes from step 1 plus live leakage plots on the first survey map. Say
which grade you got in the closing comment.

### Step 3 — commit validators (HERA handshake)

After both polarities of every gate have confirmed limits and the
corners pass:

1. Commit hard validators on every gate parameter **as actually wired
   for the rest of the cooldown** — attach them to the parameter object
   that sweep cells will use, not to a repatch-era stand-in
   (`gate.vals = validators.Numbers(lo, hi)` in qcodes terms).
2. Reset the leakage channels' integration mode to the rig's standard.
3. Print the committed validators; mirror the numbers to the device
   card — the card is the durable cross-session record, and the rig
   prompt's SAFETIES gate compares against it numerically.

When an agent is proposing the cells: it provides the sweep cell and
the validator cell together, but **does not propose any subsequent
recipe step until the human reports the discovered ranges and the
validator cell has run**. Asking for the limits is the explicit
handshake; the human is the gate.

## Examples

- `vti/qingrui/20260601-QC0426-3LGr/measurement.ipynb` cells 36–48
  *(our-measurement)* — step 1 in its rawest form: 13 sequential 1D
  back-gate sweeps walking 0 → +5 V in half-volt legs then back through
  0 → −5 V, gate-current integration raised for the whole search
  (cell 34), one cell per leg. Outcome recorded as a markdown header
  ("choose [−5, 4.8] V for BG", cell 50). Cells 52–61 are the top-gate
  walk on the same device via that rig's repatch idiom — see
  `gate-range-finding-vti` — ending with a fine 0.1 V bracketing sweep
  (cell 61) just below the negative-side onset; header "choose
  [−6.5, +7.5] V for TG" (cell 62).
- Same notebook, cells 64–80 *(our-measurement)* — the four-corners
  source: "check four corners". Park one gate at an endpoint, sweep the
  other to each of its endpoints, all four combinations (cells 65–75),
  then integration reset (cell 77). **This block is also the
  measurement_config war story**: by cell 66 the "k_bg"-labeled
  Keithley was physically driving the *top* gate and the Si-labeled
  Keithley held the *back*-gate corner values — every channel label in
  those runs lies, and the only truthful record is the config comment
  ("push top gate with k_bg with BG at -5V (changed cable)"). Reading
  those runs by column name silently swaps the gate axes. Hence the
  precondition above.
- `isaac/b1c2_toploader/20260505_measure.ipynb` cells 17–27
  *(our-measurement)* — the toploader branch of step 1 live, including
  the grounded-device failure mode; documented as
  `gate-current-sanity-check`'s worked example, with the failure-mode
  catalog this recipe leans on.

## Next

- Default: the cooldown's first survey map (`gatemap`), or the rig's
  remaining device-init recipes (`silicon-backgate-survey` where the
  device has a global back gate), now bounded by committed validators.
- Leakage anomalies anywhere above — cross-gate tracking, corner-only
  onset, onset that moves with the parked gate — `gate-leakage-survey`
  before any long map.
- Validator cell not yet run: no advance; the handshake in step 3 is
  the gate.
