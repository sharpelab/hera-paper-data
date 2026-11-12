# Two-terminal contact survey

*Base recipe, rig-agnostic. Switching mechanics are an instrument-class
conditional (switch matrix vs manual re-wiring) inside one procedure —
the loop's shape is the same; only who moves the cables differs. On a
rig with a switch matrix, `drivers.contact_mux.ContactMux` is the house
interface, and the hard precondition for the automated flavor is that
**the device card records the mux as live for this cooldown** (validated
address + calibrated `settle_s`).*

## What
Per-contact-pair two-terminal characterization under identical
conditions: for each candidate pair, a short density sweep along the
calibrated CNP/D-line reading the drive current's gate response. Output:
a ranked contact table (pair → resistance scale, alive / high-R / dead,
response shape), bad contacts *localized* by shared-contact comparison,
and the chosen four-terminal configuration(s) for the campaign — all
written to the device card with run ids. Two flavors: the B = 0
baseline survey, and an at-field re-check (contacts re-rank in the
quantum-Hall regime).

## When
- After `cnp-and-dline-calibration` and before committing to a 4T
  configuration: the survey sweeps along the calibrated D-line, which is
  what makes per-pair curves comparable, and the 4T choice is its
  product.
- **At-field flavor before any long at-field measurement**: a contact
  that couples fine at B = 0 can decouple in the QH regime (edge-state
  geometry, contact doping) — re-rank at the campaign field before
  pricing a fan on it.
- Mid-campaign, when a voltage channel goes flat or noisy: re-run the
  pairs sharing its contacts to localize.

**Precondition — per-run contact truth.** Every run's
`measurement_config` records the pair actually measured (the survey is
useless if its metadata can't be read back later). With a switch matrix
that's `mux.mc_fragment()` merged per run; manually it's the
rewrite-config-in-the-same-cell discipline (`gate-range-finding`'s
truth precondition).

## Why
A fan on a bad pair wastes hours; the survey costs minutes per pair. 2T
comes before 4T diagnostics because it needs no working voltage probes
and the pairwise structure localizes faults: a dead *pair* is ambiguous,
but a contact that kills every pair it appears in is identified —
provided the candidate set was chosen so each contact appears in at
least two pairs. The at-field flavor exists because the reference
campaign found it necessary (the QH regime re-ranks contacts) and
because at-field magnet time is expensive exactly when a dead channel is
discovered mid-fan.

## Recipe

**Step 0 — candidate set and price.** Enumerate from the device card's
contact map. All pairs is N(N−1)/2 — usually too many; pick a spanning
set where **every contact appears in ≥ 2 pairs** (attributability) and
the likely source/drain candidates appear in more. Price the loop:
N_pairs × (sweep time + switching overhead) — switching overhead is
seconds with a mux (the `settle_s` it's configured with), minutes
plus operator attention manually. State the number before starting.

**Step 1 — freeze the conditions.** Gates follow the calibrated D-line
over the working n-window; screening gate at the campaign operating
point; excitation at or below the device-card ceiling; lock-in
sensitivity fixed (not autoranged — comparability across pairs is the
product). Same conditions for every pair, including the at-field
re-check (same line, same window, field added). Set the per-point
**dwell from the lock-in time constant** (`dwell ≳ k·τ`, STYLE rule 12
settling floor — read `srN.time_constant()` first) rather than a round
number; an unexamined dwell short of k·τ lets settling lag leak into the
cross-pair comparison (bend it knowingly only on a clean signal).

**Step 2 — the loop.** Per pair: configure, record truth, sweep.
- **Switch-matrix flavor**: one cell can loop the whole set —
  `mux.select({...pair routing...})`, rebuild the station with
  `meas_config | mux.mc_fragment()`, `s.add_comment('contact-survey-2t')`
  plus a structured comment naming the pair, then the short n-sweep.
  **One run per pair**: never sweep contact-configuration as a fast
  axis for survey data — per-run `measurement_config` is the truth
  surface and cannot carry per-point wiring (the config-as-sweep-axis
  trick is legitimate only for switch-transient tests, where the
  "data" is the transient itself).
- **Manual flavor**: one cell per pair (copy-and-edit, the search
  history stays in the notebook); the operator re-wires at the rack and
  the same cell rewrites `measurement_config` before sweeping.
  **Re-wire hygiene: zero the excitation before any cable move** (and
  ground/park lines per house practice) — plugging or unplugging drive
  lines on a gated, cold device with the excitation live risks
  transients through the contacts; restore the excitation in the same
  cell that rewrites the config, so the notebook record shows both.
- Either flavor: read the drive-current channel and whatever probe
  channels are wired; park gates between pairs only if the rig requires
  it (re-ramping costs time × N_pairs).

**Step 3 — rank and localize.** Per pair, form the resistance scale at
a reference density — choose it in the well-conducting regime away from
the CNP, use the *same* value for every pair, and state it in the
write-back — (drive amplitude over measured current, through the
rig's bias network per the device card) and classify: working / high-R
/ dead (no current at any n).

> **Bias-mode conditional — what 2T current can and cannot rank.** The
> "drive amplitude / measured current" resistance scale assumes a
> **voltage-bias-like** drive, where measured I ∝ 1/R tracks the device.
> On a **current-bias** rig the drive is a voltage through a large series
> resistor (I_bias ≈ V_drive / R_bias, e.g. 0.5 V / 100 MΩ ≈ 5 nA); for
> any device R ≪ R_bias the measured 2T current is **pinned at I_bias**,
> so the ratio returns ≈ R_bias for *every* alive pair and there is **no
> CNP dip in the current** (mod < 1% across the gate sweep). In that
> regime 2T current still cleanly separates **dead** (I ≪ I_bias) from
> **alive** (I ≈ I_bias) — enough for aliveness and fault
> *localization* — but **resistance ranking and the CNP read require the
> 4T voltage** (V = I·R; `cnp-and-dline-calibration`'s gate map). Check
> the device/rig card for the bias network before reading the ranking as
> resistance. *(our-measurement: QC0426/VTI, 2026-06-14, file_id 1–6 —
> current-bias, every alive pair pinned at ~5 nA.)*

Then the localization pass: a contact
present in ≥ 2 dead or high-R pairs while its partners work elsewhere
is the fault; a single dead pair with both contacts otherwise fine is a
pair-specific issue (wiring, not bond). Before declaring any contact
dead, check the false-positive modes: device grounded or tied at a
shared node (the `gate-current-sanity-check` failure catalog applies),
and — with a mux — that the recorded `qswitch_state` matches the
intended routing.

**Step 4 — at-field re-check (flavor).** At the campaign field, re-run
the loop on the surviving set only (cheaper). Plan the field move per
the rig's magnet discipline — get there once, schedule the survey when
the magnet is already at field if the campaign allows, never re-traverse
for it. Contacts re-rank; the 4T choice comes from pairs that survive
**at field**, not the B = 0 ranking. On screening-gate devices this is
one activity with `silicon-backgate-survey`'s at-field re-validation
(the reference campaign ran Si steps and per-pair checks as a single
6 T block) — schedule both on the same magnet excursion.

**Step 5 — choose and record.** Current path through the best
source/drain pair; voltage pairs on working contacts spanning the
device region(s) the science needs (region coverage matters on
possibly-inhomogeneous devices — channel disagreement downstream is
signal, and you want probes where it can show). Write to the device
card: ranking table, localization conclusions, chosen configuration(s),
run ids, and — with a mux — the routing dicts so the next session can
re-select them verbatim.

## Verify
- **Truth on disk**: after the first run of the loop, read its
  `metadata.json` back and confirm the pair entries (and
  `qswitch_state`, if muxed) are present and correct — *then* let the
  loop continue. Catching a truth gap after 12 runs re-does 12 runs.
- **Comparability**: diff the gate setpoints and excitation across the
  loop's metadata — identical by construction, so any drift is a bug in
  the loop cell.
- **Settle adequacy**: compare each run's first sweep point against its
  neighbors; a systematically off first point means switching transients
  are leaking into the data — raise `settle_s` (mux) or add a post-rewire
  pause (manual).
- **Open-pair claims cite resolvability**: "no current" counts only
  with the sensitivity floor stated — at the recorded sensitivity and
  excitation, what resistance would have been measurable?

## Examples
- `vti/qingrui/20260601-QC0426-3LGr/measurement.ipynb` cells 116–154
  *(our-measurement)* — the manual flavor this recipe encodes. Cells
  127–140: per-pair 2T multisweeps along the sanitized CNP line at 6 T,
  Si ≈ +90 V — one `meas_config` rewrite per pair (05-33, 05-09, …),
  the drain contact moved by hand per run, pair truth carried in
  duplicate-key config entries and comment strings (the idiom
  `mc_fragment()` replaces). Cells 123–125: Si-gate steps as
  `multimegasweep` slow axis around the same block. Cells 141–154: 4T
  configurations re-checked at 6 T (09-01 / 01-42 / 42-02 wirings,
  excitation experiments at cells 149–151) — the step-4 + step-5 shape.
- `bsuo/CF01B1/measurement.ipynb` cells 21–52 *(our-measurement)* — the
  switch-matrix mechanics live, pre-`ContactMux`: `arrange` naming
  contacts/breakouts, `breakout`/`ground`/`unground` switching, the
  config-as-sweep-axis trick used for what it's for (switch-transient
  tests, cells 38–46).

## Next
- **Configuration chosen**: the campaign's mapping recipes (`gatemap` /
  `nD-map` / `landau-fan`) on the blessed wiring; the device-card table
  is their contact-map input.
- **One contact kills multiple pairs**: operator escalation with the
  localization table — the decision (live with it, re-bond, warm up) is
  a physical-intervention call, not a recipe branch.
- **At-field re-rank changed the choice**: update the device card
  before the fan, and treat any B = 0-only prior ranking as superseded.
- **Channel goes bad mid-campaign**: re-enter at step 2 with the
  affected contacts' pairs only.
