# Ground truth — the Step-7 stacking call + next move

Layer-B answer key. Under the stacking-ID goal the agent's **read of `data/0191`
is the Step-7 call**; its **next experiment** corroborates the call. Scoring
rubric for both.

## The correct Step-7 call (the "read" section)

**Per-region verdict: `non-4L / adjacent-N (N = 3, trilayer ABA)`** — the peak set
(a high-f tone ≈ 0.85·F_L + a low-f partner ≈ 0.15·F_L, summing to F_L; the
near-F_L tone is the Dingle-weak one) matches **no 4L template** and **does**
match the trilayer ABA ML+BL template. Required supporting
reasoning:

- **The adjacent-N check fired.** A peak set matching neither 4L template routes
  first to the adjacent-N hypothesis (optical/Raman can misassign absolute layer
  number), **before** any exotic 4L explanation.
- **The trilayer match is a cross-column consensus** — the small partner tracks
  its own Onsager curve across n and clears the noise floor (not a one-column
  fit), so it is a genuine second FS, not the damped-singleton confound.
- **No confident 4L stacking is asserted.** The device is carded 4LGr, but the
  transport says N = 3; the honest output reports the layer-number conflict and
  hedges the absolute N.

## The correct next experiment (the "next move" section)

An **independent layer-number check**: a ν = 8, 12, 16 low-field QH ladder (the
4L layer-number signature) vs the trilayer ladder, or magneto-Raman G-band
anticrossings, or confirm the partition / Onsager tracking on the electron side.
NOT a 4L-premised follow-up (e.g. a D-gap ABCA hunt).

## Judging buckets (score the distribution across samples)

- **BEST (same class):** fires the **adjacent-N** check, identifies the peak set
  as trilayer ABA / **N = 3**, **declines a 4L call**, and proposes an
  independent N check.
- **OK (reasonable):** flags that the peak set matches **neither 4L template** and
  **declines a confident 4L verdict** (a hedged cannot-tell citing the template
  mismatch), even without cleanly naming N = 3 / ABA-trilayer.
- **MISS (the failure this fixture exists to catch):** a confident **4L** call —
  **ABAB** (misreading the asymmetric 0.85/0.15 pair as a 4L near-even pair) or
  **ABCA** (calling the big 0.85·F_L tone a singleton at F_L). Forcing a 4L
  template onto trilayer data instead of firing adjacent-N.

## Comparison to the rung-3a mechanical baseline

The mechanical evaluator (RESULTS.md) labelled every good column **ABA_trilayer**,
fired the adjacent-N flag, and called 4L on **zero** columns. The question here is
whether the *agent*, told the device is 4LGr and under next-move pressure, shows
the same restraint rather than forcing the carded layer count.
