## Run 8 — the FS-count fan: B 8 → 1 T uniform in 1/B, τ = 300 ms, 101 × 57

`recipe: measurements/landau-fan-vti.md`, investigation **Step 4/5**.
Operator-directed. B slow **8.0 → 1.0 T descending, 101 rows uniform in 1/B**
(Δ(1/B) = 0.00875 T⁻¹, finer than the recipe's preferred 1/(3·F_L) = 0.01057);
n fast **+1.20 → +3.05 × 10¹² cm⁻², 57 columns** along the session-measured D = 0
line; τ = 0.3 s / 24 dB/oct → 2.10 s dwell; I_bias = 49.2 nA; sr1 at 100 µV.
5757 points, 4.6 h, complete. Usable record **δF = 1.143 T**.

Three parameter choices, each aimed at a named failure of the run-7 spot check:
**τ = 300 ms** for 2.5× the SNR (partner tones had reproduced in only 3–9 of 18
extraction choices); **57 columns** so the Luttinger sum becomes a trajectory test
across density rather than a two-point coincidence; and **uniform 1/B** so that
splitting the record at its 1/B midpoint yields two halves of *equal* δF = 2.29 T
— which is what makes the F_L-tone origin test readable at all. Run 7's uniform-B
record split into halves of δF 2.5 and 10 T, and the 10 T half could not separate
tones 8 T apart, which is exactly why that test came back "suggestive".

Raw first, then per-column FFT with the harmonic screen, then the Verify suite.
