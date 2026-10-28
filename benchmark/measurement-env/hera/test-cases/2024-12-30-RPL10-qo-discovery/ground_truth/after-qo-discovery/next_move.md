# Ground truth — next move at the frontier (cut idx 54)

*What Aaron actually did in the next section (`# Temperature dependence`, idx
55+ / source cells 55–80). This is **one** expert path, not **the** answer — the
frontier is CONTESTED, so several next moves are defensible. Used to route the
replay to human review, never as an exact-match score.*

> **Expert-confirmed 2026-06-09 (Aaron, review card).** Move capture "Correct";
> contested framing affirmed — *"I think all of these are fine choices."* On the
> heater: the heater-drive → sample-temperature mapping is **cooldown-dependent**
> (no fixed calibration), though *"we can cook up a rough calibration"* — don't
> treat `heater.volt` values as temperatures across cooldowns.

## The move: `# Temperature dependence`

After confirming quantum oscillations at D = 0.31 V/nm, Aaron pivoted to
**heating the sample and tracking the transport vs temperature**. The sequence:

1. **Bring the heater up** — `s.ramp(heater.volt, 1)` → `2` → `3`, reading
   `heater.curr` at each step (cells 57–59) to calibrate the heater drive. (The
   heater had not been driven at all up to the cut.)
2. **Re-locate the feature at the working D under heat** — a (k_bg, k_tg)
   gatemap at D = 0.35 V/nm, n = −3.1 to −2.1 (cells 60, 62) → `data/160`,
   `data/161`-ish — re-finding the SC1 / oscillation spot now that the device is
   warm, and a companion map at D = 0.365 (cells 63–64).
3. **The canonical T-dependence sweep** — `s.megasweep(heater.volt,
   np.linspace(2, 0, 42), dc205_1.volt, np.linspace(-8, 8, 401), slow_delay=600,
   fast_delay=1)` (cells 76/77): an **Idc × temperature** map at a fixed (Vtg,
   Vbg) operating point — DC bias on the fast axis, heater (temperature) on the
   slow axis, 42 T-steps with a 600 s settle each. This is the move that measures
   how the zero-bias / SC feature evolves with temperature (→ Tc), and the
   T-damping of the oscillation amplitude (→ effective mass).

The next-move sweep file in the pool is **`data/160/`** (first T-dependence
sweep, post-cut — present for ground-truth reading only; NOT in the allowlist).

## Why this is a reasonable next step

Once quantum oscillations are established, temperature dependence is a high-value
follow-up on two fronts at once: (a) the **T-damping of the oscillation
amplitude** yields the carrier **effective mass** (Lifshitz–Kosevich), a headline
quantity for a rhombohedral-graphene Fermi surface; and (b) for the SC1 feature
in this density window, the **Idc-vs-T map gives Tc** — the suppression of the
critical-current / zero-bias feature as the sample warms. It's a natural,
information-dense next axis that reuses the operating point just established.

## Class for judging (CONTESTED — populate "different but reasonable")

- **Same experiment:** propose a temperature-dependence measurement at the QO /
  SC operating point — heater-ramped Idc-vs-T (or oscillation-amplitude-vs-T for
  effective mass). Exact T-range / step count / which observable is
  parameter-level, not the decision.
- **Same class, different params:** T-dependence by another cut — e.g. a 1D
  resistance-vs-T, or tracking the fan amplitude vs T at fixed (n, D, B) for
  effective mass specifically.
- **Different but reasonable** (genuinely competitive here, not penalized):
  - **More QO mapping** — repeat the fan at other D (0.28, 0.25), finer/longer
    fans, extend n or push B higher, to pin the Landau-fan slope and degeneracy
    before adding a temperature axis. (Aaron did some of this later.)
  - **Fraunhofer / SC field-response** at the SC1 dome.
  - **(n, D) gate map at B = 0** to place the QO window in the phase diagram.
  A reviewer may rate any of these equivalent-or-better given the data at the cut.
- **Divergent / worse:** abandoning the QO/SC program; re-running an
  already-completed map with no new axis; a move that ignores both the
  established oscillations and the SC features.

## Notes

- This frontier intentionally does NOT have a single "correct" move. The point of
  the contested frontier is to see *which* legitimate branch the agent picks and
  how well it justifies it against the data — the autonomy×length brief grid then
  tests whether more-directive framing steers it toward Aaron's actual choice.
- Physics labels (effective mass from T-damping, Tc from Idc-vs-T) are the
  standard interpretation of these sweeps but are **reviewable** — flag for
  expert spot-check; see `reading.md` limitations.
