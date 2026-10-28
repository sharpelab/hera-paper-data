# Silicon backgate survey

## What
Survey the device's response at multiple Si BG voltages (typically ±10 to ±48 V) to find a working operating point — the Si BG value at which the device sits in the desired carrier-density regime and the lock-in channels show useful signal. Two patterns: (a) discrete gatemaps at a handful of Si BG values, or (b) a systematic 2D sweep with V_Si as the slow axis.

## When
After `gate-current-sanity-check` has blessed safe TG/BG ranges (Cell B committed), when the device's Si BG matters for the science (most rhombohedral-graphene devices) and you don't yet have a known-good V_Si from a prior cooldown. Often interleaved with the first `gatemap` runs rather than run as a strict prerequisite — the survey itself is built out of small gatemaps.

## Why
The Si BG biases the entire substrate, shifting the device's chemical potential globally and changing the screening environment. Picking a wrong V_Si means the (n, D) region of interest may sit outside the (V_tg, V_bg) safe polygon, or the device may be in a depleted/insulating regime that masks features. Sweeping V_Si over a wide range identifies the operating points where the lock-in channels have signal and the gatemaps look clean.

## Recipe
Two flavors:

**Flavor A — discrete gatemaps at multiple V_Si:**
1. Pick 3–5 V_Si values to try (e.g., +20, +10, −10, −20, −30 V; or for thicker Si BG dielectrics, ±40 V).
2. For each V_Si:
   - Build `s = sweep.AsyncStation(mc)`. `s.add_comment('silicon-backgate-survey')` and tag the V_si (`s.add_comment(f'V_si = {V_si}')`). `s.ramp(k_si.volt, V_si); time.sleep(5)`.
   - `fp` temperature, all three gate currents, all lock-in X and P. Plot `k_tg.volt` vs `k_tg.curr` and `'time'` vs `k_bg.curr`.
   - `s.megasweep(k_bg.volt, np.linspace(...), k_tg.volt, np.linspace(...), slow_delay=3, fast_delay=1)` — a small fast (n, D) gatemap. 101×101 is plenty for a survey; full 201×201 only after you've picked a V_Si.
   - Park `k_bg.volt(0); k_tg.volt(0); k_si.volt(0)` between V_Si values.
3. Pick the V_Si whose gatemap shows the clearest features and use it for subsequent science.

**Flavor B — systematic 2D sweep with V_Si as slow axis:**
1. Pick a fixed (V_tg, V_bg) operating point (typically near zero).
2. Build the AsyncStation as in Flavor A. `s.add_comment('silicon-backgate-survey, 2D')` and tag the V_si range and the held (V_tg, V_bg).
3. `s.megasweep(k_si.volt, np.linspace(-40, 40, 41), k_bg.volt, np.linspace(...), slow_delay=5, fast_delay=1)` — Si BG outer, BG inner.
4. Park gates at the end. Visualize as a 2D map of V_si × V_bg; the V_Si values where the device responds are the candidate operating points.
5. Optionally narrow with a follow-up sweep over a tighter V_Si range (e.g. −40 to −20 V) at higher density.

**Flavor C — V_Si stepping with TG sweeps in a Python loop:**
A middle-ground pattern: build the station with the recipe-name `add_comment`, then per-iteration `s.add_comment(f'{i}: V_si = {Vsi}')`, `s.ramp(k_si.volt, Vsi)`, then `s.sweep(k_tg.volt, ...)` forward and back. Uses regular `s.sweep` calls inside a Python `for` loop, with the V_Si index logged to the sweep comments for downstream parsing (recoverable via `comment_to_gates` or a custom tag parser).

**At-field re-validation (flavor, not optional when the campaign runs at
field):** a V_Si chosen at B = 0 can stop being optimal in the
quantum-Hall regime — the Si gate sets the screening environment and the
contact-region doping, and both matter differently once edge transport
carries the signal. Before committing at-field campaign time, repeat a
reduced survey (Flavor B/C shape — V_Si stepped over the candidate
range, density sweeps at each step) **at the campaign field**, and pick
the operating point from that. This is one activity with the at-field
contact re-check (`contact-survey-2t` step 4): the reference campaign
ran Si steps and per-pair contact checks as a single 6 T block, and the
combined Si + contact optimization is what made its at-field data
usable. Schedule both for the same magnet excursion — never a separate
traverse for each.

Whichever flavor: the goal is to identify one or two V_Si values where you'll commit to longer gatemaps and science.

## Examples
- `aaron/RPL_19/20251008_measure.ipynb` cells 41–58 — both flavors in one section. **Cell-range adjustment vs. index** ("cells 41–55"): the natural section runs 41 (`# Initial gatemap` header) through 58 (last 2D Vsi sweep). Cells 45–54 are Flavor A: discrete gatemaps at V_Si = −20, −15, +20 V with mid-section markdown notes ("Trying +20 V going from +1 V down on top gate"; "Just going back to -20 V. I calibrated at 0 V on the top gate..."). Cell 55 marks the sub-section "## sweeping silicon back gate systematically (-40 to 40 V)". Cell 56 is Flavor B (megasweep with `k_si.volt` slow axis, 41 points). Cell 58 narrows to V_Si = −40 to −20 V at higher slow_delay.
- `aaron/RPL_10/241207_measure.ipynb` cells 62–77 — all three flavors. Cells 62–74 ("Changing config a bit" / "Returning to gate maps after rat cleansing") are Flavor A: gatemaps at V_Si = +20, −20 V using mc_2 then mc_3, with config redefinitions and a comment cell ("## Testing out different Si back gates" at cell 66). Cell 76 ("Quick Si back gate testing") is Flavor C: a Python `for` loop over `Vsis = np.linspace(10, -40, 11)`, doing forward+backward TG sweeps at each V_Si with per-iteration `add_comment` tagging. Cell 77 is a follow-up small gatemap at V_Si = −30 V.
- `vti/qingrui/20260601-QC0426-3LGr/measurement.ipynb` cells 103–115 and 123–125 *(our-measurement)* — the VTI shapes. Cells 103–110: the Si gate introduced mid-campaign via a TG–Si map (cell 107; Flavor B with the Si Keithley as one axis) and a 6 T megasweep stepping V_Si = 50/55/60 as the slow axis (cell 110). Cells 123–125: the at-field re-validation — `multimegasweep` blocks stepping V_Si over +50…+100, −50…−100, −25…+25 at 6 T, interleaved with the per-pair contact checks of `contact-survey-2t` (cells 127–140) as one optimization block. Per-run V_Si lives in `measurement_config`, not a campaign constant — read it per run.

## Next
- Default: first measurement campaign begins. The standard first move is `gatemap` at the chosen V_Si (axis-aligned, no cap-ratio dependency); promote to `nD-map` once `cap-ratio-calibration` has blessed the cap ratios.
- **Changing V_Si moves the CNP intercept**: re-run `cnp-and-dline-calibration` at the committed operating point before trusting any previously designed D-lines (that recipe's When already lists this trigger; this closes the loop from the other side).
- Campaign runs at field: the at-field re-validation flavor above, scheduled with `contact-survey-2t` step 4 on the same magnet excursion.
- If no V_Si gave clean signal: revisit the `gate-current-sanity-check` validators (a too-narrow safe range can miss the device's operating window) and consider whether the device may have a wiring problem masquerading as a gating problem.
