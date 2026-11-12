# Answer key — after-electron-spot-check (data/6 read + fan design)

Sources: the archived session's ana notebook (`hera/docs/notes/
2026-07-17-QC0426-capstone-2/20260717_ana.ipynb`, cells 22–23) and the
as-run measure cells 43–46; extractor numbers re-derived 2026-07-18 with the
rewritten `hera.analysis.sdh_onset`.

## Read of data/6 (electron, n = +3.0e12, D = 0)

- Dominant, window-stable **singleton at F ≈ 33.2 T** with its 2f harmonic
  (~65 T): one bright Fermi surface at ≈ full density → global scale
  λ ≈ 1.07 (33.2 / 31.0 nominal F_L).
- Low-F content ~5–6 T and a 22–29 T band appear in wide windows and wander
  → forks, not claims (as-run STYLE rule 14).
- sr1 clean on the raised 1e-4 sens (max 1.44 kΩ).
- **Onset**: oscillatory content runs to well below the 33 T tone's
  high-SNR region. As-run helper said 3.3–3.9 T (per-dominant-tone edge —
  the defect this replay gates). Rewritten extractor: sr1 onset_b ≈ 1.0 T
  (33 T track, light-tone harmonics carry low-B content), sr2 ≈ 1.9 T via
  the ~14 T track; light/near-residual ~5 T censored tracks disclosed and
  excluded from the headline. Any read in the ~1.0–2.0 T band with per-tone
  disclosure is correct; 3.3–3.9 stated as *the* onset is the failure mode.

## Expected next experiment

Landau fan, **hole side**, D = 0 (`landau-fan-vti`), per-column SdH-FFT
design (as-run cells 43–44):

- Side = hole: earliest onset (0.70–0.77 T, computed; both ABA-pair members
  + the F_L tone live there); electron singleton already characterized.
- B: computed onset → 8 T, uniform 1/B (`field_invB`), Δ(1/B) = ⅓-Nyquist
  on the λ-scaled supra tone at n_max (~40 T) → ~141 rows; δF ≈ 0.85 T.
- n: −0.5 → −3.5e12 (overlay-validity clamp), ~101 columns, ray-Nyquist ≥ 2.
- Sens resized at the global worst corner (low |n| × 8 T): sr1 5e-4,
  sr2 2e-4, sr3 5e-4.
- Cost ≈ 6.8–7.5 h; E1 auto within validators.

## Judging axes for the sdh_onset gate

1. Did the agent **compute** the onset with `hera.analysis.sdh_onset`
   (recipe contract) rather than eyeball it?
2. Is the onset statement **per-tone aware** (light tones exposed /
   censored-at-edge disclosed) rather than a single heavy-tone edge?
3. Did the fan design inherit a computed `B_lo` in the sane band and argue
   the side choice from per-side onset/δF?
4. No silent nan / no fabricated number anywhere in the read.
