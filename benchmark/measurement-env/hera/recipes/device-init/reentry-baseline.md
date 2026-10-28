# Re-entry baseline

*Base recipe, rig-agnostic. This is the recipe form of the rig prompts'
precheck "gate C": it exists so re-entry runs carry their own slug and a
defined comparison procedure instead of being improvised under borrowed
slugs (see Examples).*

## What
Reproduce the **designated** cheap reference measurements at the start
of a session that re-enters an already-characterized cooldown, and
compare them quantitatively against the designated reference traces.
Output: an explicit verdict — *device survived the handover unchanged*,
or *stop-and-report* with the specific disagreement — before any
campaign time is committed. Minutes of sweeps protecting hours.

## When
- First measurement activity of any session on a device loaded and
  characterized in a previous session (fresh measurement directory, new
  operator or agent, days idle — any handover).
- A reduced re-run after mid-session interventions: thermal excursion,
  rewiring, instrument swap, anything that re-opens the question "is
  this still the same device?"
- Not applicable on a first session of a cooldown — that's the
  device-init path (`gate-range-finding` onward), which *produces* the
  references this recipe later consumes.

**Precondition — designated references only.** The session brief or
device card names the reference runs/pack this recipe compares against.
If nothing is designated, ask the operator to designate by name — do
**not** trawl prior campaign directories for substitutes: other
sessions' notebooks carry their authors' *conclusions*, and when the
campaign asks for an independent read of the data, those conclusions
are contamination, not context. (The blinding rule is campaign-design
policy; it lives here as recipe text because the trawling temptation
arises exactly at this step.)

## Why
Devices change across handovers — thermal-cycle drift, contact aging,
gate stress, static discharge — and a campaign measured on a changed
device is misattributed at best. The baseline's cost asymmetry is
extreme: 1D sweeps at zero field, minutes each, against multi-hour maps
whose interpretation silently inherits whatever changed. The slug also
matters in its own right: re-entry runs tagged with their own
`add_comment` slug are findable as a class across sessions, which is
what lets a later session ask "what did re-entry look like last time?"

## Recipe

1. **Read the references first.** Load the designated reference data
   from disk; extract the comparison targets before sweeping: resistance
   scale at named points, feature positions, trace shape, leakage/drain
   floor — and the conditions they were taken under (`measurement_config`,
   operating points, field, excitation).
2. **Re-create the conditions.** Same sweep axis and range, same
   excitation, same contact configuration, same operating points (e.g.
   a global back gate at the reference value, field at the reference
   value — usually zero), and **temperature at the reference value** —
   re-entry after idle days is exactly when base T can sit differently,
   and resistance at a charge-neutrality point is steep in T; read the
   thermometry and compare against the reference's recorded T before
   sweeping. Any deviation you can't avoid gets named in the run's
   structured comment; an unnamed deviation invalidates the comparison,
   not the device.
3. **Run the designated checks.** The canonical pair (the card may
   designate others):
   - a 1D gate-response sweep — qualitative: smoothness, leakage floor,
     feature visibility. Useful even with no reference trace; judged on
     its own terms.
   - a short cut through a known feature with a designated reference
     trace — quantitative; this is the check that carries the verdict.
   Tag every run `s.add_comment('reentry-baseline')` plus a structured
   comment naming the reference being reproduced.
4. **Compare quantitatively** — four checks, numbers not eyeball:
   - **resistance scale**: ratio to reference at matched points;
   - **feature positions**: shift of CNP/peak/dip locations along the
     swept axis;
   - **trace shape**: overlay; same feature set, same ordering — a
     missing or extra feature is a shape fail even at matched scale;
   - **leakage / drain-current floor**: at or below the reference's.
   Pass bands come from the designated pack's own README where it has
   one; otherwise propose bands from the reference's noise/repeatability
   and say so (heuristic, stated — not silent judgment).
5. **Verdict, then the handshake.** State pass/fail per check and the
   overall call in the notebook. Disagreement is **stop-and-report** —
   surface the specific check, magnitude, and candidate explanations,
   and wait; it is the operator's call whether the session recalibrates,
   investigates, or accepts the change as the new baseline. Do not
   silently recalibrate to the new behavior: an accepted change must be
   recorded (device card + a structured comment), because it becomes the
   *next* session's reference.

## Examples

- `zack/20260610-QC0426-hera-live` runs 0–2 *(our-measurement)* — the
  motivating gap: the first live VTI session ran exactly this procedure
  at gate C (gate-response sweep + density-cut reproduction against a
  curated `./reference/` pack with a four-check README) but had no slug
  for it; the runs are tagged under `gate-current-sanity-check` and
  `trilayer-stacking-id`, and the session notes flagged the missing
  recipe. This file is that flag's resolution.
- QC0426 device card, gate-C section *(our-measurement, mechanical)* —
  the reference-pack convention, including its correction history: the
  first designated references were bad picks (cable-swapped sweeps; a
  cut taken at 6 T) and were superseded by a curated pack on the session
  wiring at B = 0. Lesson encoded in step 2: a reference is only valid
  for comparison under reproduced conditions, and reference *selection*
  is part of campaign design — a bad pick fails the baseline spuriously.

## Next

- **Pass**: the campaign's first recommended recipe; the verdict line in
  the notebook is the record that gate C closed.
- **Fail / changed**: stop-and-report (step 5). Depending on the
  operator's ruling, the usual follow-ups are `gate-range-finding`
  (validator re-verification if gate behavior moved) or
  `gate-leakage-survey` (if the leakage floor moved); an accepted change
  updates the device card and the designated references.
- **No references designated and none exist**: this was a first session
  in disguise — switch to the device-init sequence.
