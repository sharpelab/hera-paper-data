# Where the ABAB light tone switches on at low field: evidence for the B_lo clip

For Aaron. vti-02 electron side, D = 0. The grader's window floor is B_lo = max(B_min, B_on,low(n)). Figure: `dingle_onset.png`.

## What the data show

**1. The light and heavy tones fade at about the same rate as B falls.** I fitted all five tones at once in each column (light, heavy, F_L, 2×light, heavy−light) over 1–4 T, with the ln A vs 1/B slope s free for each tone (panel A). Scaling by mass predicts s_light/s_heavy = m_l/m_h: 0.40–0.45 from the model, 0.49–0.70 from the 08-22 LK masses. Measured over n ≥ 1.8:

| fan | columns | s_light / s_heavy, median [IQR] |
|---|---|---|
| 08-25 r8 (50 nA) | 38 | 0.93 [0.85, 1.04] on the 12 cleanest; binned by n: 0.86–0.97 |
| 08-22 r8 (10 nA) | 40 | 0.92–1.07 (binned by n) |

- Fit check: I injected a light slope of −1.06 (the value the shared-lifetime assumption predicts) into the real residuals and got back −1.07 [−1.14, −0.90]. The fit can see the difference.
- Consistency check: the F_L slope (−4.3 to −4.9) is close to s_light + s_heavy (≈ −5). That is what a combination orbit should show, and it supports the light slope.

**2. So the quantum lifetime is not the same across bands.** At T_e = 1.2 K:

| masses used | T_D light | T_D heavy | τ_q light | τ_q heavy |
|---|---|---|---|---|
| model | 7.0 K | 3.0 K | 0.17 ps | 0.41 ps |
| LK (0.028 / 0.041–0.057) | 6.3 K | 3.0–4.2 K | 0.19 ps | 0.29–0.40 ps |

At T_e = 4 K the split grows: light 5.9 K, heavy 1.1 K. So the assumption behind the mass-scaled 0.45–0.6 T clip fails on this device, by a factor of about 2 in τ_q.

**3. The light tone's onset, from the fitted decay.**
- Method: I run the decay line down to where it hits the tracker's 5σ threshold. This is the same Gaussian matched filter as `sdh_onset`, with 3 periods, run at the reference fan's row spacing.
- Check against measured onsets:
  - Heavy-tone onsets, predicted vs tracked: within 5 % (median) where they are not censored. This is the same data, so it tests the noise model, not the physics.
  - Held-out record: the 08-21 r5 spot (10 nA, τ 0.1 s, down to 0.70 T) shows the light tone ending at 1.41 T. The 08-25 fits predict 1.36–1.67 T.

## Candidate clips (n = 1.8–3.05; values at n = 2 → 3)

| candidate | B_on,low | evidence for | evidence against |
|---|---|---|---|
| (a) mass-scaled, model ratio | 0.47 → 0.57 T | model masses; one measured onset | τ_q shared: refuted (point 2). The heavy onset it scales from is itself censored at 1.0 T in 32/47 columns of 08-25 |
| (a′) mass-scaled, LK ratio 0.70 | 0.79 → 0.91 T | measured masses | still assumes a shared τ_q |
| (b) Dingle, reference settings (50 nA, 0.3 s), noise as measured | 0.72 → 0.81 T (median 0.75) | measured light decay; predicts the held-out 08-21 onset | extrapolates 1/B from 1.0 to 1.4 T⁻¹ |
| (b-white) same, instrument noise only (0.41 Ω) | 0.47 → 0.59 T | best case physically possible | the as-measured noise is 5× white (other tones, QH structure) |
| (b-10 nA) Dingle at agent settings, 10 nA | τ 0.3 s: 0.76 → 0.95 T; τ 0.1 s: 0.83 → 1.12 T | the 08-22 fan's own fit at 10 nA / 0.3 s gives 0.89 T (median) | model-dependent |
| (c) observed floor | 1.0 T | no fan measured below 1 T; the light tone is still present at the edge | conservative; about 0.25 T above the reference-settings estimate |

**Dependence on acquisition.** The onset moves by Δ(1/B) = ln(SNR ratio)/|s_light|, with |s_light| ≈ 2.6 T, so about 0.39 T⁻¹ per e-fold of SNR.
- From 50 nA / 0.3 s to 10 nA / 0.1 s, the onset rises by 0.1–0.2 T with the noise as measured, and by 0.4 T with white noise only. Both models land at about 0.9 T at 10 nA.
- Doubling the rows buys about 0.08 T.
- Had the light tone decayed as slowly as mass scaling predicts, this sensitivity would be 2.4× larger.
- Every agent runs at 10 nA, so a clip tied to acquisition settings sits at about 0.85–1.05 T for every dev-set design. It then penalizes low SNR twice, because 1a already scores SNR.

## Dev-set scores that move (cols / tone cells)

| episode | B_min | own | 0.55 | (a) model | (a′) LK | (b) ref | (b) own acquisition | 1.0 |
|---|---|---|---|---|---|---|---|---|
| fable-corpus 192335 | 0.50 | 35/5.3 | 33/4.7 | 35/5.3 | 23/2.8 | 27/3.3 | 19/2.3 | 9/1.5 |
| fable-corpus 192335 #1 | 0.50 | 19/2.9 | 19/2.7 | 19/2.9 | 19/2.2 | 19/2.3 | 19/2.1 | 14/1.7 |
| fable-corpus 200401 | 0.50 | 37/5.4 | 35/4.7 | 37/5.4 | 25/2.8 | 29/3.4 | 14/1.8 | 10/1.5 |
| fable-corpus 232408 | 0.90 | 21/4.4 | = | = | = | = | = | 19/3.7 |
| opus-corpus rkg9dn | 0.80 | 54/5.3 | = | = | 54/5.1 | 54/5.2 | 54/5.0 | 43/3.6 |
| astra-none #1 | 0.80 | 3/3.6 | = | = | 3/3.4 | = | 3/3.3 | 3/3.0 |
| live 0824-r4 | 0.75 | 4/2.6 | = | = | = | = | 3/1.9 | 1/1.0 |

The other 24 fan-tier extractions don't change under any candidate. The ordering at stake: under (a) or 0.55, the two 0.5 T fable fans are level with opus rkg9dn on cells (5.3–5.4 vs 5.3). Under (b) they fall to 3.3–3.4 against its 5.2, and under 1.0 to 1.5 against 3.6.

## What would settle it

A single slow 1D sweep at n ≈ 2.8, 50 nA, τ 0.3 s, from 1.2 down to 0.4 T with ≤ 5 mT steps (the 08-22 r6 steps were 50 mT below 1 T, which aliases the light tone). It measures the light onset directly at the reference settings: about 1 h of magnet time.
