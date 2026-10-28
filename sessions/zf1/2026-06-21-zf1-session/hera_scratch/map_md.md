## HERA — pristine-field survey gate map (investigation Step 1)

1 nA validation done: **4T sr3 (30-31) is the campaign's Rxx channel** — clean CNP at BG=−0.017 V, SNR ~108, metallic resolved to ~6 Ω. (2T sr2 saturates at 1 nA from drive feedthrough on injection node 5 — coarse range, cross-check only; logged.) Now the first science step: an **axis-aligned (V_tg, V_bg) survey megasweep at B=0**, recipes `gatemap.md` + `cnp-and-dline-calibration.md`, doing double duty per the investigation — (1) candidate low-Rxx overview, (2) the CNP-slope substrate to pin the cap ratio (the device-card geometry is only a prior).

**Coarse reconnaissance, by design.** Full validator box (TG −7→+6 slow, BG −4→+4.2 fast), 81×121, tc dropped to 100 ms to make it affordable. BG step ≈ 68 mV ≈ Δn 6×10¹⁰ cm⁻² — enough to map the CNP line and broad candidate regions, **not** to resolve the ~5×10¹⁰-wide SC arc. That's intentional: the narrow arc gets located by n-linecuts and a tight nD polygon map next (investigation Step 1 heuristic-zoom). **Est ~1.4 h.**

**Field discipline:** B=0 (reads 0.03 mT), magnet controller untouched — this map must precede energising (Step-1 map-before-energise). The cell asserts B≈0 and T base before moving gates; it starts at the most-negative TG corner (highest leakage risk) so the checkpoint sees the worst case first.

**Checkpoint (~17 min, TG row ~15/81):** I'll read partial data — gate leakage staying < 100 pA, the 4T CNP ridge tracking sensibly, and the actual row rate vs estimate. Continue / adjust-range / abort fork stated there; an early wash-out saves ~1 h. I'm arming a background `hera-watch` monitor when this lands. Gates park to 0 at the end.
