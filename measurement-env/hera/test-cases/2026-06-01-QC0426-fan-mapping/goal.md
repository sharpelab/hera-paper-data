# Goal

> "Figure out the stacking order of this trilayer-graphene flake — is it ABA
> (Bernal) or ABC (rhombohedral)? Map the Landau-fan / quantum-Hall structure vs
> carrier density and displacement field; the fan pattern and its D-dependence
> are the fingerprint that tells ABA from ABC. Get the fan at the charge-neutral
> D = 0 line working, then sweep it across D to read off the stacking."
>
> — expert framing (Qingrui, QC0426 trilayer-graphene device, VTI cooldown,
>   2026-06-01; classification purpose confirmed 2026-06-09)

**Why this campaign exists:** QC0426's stacking order was *unknown* — the sample
was loaded into the VTI specifically to **classify ABA (Bernal) vs ABC
(rhombohedral)** trilayer graphene, which have distinct Landau-fan signatures and
displacement-field dependence. (Outcome: the VTI didn't get cold enough for a
definitive call; Qingrui suspects **ABA**. The fans in this fixture are visibly
washed out at the VTI's ~1.2 K base — consistent with "not cold enough.")

This is the experimentalist's stated intent for the section of measurements
captured here. An offline HERA test should treat this as the campaign-goal
context an analyst would receive at the start of the session.

The section captured spans the cooldown's full arc: instrument bring-up and
gate-range calibration, a 0 T TG-BG gate map, the first **B-n Landau fan at
D = 0** (with and without Si-gate screening), a block of contact and 6 T
characterization, and finally the systematic **D-series of Landau fans**
(D = 0.25, 1, −1, −0.25, −0.5). The fixture carries **three decision frontiers**
drawn from this arc (see `README.md` and the `frontiers/` files); the one built
here is:

- `after-density-cut` (COVERAGE) — device characterized, a 0-field density cut
  along the D = 0.25 gate-line in hand → sweep it into a Landau fan and map the
  fan across a series of displacement fields.

It is a clear-answer *decision* frontier (what experiment next), not a depth/rigor
probe.
