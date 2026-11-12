# Step 7 — the call: QC0426 is ABC (rhombohedral) trilayer

Landau fan `data/7` (D=0, hole, n=−3→−6.5e12 × B 0→8 T), per-column 1/B FFT → F(n).

## 1. Per-region verdict (STYLE strength scale)
- **sr2 / B4–B5: ABC (strong)** — a single SdH tone tracking F_L(n), F/F_L = 1.07±0.09 over |n|=4.3–6.5e12.
- **sr1 / T3–T4: ABC (strong)** — single tone tracking F_L, F/F_L = 1.04±0.04.
- **Both regions agree → single-stacking ABC across the probed contacts (not a mosaic).** The
  earlier single-density (data/6) impression of an ABA pair (15+42 T) in sr1 was a **short-window
  FFT artifact** — it fails the FFT-stability check and does not survive the fan's longer records
  and density-tracking (STYLE rule 14 fork, resolved).

## 2. Evidence
- **The tone set vs F_L**: one dominant frequency F(n) = (1.0–1.1)·F_L, both channels, across density
  — a single Fermi surface carrying the *full* gated density (the ABC template). An ABA BL tone
  would sit **below** F_L (F/F_L<1) with a resolved ML partner; **neither is present**.
- **No resolved ML partner** (searched; absent above the per-column δF≈5–7 T / SNR≈4 threshold).
- **Harmonic screen**: the ~2F peak (e.g. ~100 T at n=−5e12) is the 2nd harmonic, not a pocket.
- **Independent support**: D-induced gap at CNP (CNP-R rises with |D|, gate map data/1) — *consistent-with* ABC.
- Artifacts: `fan_fn.png` (F(n) + F/F_L); per-column tones table in session record.

## 3. Confidence + hedges
**Strong ABC.** Hedges (why not *decisive*):
- **Onsager forward-model overlay UNAVAILABLE at the operating density** — `fs_count_b0` F(n) is
  numerically clamped above |n|≈3.5e12 (solver-domain TODO), so the ABA/ABC curve overlay could not
  be run at 4–6.5e12. The call rests on the **model-independent Luttinger argument** (F=F_L ⇒ single FS).
- A **very small ABA ML partner** (f_ML ≲ 5–10 T, below δF; ML fraction is often small) cannot be
  strictly excluded — ABA-with-tiny-ML would mimic ABC within the ~7% lever-arm scale prior.
- The **model-valid low-|n| columns (<4e12) were too noisy** (short SdH record at T_e≈8 K) to cross-check.
- **Hole side / D=0 only**; the electron-side both-signs check was not run.
- **LK-mass split unavailable** (temperature-dependence blocklisted this session).
- Absolute scale is geometry-prior (~10–15%); ratio is data-calibrated.

## 4. What would firm it (toward decisive)
Extend the model solver to ±8e12 (README TODO) → run the Onsager overlay; resolve/exclude the ML
partner with a longer 1/B record (mK rig: colder → less damping → lower onset → finer δF, or higher
field); electron-side fan (both-signs); high-field Streda/Chern complement once an ABC LL model exists
(Step 6); LK effective-mass split (needs temperature-dependence).

## 5. Outcome
A **confident, feature-level-evidenced call (ABC), not a "cannot tell"** — and not a bare lean.
ABC is the interesting outcome (flat-band / rhombohedral correlated-physics candidate): the device
warrants a **low-T (mK) campaign** with the D-gap systematics and the firming steps above.
