**Read — runs 6 & 7.**

**Acquisition.** Both sides show strong, *well-developed* SdH at base T: the minima
reach R ≈ 0 (run 6 from ≈ 2 T up, run 7 from ≈ 1.5 T), i.e. the device is in the
quantum-Hall regime over most of the window, not the weak sinusoidal-SdH regime.
That is the single most important fact for the read that follows — **a spiky,
strongly non-sinusoidal waveform generates a rich harmonic comb**, and the comb is
frequency-degenerate with the stacking templates. Channel fill is 0.10–0.12 of the
5 kΩ full scale: no clipping, `sdh_onset` flagged no soft-clip truncation.

**Onset is *not* measured on either record.** The carrying tone is `censored@edge`
in both (run 6: 7.3 T, SNR 96, alive at the window's low edge 1.00 T; run 7: 7.0 T,
SNR 56 at 0.70 T). Oscillations persist below where the *grid* can be trusted, so
each `onset_b` is that record's low edge — a **valid lower bound for a fan's
`B_lo`**, not a measured die-off (`landau-fan` step 1, lever 1).

**Run 6 (electron, n = +3.20×10¹², F_L = 33.1 T) — one column cannot decide.**
The peak set is a comb: 7.3, 14.8, 22.3, 29.4, 43.7, 58.6, 88.4 T, and `sdh_onset`
flags every member above the first as k × 7.3 T. Two facts pull against each other:

- 7.3 T is **0.22 F_L**, and the forward model's ABAB *light* tone at n = +3.2×10¹²
  is 7.2 T (fraction 0.217) — a match well inside δF = 1.11 T. So the fundamental
  sits exactly where the ABAB light pocket is predicted.
- But 7.3 T **cannot be the only pocket**: a lone tone carrying all the density
  would need F = F_L = 33.1 T. Reading 7.3 T as the whole Fermi surface implies a
  global density rescale of 4.5×, far outside the 0.8–1.2 lever-arm band — a red
  flag, not a fit (`Verify: Onsager forward-model overlay`). **Something carries
  the other ~78% of the density**, and the ABAB heavy partner is predicted at
  25.9 T — which lands between the comb's 3rd (21.9 T) and 4th (29.2 T) members.
  The observed peaks sit at 22.3 and 29.4 T, i.e. on the comb, not on 25.9 T; but
  a genuine heavy tone within ~1–2 δF of a strong harmonic is not separable here,
  and the recipe forbids screening a tone as a harmonic when doing so breaks the
  partition sum.

So the electron spot check is **uninformative on stacking by itself** — and it is
uninformative for a *nameable* reason: harmonic/template frequency degeneracy on a
single density. The discriminator the investigation prescribes is the one this
record structurally cannot supply — **n-dependence**: a harmonic tracks k·f(n)
exactly, a real pocket follows its own Onsager curve. That is the fan.

**Run 7 (hole, n = −1.20×10¹², F_L = 12.4 T) — suggestive, not decisive.**
Tones at **5.0 and 7.0 T** (both censored at the record edge) plus a strong
**12.3 T** (SNR 112, 0.99 F_L). 5.0 + 7.0 = 12.0 ≈ F_L closes the Luttinger sum,
and the model's ABAB hole pair at n = −1.2×10¹² is ≈ 5.3 / 7.1 T — a close match;
the 12.3 T tone at F_L is then exactly the **symmetry-allowed ABAB inter-block
breakdown / sum tone** the investigation says to *expect* rather than treat as
exotic. Consistent-with ABAB, and nothing more, because: (i) n = −1.2×10¹² is
inside the near-CNP hole exception regime the investigation flags, where the pair
is close and balanced and beat-like; (ii) 7.0 − 5.0 = 2.0 T is only 2.7 δF
(δF = 0.75 T here); (iii) one column, one density — the hole side of the D = 0
line dead-ends at −1.27×10¹² (TG −0.3 V), so it cannot be pushed into the regime
where the templates separate. **No hole-side fan is possible at design density.**

**Decision — the fan runs on the electron side.** It is the only side that reaches
|n| ≳ 2–3×10¹², where the ABAB pair and the ABCA singleton separate (0.22/0.78 F_L
vs 1.00 F_L), and it has the better-resolved record (δF = 1.11 T over B ≥ 1 T vs
0.75 T but capped at F_L = 12.4 T on the hole side). Inherited to the fan:
**B_lo = 1.00 T**, **Δ(1/B) = 0.010 1/T**, **sr1 at 50 µV**, and the 6τ settling
floor on the gate axis. Design arithmetic in the next cell.
