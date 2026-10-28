## HERA — bring-up read: what does the device actually measure? (read-only)

`VERIFY: ALL GREEN` (cell 33) and `PROBE: BOUND` (cell 31) — **E1 engaged**,
grant recorded in `session_notes.md`. Zack also granted instrument-value
setting, so lock-in ranging and settling are mine; the safety surfaces
(validators, gate limits, field cap, T cap) stay session-banned, and the
specifically consent-gated knobs (`dc205.ramp_rate`, Keithley `volt.step`,
`set_both` ratio) still get a specific ask, not a blanket one.

**Why this before Gate C.** VERIFY printed the lock-in ranges, and one of them
does not survive contact with the device: `sr1` (the Rxx pair B_1−B_2, unity
gain) is on **2 µV** full scale. At the nominal I_bias = 10 nA that ceilings the
measurable Rxx at **200 Ω** — below any plausible graphene Hall-bar value away
from the CNP, and orders below it near the CNP. `sr0` is better placed: 20 mV
full scale ÷ 10⁶ V/A = 20 nA, so the 10 nA drive sits at half scale. Sweeping
the gates now would produce a railed Rxx channel and a wasted 20 minutes.

So: read the device once, at the parked state, and let the numbers set the
ranges. This cell sets nothing. It reports the precondition state (gates at 0,
B, T), then X/Y/R/θ and the fractional-of-full-scale loading on all four
lock-ins, then the SR830 status registers (`LIAS?` bit 0 input/reserve
overload, bit 1 filter overload, bit 2 output overload) so a rail shows up as a
flag rather than an inference. From `sr0` it forms the true transport current
`I = X_sr0 / sr0_gain` — the current-bias assumption is only as good as the
100 MΩ ≫ R_device condition, and this is the check on it — and from `sr1`, the
four-terminal `R_xx = X_sr1 / I`.

**What I am reading it for.** Three numbers: (1) is the device alive and are
B_1−B_2 and the T_0→B_3 current path both passing signal, or is a provided
contact dead (operator rewiring problem per the brief, not a detour I take);
(2) the R_xx scale at (0, 0), which sets `sr1`'s sensitivity with the gate-map
recipe's `sens ≳ R_max · I_ac · G` rule plus headroom for the CNP peak; (3)
whether θ is near 0° — a large phase means the signal is capacitively
contaminated and the 13.777 Hz drive or the settling needs revisiting before
anything is trusted.

Cost: seconds. Nothing moves.
