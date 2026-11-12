# THE CALL — vti-02 stacking (tetralayer-stacking-fs-count, Step 7)

## 1. Per-region verdict

- **Channel B_1−B_2 (the only wired 4T pair; probes regions A + B in series): ABAB (Bernal) — strong.**
- Region B separately (the faint parallel CNP ridge, +0.43×10¹² electron-doped vs A): **uninformative on its own** — no tone set attributable solely to B was resolved (expected B-region tones at ×1.13 the A-frequencies fall within δF of the A set at low weight); its presence does not perturb the A read.
- No other regions are addressable this cooldown (T_1–T_4 dead, hardwired configuration).

## 2. Evidence (all runs this session; per-tone coordinates at n_cal = +3.2×10¹², D = 0 unless stated)

1. **Pair partitioning F_L** — tones **7.3 T** and **22.0 T** (run 6, FFT [1, 5.5] T, δF 1.2), sum 29.3 T = F_L(g = 4) at one global scale **0.886** (partition 0.25 / 0.75; ABAB model 0.23 / 0.77 at this n). Luttinger check: closes at scale 1 of the calibrated density × 0.886.
2. **Onsager overlay across density** (run 8 fan, 61 columns, n_cal 1.6–3.25×10¹²): both branches track the **ABAB F(n)** curves under the single scale; sum = F_L(n) column-by-column; dual overlay vs trilayer ML+BL fails by trajectory (adjacent-N check passed — the transport supports N = 4).
3. **F_L-tone origin (mandatory discrimination): combination/breakdown, not a pocket** — (a) a **difference tone** f_heavy − f_light appears at every fan column with a non-Onsager (n-flat) trajectory; (b) B-window split: sum/heavy amplitude 0.55 → 1.03, diff/light 0.27 → 1.6 with rising B (run 6); (c) LK mass of the F_L tone 0.051–0.069 mₑ ≥ heavy branch, toward m_l + m_h.
4. **LK mass split** (runs 9–14, rungs 1.2–30 K): light 0.028 ± 0.002 mₑ (= ABAB model), heavy 0.041–0.057 (window fork; model 0.061), 2×light harmonic confirmed by mass; beat exclusion decisive (light < heavy).
5. **Degeneracy audit:** g = 4 scale 0.886 independently confirmed by the hole-side symmetry-broken integer ladder (run 7: scale 0.80–0.92) and the fan's QH minima spacing (0.87–0.88 at 8–10 T) — no flavor polarization at the operating point.
6. Hole side (run 7, n_cal = −1.2×10¹²): content at/below F_L×0.886 consistent with the ABAB near-CNP balanced pair; **consistent-with** only (4–6 periods, δF ≈ 1.2 on 4–7 T tones).

## 3. Confidence and hedges

- **Strong, not decisive**: the heavy-branch mass is extraction-window dependent (0.038–0.057; the [3.5, 7] T window cannot separate heavy from sum, δF = 7 T) — the φ² mass-ratio check reads 1.4–2.0 vs the predicted 2.2, a **fork**, not a failure; every window preserves the ordering m_light < m_heavy < m_F_L-tone.
- **Absolute layer number**: transport supports N = 4 (pair partition 0.20–0.25, not the trilayer 0.11–0.15; ν = 8, 12, 16-specific low-field ladder not separately audited — the 4L LL ladder is stacking-blind anyway). Optical N-assignment not independently checked this session.
- **Mosaic caveat**: one 4T pair; regions A + B in series, B's stacking is **not** established — a different stacking in B with weak weighting cannot be excluded (its tones would be below our floor). The call is for the region dominating the B_1−B_2 channel.
- **ABCB**: no supra-linear light Dirac branch seen; resolvable only for f ≳ 2.5 T (δF floor) at low n — a J = 1 partner below that is not excluded (citation-grade template anyway).
- Absolute n and D carry the geometry-prior scale (now pinned to 0.886 ± 0.03 by three independent reads); D = 0 is set by the R_CNP(D) symmetry (±0.01 V/nm).

## 4. What would firm it

- The heavy/light mass ratio at φ²: an LK ladder over 1.5–10 T at 10 mT (δF 1.8 T per half-window), ~3 h/rung, or the same at lower electron temperature.
- A second, independent 4T pair (operator rewiring at the breakout) → per-region resolution of the A/B mosaic.
- Magneto-Raman or optical stacking ID on the flake for region-resolved cross-check (`stacking-raman-transport-fusion`).
- A ν = 8, 12, 16 low-field ladder audit for an independent N = 4 check.

## 5. Protocol statement

A reasoned "cannot tell" would have been a valid outcome; this call is made because every mandatory Verify item — TSV-first, forward-model dual overlay with one global rescale, F_L-tone origin, LK masses with beat exclusion, degeneracy audit, adjacent-N, FFT stability, Luttinger sum — was executed and cited above. Blocklist respected; no reference data consumed (first-session branch).

## Next (investigation `## Next`, ABAB-confirmed)

Conventional tetralayer: QH degeneracy-lifting / even-N interaction physics is the remaining campaign value (the device shows full symmetry breaking by 5 T at low n — run 7); flat-band/correlated ABCA physics is **not** available on this flake's measured region. Deprioritise accordingly.
