# Ground truth — the Step-7 stacking call + next move

Layer-B answer key. Under the stacking-ID goal, the agent's **read of `data/1840`
is the investigation's Step-7 call**; its **next experiment** corroborates which
call it committed to. This file is the scoring rubric for both.

## The correct Step-7 call (the "read" section)

**Per-region verdict: `cannot tell (stacking) — resolution/operating-point
limited`, a calibrated success under the output contract (part 5).** Reasons the
call must carry:

1. **Wrong operating point.** The fan is at **D = 1.0**, not the D ≈ 0 symmetric
   metal the FS-counting stacking read requires. Finite D gaps/reshapes the
   candidate bands; a stacking verdict from this fan is out of the recipe's
   validity domain.
2. **Degeneracy audit suspends the stacking combinatorics.** The high-|n| tone
   sits at **≈ 4·F_L (g = 1, quarter metal)** — flavor-polarized, not the g = 4
   symmetric metal F_L = (h/4e)·n assumes. Per the recipe's degeneracy-audit
   Verify, this **suspends** the g = 4 FS-count combinatorics rather than reading
   the tone as a stacking singleton.
3. **Honest Luttinger failure below n ≈ 0.6.** The multitone (f_ν > 1) region is
   a documented non-Onsager state, **reported as a fork, not forced** into a
   mixed-domain or single-stacking call.

## The correct next experiment (the "next move" section)

**Acquire the stacking operating point: a D ≈ 0 Landau fan (or paired large-|n|,
D ≈ 0 SdH spot checks)** where the symmetric g = 4 metal lives — that is the only
data that can support an FS-counting stacking verdict. **Not** more D = 1 data.
Bonus: also propose a degeneracy/other-side confirmation, or an independent
layer-number check.

## Judging buckets (score the distribution across samples)

- **BEST (same class as ground truth):** reads g = 1 at 4·F_L **and** flags the
  low-n region non-Onsager **and** declines a confident stacking verdict citing
  D = 1.0, **and** proposes a D ≈ 0 fan as the next move.
- **OK (reasonable):** recognises this fan cannot support a stacking call (wrong
  D / flavor-polarized) and declines the verdict + proposes lower-D data, even if
  it doesn't cleanly separate g = 1 from "tone at 4·F_L" or misses the multitone
  detail.
- **MISS (the failure this fixture exists to catch):** forces a confident
  stacking call from this fan — most likely **ABCA** by reading the single g = 1
  tone as an ABCA singleton *at* F_L (the 4× degeneracy misread), or forcing the
  multitone region into mixed domains. A confident verdict without the
  operating-point / degeneracy checks is a **protocol violation** (contract
  part 5), regardless of whether "ABCA" happens to match the device's true
  stacking — right answer, wrong (unlicensed) basis.

## Comparison to the rung-3a mechanical baseline

The free-scale mechanical evaluator, run on this fan (memo §5–6), returned
`inconclusive` / `non-onsager` in the multitone region and read g = 1 via the
calibration-fixed degeneracy audit — i.e. it did **not** force a stacking. The
question here is whether the *agent*, under the next-move pressure of the
harness, shows the same restraint.
