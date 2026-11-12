## HERA — Step 1: pristine-field gate map (candidate ID)

Bring-up complete (runs 0–1): device alive, 4T Rxx (sr3, 30-31) live at ~2.6 Ω noise floor @ 0.5 nA, both gate validators exercised clean (BG ±4: ≤45 pA; TG 0→−7: ≤61 pA), CNP at ≈(k_tg 0, k_bg 0). This is the **investigation Step 1** map — `gatemap` (axis-aligned in raw V_tg/V_bg, since the cap-ratio/geometry prior is unconfirmed; this map is the substrate for `cnp-and-dline-calibration`). **Taken before the magnet is ever energised** — the field-history protocol's map-before-energise step (asserted |B|<5 mT in-cell).

**What:** 2D megasweep over the full validator box. **BG slow** −4→+4.2 V (61 pts, 0.137 V) × **TG fast** −7→+6 V (101 pts, 0.13 V), `slow_delay=3, fast_delay=1`, drive 0.5 nA, B≈0. All lock-ins + both gate currents read at every point. Grid ~0.13 V resolves SC domes ≳0.25 V wide; coarse-first reconnaissance per the investigation (zoom into candidates after).

**Why TG fast:** the +6 V TG corner is the one extreme not yet exercised this session (safer polarity, validator-trusted). As the fast axis, TG sweeps to +6 at the end of **row 1** (~3 min) and every row after, keeping the worst leakage corner under the live `k_tg.curr` plot throughout.

**Price:** ~6161 pts. From run 1's measured 2.18 s/pt (nplci=10); map runs nplci=1 → ~1.9 s/pt → **~3.5 hr** (3–4 hr realistic, incl. fast-axis retrace + 61 slow settles). Quoted as the realistic case, not the floor.

**Checkpoint @ ~12 BG rows (~40 min):** I'll read the partial run from disk — (i) leakage stayed <100 pA across the +6/−7 corners; (ii) no channel flat/saturated; (iii) the CNP ridge is forming where expected; (iv) any low-Rxx candidate regions. Fork: continue / re-scope the box / abandon. `hera-watch` armed to digest the rows live.

**Preconditions** (asserted in-cell): T base (<100 mK); **|B|<5 mT (pristine field — magnet untouched)**; drive = 0.5 nA (sr830_1.amplitude=0.05); gate setpoints printed. **Watch the live `k_tg.curr` / `k_bg.curr` plots** — if either climbs toward 100 pA / rolls into nA at any corner, interrupt (`nb-collab interrupt`); that's leakage onset, we re-scope the box. Gates park to 0 at the end.
