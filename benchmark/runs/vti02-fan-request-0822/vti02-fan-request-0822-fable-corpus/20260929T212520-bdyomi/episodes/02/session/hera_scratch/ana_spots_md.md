## Runs 6 + 7 — SdH spot checks (`sdh-spot-check`), the Step-3 read: **electron side carries the fan**

**Run 6, electron, n = +3.2×10¹², D = 0 (F_L = 33.1 T), B 0→10 T.** Clean, ABAB-shaped tone set:

- **7.1 T** — dominant light tone, alive down to the 0.3 T record edge (**onset censored ≤ 0.3 T**; SNR 40 at the edge).
- **22.1 T** — heavy-tone candidate. Flagged `~3×7.1` by the tracker, but 3×7.1 = 21.3 vs 22.1 is ~2.6·δF (δF = 0.31 T) off an exact harmonic, and discarding it as one leaves 7.1 T alone against F_L = 33.1 — breaks the Luttinger sum badly (the investigation's harmonic-screen caution). Kept as the heavy pocket; the fan's n-dependence decides (a harmonic tracks 3.00·f_light exactly; the model heavy/light ratio sweeps 4.8→3.5 over n = 2.0→3.2×10¹²).
- **14.1 T** = 2×7.1 exactly — harmonic. **29.5 T** ≈ 7.1 + 22.1 = 29.2 — breakdown **sum-tone candidate** (symmetry-allowed in ABAB), sitting at 0.89·F_L.
- Pair sum 7.1 + 22.1 = 29.2 = **0.88·F_L** — a single global scale inside the lever-arm prior (0.8–1.2). Partition 0.24/0.76 vs model ABAB 0.22/0.78 at this n. **No tone at F_L = 33.1** → ABCA singleton disfavored on this side. Sub-4 T low-f peaks wander with detrender/cutoff (stability sweep, `hera_scratch/ana_spots.py`) — background residue, not claimed.

**Run 7, hole, n = −1.2×10¹², D = 0 (F_L = 12.4 T), B 10→0.3 T.** The recipe's stated near-CNP exception regime (model ABAB pair 5.9/6.5 T — close and balanced, beat-like): dominant ~6.6 T with a comb of mutually-inconsistent partners (4.7, 8.5, 9.4, 12.3), and the stability sweep wanders (top-3 peaks move ~1 T across reasonable cutoffs). Uninformative for the count at this density by design; **the hole side within our gate limits (|n| ≤ 1.27×10¹²) cannot leave the exception regime** — that is a coverage fact for the hedges, not a re-measure trigger.

**Take:** electron side is the fan side. Provisional lean ABAB (light 7.1 + heavy 22.1, sum 0.88·F_L, sum-tone at f₁+f₂) — **not a verdict**; the fan must show both branches tracking the ABAB F(n) curves (vs the trilayer ML+BL curves — adjacent-N dual overlay), the partition holding across n, and the 22.1 T tone diverging from 3·f_light. Handoff to the fan: onset ≤ 0.3 T (censored), Δ(1/B) = 1/(3·F_L(n_max)) ≈ 0.0101 T⁻¹, sr1 50 µV / τ = 0.3 s inherited.
