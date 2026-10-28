## Runs 6–7 — SdH spot checks (`sdh-spot-check`), D = 0, n_nom = +3.2 and −1.2 ×10¹²

*(Analysed on handoff; not landed by the previous instance.)* Both runs complete. The drain current is flat (9.8–9.9 nA), there is no leakage, and the channel peaks at 6 µV of the 50 µV range, so nothing clipped.

**Read:** strong quantum oscillations on both sides.
- **Run 6 (electrons):** Rxx falls to ~1–4 Ω in its minima from 1.5 T upward, so the Landau levels are well developed at 1.2 K. The minima sit at ν_nom ≈ 89, 72, 67, 54, 49, 41, 36, 31, 22, 18. That is *not* a ladder spaced by 4, so more than one Landau-level family or level crossings are present.
- **Run 6 FFT:** 7.1–7.5 T, plus content at 15/22/30 T. Above 4 T it collapses to 33 T ≈ F_L(n_nom) = 33.1 T. `sdh_onset` reads the 15/22/30 T peaks as harmonics of 7.1 T. The alternative is two independent pockets: the ABAB model pair is 7.5 + 25.6 T. **One trace can't separate these two readings** — the resolution is about 2.5 T and there is no n-dependence.
- **Run 7 (holes):** tones at 4.7, 6.6, 8.5 and 12.3 T, with onset down to 0.7 T.

**Not yet a stacking read.** The discriminator is how each tone scales with density — independent pockets vs k× a fundamental, and whether ΣF_i closes on F_L — plus the Landau-level crossing pattern. That is plan step 4: the Landau fan.
