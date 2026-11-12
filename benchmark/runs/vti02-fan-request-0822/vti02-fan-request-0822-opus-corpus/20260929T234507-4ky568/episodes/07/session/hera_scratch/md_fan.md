## HERA — Step 4: Landau fan (`landau-fan-vti`), electron side, D = 0 — the stacking call

Investigation Step 4. The spot checks (runs 6–7, analysed in ana) settled the side
and handed over the acquisition settings; what they could **not** do is separate a
harmonic comb from a stacking template on a single density. Run 6 (n = +3.2×10¹²,
F_L = 33.1 T) is in the quantum-Hall regime — minima at R ≈ 0 from ~2 T — so its
FFT is a comb at 7.3, 14.8, 22.3, 29.4 … T, every member flagged k × 7.3. The
fundamental at **0.22 F_L** sits exactly on the model's ABAB *light* tone (7.2 T at
this n), and 7.3 T alone cannot carry the density (that would need a 4.5× global
rescale, far outside the 0.8–1.2 lever-arm band) — so a heavy partner exists, the
model puts it at 25.9 T, and 25.9 T falls between the comb's 3rd (21.9) and 4th
(29.2) members. **The discriminator is n-dependence** — a harmonic tracks k·f(n)
exactly, a real pocket follows its own Onsager curve — which is exactly what a fan
supplies and a single column cannot. Hole side is out: it dead-ends at
−1.27×10¹² (TG −0.3 V), inside the near-CNP exception regime.

**Design (all levers at their floor — `landau-fan` step 1 cost-floor check; the
arithmetic is the preceding ana cell).** `B_lo` = **1.00 T**, the run-6 record's
Nyquist-valid low edge where the carrying tone is still `censored` — a valid lower
bound, and going lower is unnecessary: δF = 1/(1/1 − 1/10) = **1.11 T** already
separates the 21.9/25.9 T pair by 3.6 δF and the 25.9/33.1 T pair by 6.5 δF, so a
low-field extension would buy resolution the claim does not need at ~2.3× the cost.
`n_max` = **3.2×10¹²**, the D = 0 line's electron reach (V_tg = +0.9836 V, 16 mV
under the limit); `n_min` = 0.8×10¹² gives the 4× density lever the branch-tracking
needs. **B axis uniform in 1/B** (per-column SdH-FFT fan): 91 rows, Δ(1/B) = 0.0100
1/T = **3.02 samples/period at F_L(n_max)** (floor 2). **n axis** 61 points,
Δn = 0.040×10¹² = **2.42 points per ray** at B_lo (2.10 even under a 15% lever-arm
scale error). Sensitivity held at **50 µV** (5 kΩ FS): the worst corner — low n ×
high B — projects to 600–1350 Ω from the run-5 R(n) anchors × the measured MR
(run 6 ×9.3, run 7 ×4 at the matched low-|n| anchor), i.e. 0.12–0.27 of full scale.
`fast_delay` = **1.8 s = 6 τ** (τ = 0.3 s, 24 dB/oct): the n-axis carries the
extracted signal, and under-settling there mixes adjacent columns, which are only
half a ray apart — it would attenuate the very tones being counted.

**Price** (calibrated on this session's run 5: 0.098 s/pt read overhead at
nplci = 1, 5.8 s row turnaround): 5551 points × 1.9 s = 2.93 h grid +
1.09 h field traverse + 0.13 h turnaround = 4.15 h, **≈ 4 h 35 m realistic** (the
session's runs have come in ~10% over), plus a 7 min bare ramp 0 → 1 T. The fan is
**measurement-dominated** (`landau-fan-vti` cost model), so the grid, not the
magnet, is what the levers buy back.

**Endpoint, deliberate:** ascending 1 → 10 T, so positioning costs 7 min rather
than the 73 min a descending fan would need from B = 0, and the run **ends at
10 T** — where the Verify step after this (LK mass split, `temperature-dependence-vti`
Flavor B) wants to start its ride-down. Gates park at 0.

**Checkpoints** (`hera-watch data --next --follow` armed before execution):
*first rows* — leakage against the 1 nA trip, rail/clip against the 5 kΩ FS, R
level against run 6's 56 Ω at n = 3.2 / B ≈ 1 T, and T holding at base; abort there
if any fail. *Then ~hourly* — with B as the slow axis a partial fan carries only
the low-B rows, so the interim read is honestly limited to signal health and
whether LL rays are resolving in n; the per-column FFT needs the full B range and
waits for completion.
