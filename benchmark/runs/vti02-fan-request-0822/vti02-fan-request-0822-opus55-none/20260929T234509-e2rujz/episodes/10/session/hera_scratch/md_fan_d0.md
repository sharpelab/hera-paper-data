## HERA — Step 4: Landau fan at D = 0 (`landau-fan`), n −1.25 → +3.25×10¹² fast, B 0 → 8 T slow

**Plan step 4** (`hera_scratch/plan.md`); this is the operator's requested stacking fan.

**What the spot checks settled.** Runs 6–7 (ana) show SdH down to 0.5 T at both spots. The n scale closes to F_L within about 1 %, so the run-5 calibration is used as is. Both spots show sub-F_L fundamentals: 0.22 F_L at +3.2×10¹², and 5.0 / 6.8 T at −1.2×10¹². That is a lean toward more than one Fermi surface, not a call.

**What the fan decides.** The spot checks cannot give the LL **degeneracy sequence and crossings near the CNP** or the **n-dependence of the tones**; the fan gives both:
- **ABCA:** a 16-fold zero-energy manifold (a dominant ν = ±8 gap, then ±12, ±16 …), no family crossings at D = 0, and a single F = F_L tone.
- **ABAB / ABCB:** two LL families with a crossing pattern, and two tones whose ratio moves with n.

It also shows whether region B (the run-5 ridge electron-doped by 0.43×10¹²) contributes a second fan with its apex near n ≈ −0.43.

**Grid**
- Fast axis: TG and BG co-swept along the calibrated D = 0 line, n from −1.25 to +3.25×10¹² in 0.025 steps (181 pts).
- Resolution: 4-fold LL gaps are resolved from about 0.8 T up, single-fold from about 3 T up.
- Slow axis: B from 0 to 8 T in 0.1 T steps (81 rows), uniform in B, so LL lines are straight.
- Per-column 1/B FFT is valid over 3–8 T for F ≲ 45 T (ΔF ≈ 5 T). Run 6 remains the high-resolution high-n record.

**Coverage trade**
- The hole side stops at −1.25 because the TG −0.3 V limit caps the D = 0 line at −1.28.
- The field stops at 8 T, not the 10 T cap: 8–10 T would add 20 rows (≈ +1 h 35 m), and at n = +3.2 that range is already on disk (run 6).

**Readout**
- fast_delay 1.0 s at τ = 0.3 s / 24 dB. The lag is uniform because every row runs in the same direction, so it shifts the n-intercept by less than one step and leaves ν slopes untouched. slow_delay 3 s after the gate flyback.
- sr1 starts at 10 µV (1 kΩ FS) with the `autorange_sr830s` hook, `lower_lim` = 10 µV. That floor stops QH zeros from chasing the range down; the hook ranges up only where the CNP goes insulating in field.
- Leak guard: >1 nA on either gate interrupts the run and parks the gates.

**Price** (from measured overheads, not priors)
- Per point ≈ 1.2 s (run 5: 1.17 s/pt, plus the autorange reads).
- Per row: 181 × 1.2 s + field step (3.1 s + 0.1 T at 0.137 T/min = 47 s, runs 6/7) + flyback about 4 s + 3 s + autorange settles ≈ 4.6 min.
- 81 rows ≈ 6 h 15 m; headline ≈ 6 h 40 m with the usual ~7 % overrun.

**Ends** with the field at **8 T** (step 5, the finite-D fan, rides it down) and the gates parked at 0 V.

**Checkpoints**
- **(1) First rows, about 10 min.** Row 0 (0 T) must reproduce run 5's D = 0 cut: CNP near n ≈ 0 at about 250–300 Ω, the region-B shoulder near −0.43, I_drain ≈ 10 nA, gates at pA. Abort on a rail, a dead channel or leakage.
- **(2) About 2 T (row 20, ≈ 1 h 35 m).** Fan lines from the CNP, ν assignment from slopes (0.0242·ν ×10¹² per T), and whether a second apex exists. If no LL structure is resolved at |n| < 1.5, abandon or re-plan.
- **(3) About 5 T (row 50, ≈ 3 h 50 m).** If the sequence and crossings are already unambiguous, consider truncating to save up to 1 h.
