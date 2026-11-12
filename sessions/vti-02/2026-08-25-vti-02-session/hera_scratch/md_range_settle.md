## HERA — range `sr1`, then measure the settling/noise trade (no sweep)

The bring-up read (cell 35) came back: **device alive**, I = 9.867 nA = 98.7% of
nominal so the current bias holds, sr0 at 0.49 of full scale and well placed —
and **`sr1` railed at |X|/sens = 1.010**, its 204.8 Ω being nothing but
2 µV / 9.87 nA, the ceiling itself. R_xx is ≥ ~205 Ω and otherwise unmeasured.
Two jobs before Gate C, both cheap, both settable now that Zack has granted
instrument values.

**Part 1 — range `sr1` off the rail.** Step the sensitivity up the SR830 ladder
from 2 µV, settling 7τ between steps, until |X|/sens < 0.5, then report the
true R_xx at (0, 0). This lands the *metallic* value; the CNP peak will be much
larger, so the sensitivity I finally commit gets headroom above what this
measures, not just above the rail. `sr0` is untouched — half-scale is where I
want it, and under current bias it only moves down as the device gets more
resistive.

**Part 2 — settle vs noise, measured.** I flagged before the grant that
τ = 0.3 s at 24 dB/oct implies a ~2–3 s settled point (STYLE rule 12, k ≈ 7–10)
against the rig card's 0.2–0.25 s/pt rule of thumb, and that I would bring
numbers rather than a front-panel guess. These are the numbers. For each
candidate (τ, slope) — (0.3, 24), (0.1, 24), (0.03, 24), (0.1, 12) — settle
10τ, then take 24 reads of `sr1.X` and report mean, standard deviation, and the
std expressed as an equivalent ΔR_xx. That last column is the one that decides:
SdH oscillations downstream are a *small fraction* of R_xx, so the question is
not "is the lock-in quiet" but "is a point at this τ quiet enough to resolve the
feature I am paying magnet time for."

Note what the std does and does not capture: it measures **output noise at a
fixed setpoint**, which is the per-point uncertainty. It does *not* measure
settling after a gate step — that stays theory (k·τ), and I price the dwell at
7τ for 24 dB/oct and 5τ for 12 dB/oct. The two combine into the real choice:
τ = 0.03 s is only 0.4 drive periods at 13.777 Hz and I expect it to be visibly
noisy; τ = 0.1 s at 24 dB/oct is 1.4 periods with ~10⁻⁵ rejection at 2f and
prices a point at ~0.7 s — my prior on where this lands, stated so the data can
contradict it.

The cell restores τ = 0.3 s / 24 dB/oct at the end and prints a recommendation
table; **committing the choice is the next cell**, so this one is reversible and
leaves the rack as it found it apart from `sr1`'s sensitivity.

Cost: ~2 minutes, no run directory, no gate or field motion.
