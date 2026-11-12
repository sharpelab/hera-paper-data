<!-- variant: open-long | autonomy: HIGH (rich context, but method left open) | length: LONG
     Tests whether more context ALONE (without prescribing the experiment) steers
     Tier-2 to the right measurement. Replaces the campaign-goal framing. -->

# Brief

## Where we are
The campaign has characterized the anomalous-Hall behavior at the dome point,
run a substantial effective-mass temperature series at (n = 1, D = 1), and just
taken two small Landau fans (data/1774–1776). The latest, data/1776 (D = 1,
n = 0.9 → 0.5, B = 0.9 → 2.5 T), shows clear field- and density-dependent
structure in the Rxx channels: **the quantum oscillations are real.** That
go/no-go is now settled.

## Why it matters / what's at stake
A confirmed oscillation is the start, not the end. The fan was deliberately small
and coarse — enough to say "yes, real," not enough to extract a number. The open
strategic question is **what to invest in next** now that the feature is
established, and the choices genuinely trade off:
- read the **oscillation frequency B_F** (→ Fermi-surface area / carrier density
  of the pocket) at one or a few operating points;
- finish the **effective mass** at the now-confirmed oscillation point (the
  temperature-series machinery is already in hand);
- **map more broadly** — a wider/denser Landau fan over (n, B) to chart how the
  oscillations and gaps evolve across the dome before drilling into a point.
Each is defensible; the right call depends on what the campaign most needs next.

## State / resources
- Operating regime: D = 1, base T, V_Si = 48 V, config `mc_25` (current on
  `sr830_4`, Rxx on `sr830_1/2/3/5`), gates parked after data/1776.
- Full instrument set in `device_card.md` (gates, AC lock-in current bias,
  AMI430 magnet to several T, heater/thermometry, Yokos for small-field work).

## The ask
**Decide the single most valuable next measurement given the confirmed
oscillations, and run it.** Justify the choice against what data/1776 does and
doesn't establish, and land the sweep.

**Depth:** deep investigation — characterize it well enough to support a
defensible physics conclusion (not a quick yes/no, not yet paper-grade).
