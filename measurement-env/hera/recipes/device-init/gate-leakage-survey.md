# Gate leakage survey (dI/dV interrupter)

> **Status: DRAFT, not yet beta-tested on a live cooldown.** Single-option rewrite of
> the old discrete-bias / 2D-survey recipe. Conforms to `recipes/STYLE.md`
> (rig/device-agnostic; setpoints cited-not-quoted; provenance-flagged). Rig-specific
> procedure shape (a gate source without leakage readback; the averaging-filter SCPI)
> lives in a **variant**, not here. Open items tagged **[BETA]**.

## What

One **continuous** outward push per gate per polarity, from parked-safe (0 V), guarded by
a live **dI/dV interrupter** (`sharpelab_nb.LeakageDetector`, wired up by
`k2400_leakage_guard`) that aborts the sweep at the *foot* of the leakage upturn — where
the gate-current channel first departs super-linearly from its flat baseline. Each push
yields one onset; the onset **inset by a policy margin** is that gate/polarity's safe
limit. The four limits define the safe operating **rectangle**; an opposed-corner check
clips it where biasing the other gate moves the onset inward.

The interrupter does, automatically and earlier, the onset-spotting a human did by eye.

## When

After `gate-current-sanity-check` flags leakage (its "rolling into nA" / "parked gate
tracks the swept gate" rows), or folded into its per-gate iterations. Always before a
gatemap that ventures far from (V_tg, V_bg) = (0, 0). Once beta-tested, this **supersedes
the manual range-finding** in `gate-current-sanity-check` — the interrupter replaces
"watch the plot and back off."

**Precondition**: device ungrounded (as `gate-current-sanity-check`); excitation/bias
disconnected for the survey, so the gate-current channel sees only leakage + broadband
instrument noise.

## Why

- **The onset is the foot of a super-linear upturn, not a fixed current** *(heuristic,
  n=1 device; our-measurement on QC0426, see Examples)*. An absolute pA threshold
  cannot separate a gentle knee from baseline because their magnitudes overlap; the
  **slope (dI/dV) departure** separates them by *pattern*, not magnitude.
- **The published limit is already inset.** The operator's real stop is the *edge of the
  swept data* (where they stopped / the kernel interrupted); the operating limit is inset
  from there. The interrupter finds the foot directly — **earlier than the manual stop on
  every leaking leg** *(our-measurement on QC0426; the per-leg margin is in the QC0426 run
  metadata, not quoted here per Rule 11)* — making the inset an explicit policy step, not a
  number buried in where someone got nervous.
- **Continuous push, not chunked** *(decisive, our-measurement, QC0426)*. Stitching
  segments injects per-segment DC offset steps that fake a sloped, noisy baseline and
  false-trip the detector; the same gate read on a *continuous* run had a flat, ~6×
  quieter baseline (QC0426 runs, our-measurement; values not quoted here). One continuous
  sweep from parked-safe gives a clean baseline.
- **The safe region is a rectangle (lab convention).** The binding constraint is the
  **opposed corner** (max |V_tg − V_bg|): the channel floats to the cap-weighted gate
  average, so there each dielectric eats its full bias and the onset moves inward.
  **Co-polarized corners are safe by construction** *(because the channel floats with the
  gates, each dielectric sees less field than at its axis endpoint)* — **weakening if the
  channel is grounded during the survey**, in which case the residual cross-gate path is
  gate-to-gate leakage, still worst at the opposed corner.
- **The violent runaway is decisively caught; gentle knees are weak at default
  integration** *(our-measurement, QC0426)*. The split is SNR-limited — see Setup.

## Setup

The Keithley-2400 configuration (pA current range, integration `nplci`, repeat-averaging)
is owned by **`k2400_leakage_guard`** (Recipe cells below) — a context manager that
configures the SMU and restores it on exit, so the survey can't run on a mis-set range or
leave the SMU mis-configured. Two things to calibrate first:

### Settle / noise diagnostic *(one-time, design-time guard — Rule 12)*

`delay` and the averaging count `avg_n` are **calibrated, not inherited** (Rule 12). Step
a gate to a fixed safe voltage and capture a fast raw time series (no filter) for a few
seconds:

- the **decay** gives the true settle time (electrical RC is sub-ms, but hBN/graphene
  gates can show slow dielectric-relaxation / charge-trapping settle — set `delay` from
  what you measure),
- an **FFT of the steady part** confirms the noise is broadband (it should be, excitation
  disconnected), so the averaging filter (which beats broadband noise down as √N) is the
  right lever; spend the otherwise-dead settle time on averaging (`avg_n`).

### The interrupter — `sharpelab_nb.LeakageDetector`

A causal, self-calibrating streaming detector. Per point it (1) causal-median-filters the
gate current, (2) calibrates a baseline line `b0` + noise from the first safe stretch, (3)
runs a **CUSUM on the local slope-excess z-score**, and trips at the **foot** when the
CUSUM crosses `H`.

- **Discriminator + confounds (Rule 3):** "local dI/dV rises above baseline ⇒ leakage
  foot" — but a **segment-boundary DC step** also spikes dI/dV (⇒ the continuous-push
  requirement removes it), and a **noisy stretch** spikes it transiently (⇒ the CUSUM's
  reset-on-dip + local-noise normalization reject it). **Known residual:** a sharp
  *non-stationary* noise burst can still false-abort — accepted (a live restart is cheap),
  and the averaging step keeps bursts small.
- **No tail-confirmation** is used: live, a false abort is cheap and a missed leak is not,
  so the gate commits forward.
- **Thresholds are labeled heuristics (Rules 5, 7):** the CUSUM `(slack, H)` *(heuristic;
  default from QC0426, n=1; raise to reject noise, lower to trip sooner)* and the
  `INSET` *(heuristic; policy margin = measured interrupter overshoot + run-to-run onset
  spread)*. **Tune both against the live continuous push at the chosen SNR**, not from the
  default.

## Recipe

### Cell A — guarded continuous push (per gate, per polarity)

```python
# === EDIT THIS BLOCK BETWEEN RUNS (copy the cell per leg) ===
gate = k_bg                 # the gate to push (a Keithley 2400)
v_endpoint = GATE_CEILING   # this leg's far end: the geometry ceiling for `gate`
                            #   from the device card, PAST where leakage is expected
n_pts = N_PTS               # dense enough to be continuous (sub-0.05 V/pt) for `gate`
delay = SETTLE              # from the settle diagnostic
# ============================================================

from functools import partial

from sharpelab_nb import k2400_leakage_guard

s = sweep.AsyncStation(measurement_config)
s.add_comment('gate-leakage-survey')
s.add_comment(f'gate: {gate.name}, leg 0 -> {v_endpoint:+g} V (continuous, guarded)')

s.ramp(k_tg.volt, 0)        # park all gates at 0; excitation disconnected
s.ramp(k_bg.volt, 0)        # (+ k_si.volt if present)
other = k_bg if gate is k_tg else k_tg
s.fp(temperature)
# Swept gate's V is already the sweep's setpoint column — re-fp'ing it writes a
# duplicate column name. gain=1 (default) -> true current, required by check_after.
s.fp(other.volt)
s.fp(gate.curr).fp(other.curr)
s.plot(gate.volt, gate.curr)

# k2400_leakage_guard configures the 2400 (pA range, nplci, averaging) and restores on exit.
# check_after feeds the detector V=setpoint + I=gate-current fp straight off the sweep's
# data row = [time, setpoint, temp, other.volt, gate.curr, other.curr] -- ZERO extra
# SMU reads (~3x faster than the re-reading run_before guard, identical detection).
i_col = 4   # `gate`'s current fp — fixed column; the fp order above is swept-independent
with k2400_leakage_guard(gate) as guard:
    s.register_run_after(partial(guard.check_after, i_col=i_col), args=())
    try:
        s.sweep(gate.volt, np.linspace(0, v_endpoint, n_pts), delay=delay)
    finally:
        s.ramp(gate.volt, 0)

print(f'{gate.name} onset (foot): {guard.trip_V}' if guard.tripped
      else f'{gate.name} no leakage to endpoint — range-bound, not knee-bound')
```

Run once per (gate, polarity). A **trip** is the leakage foot; **no trip** means the leg
is range-bound (no knee in range), and the limit is just where you chose to stop. Manual
`Kernel → Interrupt` always available; `try/finally` parks the gate; the guard restores the
SMU on context exit. Keep the device-card geometry ceiling as a hard "don't push past,
even if nothing trips."

### Cell B — opposed-corner verify

Only the opposed corners (max |V_tg − V_bg|) can clip the rectangle. Hold one gate at its
inset limit, push the other to its inset limit, guarded:

```python
# === EDIT THIS BLOCK ===
held  = k_tg;  held_V = HELD_LIMIT      # held gate at its inset limit (Cell A onset + INSET)
swept = k_bg;  swept_endpoint = SWEPT_LIMIT   # push the other to its inset limit, opposed sign
# =======================
s = sweep.AsyncStation(measurement_config)
s.add_comment('gate-leakage-survey: opposed-corner verify')
s.add_comment(f'{held.name} held {held_V:+g} V, push {swept.name} -> {swept_endpoint:+g} V')

s.ramp(swept.volt, 0); s.ramp(held.volt, held_V)
s.fp(temperature)
s.fp(held.volt)                 # swept.volt is already the sweep's setpoint column
s.fp(swept.curr).fp(held.curr)
s.plot(swept.volt, swept.curr); s.plot(swept.volt, held.curr)

i_col = 4   # `swept`'s current fp — fixed column; fp order above is swept-independent
with k2400_leakage_guard(swept) as guard:
    s.register_run_after(partial(guard.check_after, i_col=i_col), args=())
    try:
        s.sweep(swept.volt, np.linspace(0, swept_endpoint, n_pts), delay=delay)
    finally:
        s.ramp(swept.volt, 0); s.ramp(held.volt, 0)

# clip the rectangle at this corner iff the onset comes inside the inset limit
print('CORNER CLIPS — clip this corner in the validator' if guard.tripped
      else 'corner clear; rectangle holds here')
```

Repeat for the other opposed corner (signs swapped). Co-polarized corners get at most one
confirmation pass — they're safe by construction; a trip there is a "both lines hot"
surprise (cross-coupling / shared ground), not a range limit.

### Cell C — commit validators

The guard already restored the SMU, so this cell is just the validators:

```python
# Per-leg onsets from Cell A, inset by INSET; clip opposed corners per Cell B.
k_tg.volt.vals = validators.Numbers(tg_neg_limit, tg_pos_limit)   # limits = onset -/+ INSET
k_bg.volt.vals = validators.Numbers(bg_neg_limit, bg_pos_limit)
# If a corner clipped: the gatemap region must INSCRIBE inside the clipped polygon
# (an axis-aligned rectangle won't — use an inscribed rect / raster polygon; see nD-map).

print('k_tg.volt validator:', k_tg.volt.vals)
print('k_bg.volt validator:', k_bg.volt.vals)
```

`INSET` is a **policy** number, not physics (Rule 7). Mirror the committed validators to
the **device card** — the durable cross-session record.

### HERA handshake

HERA proposes Cells A/B/C together but **does not advance to a gatemap until the operator
reports the per-leg onsets, the corner-verify outcome, and the validator cell has run.**

## Rig variants

- **Gate source without leakage readback** (e.g. a standalone DC voltage source on a gate):
  that gate can't be its own leakage ammeter, forcing a repatch so a current-measuring
  source drives it during the survey. This changes the *procedure shape* → it is a
  **variant** (`gate-leakage-survey-<rig>.md`, Rule 13), not base prose. The variant names
  the repatch and its obsolescence condition (a switch matrix or a leakage-readback gate
  source deletes it).
- **Averaging-filter SCPI** *(`[BETA]`)*: `k2400_leakage_guard` enables the 2400 repeat-
  average filter via raw SCPI (`SENS:AVER:*`) — there is no qcodes parameter for it.
  Verify the SCPI against the instrument on first use.

## Examples

- **QC0426 / 3LGr (Qingrui, VTI)** *(our-measurement; onsets/limits recorded in the QC0426
  notebook index and run metadata — cited, not quoted, per Rule 11)*. The device's gate
  leakage spans the full range this recipe targets: a **decisive** negative-top-gate
  runaway (the leg Qingrui kernel-interrupted), **gentle** super-linear knees on the
  positive legs, and one back-gate leg that was **range-bound** — no knee, he simply
  stopped. The gentle knees sat near the noise floor at his integration settings — the
  motivation for the averaging step. This rig drives the top gate from a source without
  leakage readback → see the variant.

## Next

- Default: `gatemap` / `nD-map` with the committed rectangle as validators, **carrying the
  same interrupter as a live guard on the gatemap** (it catches interior leakage the frame
  survey missed). If a corner clipped, inscribe the region inside the clipped polygon.
- If the rectangle is too small for the (n, D) region of interest: `silicon-backgate-survey`.

## Beta-test checklist

- [ ] Run the settle/noise diagnostic; set `delay` and `avg_n`; confirm broadband noise.
- [ ] Write the rig variant (repatch workflow).
- [ ] Verify the `SENS:AVER:*` averaging SCPI in `k2400_leakage_guard` against the instrument.
- [ ] Verify `register_run_after` + `interrupt_requested` aborts a live continuous sweep and parks the gate.
- [ ] Confirm the `run_after` guard timing/detection on the rig: a guarded leakage-find vs the no-guard single-read timing cell (expect ~3.11 -> ~1.19 s/pt at nplc=10 / avg_n=2 / autozero-on, foot unchanged).
- [ ] Tune `(slack, H)` and `INSET` against a real continuous push at the chosen SNR.
- [ ] Confirm the foot matches eyeball on the live plot.
