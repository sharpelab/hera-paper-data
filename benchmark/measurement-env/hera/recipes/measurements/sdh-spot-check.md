# SdH spot check

## What
A fixed-(n, D) magnetic-field sweep over a **low-field window**, designed to resolve
Shubnikov–de Haas / quantum-oscillation **frequency content** at one density — the
onset field and the tone frequencies — by FFT in 1/B. Mechanically this is a
`field-sweep-1d` (see it for the Station / sweep / fp / plot call surface); what
makes it a *spot check* is the design discipline below — the field range, 1/B spacing
Δ(1/B), and settling are chosen to resolve the tones cleanly, and the read is the 1/B
FFT.
It is the cheap 1D precursor to a `landau-fan`: one density, but **full per-point
quality**.

## When
- **Before committing a `landau-fan`.** A spot check pins the **onset** (sets the
  fan's B-range), the **observed tone frequencies** (confirm/correct the fan's
  Δ(1/B)), and the **settling/sensitivity** the fan inherits. A fan is the dense
  version; a couple of clean spot checks de-risk it — and can answer the question
  outright (`investigations/trilayer-stacking-fs-count.md` Step 3).
- Whenever a `field-sweep-1d` or `gatemap` showed QO-like wiggles and you want the
  frequency content at a point, not the whole (n, B) plane.

## Why
A spot check is cheap because it is **one density (1D), not because it is
low-quality**. Its whole value is being acquired *well* — at the settling floor and
Nyquist on the fastest tone — so a clean spot check can be decisive on its own and a
noisier fan cannot overturn it (`landau-fan`). Two knobs carry the quality:

- **Sampling.** The fastest tone sets the finest 1/B period. The reference frequency
  **F_L = (h/g·e)·n** (g = 4) — what a single four-fold pocket carrying all the
  density would give — is an upper bound on the fastest tone; Nyquist it. Undersampling
  the fast tone folds its aliases into the low-frequency band, where they masquerade
  as a small/slow tone (Verify).
- **Settling.** A swept-point dwell has a floor near the lock-in time constant
  (dwell ≥ k·τ; k ≈ 5 at 6 dB/oct, 7–10 at 24 dB/oct). Under-settling **attenuates
  the oscillation amplitude itself** (the filter cannot track the QO) — benign on a
  smooth slope, but it *buries a small tone* (Verify). The floor is non-negotiable
  when the target is a weak tone.

## Recipe
1. **Density + range.** Pick the density — high |n| gives the most periods and the
   clearest tones. Sweep a field window **[B_lo, B_hi]**; the sampling grid follows
   the magnet class:
   - **Field moves cheap** (non-blocking magnet): sample **uniformly in 1/B**
     (`field_invB`) — constant points-per-period, FFT the raw points (no resample).
     `B_lo` is a small positive floor (~0.1–0.3 T) below the expected **onset** (the
     lowest B where oscillations emerge once the MR background is subtracted) —
     uniform-1/B is densest in B at low field, so it captures the onset for free.
   - **Blocking rate-limited magnet** (traverse dominates wall-clock): sample
     **uniformly in B** with **ΔB = Δ(1/B)·B_lo²** (Nyquist held at the low-B edge;
     `sdh_fft` resamples internally). Same wall-clock — the points ride the traverse —
     with ≳30× the per-period averaging at high B and no blind ramps between sparse
     high-B points. ΔB scales as B_lo², so put `B_lo` just below the expected onset,
     not at a deep floor.
2. **Δ(1/B) from F_L.** Compute F_L = (h/4e)·n and Nyquist-resolve it: Δ(1/B) ≤ 1/(2·F_L)
   (prefer 1/3). Set N from the window: N = (1/B_lo − 1/B_hi)/Δ(1/B) + 1 uniform-1/B,
   N = (B_hi − B_lo)/ΔB + 1 uniform-B. This Δ(1/B) (and N) is what a committed fan
   inherits.
3. **δF from the record.** The tone resolution is set by the usable 1/B record above
   onset: **δF = 1/(1/B_onset − 1/B_max)** — tones closer than ~δF merge; trust a
   split only past ~2·δF. On high-T_e rigs the onset, not the field cap, sets δF:
   once 1/B_max ≪ 1/B_onset, raising B_max buys little — the lever is the
   density/side with the lower onset. Compute δF against the tones the claim must
   separate before sweeping.
4. **Lock-in.** Set sensitivity so full scale ≈ I_bias × R_target — a signal at a
   few % of range is coarse-ADC digitized (the grainy-FFT failure). Set the dwell at
   the settling floor (Why); read τ and the filter slope, do not guess them.
5. **The sweep.** Run it as a `field-sweep-1d` (its Recipe is the call surface):
   build the Station, ramp the gates to (n, D), `s.sweep(mag.field, B_vec,
   delay=dwell)` with the step-1 grid, fp the temperature(s) and every lock-in X/P,
   plot the live MR and gate-current leakage.
6. **FFT read.** Re-form Rxx from the TSV (rendered PNGs alias).
   - **Onset** — `hera.analysis.sdh_onset(R, B)` returns an `SdhOnset`: `onset_b` is
     the low-B edge of usable oscillation content (minimum over the tracked tones —
     a light tone that outlives the dominant one carries it), `clip_high_b` the high
     edge. `tones` holds each tone's own track: `freq`, per-tone `onset_b`,
     `snr`/`amp` curves over `b_centers`, `delta_f(b_max)` (that tone's usable-record
     resolution), and flags — `censored` (still above threshold at the record's low
     edge: `onset_b` is the record edge, not a measured die-off), `revived`,
     `marginal`, `near_residual`, and the bidirectional harmonic pair
     `harmonic_of` (this tone sits at k× a lower tone) / `harmonics` (freqs of
     tones sitting at k× of this one — a comb member is flagged from both ends
     regardless of which is stronger). Print `on.summary()` in the read
     cell. Pass `r_full_scale = sensitivity / I_bias` so a soft-clipped channel
     truncates the analysis window (with a warning) instead of feeding a flat-topped
     record to the FFT. Failure raises `SdhOnsetError` naming what was untrackable —
     that is a read result (no usable oscillations), not a prompt to eyeball.
   - **FFT** — `hera.analysis.sdh_fft(R_grid, B, *, b_range=(cutoff, B_max), bg_degree=5)`
     takes `R_grid` as `(n_B, n_fast)` — pass a single trace as `R[:, None]` — removes
     the MR background with a degree-`bg_degree` polynomial **in B** (the background is
     smooth in B, not 1/B), then FFTs in 1/B per column, and returns
     `(freqs, spec[n_fast, n_freq])` with `freqs` in Tesla. It needs a field range wide enough that
     the polynomial captures the background without absorbing the oscillations.
     `cutoff ≥ onset_b`, and often **above** it (Verify). Read the **tone frequencies**
     against F_L.

## Verify
- **Settling — under-settling buries a small tone.** A dwell below the floor
  attenuates the oscillation amplitude (the filter can't track it). On a smooth slope
  that's a benign uniform lag; when the target is a small/weak tone it *erases* the
  feature. Non-negotiable for a weak-tone hunt; bend it only for a slope read on a
  strong signal.
- **Sampling — an undersampled fast tone aliases down.** If Δ(1/B) under-samples the
  fastest tone (≈ F_L), its aliases fold into the low-frequency band and masquerade
  as a small/slow tone. Nyquist the *fast* tone even when the target is the slow one
  (worked case: Examples).
- **Grid-change reproduction separates tones from aliases.** A real tone survives a
  change of sampling scheme (uniform-B vs uniform-1/B); an alias moves with the grid.
- **FFT stability sweep.** Vary `bg_degree` and the window; a real peak **sharpens**
  as the 1/B record lengthens, an alias/artifact **wanders**.
- **Onset is read from the background-subtracted data, not the FFT.** It is the
  low-field point where oscillations emerge in ΔRxx(B) (the MR background removed), not
  a quantity the FFT returns. It is a **lower bound** on the FFT low-field cutoff:
  residual background near the low-B end inflates the slowest tones, so raise the cutoff
  above the onset until the slow-tone amplitudes stop shrinking. Report the onset — it
  sets a fan's B-range and tracks quantum mobility (a rise on a later cooldown is a
  device-quality regression).

## Examples
- *(our-measurement)* — a fine-step spot check resolved two tones (a main tone + a
  low-frequency partner), where a same-session fan run at a coarser B-step and
  under-settled did not. An earlier 4× coarser step had under-sampled the main tone,
  folding its aliases into the small-tone band. The worked case for "acquire the
  spot check well, *then* commit the fan."

## Next
- **Clean QO, tones resolved** → run a `landau-fan`, inheriting this spot check's
  Δ(1/B), settling, and onset; or take a couple more spot checks across density for a
  cheap preview of the n-dependence.
- **Two tones at D ≈ 0** → `investigations/trilayer-stacking-fs-count.md` (the
  FS-count combinatorics).
- **Tone amplitude vs T wanted** (effective mass) → `temperature-dependence`
  Flavor B.
