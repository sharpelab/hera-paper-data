## HERA — 0 T gate map (`gatemap`), investigation step 1

Gate C passed (runs 0–3 clean; ana notebook has the verdict). Next per
`trilayer-stacking-fs-count` step 1: the cooldown's first 0 T (V_tg, V_bg)
map, raw gate voltages (cap ratios not yet trusted), full validator box —
**TG fast [−3, +3] 101 pts (60 mV) × BG slow [−4.5, +4.5] 101 rows (90 mV)**,
Si at 0 V. Gate C puts the CNP near (0,0) with R ~ 1–3 kΩ, so the geometry
prior (slope −1.3) predicts the CNP ridge crossing the TG window for
|V_bg| ≲ 2.3 V — comfortably inside this box; the box's D-span also buys the
CNP-vs-D read (gap systematics) for free.

**Settings**: 5 nA bias (0.5 V/100 MΩ, card starting point); sens sr1–sr3
2×10⁻⁴ (R ceiling 40 kΩ at 5 nA — headroom for a D-gapped CNP; a railed
ridge row is handled by the calibration recipe's robust-fit guard), sr0
10 mV. **Settling**: fast_delay 1 s + ~0.35 s reads ≈ 1.35 s/pt = 4.5·τ —
the device card's stated 4τ dwell floor, below the rig card's conservative
7–10·τ; accepted knowingly for broad CNP-ridge extraction (≲2% settling
error, irrelevant to ridge position).

**Cost**: 101 × (101 × ~1.35 s + 7 s flyback + 3 s) ≈ **4.2 h** (from gate C
measured overhead, runs 0–3: predicted read time confirmed at NPLC=10;
NPLC=1 scales reads to ~0.35 s/pt). Headline 4.2–4.6 h.

**Checkpoints**: first rows (railing / dead channel / leakage), then every
~15 rows via the armed watch — interim CNP-ridge read as rows accumulate;
abort criteria: gate current off the pA floor toward nA, all-channel flat
(grounding), or T excursion. E1 auto bucket: endpoints = validator limits,
preconditions asserted in-cell.
