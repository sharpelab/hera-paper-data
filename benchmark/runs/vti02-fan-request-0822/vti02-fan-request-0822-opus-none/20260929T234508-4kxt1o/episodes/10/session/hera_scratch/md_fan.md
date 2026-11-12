## HERA — Step 4: Landau fan at D = 0 (`landau-fan`), n = −1.20 … +3.20×10¹² × B = 0 → 10 T

**Why this, now (plan step 4).** The spot checks (runs 6, 7 — analysis landing
in ana alongside this) say the measurement is easy: SdH onset **below 1 T**,
oscillation amplitude 50–300 Ω against **≈ 2.5 Ω** per-point noise, no clipping
at 50 µV, gate leakage ≤ 2×10⁻¹⁰ A over 3.5 h of field sweeping. What they
*cannot* say is the thing the campaign turns on. Run 6 (n = +3.2×10¹²,
F_L = 33.1 T) resolves a 7.1 T fundamental carrying 2×/3×/4× harmonics at
14.1 / 22.1 / 29.5 T. Either reading is consistent at one density: a **single**
Fermi surface plus harmonics, or **two** Fermi surfaces (7.1 T light +
≈ 26 T heavy, summing to F_L) — which is exactly the ABCA-vs-ABAB question. A
harmonic sits at exactly k·F₁(n) at *every* density; a second Fermi surface has
its own n-dependence, its own band-edge onset density, and must satisfy
Σ F_i = F_L(n). One density cannot separate those; a fan does.

**What the fan measures.** R_xx over the whole realized D = 0 line against
field, i.e. the three model-free discriminators at once: (i) how many frequency
families exist and whether they close on Σ F_i = F_L(n); (ii) the Landau-level
gap-line slopes dn/dB = ν·e/h, which give the filling sequence and the
degeneracy per family directly off the map; (iii) electron–hole symmetry and
the ν = 0 behaviour at the CNP. **Bonus, and not a small one:** those ν lines
are an absolute quantum-Hall lever-arm check, so this run upgrades c_tg from
the 9.5 nm *geometry prior* (run 5 calibration, still uncalibrated in absolute
scale) to a measured number — without which the Σ F = F_L closure test is only
relative.

**Both regions in one map.** Run 5 found two CNP ridges (A, slope 0.773; B,
slope 0.691, neutral at n_A = −0.43×10¹²) — a series mosaic under the single
hardwired pair B_1 − B_2, not something a rewire could separate. In a fan they
appear as **two fan origins**, at n_A = 0 and n_A ≈ −0.43×10¹², so one map
gives the brief's per-region verdict for both. Region B's lever arm is 11 %
different, so its own density scale is read off its own origin and line slopes,
not assumed from A's.

**Design and its trades.** Fast axis = (V_tg, V_bg) co-swept along D = 0
(`multimegasweep`), n = −1.20 … +3.20×10¹² in 119 points (Δn = 0.0373×10¹²);
the endpoints are **exactly the two spot-check densities**, so runs 6 and 7 are
built-in cross-checks on the fan's first and last columns. Slow axis = B,
0 → 10 T in 81 rows of 125 mT, uniform in B — deliberately not uniform in 1/B:
the LL gap lines are straight in (n, B) and their slopes are the primary,
model-free read, and I already hold two fine-ΔB traces (runs 6, 7 at 10/20 mT)
for precision FFT work. **Coverage trade, stated:** uniform-B sampling at
125 mT means the per-column 1/B FFT is a *secondary* read, valid above ≈ 3 T
(Nyquist 36 T there) with resolution ΔF ≈ 4.3 T over 3–10 T — enough to
separate 7 T from 26 T, not enough for a precise partition. Buying that
precision across all 119 densities would mean a 1/B-uniform fan, i.e. giving up
the straight-line fan read; plan step 5a buys it instead at 2–3 selected
densities on the ride down from 10 T, ~45 min each. Δn resolves the ν = 4 gap
with 5 points at 2 T and 26 at 10 T, but only ~2.6 at 1 T — below ~1.5 T the
map reads as SdH-in-n, not as resolved levels, by design.

**Dwell, priced against a known τ.** sr1 is at τ = 0.3 s / 24 dB/oct
(operator-set, read at bring-up). `fast_delay = 1.5 s` = 5τ: knowingly under
the ~9τ hard-settling floor, which costs ≈ 1.3 points of smoothing along n and
a *rigid* lag in n — rigid because every row is swept in the same direction at
the same rate, so **the LL line slopes (the ν read) are untouched**; only the
sharpest minima lose amplitude. 9τ dwell would cost +2.6 h for that amplitude.

**Sensitivity.** sr1 at 100 µV = 10 kΩ full scale (run-5 lesson: size to the
map's worst corner, not the 1D peak). R_CNP at D = 0 is 297 Ω at B = 0, so
30× headroom — but if a ν = 0 gap opens, the n ≈ 0 **column** may soft-clip
above 10 kΩ at high field. That is an accepted, bounded loss: 1–2 columns of
119, flagged by the clip detector, and a clipped ν = 0 is itself a result worth
re-measuring cheaply at the end rather than paying 2× noise everywhere now.

**Price.** 81 rows × (119 × 1.65 s + 55 s field ramp + 3 s magnet settle + 2 s
slow_delay + ~3.5 s gate flyback) ≈ 5 h 50 m computed from *this* session's
measured rates — 1.098 s/pt fast-axis (run 5) and the blocking 0.137 T/min ramp
(runs 6, 7) — carried at **≈ 6 h 20 m** for the 5–10 % over-run this session has
shown. The 73 min of magnet traverse is a fixed cost paid once. **Ends at 10 T
with the gates at n = +3.20×10¹²**, which is where plan step 5a wants to start
its ride down — no re-traverse.

**Checkpoints** (all read off the armed `hera-watch` digest, no re-forming
partial TSVs): **(1) first 2 rows, ~9 min** — signal level and no rail, leakage
under the 1 nA trip, gate vectors tracking, and the per-row rate against the
prediction above (reprice or abort). **(2) B ≈ 2 T, ~1.5 h** — is there fan
structure beyond the CNP ridge; if the map is featureless the read is
resolution-limited and the run is wrong, kill it. **(3) B ≈ 5 T, ~3.5 h** —
interim analysis on the landed rows: line slopes → ν sequence, family count,
whether two origins are resolving. **(4) completion.** A hardware leak above
1 nA on either gate trips the run from inside the sweep hook.
