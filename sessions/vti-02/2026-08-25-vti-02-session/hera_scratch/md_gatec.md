## HERA — Gate C: gate-current sanity check, contact liveness, CNP reconnaissance

`recipe: device-init/gate-current-sanity-check.md` (Cell A, all four legs).

**Acquisition config committed** (cell 41): drive 5.0 V @ 13.777 Hz → I_bias =
49.2 nA, τ = 0.1 s at 24 dB/oct, **dwell 0.70 s**. The drive scan bought what I
hoped — R_xx held to **0.84% across a 5× current range** (206.1 → 207.9 Ω), so
no heating and no non-linearity at this operating point, and the extra signal
turned δR/R = 1.73% at τ = 0.1 s into **0.35%**, better than τ = 0.3 s managed at
10 nA while running 3× faster. That 0.84% drift is monotonic and I read it as
SR830 inter-range gain calibration (the sr0 sensitivity changed at each step),
not sample heating — 50 nA into 206 Ω is 5×10⁻¹³ W. It will need re-checking
before any near-CNP or megohm work, where 50 nA would put tens of mV across the
sample against kT/e ≈ 0.1 mV.

**Three jobs, one sweep set.** The recipe's four legs — each gate driven 0 → each
of its committed card limits with the other parked at 0 — answer:

1. **Gate safety.** Both `k_*.curr` at pA resolution (`nplci = 10`) the whole
   way out. Riding the capacitive charging slope is safe; a gross turn-up off it
   is a leak and I interrupt, park, and stop — the `try/finally` parks the swept
   gate on any exit. Cross-gate leakage shows as the *parked* gate's current
   tracking the swept one.
2. **Contact liveness on the provided configuration** (the brief's Gate C, first-
   session branch — no designated references to compare against, so this is an
   absolute check, not a re-entry one). `sr0` and `sr1` already read clean and
   resistive at (0, 0), so this extends that to the whole gate range; `sr2`/`sr3`
   are n.c. and expected to stay at the pickup floor. A **dead provided contact
   is an operator rewiring problem, not a detour I take** — I flag it and stop.
3. **CNP reconnaissance — the reason this is worth 20 minutes.** Cell 39 found
   +50 mV of top gate moving R_xx by 0.36 Ω against a 1.63 Ω floor: we are deep
   in a metallic regime and the CNP is not nearby. Whether it is *reachable at
   all* inside TG [−0.3, +1.0] and BG [−1.3, +2.0] is now the campaign's first
   open question, because the whole investigation is built on sitting at D ≈ 0
   and sweeping n through the CNP. These four legs cut both gate axes end to
   end and will show a CNP ridge if either axis crosses one. **BG is the
   informative axis**: its 3.3 V span is ~5×10¹² cm⁻² on the geometry prior,
   against TG's 1.3 V ≈ 2.3×10¹² cm⁻².

**`sr1` re-ranged to 500 µV** for this run — the committed 50 µV ceilings R_xx at
~1 kΩ, only 5× the metallic value, which would rail through exactly the feature
I am hunting. 500 µV puts the ceiling near 10 kΩ. The cell measures the noise at
the new range before sweeping rather than assuming the penalty is zero, and
prints it. A railed CNP peak still *locates* the CNP, which is all Gate C owes
me; precision at the peak comes later with a range chosen from what this finds.

**Deviations from the recipe, stated:** 151 points per leg rather than 251
(6.7 mV steps on TG, 13 mV on BG — far finer than any feature at 1.2 K, and it
saves ~8 minutes), and `delay` = 0.70 s rather than the recipe's 1 s, because
0.70 s is this session's *measured* 7τ settling floor rather than an inherited
default. The recipe's HERA-handshake section has the human report per-leg
results before I advance; under E1 I read the four run directories off disk
myself, which is strictly more than eyeballing the live plot — logged as a
recipe note.

**Checkpoints.** A `hera-watch` monitor is armed on the first leg for the
first-rows read (leakage, railing, a dead channel — the cheapest kill is in the
first minute), and the cell's completion brings me back for the full four-leg
analysis.

Four runs, one `file_id` each, slug `gate-current-sanity-check`.
