# vti-02 hole side: can the fan grader score it? (agent, 2026-09-26)

Read-only analysis of existing data; nothing in the repo, the grader or git was touched, and no replay or agent runs
were made. Densities are |n| in 1e12 cm^-2 (actual frame). "Halder" is the grader's tone model (`box.py` `_T`, column
`F_light_Halder_ABAB`, n < 0 rows).

## Bottom line

**No: there isn't enough to grade the hole side with the box scheme.**
- The hole light tone is not established in any trace. The live-check rules find it in 14–33 % of hole column-windows at
  1.5–3.5 light-tone periods, against 50–84 % on the electron side at the same periods.
- The F_L / heavy split is found once in 58 hole column-windows, against 41–79 % on the electron side.
- The reachable hole range, |n| ≤ 0.92–0.94 (V_tg ≥ −0.3 V at D = 0), holds F_light 1.6–2.8 T: at most two independent
  light-tone points in the best window, against CAP 5.
- What the hole data do carry is the heavy (dominant) tone, at 0.70–0.82 F_L, with the partition predicted by Halder to
  rms 0.03. ABCA would put that tone at F_L. Using it as evidence needs an absolute density frame, which the box does not
  score.

Keep "only electron-side columns count" for the freeze; grading the hole side needs new data (Q7).

## Q1. Inventory

Each multi-density sweep holds exactly one hole density (column 0; the others are electrons), so the split gives one
hole trace per sweep.

| trace | kind | n_frame | grader \|n\| (e-side n_scale) | reference \|n\| (source) | B (T) | grid | I, τ | pts |
|---|---|---|---|---|---|---|---|---|
| 08-22 r7 | 1D spot | −1.200 | 1.063 (0.886) | 0.907 (own F_L-like tone); QH ladder 1.011 | 0.30–10 | uniform-B 20 mT | 10 nA, 0.3 s | 486 |
| 08-24 r4 c0–c14 | fan columns | −1.036…−0.059 | 0.933…0.053 (0.90) | grader frame (LL fan agrees ≤ 2.5 %) | 0.76–6.0 | 1/B, 40 rows, dF 0.87 | 10 nA, 0.1 s | 40 each |
| 08-24 r5 c0 | split from 5-density sweep | −0.800 | 0.720 (0.90) | 0.726 (own F_L tone 7.51) | 0.51–6.0 | 1/B, 100 rows, dF 0.55 | 10 nA, 0.1 s | 100 |
| 08-25 r7 c0 | split from 5-density sweep | −0.900 | 0.855 (0.95) | 0.842 (QH ladder ν 8,7,6) | 1.5–6.0 | uniform-B, dF 2.0 | 50 nA, 0.1 s | 187 |
| 08-23 r6 c0–c36 | continuous-ramp fan | −1.40…−0.06 (geometry prior) | — | LL fan: 1.14…0.03 | 0.6–8.0 | 38 rows, 0.2 T each | 10 nA, 0.1 s | 38 each |

- **Usable for tones:** 08-22 r7, 08-24 r5 c0, 08-25 r7 c0, and 08-24 r4 c0–c7 (the 8 columns at |n| ≥ 0.49).
- **08-23 r6:** LL frame only. Its worst-row Nyquist is 1.3–1.5 T (5.6 T over [1.5, 8] T, 11–13 T over [2, 8] T); one
  column shows a tone in 1 of 8 choices.
- **Excluded:** 08-23 r7 (D − D0 ≈ +0.20 V/nm); 08-25 r5/r6 (13 and 6 field rows, D varying along the gate axis);
  08-21 r6/r7 (gate cuts at a fixed 10 T); every B = 0 run. 08-21 has no hole B-sweep.
- Full table: `inventory.csv`.

## Q2. Tones, identities, frame

Consensus tones are those found in at least half of the window × background choices at contrast ≥ 4 (`tones.csv`).
Identities use Halder at the reference |n|.

| trace | tones (T) | identity and evidence |
|---|---|---|
| 08-22 r7 (0.907) | **6.53–6.59** at low field (12/12 choices; 7.0–7.4 in windows up to 4.5 T, pulled by 9.4) | **heavy**: Halder 6.81 |
| | **9.36–9.38** (sdh_onset contrast 268–392) | **F_L-like**: 6.59/9.38 = 0.703 against Halder 0.727; merges with heavy in every FFT window up to 4.5 T (dip 0.5–1.0) |
| | 4.72 (onset 1.03 T); 14.83 | F_L/2 (4.69); F_L + 2·light (14.5)? neither secure |
| | 2.2–2.5 (4/12, contrast 11) | light candidate (Halder 2.56); the regression scan also peaks at 3.36 (SNR 5.6), so not established |
| | 1.0–1.75 | low-F residual / series-segment band |
| 08-24 r5 c0 (0.726) | **5.76** (5.20–6.22; 12/12, contrast 18) | **heavy**: Halder 5.99 |
| | **7.51** (6/12, contrast 6) | **F_L** (7.50) |
| | 11.41 (12/12) | 2·heavy |
| | 1.12 (6/12) | 2 dF: residual band; light regression-scan SNR ≤ 3.1, so no light tone |
| 08-25 r7 c0 (0.842) | **6.54** (8/8, contrast 25, 132 Ω) | **heavy**: Halder 6.53 |
| | 13.5 (7/8) | 2·heavy; F_L and light unresolved at dF 2.0 |
| 08-24 r4 c0–c5 (0.62–0.93) | 5.4–6.9 (4–8/8, contrast 4–11) | **heavy**, within −0.4…+0.1 T of Halder heavy; F_L sub-threshold (contrast 2–3.3 at c1–c3, within 0.15 T of F_L); no light tone (scan SNR ≤ 2.8) |
| 08-24 r4 c6–c10 (0.30–0.56) | 4.6 → 3.9 | stops scaling with n: 0.81–0.85 F_L at 0.49–0.56, 1.08–1.24 F_L at 0.30–0.37; not a single-channel Onsager tone near the CNP |

- The dominant hole tone is the heavy tone everywhere; F_L shows as a tone in 2 traces; light in none.
- 2·heavy appears everywhere; 08-22 r7 carries the most combination content and a symmetry-broken QH regime above
  about 5 T, so hole windows should stop at about 4.5 T there.

**Frame** (`frames.csv`, `ll_frames.csv`)

| trace | grader | own F_L tone | QH / LL | tone ÷ grader |
|---|---|---|---|---|
| 08-22 r7 | 1.063 | 0.907 | 1.011 (QH ν 7,6,5, spread 0.3 %) | **0.853** |
| 08-24 r5 c0 | 0.720 | 0.726 | 0.714 (LL hole fit) | 1.008 |
| 08-24 r4 c1 / c2 | 0.870 / 0.807 | 0.857 / 0.798 (sub-threshold) | 0.847 / 0.788 | 0.985 / 0.989 |
| 08-25 r7 c0 | 0.855 | — | 0.842 (QH ν 8,7,6; ν 7,6,5 = 0.720 excluded by the heavy tone) | 0.985 (QH) |

- LL-fan lever arms are side-symmetric: 08-23 hole s 0.935 ± 0.029 against electron 0.925 ± 0.007; 08-24 0.850 ± 0.025
  against 0.873 ± 0.006. What differs between sessions is the CNP offset n0 (−0.18 / −0.155 in the 08-23 geometry frame,
  +0.03 / +0.04 in 08-24).
- The electron n_scale holds on the hole side to ≤ 1.5 % for 08-24 and 08-25.
- 08-22 needs its own frame. The scale-only 0.886 puts r7 15 % high against its own tones (a hole scale of 0.756 on the
  session frame, or s 0.886 with n0 ≈ −0.18); the session's offset frame (0.8625, n0 −0.10) gives 0.949 (+4.6 %). The QH
  ladder (recorded first, 6–8.4 T) and the SdH tones (0.6–4.5 T) disagree by 10 %; the instantaneous heavy frequency
  shows no monotone drift (6.2–7.8 T scatter), so the discrepancy is unresolved.

## Q3. Onsets

Two walks: `sdh_onset` (f_min 1.0) and a joint matched-filter walk (`jointwalk.py`: the same 5σ walk and gap rule, with
all tones fitted together so heavy cannot leak into F_L). Results in `onsets.csv`, `onsets_joint.csv`.

| tone | onset (T) | trace, \|n\|, acquisition | status |
|---|---|---|---|
| heavy | 0.69 (b_hi 10) / 0.83 (b_hi 4.5); sdh_onset 0.71–0.73 | 08-22 r7, 0.91, 10 nA / 0.3 s | uncensored; alias edge 0.49–0.51 |
| heavy | ≤ 0.51 | 08-24 r5, 0.73, 10 nA / 0.1 s | censored at the record edge |
| heavy | ≤ 0.76 | 08-24 r4 c0, c3–c7, 0.49–0.93, 10 nA / 0.1 s | censored at the record edge |
| F_L | 1.27 | 08-22 r7 | uncensored |
| F_L | 0.75 | 08-24 r5 (max SNR 16) | uncensored |
| F_L | 1.52 / 1.79 / 1.55 | 08-24 r4 c0 / c2 / c4 (max SNR 6–10) | uncensored; high because first-difference σ on 40 rows is 12–25 Ω |
| F_L | ≤ 1.2–1.34 | 08-24 r4 c5–c7 | censored |
| 2·heavy | 1.0–2.1 | all | — |
| light | not measurable | — | a 2-period filter needs 1.6–5.2/T of record at F_light 0.8–2.7 T; the 1/B records span 1.15–1.81/T. 08-22 r7 (3.2/T) walks to 0.66 T at 2.63 T, but the tone itself is not established |

- No resolvable |n| trend: only one heavy onset is uncensored. Every hole record below 1.5 T is at 10 nA; the only
  50 nA trace (08-25 r7) starts at 1.5 T.
- Electron reference: light floor 0.75 T (Dingle extrapolation, reference acquisition); heavy 1.31 / 1.54 T and F_L
  1.54 / 1.93 T (50 / 10 nA). On the hole side heavy lives to at least as low a field, and F_L sets in lower.

**Recommended hole floors:** light window 0.75 T (range 0.5–1.0): no hole light onset is measurable, the hole heavy tone
persists to 0.51–0.83 T at 10 nA, and electron light and heavy share one Dingle slope. Split window 1.0 T (range
0.75–1.3): F_L onsets 0.75 T (08-24 r5) and 1.27 T (08-22 r7); the 1.5–1.8 T values from 08-24 r4 are noise-inflated.

## Q4. Does Halder predict the hole partition?

Yes, at |n| ≥ 0.6. p = 1 − F_heavy / F_L (`partition.csv`).

| basis | N | Halder bias / rms | corpus bias / rms |
|---|---|---|---|
| frame-free (own F_L tone), one row per trace | 5 | +0.027 / 0.032 | −0.099 / 0.100 |
| frame-free, all heavy-frequency choices | 7 | +0.013 / 0.029 | −0.113 / 0.116 |
| frame (QH or grader), \|n\| ≥ 0.6 | 5 | +0.024 / 0.035 | −0.107 / 0.109 |

- Observed against Halder: 08-22 r7 0.25–0.30 / 0.273; 08-24 r5 0.18–0.23 / 0.203; 08-24 r4 c1 0.253 / 0.258; 08-25 r7
  0.249 / 0.252.
- Below 0.6 Halder fails: observed 0.14–0.18 at |n| 0.49–0.56 against 0.02–0.07, matching the non-scaling tone in Q2.
- Consistent with model-reconcile's held-out hole rmse 0.022. The heavy frequency's window dependence (6.5 against
  7.0 T in 08-22 r7) is the dominant ±0.02 systematic.

## Q5. Where the hole side can discriminate ABAB from ABCA

- Halder's F_light: 0.10 T at 0.50, 0.35 at 0.55, 0.67 at 0.60, 1.04 at 0.65, 1.67 at 0.75. The light pocket empties at
  |n| ≈ 0.45–0.50 (Shi, graphite and B within 0.15 T; the corpus model keeps 0.84 T at 0.50). Below that both stackings
  give one tone at F_L; the data don't show that limit cleanly (0.81–0.85 F_L at 0.49–0.56).
- In the best window, 0.75–10 T (W 1.23/T, dF 0.81): the light tone at ≥ 2 periods needs F_light ≥ 1.62 (|n| ≥ 0.74);
  the split at ≥ 2.5 periods needs F_light ≥ 2.03 (|n| ≥ 0.81). Reach is |n| ≤ 0.92–0.94, so the discriminating window is
  |n| 0.74–0.94 (F_light 1.6–2.8 T, 1.4 FFT bins).
- The 1–2.5 T band where these light tones live also holds residual / series-segment content (the 1.0–1.75 T peaks):
  the B_1–B_2 geometry limit that 08-21 recorded.
- The heavy tone at 0.70–0.82 F_L discriminates on its own wherever the frame is good to ≲ 10 % (|n| ≥ 0.6), since ABCA
  would put its tone at F_L.

## Q6. Detection against periods (live-check rules, hole bands)

`detect.py`, `detect_columns.csv`: 58 hole column-windows at |n| ≥ 0.5 from 08-24 r4 c0–c7, 08-24 r5, 08-22 r7 and
08-25 r7.

| light periods k | N | hole light | hole split | hole heavy | electron light / split (pooled live fans) | electron 08-24 r4 (same acquisition) light / split |
|---|---|---|---|---|---|---|
| 1–1.5 | 11 | 0 % | 0 % | 91 % | 31 / 16 % | 67 / 0 % |
| 1.5–2 | 9 | 33 % | 0 % | 89 % | 50 / 41 % | 60 / 20 % |
| 2–2.5 | 7 | 14 % | 0 % | 86 % | 78 / 55 % | 33 / 67 % (N 3) |
| 2.5–3.5 | 7 | 14 % | 14 % | 100 % | 84 / 79 % | 75 / 25 % (N 4) |

- The one hole split is 08-24 r5 over 0.51–6 T (k 2.66: heavy 6.11 / F_L 7.48, dip 0.67). No 08-24 r4 hole column
  reaches k > 3.03, and none detects the split.
- The hole heavy tone is detected like the electron one; the light tone and F_L are what is missing, so the electron
  k-ramp (1.5 → 3.5) can't be reused for holes.

## Q7. What a hole grader would need, and what's missing

- **Tone table:** Halder n < 0 rows exist and hold at |n| ≥ 0.6 (Q4); below 0.6 the table and the data disagree.
- **Windows:** 0.75 T / 1.0 T, provisional (Q3). Cap windows at about 4.5 T when B_max ≥ 8 T (QH regime).
- **Frame:** n = s·(n_frame − n0) with a per-session hole check (F_L tone or QH ladder). The electron n_scale serves 08-24
  and 08-25; 08-22 needs its own (tone ÷ grader 0.853).
- **Scoring:** a separate hole component with its own column spacing (hole F_light 1.6–2.8 T collides with electron
  F_light at n 1.2–1.6, so a shared best-spaced selection would trade one against the other), and a hole detection curve;
  the electron k-ramp does not transfer.
- **Missing data:** (a) any hole trace at reference acquisition (50 nA, τ 0.3 s) below 1.5 T; (b) a hole 1/B fan or
  ladder at |n| 0.74–0.94, 0.5 → ≥ 8 T, 1/B span ≥ 1.8/T, to measure the light and F_L onsets and the light tone itself;
  (c) a wider negative top-gate range (|n| 1.5–2, F_light 5.6–7.9 T), which would make holes as gradeable as electrons;
  (d) an absolute density anchor per session (a Hall pair or a QH ladder to ≥ 8 T) to settle frames like 08-22's.

## Figures

- `fig/spectra.png`: the three dense traces, a low-field and a full window each, with Halder tones overlaid.
- `fig/hole_nF.png`: the 08-24 r4 hole (n, F) contrast map with Halder light / heavy / F_L lines and every trace's
  consensus tones.
- `fig/onsets_detection.png`: onsets against |n| with the electron floors, and detection against periods, hole against
  electron.

## Files

- Code: `load_hole.py`, `common.py`, `llframe.py`, `qh_ladder.py`, `tones.py`, `detect.py`, `onsets.py` (run from the
  measurement-env checkout), `jointwalk.py` + `onsets_joint.py`, `lightscan.py`, `partition.py`, `inventory.py`,
  `figures.py`, `tonefit.py` (a parametric multi-tone fit, unstable on these traces and not used). Exploration:
  `scratch/`.
- Tables: `inventory.csv`, `frames.csv`, `ll_frames.csv`, `tones_raw.csv`, `tones.csv`, `detect_columns.csv`,
  `onsets.csv`, `onsets_joint.csv`, `lightscan.csv`, `partition.csv`.
