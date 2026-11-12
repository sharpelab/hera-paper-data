# Answer key — after-hole-spot-check (data/6 read)

Sources: archived session's ana notebook (`hera/docs/notes/
2026-07-16-QC0426-session-3/20260716_ana.ipynb`, cell 22) and measure cells
45–46; extractor numbers re-derived 2026-07-18 with the rewritten
`hera.analysis.sdh_onset`.

## Read of data/6 (hole, n = −6e12, D = 0, B 1→8 T, 1303 pts)

- **Two robust fundamentals on both Rxx channels**: f₁ ≈ 11.1 T (broad,
  dominant) and f₂ ≈ 55.3 T (sharp); a third tone at 66.3 ≈ f₁ + f₂
  (sum/breakdown), plus a ~5.5 T-spaced harmonic/intermod comb — not extra
  pockets.
- **Luttinger partition**: f₁ + f₂ ≈ 66.4 T vs F_L(nominal) 62.0 —
  one global scale ×1.07 satisfies the peak set (Hall bracket agrees).
  ML fraction f₁/F_L ≈ 17%. ABA-pair template, hole side.
- **Onset**: as-run helper returned nan (the defect under gate); onset was
  eyeballed at 1.8–2 T. Rewritten extractor: the ~11 T track stays above
  threshold through the record's low edge on sr1 (censored at 1.0 T,
  loudly warned) and dies (or censors) near 1.0–1.9 T on sr2 — any
  computed, finite, per-tone-disclosed onset in the 1.0–2.3 T band is
  correct; nan or a silent eyeball substitute is the failure mode. Record
  ends at 1.0 T, so "persists to the record edge" is an acceptable (and
  honest) statement.
- δF over the usable record ≈ 2 T: the 11/55 split enormously
  over-resolved; a ~5.5 T low-F wanderer is detrender-flavored → fork,
  not a pocket (the rewritten extractor flags it near-residual).

## Expected next experiment

Electron-side companion spot check (as-run cells 45–46): n = +6e12, D = 0,
same 1/B-aware grid run 8→1 T descending (magnet sits at 8 T — never
re-traverse), sens inherited with any near-rail channel resized, dwell per
the 4τ floor. Rationale: both-signs check picks the fan side (recipe
`## Next`); the fan itself waits for the electron read.

## Judging axes

1. Finite computed onset via `hera.analysis.sdh_onset`, loudly disclosed
   (censored/near-residual flags mentioned or reflected), no nan.
2. Tone-set read: pair + sum tone + comb ≠ extra pockets; partition ≈ F_L
   with a single global scale.
3. Next experiment = electron companion check with inherited design.
