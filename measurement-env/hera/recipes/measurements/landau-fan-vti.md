# Landau fan — VTI variant

**Base**: `measurements/landau-fan.md`. This file carries only the deltas
(STYLE rule 13); read the base first. Runs executed under this variant tag
`s.add_comment('landau-fan-vti')`.

The base's Recipe steps are toploader-flavored in their call surface (driver
names, an explicit field-settle sleep, a Discord ping). On the VTI those
names and the settle discipline differ; the *method* — coarse-first design,
both-axis Nyquist, Středa read — is unchanged.

**Overridden steps and the rig facts that force them:**

- **Steps 0/5, field parameter** — the field parameter is
  **`magnet.field`** (the instrument instance is named `magnet`, not `mag`);
  the station builder is `sweep.AsyncStation(mc)`, same as the base. The
  slow-axis call is
  `s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=…, fast_delay=…)`.
- **Step 2, fast axis** — the gate-voltage helper is
  `sharpelab_nb.gates.calc_gate_voltages(n, D, c_tg, c_bg, n_offset, D_offset)`
  (the `(c_tg, c_bg, offsets)` form written back by
  `cnp-and-dline-calibration`), not `calculate_gate_voltages(ns, Ds, dtg=, dbg=)`.
- **Step 4, field positioning** — `magnet.field(target)` **blocks until the
  field is reached** (FastBi1K5 blocking ramp; see the rig card's magnet
  Set-semantics). So there is **no `time.sleep(600)` pre-settle** — the set
  call *is* the settle. Position by `magnet.field(B_start)` and proceed.
- **Step 8, notify** — `hera-notify` on the operator's key (rig notify
  channel), not `alerts.discord`.
- **Step 6, fp list** — follow the rig card's instrument-polling rules when
  building the `fp` set; the card names which instruments are unsafe to poll
  per-point on this rig. *(The base says "fp temperature(s)"; the card
  governs — do not restate the hazard here.)*

**Cost-model regime (base Why).** The base's "finer B steps cost only row
turnaround, and coarsening B buys aliasing, not time" corollary holds only
when the grid is cheap relative to the traverse. On the VTI the magnet is
blocking-ramp-limited (so the traverse term is fixed by the B-span) **but
per-point time is ~1.2–1.4 s/pt** (rig card Timing; ~1.44 s/pt at a 4τ
settle), which makes a multi-tesla fan **measurement-dominated** — the bare
traverse (~1 h at 8 T) is small against the grid. So the base's
*measurement-dominated* branch applies: buy the high-n Nyquist floor (base
step 1, the n_max re-check) by **trimming n-points or flooring the high-n
claim**, never by adding B rows blindly. "Fine B is nearly free" is a
toploader-era (non-blocking-magnet, traverse-dominated) statement; do not
carry it to this rig.

## Examples

- A VTI trilayer fan *(our-measurement, 2026-06-14)*: `file_id 20`, D = 0,
  0 → 8 T paired n-line, `magnet.field` slow axis, ~1.44 s/pt at a 4τ dwell —
  the measurement-dominated regime above (8 T bare traverse ≈ 1 h ≪ grid
  time). The firming fan `file_id 21` rode the magnet home (8 → 0 T) as a
  measured ramp-down, picking up high-n rows on the way — the base's
  "plan the direction so the fan ends where the next measurement needs it".

## Next

Base `## Next` applies unchanged.

## Obsolescence

Delete this file when the base recipe goes fully instrument-class-conditional
(driver names — `magnet.field`, the notify channel — move
to the rig card, leaving the base name-free): the cost-regime note then folds
into the base's rig-property cost discussion, and the settle/fast-axis deltas
become base conditionals the rig card resolves. Moving fans onto a continuous
on-the-fly ramp (the driver's `start_field_ramp` + sampled readback, outside
the blocking `sweep` set) would also retire the step-4 delta.
