## HERA — P1 / Gate C: back-gate liveness, find the CNP

Plan step **P1** (`hera_scratch/plan.md`) and the brief's Gate C — a cheap liveness
check on the provided contact configuration, inside the committed limits. Nothing
expensive runs until this passes.

**Why this cut.** VERIFY says the contacts are alive from the source side already:
I_measured = 9.86 nA is 98.6 % of the 10 nA bias, so T_0 → B_3 is carrying and the
device is far below the 100 MΩ bias resistor. What I do not have is where the charge
neutrality point sits — the brief withholds it, and every later step (the gate map's
window, the fixed-D cuts, the fan's density axis) is anchored on it. A single 1D
V_bg cut at V_tg = 0 across the whole committed back-gate range sweeps
Δn ≈ 5.0 × 10¹² cm⁻² on the geometry prior, which should bracket the CNP unless the
intrinsic doping is larger than that.

**Read the current channel, not Rxx, this run.** sr1 is railed — sens 2 µV against a
2.022 µV reading, fs = 1.01 — so its Rxx number (205 Ω) is a lower bound, not a
measurement. sr0 is at fs 0.50 and cannot rail going forward (the drain current only
*falls* as the device approaches the CNP), so the two-terminal conductance dip is the
valid CNP locator here. sr1 is still followed and plotted so the sensitivity fix shows
up the moment it lands. Ask is out to the operator: sr1 sens → 1 mV, and τ → 0.1 s on
sr0+sr1.

**Dwell is compliant, not bent.** τ = 0.3 s at 24 dB/oct ⇒ 7τ = 2.1 s, which is what
`delay` is set to. That is the whole reason the τ ask matters: it prices this 133-point
cut at ~5 min and the coarse gate map at ~2 h.

**Preconditions asserted before anything moves:** thermometry worker live (age +
cadence, so a frozen logfile cannot pass), T_sample in the base window, |B| ≤ 0.02 T
(this cell never touches the magnet), V_si = 0 (silent inherited axis), and — the one
that would silently waste the run — **both Keithley source outputs ON**, since a gate
set into a disabled output is inert and would look like a featureless trace.

**Checkpoint:** first rows watched live for railing, a dead channel, or leakage
excess; the run is short enough that the periodic checkpoint is the completion read.
