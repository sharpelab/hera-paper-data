## HERA — Step 4: Landau fan (`landau-fan-vti`), electron side, D = 0, n 2.2→3.2×10¹², B 0.65→10 T

**Side: electron — decided on reach, not taste.** The D = 0 line inside the committed
validators spans n = −1.27 … +3.23×10¹² (TG binding at both ends), so the **hole side can
never reach the investigation's |n| ≳ 2–3×10¹² design band**. Run 7 (hole, n = −1.2×10¹²)
confirms it empirically: tones 3.9 / 7.0 T against δF = 0.77 T and F_L = 12.4 T — the
near-CNP semimetal-overlap regime the investigation names as the low-|n| exception, where
the pair is close, balanced and not resolvable into a partition. Run 6 (electron,
n = +3.2×10¹²) is the clean one: **7.1 T** (SNR 40, persists to the record's low edge),
**22.9 T**, and **30.0 T**, with tone-specific onsets 1.36–1.91 T for the fast tones.

**What run 6 already says, and what it can't settle.** 7.1 + 22.9 = 30.0 — a pair summing
to a tone. Model (`hera/models/tetralayer_fs_count`) at +3.2×10¹²: ABAB (7.31, 25.78)
summing to F_L = 33.09 T; ABCA a singleton at 33.08 T; trilayer ABA(ML+BL) (1.92, 31.17).
One **global** density rescale of **0.907** (30.0/33.09, inside the 0.8–1.2 lever-arm prior)
puts the measured pair on the ABAB curves — partition 0.237/0.763 vs the model's
0.221/0.779 — and leaves the 30.0 T tone sitting exactly at the rescaled F_L. **The
adjacent-N alternative is already excluded at this density**: the trilayer partner would be
1.9 T, 3.7× off the measured 7.1 T. So the peak set is ABAB-shaped, but a tone at F_L with
resolved partners is the confound the investigation calls *expected* (ABAB inter-block
breakdown is symmetry-allowed) — it is **not** a reason to read ABCA, and it is not
discriminable from one density. That discrimination is this fan's job.

**What the fan buys:** (1) partition robustness — f₁(n) + f₂(n) = F_L(n) across 33
columns, algebraic and model-free, which a coincidental one-density match will not survive;
(2) the **F_L-tone origin** B-window split (breakdown/mixing strengthens with B, a real
pocket keeps its Dingle envelope); (3) per-branch F(n) trajectories for the mandatory dual
ABAB/trilayer overlay. Per the investigation, the binary ABAB-pair vs ABCA-singleton call
needs exactly (1) + (2). The last fan column is **n = +3.2×10¹² on a different B grid**
(uniform-1/B here vs run 6's uniform-B), so the Verify "grid-change reproduction" check
against run 6 comes free.

**Design — every lever at its floor, one fan (`landau-fan` step 1).**

| lever | value | the binding number |
|---|---|---|
| n window | 2.2 → 3.2×10¹², 33 pts | n_min is the design band's 2.0×10¹² floor **in true density** (2.2 × 0.907) |
| Δn | 0.03125×10¹² | ray-Nyquist floor at B_lo = 0.03143×10¹² (≥2 pts per g = 4 ray spacing) |
| B window | 0.65 → 10.0 T, 144 rows, uniform in 1/B | B_max = session cap |
| Δ(1/B) | 0.01006 1/T | 1/(3·F_L(n_max)) = 0.01007 — at the preferred floor, Nyquist 0.01511 |
| δF | 0.70 T | heavy-vs-F_L separation at n_min = 3.53 T = **5.1 δF** (≥2 needed) |
| partner periods at n_min | **5.1** | ≥5 required — this is what sets B_lo |
| B-window split | halves δF = 1.39 T | heavy-vs-F_L = 2.5 half-δF at n_min, so the origin split is live across the whole window |
| fast_delay | 2.1 s = **7τ** | measured τ = 0.3 s at 24 dB/oct (STYLE rule 12 floor; asserted live) |
| sensitivity | 50 µV = 5 kΩ FS at 10 nA | worst corner (n = 2.2, B = 10 T) ≈ 700 Ω |

**B_lo is not the `sdh_onset` value, deliberately.** `sdh_onset(run 6)` returns
`onset_b = 0.30 T` with the **carrying tone censored at the record's low edge at every
cutoff tried** (0.3 / 0.8 / 1.0 / 1.2 T) — and run 6's sub-1 T segment is *undersampled*
(max Δ(1/B) = 0.476 vs the 0.0151 Nyquist need there), so tones tracked below 1 T are not
trustworthy. 0.30 T is therefore a **lower bound on the onset, not a measurement**. B_lo is
set instead by the claim's own resolution requirement (≥5 partner periods at n_min), which
lands at 0.65 T — safely above the bound, and not paying for the 185 extra rows a literal
B_lo = 0.30 T would cost (+6 h).

**Dynamic range.** Fixed 50 µV for the whole fan, inherited from run 6. Worst corner is
structurally low-n × high-B: run 5 gives R(n = 2.2, D = 0, B = 0) ≈ 68 Ω, run 6 gives a
*measured* MR factor of 10.5× at 10 T → ≈ 700 Ω, 14 % of full scale. Three-fold headroom
even if MR triples toward the CNP. Graininess at the low-B end is measured, not feared: run
6 ran at 1–10 % FS and returned tone SNRs of 40–89. Saturation is the asymmetric failure, so
the cell carries a **soft-clip trip** (5 consecutive points ≥ 0.95 FS aborts) — a
flat-topped column is harmonically corrupted across its *whole* FFT and no B-window
recovers it.

**Cost, calibrated on this session (no inherited constants).** t_pt = 2.20 s — run 5
measured 1.098 s/pt at fast_delay = 1.0 with this exact 7-channel fp set at NPLC 1, i.e.
0.098 s of readback overhead, plus ~0.03 s for the second paired gate write. Grid
144 × 33 × 2.23 = 2.94 h; bare traverse 9.35 T / 0.137 T/min = 1.14 h; per-row fixed
(settle_s 3 s + slow_delay 1 s + 0.79 s gate flyback) = 0.19 h. **Total 4.27 h → 4h45m with
10 %.** Field is the slow axis precisely because runs 6/7 both measured 3.07–3.09 s of
per-point overhead on top of the bare ramp rate — sampled per-point, field costs 40 % more
than it does as a monotonic traverse. `slow_delay = 1` (not 3) because `magnet.field()`
already dwells `settle_s = 3 s` after each blocking ramp; double-dwelling would buy nothing.

**Coverage trade — what this fan does not cover.** (a) The **hole side entirely**: reach
caps at |n| = 1.27×10¹², so a ~4 h hole fan would buy a read that is resolution-limited by
construction. Not bought. (b) **n < 2.2×10¹²**: the partner tone falls under the 5-period
floor there; reaching n = 2.0×10¹² needs B_lo = 0.59 T and Δn = 0.0285×10¹² → 159 × 43 =
**+1.9 h** (6.1 h total). Deferred, not rejected — watching the partition collapse toward
0.95·F_L at low electron density would *strengthen* an ABAB call, but the investigation says
the binary needs only the partition sum plus the F_L-origin split, both of which this window
delivers. (c) B_max sits at the 10 T session cap.

**Preconditions asserted in-cell** (state the fan assumes but does not set): thermometry
logfile live and advancing; T_sample 1.0–1.5 K; |B| < 0.05 T (state0 after the handoff
close-out, so the fan starts where the magnet sits and ends at 10 T — never re-traversing);
V_si = 0; gates at 0; PS heater on and output enabled; and — because the whole dwell
derivation rests on them — **sr1 τ = 0.3 s, filter slope 24 dB/oct, amplitude 1.0 V**
(I_bias = 10 nA). The (V_tg, V_bg) vectors are **asserted** inside the validators rather
than passed through `sanitize_tg_bg`: silently dropping out-of-range points would break the
uniform Δn grid the n-axis Nyquist check rests on.

**Checkpoints.** *First rows* (rows 1–8, B 0.65–0.68 T, ~10 min): R across the n-line should
read ≈ 68 → 55 Ω (run 5 at B = 0), gate currents ≲ 220 pA, T_sample ≈ 1.17 K, sr1 phase
stable, nothing railed — the cheapest kill is in the first minute. *Then periodically* off
the `hera-watch` digest: **row 55** (B = 1.0 T, t ≈ 1.2 h) data health + partner-tone
emergence; **row 105** (B = 2.0 T, t ≈ 2.4 h) first meaningful per-column FFT — run 6's fast
tones had their own onsets at 1.36–1.91 T, so this is where continue/abandon is actually
decidable; **row 121** (B = 3.0 T, t ≈ 2.9 h); completion at row 144. Unattended guards in
the cell: leak trip 1 nA, fridge-event trip at T_sample > 1.6 K, soft-clip trip as above.

Ends at **10 T with the gates parked at 0 V** — the follow-up (LK mass split, or a firming
fan) rides the magnet down rather than re-traversing.
