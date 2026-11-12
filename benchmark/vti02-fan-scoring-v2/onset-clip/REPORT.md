# Onset clip: report (agent, 2026-09-23)

The one-pager for Aaron is in `onepager.md`, the figure in `dingle_onset.png`, and the
rescore in `rescore.md`. This file covers what the one-pager leaves out.

## Headline

The mass-scaled clip rests on a shared quantum lifetime, and the data refute that. The light
tone's Dingle slope matches the heavy tone's: ratio 0.93 [0.85, 1.04] in 08-25 r8, and
0.86–1.07 by density bin in 08-25 and 08-22. A shared τ_q predicts 0.40–0.45 with model
masses or 0.49–0.70 with the 08-22 LK masses. At T_e = 1.2 K the fitted lifetimes are:
- light: τ_q 0.17–0.19 ps (T_D 6.3–7.0 K)
- heavy: τ_q 0.29–0.41 ps (T_D 3.0–4.2 K)

Running the fitted decay forward to a 5σ matched filter gives the light-tone onset:
- 50 nA / 0.3 s with the noise as measured: ≈ 0.75 T (0.72 → 0.81 T at n = 2 → 3)
- 10 nA: ≈ 0.85–1.0 T

This forward model reproduces the tracked heavy onsets to within 5 %. On the held-out
08-21 r5 spot (0.70 T floor) it predicts 1.36–1.67 T, and the observed onset is 1.41 T.

## Method notes

- The only usable data below 1 T with the light tone is 08-21 r5. It is excluded as unusable
  for fitting and kept as the held-out check.
  - 08-22 r6 aliases below 1 T (50 mT steps).
  - The 08-23 ramps have 38–40 rows.
  - 08-25 r5 has 13 rows.
  - 08-24 r5 has a weak light tone at low n.
- The five tones (light, heavy, F_L, 2·light, heavy − light) are fitted jointly per column,
  each with its own decay slope: 24 parameters. Injection recovery: −1.06 → −1.07 and
  −2.5 → −2.44. The F_L slope ≈ light + heavy, which fits a combination orbit.
- `sdh_onset` can't track the light tone inside a 1–8 T record: at F ≈ 6 T its 3-period
  window fits only 1–2 windows.
- The tracked heavy onsets are 1.31 T at 50 nA (only 16/57 columns; the rest are present at
  1.0 T) and 1.54 T at 10 nA. The F_L onsets are 1.54 / 1.93 T. At 50 nA the tracker's noise
  estimate (~2.1 Ω) takes in other-tone signal: instrument noise is ~0.4 Ω. So onsets
  read pessimistically there, and the doc's "heavy 1.1–1.4 T" is partly an artifact.
- The amplitude in ohms is the same at 10 and 50 nA, so 50 nA shows no heating.
- Acquisition dependence: ~0.39 T⁻¹ of 1/B per e-fold of SNR.
  - From the reference to 10 nA / 0.1 s the onset rises 0.1–0.4 T; both noise models land
    near ~0.9 T.
  - Doubling the rows lowers it by ~0.08 T.
  - A clip that depends on acquisition penalizes SNR a second time (1a already scores it).

## Caveats

- T_e is taken as 1.2 K; the 08-22 LK ladder bounds it at ≤ 4 K, and the conclusion holds at
  either.
- The curves are fitted for n ≥ 1.8 only. Below that, and on the hole side, they are
  extrapolated.
- The fits cover 1–4 T. Candidate (b) extrapolates 1/B from 1.0 to ~1.4 T⁻¹.
- The 08-21 r5 check crosses sessions: same device and contacts, matched on actual n.

## A direct measurement would settle it

One slow 1D sweep at n ≈ 2.8, 50 nA, τ 0.3 s, from 1.2 → 0.4 T in ≤ 5 mT steps: about 1 h of
magnet time.
