# Updated stacking call — QC0426 (after resolution fixes + F(n) fan)

*Supersedes the first call (cells 14–16, "cannot tell — resolution-limited"). The first call was on data taken at 2 mV lock-in sensitivity (coarse ADC digitization) and 50 mT field steps (main-tone aliasing). Two fixes this session — voltage sensitivity 2 mV→200 µV and field sampling 50→12.5 mT — gave clean, eye-visible QO and a usable F(n) fan. (Mid-session the drain contact T7 died under high |n| + Si=+50 V; recovered by swapping drain T7→B7, device otherwise healthy, 9/15 contacts alive.)*

## 1. Per-region verdict (STYLE strength scale)
Region: main Hall bar, **electron side** (n = +2→+8×10¹²), D=0, drain B7.
- **sr1 (T3–T4): ABC — weak-to-moderate** (consistent-with a single full-density Fermi surface; no second Onsager-tracking branch).
- **sr2 (B4–B5): ABC — weak-to-moderate** (same; channels agree).
- **Hole side: not measured at this resolution → no verdict** (band-structure prior actually favors the hole side for a resolvable ML tone — a gap).

## 2. Evidence
- **Clean SdH QO** at 200 µV / 12.5 mT — eye-visible, ΔR_xx ~±20 Ω at B>1.5 T (ana cells 47, 50).
- **F(n) Onsager map (file 39, cells 52–53): the dominant tone tracks the full-density line F = n·h/4e across n = 2→8×10¹² on both channels; no clean second branch on a distinct Onsager curve.** → one Fermi surface carrying the full Luttinger density.
- **The one-density "two-tone" hint did not survive F(n)**: file 38 (n=+8×10¹²) showed a ~69 T tone + a ~16 T tone summing to ≈ full density (looked ABA), but the second peak does **not** track its own Onsager curve with n → it is a harmonic / second-region / window artifact, **not** a Fermi surface. F(n) was the decisive test.
- **Hall lever-arm** (n_Hall/n_gate = 0.95, cell 17–18) → absolute density scale confirmed to ~10 %, so "tracks full-density" rests on a sound scale.
- **(n,D) calibration** data-grade (c_bg/c_tg = 1.298, file 1).

## 3. Confidence + hedges
**Weak-to-moderate ABC lean.** Hedges:
- The *big* tone is intrinsically near-degenerate (ABC-single ≈ ABA-BL ≈ full density). The true discriminator is the *small* ML tone, which we do **not** cleanly resolve; its **absence** as a tracking branch leans ABC, but absence is weaker than presence — the ML tone could sit below our amplitude/resolution floor (T_e ≈ 8 K damping; δF ≈ 1.7 T; onset ≈ 1.2 T).
- **Electron side only**; hole side not measured at 12.5 mT.
- F(n) map **noisy above n ~ 6×10¹²**; per-column peak-pick unreliable → relied on the 2D |FFT| ridge.
- Single region (2 pairs agree); no mosaic survey at this resolution.
- **No LK-mass split** (`temperature-dependence` blocklisted) — the decisive 1-band-vs-2-band cross-check was not done.

## 4. What would firm the call
- **Hole-side fan at 12.5 mT** + per-channel triage (the band-structure prior for a resolvable ML tone).
- **Harmonic / FFT-stability audit** of the low-F weight + a proper ridge-tracking F(n) extraction.
- **LK-mass split** (`temperature-dependence` Flavor B; blocklisted here) — two masses → two bands (ABA), one → one (ABC). The decisive cross-check.
- High-field **Streda/Chern offset** as an independent complement; lower T / higher mobility to drop below the ML cyclotron gap.

## 5. Bottom line
**Consistent-with ABC (single full-density Fermi surface) — weak-to-moderate**, a real improvement over the prior resolution-limited "cannot tell." The dominant carriers occupy one pocket carrying the full Luttinger density, with no second Onsager-tracking branch resolved across n. **ABA is not decisively excluded** (the small ML discriminator remains below clean resolution, and ABA-BL ≈ full-density within our noise). So this is a *lean*, not a decisive call; the honest deciding tests (hole-side fan + LK mass at this resolution) are next-session items. Per the contract: a confident binary call is still not warranted on feature-level evidence — **"weak ABC lean, ABA not excluded"** is the calibrated statement.

*Method note (the session's main scientific lesson): the original "cannot tell" was never about the physics — it was instrumental resolution. Lock-in sensitivity matched to I_bias×R (200 µV, not 2 mV) and field sampling fine enough to keep the high-n main tone Nyquist-clean (12.5 mT, not 50 mT) were both required before SdH/F(n) became interpretable. And one density can mislead (file 38 looked ABA); F(n) is what discriminates.*
