## HERA — device health re-check at reduced extents (post-excursion baseline)

Recipe: `device-init/reentry-baseline` (reduced re-run after an intervention —
here the +7 V / 1.3 nA and −6 V / 0.5 nA TG excursions of runs 0/1). Four legs
at the proposed design extents — **TG 0→±4.0 V, BG 0→±4.5 V** — identical
acquisition to runs 0–3 (same drive 0.5 V/13 Hz, delay 1.2 s, nplci 10 — Cell B
still deliberately unrun so offsets match). References: **this session's runs
0–3, in-range portions** (pre/immediately-post-excursion state).

Pass bands (quantitative, per reentry-baseline step 4):
- **Leakage floor**: TG within ~±50 pA of its +20 pA offset over the full ±4 V;
  BG within ~±50 pA of its −100 pA offset. Any exponential turn-up **inside**
  ±4 V that wasn't there in runs 0/1 = FAIL (dielectric degraded).
- **Resistance scale**: sr1/sr2 |X| ratio to reference at matched V within ~2×
  (hysteresis between legs was already present pre-excursion — sr0 railed from
  leg 2 on — so shape and positions carry the verdict more than absolute scale).
- **Feature positions**: neutrality-like maxima on sr1/sr2 within a few steps
  (≲0.1 V) of the run-0/1 positions.
- **Trace shape**: same feature set, no new structure.

**~26 min** (4 × 151 pts × 2.33 s/pt measured on runs 0–3, + ramp-backs).
Watch the live gate-current plots; interrupt on any turn-up — legs stay inside
the range runs 0/1 showed clean. I compare against reference quantitatively
when the data lands and state pass/fail per check.
