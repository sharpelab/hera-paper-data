# Temperature dependence — VTI variant

**Base**: `measurements/temperature-dependence.md`. This file carries only
the deltas (STYLE rule 13); read the base first. Runs under this variant
tag `s.add_comment('temperature-dependence-vti')`.

The base is toploader-flavored: the T knob is a raw heater voltage, no
closed loop. On the VTI the knob is the LS335 closed-loop setpoint and the
readback is worker-logfile-based (rig card Thermometry). The *method* —
two flavors, warm-first ordering, fp the readback — is unchanged; the
control idiom and settle discipline are not.

**Overridden steps and the rig facts that force them:**

- **Heater drive (base steps 3, 6–8)** — command temperature directly:
  `heater.set_both(target, ratio=…)`, the rig card's sanctioned method and
  authorized range; heater ranges are set by the call. The base's
  heater-voltage ramps and `s.read(heater.curr)` open-line check are
  replaced by checking the ranges went nonzero and the logfile T responds.
- **Readback (base step 1)** — `s.fp(T_sample)` (add `T_vaporizer` during
  ladders): file-based, never GPIB (rig card). Every settle poll passes a
  logfile-freshness guard sized per the rig card's cadence rule (≥ 2–3
  write periods — a threshold at the cadence false-fires; ladder v2).
- **Settle acceptance (base step 4)** — the sample-loop PID is untuned
  (rig card): tolerance-settling never passes below ~20 K. Use **hover
  acceptance**: accept when T is *stable* — spread < 0.1 K over 90 s —
  within [nominal − 0.5, nominal + 3] K; the fp'd per-point T is the fit
  axis, rung labels stay nominal. [our-measurement: ladder v5,
  runs 10–17] *Interim: delete when the PID is tuned (eng-backlog).*
- **Descending rungs (base step 4)** — heaters only lift; a descent with
  `set_both` held is passive-cooling-limited (rig card Timing). Use
  **descend-catch**: `heater.off('both')` through the descent, wait
  (interruptible, freshness-guarded) for T ≤ target − 0.2 K, then
  `set_both(target)` lifts the last 0.2 K and holds — a minutes-scale
  catch instead of an hours-scale tail. [our-measurement: ladder v4]
- **Runaway guard (base step 4's direction-aware principle, concretely)**
  — fault only on true runaway heating: T_vap rising > 2 K above *both*
  its rung-start value and the target; never while cooling toward
  setpoint. [our-measurement: ladder v2]
- **Flavor B field sweeps** — `magnet.field` blocks and never re-traverses
  (rig card Magnet): alternate the sweep direction each rung, derived from
  the live field, not a flag. (Base step 7's alternating variant is
  mandatory here.)
- **Notify** — `hera-notify`, not `alerts.discord`.

## Next

Base `## Next` applies unchanged.

## Obsolescence

The hover-acceptance delta (and the rig card's overshoot figures) deletes
when the sample-loop PID is tuned (eng-backlog, Bingcheng) and
tolerance-settling passes at ≤ 20 K; re-measure descend/catch timings at
the then-current ratio in the same pass. Delete the whole file when the
base goes instrument-class-conditional on "closed-loop setpoint vs raw
heater voltage" — the deltas then become base conditionals the rig card
resolves.
