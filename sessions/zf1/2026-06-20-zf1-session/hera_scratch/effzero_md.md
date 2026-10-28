## HERA — effective-zero-field calibration (trapped-flux hint)

**Why this, not the bias-spec (hold cell 44).** My Step-1 map was taken at `magnet.field()≈0` — the *controller's* nominal zero. With the device card's **~2 mT trapped flux**, the sample actually sat at ~2 mT, not true zero. These BLG-WSe₂ proximity SCs live on the mT scale (refs sweep B_eff 0–3 mT), so a fragile SC could have been **suppressed across the whole map** → "no candidate" is not yet safe. The true operating field is the SC's own field maximum (≈ where the trapped flux is cancelled), not the controller's zero (investigation Step 3).

**What:** Rxx(B) at a moderate hole point **(Vtg −4.79, Vbg 1.06; n≈−2.5e12 cm⁻², D≈−0.4 V/nm; 4.7 kΩ, clear of the k_bg≈0 feature)**. Two **one-sided** segments per the session field discipline (never increase |B| through 0 while measuring): ramp to **−8 mT**, settle, sweep **−8→0**; then ramp to **+8 mT**, settle, sweep **+8→0**. Stitched → Rxx(B) over ±8 mT bracketing zero from both sides. 0.2 mT steps (41 pts/segment), AC 0.5 nA, Rxx = `sr830_2`.

**Reads:** (1) the **MR symmetry center / weak-(anti)localization feature = true B=0** → the trapped-flux offset (transfers to the whole map); (2) a sharp **Rxx dip at the effective zero ⇒ a field-suppressed SC** revealed; (3) magnet ramp_rate (read live) + thermal settle behavior, to price a follow-up 2D Rxx(n,B) search.

**Forks:** dip at B_eff → SC candidate found, characterize (bias-spec/Fraunhofer at B_eff). Smooth symmetric MR, no dip → no SC at this (n,D); next is a 2D (n,B) search across density at the corrected zero before any not-SC call.

**Discipline/safety:** |B|≤8 mT ≪ 100 mT cap (validator-guarded). Heating is worst near 0 (flux-motion loss) — `temperature` is fp'd + the per-point delay=1 lets it settle; watch the live MR + T. No `volt.step` change. First magnet energisation this session — if interrupted mid-ramp the supply keeps ramping to its last target (re-issue `magnet.field(0)` to recover). **~6–8 min.** Magnet ends at 0; gates stay at the op point for the follow-up.
