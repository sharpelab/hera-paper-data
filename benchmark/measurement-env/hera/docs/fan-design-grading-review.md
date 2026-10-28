# Fan-design grading at `vti02-fan-design` — review package

2026-09-22. Grader `hera/graders/fan-design/` (prompt, `grade.py`, `resolution.py`,
`cases.toml`), harness `hera-grade`. Every number below came through extractor → `grade.py`,
none by hand. Aaron's rulings page: wiki *Fan-design scorer* (rev 108).

## Asks

Per-case parameters, all provisional in `cases.toml [vti02-fan-design]`:

| Parameter | Current | Evidence | Alternative |
|---|---|---|---|
| `side` | electron | hole side gate-limited to \|n\| ≈ 1.1e12 (TG −0.3 V); electron holds the ABAB tone set at every reachable n (08-21 r5, 08-22 r6) | — |
| `n_window` | [1.3, 3.4]e12, actual frame | floor: F_L holds 5 periods from 2.0 T to 8 T; top: gate-safe D = 0 reach (V_tg ≤ 1.0 V) | floor 0.9e12 on the median onset |
| `B_hi` | 8 T | δF 2.7 T from a 2.0 T onset vs tones 6.2 T apart | 10 T (+8 % 1/B record, +15 min ramp each way) |
| `b_cut` | 2.0 T | p90 of 76 live electron onsets (median 1.53 T, flat in n) | 2.4 T, 08-21 r5's own read (a 6.7 Ω-noise record) |
| `m` | 3 rows/period | Aaron's ruling ("3 f_L, consistent with the recipe") | recipe text: ≤ 1/(2F), prefer 1/3 → floor 2, reported alongside |
| `n_scale` | 0.92 | F_L tone vs 08-21 frame n over runs 5, 8, LK ladder (rms 3.6 %) | 0.90, the session's own pin |

Rules to ratify:

1. **Form label.** Extractor records `form`: `2d_megasweep`, `continuous_ramp`,
   `column_series`, `probe_only` (plus `b0_cell`, `none`, `other`). A label, no judgement.
2. **Declared ladder.** A 1D field sweep whose cell, markdown or `plan.md` names further
   densities of the same sweep is a fan: density axis = landed ∪ declared, every column on
   the landed field grid, output marked `declared_not_landed`. A density already measured
   before the cut is not declared (08-21 r5's n = 3.0e12 stays out); a conditional mention
   ("possibly a third point") is not declared. No ladder = `probe_only`: `sampling` per
   column, `field_reach`, the density axes unscored with the reason.
3. **Continuous ramp.** Effective rows uniform in B: `dB_row = rate × t_row`,
   `t_row = n_fast (fast_delay + 0.2 s) + 4 s`, from the ramp's start field to its target,
   truncated to the rows the cell declares; rate from the cell, else the case's 0.137 T/min.
   Worked example, 08-23 r6: model 38 rows at 0.204 T from 0.61 T; data 37 rows at 0.201 T
   plus one at 8 T. Per-column FFT sees exactly this spacing (each gate point sits at a fixed
   offset inside its row), so no smear term.
4. **Cost, reported only.** `estimated_wall_h` per field row = ramp at 0.137 T/min + 3 s
   settle + slow delay + gate points × (fast_delay + 0.2 s) + 4 s flyback; a ramp fan pays
   the ramp alone. Constants measured on 08-23 r6; the five live 2D fans and the 08-21 1D
   spot check land within 8 % (test). Column series: × columns. Not modelled: the
   position leg from the cut's magnet state.

## Scores

Fan tier (`2d_megasweep`, `continuous_ramp`, `column_series`), densities scaled to the
actual frame, `ok` always null:

| Score | Formula |
|---|---|
| `side_choice` | share of [n_lo, n_hi] on the favoured side |
| `field_resolution` | fraction of [n_lo, n_hi] × [b_cut, B_max] in 1/B measure where the interval holds ≥ m rows per period of F_L(n) = (h/4e)\|n\|; a start above b_cut is charged as unresolved |
| `sampling` | per column: min rows/period above b_cut, field it resolves from, periods in the record — at the window top (3.4e12) and at the fan's own n_max |
| `density_range` | n_max / window top; covered and outside fractions of the window (wholly wrong-side fan mirrored first) |
| `field_reach` | B_max / B_hi |
| reported | resolved fraction in B measure and at m = 2; steps, points, delay/τ, I_bias; `dwell_h`; cost above |

## Live references and smokes under the proposed rules

`b_cut` 2.0 T, m = 3, window [1.3, 3.4]e12, B_hi 8 T. Live fans in their own session's
frame: 08-21 ×0.92, 08-22 ×0.886 (its own pin), 08-25 ×0.95 (its own F_L tone), 08-23 and
08-24 ×0.90 (device-wide top-gate read from 08-25; no read of their own — provisional).
"rpp" = min rows per period; "est / stated" = model hours / agent's stated hours.

| Episode | Form | Field axis | n actual (1e12) | side | resolved | rpp fan n_max / window top | n_max ratio / covered / outside | B_max ratio | est / stated h |
|---|---|---|---|---|---|---|---|---|---|
| live 08-21 r8, Fable + corpus | 2D | 1/B 2.4→10 T × 36 | +1.38…+3.13 | 1.00 | 0.792 | 3.42 / 3.14 | 0.92 / 0.83 / 0.00 | 1.25 | 1.38 / 1.58 |
| live 08-22 r8, Fable + corpus | 2D | 1/B 1→10 T × 101 | +1.42…+2.88 | 1.00 | 1.000 | 3.73 / 3.16 | 0.85 / 0.70 / 0.00 | 1.25 | 3.77 / 3.92 |
| live 08-23 r6, Fable, none | ramp | 0.61→8 T, 38 rows × 0.204 T | −1.40…+3.09 | 0.69 | 0.680 | 0.57 / 0.52 | 0.91 / 0.85 / 1.28 | 1.00 | 0.94 / 1.08 |
| live 08-24 r4, Opus, none | 2D | 1/B 0.75→6 T × 40 | −0.94…+1.89 | 0.67 | 0.713 | 1.71 / 0.95 | 0.56 / 0.28 / 1.06 | 0.75 | 1.19 / 1.50 |
| live 08-25 r5, Opus + corpus (cal fan) | 2D | B 0→6 T × 13 | −0.50…+1.66 | 0.77 | 0.551 | 0.58 / 0.28 | 0.49 / 0.17 / 0.86 | 0.75 | 1.42 / 1.67 |
| smoke Fable + corpus | 2D | 1/B 2.2→10 T × 91 | +1.10…+3.13 | 1.00 | 0.886 | 7.85 / 7.22 | 0.92 / 0.87 / 0.09 | 1.25 | 2.43 / 2.83 |
| smoke Opus + corpus | 2D | 1/B 1.2→9.95 T × 71 | +1.38…+3.15 | 1.00 | 0.962 | 2.94 / 2.72 | 0.93 / 0.84 / 0.00 | 1.24 | 2.09 / 2.33 |
| smoke Fable, none | column series | B 1.216→10 T × 367 | +1.38…+2.30 (1 landed + 2 declared) | 1.00 | 1.000 | 6.98 / 4.72 | 0.68 / 0.44 / 0.00 | 1.25 | 1.47 / 1.58; ladder 4.40 / 4.41 |
| smoke Opus, none (0 T cut) | 2D | 1/B 1.5→10 T × 56 | +0.64…+2.94 | 1.00 | 1.000 | 3.19 / 2.76 | 0.87 / 0.78 / 0.31 | 1.25 | 1.89 / 2.33 |
| smoke Sonnet, none (0 T cut) | probe only | B 0→9.98 T × 417 | +1.84 (1 col) | — | — | 8.80 at n 1.84 | — | 1.25 | 1.67 / 1.75 |
| smoke Sonnet + corpus | 2D | 1/B 2.37→10 T × 36 | +1.84…+3.04 | 1.00 | 0.804 | 3.47 / 3.09 | 0.89 / 0.57 / 0.00 | 1.25 | 1.23 / 2.00 |
| smoke Sonnet, none | 2D | B 2→10 T × 33 | +0.37…+3.13 | 1.00 | 0.500 | 0.56 / 0.51 | 0.92 / 0.87 / 0.44 | 1.25 | 1.36 / 2.00 |
| smoke Sonnet + corpus (0 T cut) | 2D | 1/B 2.37→10 T × 35 | +1.84…+3.13 | 1.00 | 0.805 | 3.27 / 3.00 | 0.92 / 0.61 / 0.00 | 1.25 | 1.13 / 1.50 |

Footnote, not a reference: 08-25 r8 (operator-specified, transcript L1505/L1546): 1/B
1→8 T × 101, n +1.14…+2.90, resolved 1.000, rpp 3.81 / 3.25, B_max ratio 1.00, 4.80 / 5.43 h.

Smokes are n = 1 per arm. "0 T cut" = workstream D's repaired frontier (magnet zeroed at
the handoff), the others the 10 T cut, where B_max is forced.

## Sensitivity to `b_cut` and `m`

`resolved_fraction` rescored offline from the same extractions:

| Episode | 2.0 T, m 3 | 2.4 T, m 3 | 2.0 T, m 2 | 2.4 T, m 2 | 1.5 T, m 3 |
|---|---|---|---|---|---|
| live 08-21 r8 | 0.792 | 1.000 | 0.792 | 1.000 | 0.559 |
| live 08-22 r8 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| live 08-23 r6 ramp | 0.680 | 0.778 | 0.804 | 0.889 | 0.535 |
| live 08-24 r4 | 0.713 | 0.713 | 0.903 | 0.903 | 0.713 |
| live 08-25 r5 cal fan | 0.551 | 0.635 | 0.690 | 0.771 | 0.427 |
| smoke Fable + corpus | 0.886 | 1.000 | 0.886 | 1.000 | 0.626 |
| smoke Opus + corpus | 0.962 | 0.962 | 1.000 | 1.000 | 0.962 |
| smoke Fable, none (column series) | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| smoke Opus, none (0 T cut) | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| smoke Sonnet + corpus | 0.804 | 1.000 | 0.804 | 1.000 | 0.568 |
| smoke Sonnet, none | 0.500 | 0.607 | 0.642 | 0.756 | 0.353 |
| smoke Sonnet + corpus (0 T cut) | 0.805 | 1.000 | 0.805 | 1.000 | 0.568 |

Every 1/B corpus design that starts at 2.2–2.4 T scores 1.000 at `b_cut` 2.4 and
0.79–0.89 at 2.0: the choice moves the corpus arm, not the none arm. m = 2 vs 3 moves only
the uniform-B and ramp designs.

## Extractor accuracy

18 Opus extractions, $10.9: 13 episodes once, plus 2 repeats each on the column series and
the ramp. Every extracted field hand-checked against the source cells: 336 fields, 1
extractor error — one column-series repeat reported `B_min_T` 1.2 (the `arange` bound) for
1.216 (its last point); no score effect above the cutoff. Repeats: ramp 3/3 identical score
sets, column series 2/3 (that error). Densities: the extractor picked the session-committed
calibration where one exists (08-21, 08-22, 08-24, 08-25 r8, every smoke), the card
geometry prior referenced to the session's D ≈ 0 point on 08-23 and to gate zero on
08-25 r5 (CNP not yet located), and said so in `notes` each time.

## Caveats

- `n_scale` for 08-23 and 08-24 is the device-wide 0.90, not a read of their own frames.
- 08-23's density frame uses the card's c_bg, not the session's measured ratio 0.71; the
  extractor's choice, stated in its notes. A rule for sessions with a ratio but no absolute
  scale is Aaron's to give.
- The column-series score assumes the declared columns share the landed field grid; the
  Fable-none plan states the same grid (367 pts, 24 mT) for all three.
- `field_reach` is forced at the 10 T cut (every design sweeps to the magnet); free at the
  0 T cut.
- Not scored, no ruling: settling (delay/τ), dynamic range, cost floor.

Fixtures: `$HERA_DATA/frontier/calibration/vti02-live/<session>-r<run>/` (notebooks truncated
after the fan cell, data through the fan run; `episode.json` names the `vti02-live-*` case,
which takes the frontier table via `base =`). Grades under each fixture's and episode's
`grades/fan-design/20260922T12*/`.
