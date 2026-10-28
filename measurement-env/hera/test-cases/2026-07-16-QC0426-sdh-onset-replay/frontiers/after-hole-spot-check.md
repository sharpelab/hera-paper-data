---
slug: after-hole-spot-check
user: zack
cut_index: 44
latest_fileid: 6
included:
  data: [0, 1, 2, 3, 4, 5, 6]
  images: []
leak_terms:
  - "landau-fan"
  - "1.6->8"
  - "-1.5->-6e12"
  - "temperature-dependence-vti"
  - "LK mass ladder"
  - "n=+3.0e12"
  - "8->1 T"
  - "sr1 re-sized"
forward_scan: "Kept region is cells 0-44 (setup / instruments / SAFETIES / helpers / meas-config / contact map / HERA session start + VERIFY + kernel probe / Gate C four legs + close-out [data 0-3] / coarse-BG 0 T gatemap [data/4] / D=0 line cut [data/5] / SdH spot check 1/2 hole [data/6]). Cell 43's '1/2' numbering legitimately says an electron check follows — the next instrument is operator knowledge; the answer under test is the data/6 READ (the record the old sdh_onset nan'd on) plus the electron check's design inheritance. 'ride-down' appears pre-cut (run-6 metadata comment 'ends at 8 T for SC2 ride-down') so it is NOT a leak term; 'x87' was dropped as a term (short string false-positives against base64 image payloads in the notebook JSON) in favor of the fan's distinctive n-grid string. Every term above verified absent from the raw JSON of cells 0-44 (sources + outputs), first appearing in cells 45-56. The post-hoc ana notebook and hera_session.md are not part of the fixture copy-set. Clean."
---

# Frontier — cut after the hole-side SdH spot check (the nan refire record)

*Decision boundary for offline replay, authored 2026-07-18 as the acceptance
gate for the `hera.analysis.sdh_onset` rewrite (subtask sdh_onset_fix).*

This is a **READ** frontier: data/6 is the clean 1303-pt hole-side record
(n = −6e12, D = 0, B 1→8 T) on which the as-run session's `sdh_onset`
returned **nan** (consensus 11.1 T was sensible) and the onset had to be
read by eye at 1.8–2 T — the eng-backlog refire. The rewritten extractor
tracks the ~11 T light tone to the record's low edge (censored at 1.0 T,
warned) or localizes a die-off in the 1.2–2.3 T band per channel.

Under test:

1. Does the replayed agent get a **finite, computed** onset from
   `hera.analysis.sdh_onset` (no eyeball fallback, no nan flowing onward)?
2. Does the read handle the tone set (f₁ ≈ 11 T dominant + f₂ ≈ 55 T +
   sum/harmonic comb) and the Luttinger partition sensibly?
3. Does the proposed next experiment (the electron-side companion check,
   legitimately known from the '1/2' numbering) inherit the design from the
   measured record (grid, sens, direction, δF reasoning)?

Answer key: cells 45–46 (as-run electron check) + `ground_truth/
after-hole-spot-check/reading.md`.
