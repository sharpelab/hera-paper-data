## HERA — Step 1: 0 T gate map (`gatemap`) for CNP line + (n, D) calibration

Gate C passed (runs 0–3, verdict in ana). Next per the governing investigation (`trilayer-stacking-fs-count` Step 1): the 0 T TG–BG map that `cnp-and-dline-calibration` consumes — CNP ridge per channel → capacitance ratio from the slope → the (n, D) conversion, plus the region survey (clean hole/electron sides, D = 0 line, contact arms staying metallic).

**Design.** TG fast −3 → +3 V, **121 pts (50 mV step)** — Gate C shows the CNP peak ~0.5 V wide, so ≥10 pts across it; BG slow −3 → +3 V, **61 rows (0.1 V step)**. BG is clipped at ±3 V (not the ±4.5 card limit) because the geometry-prior slope (−c_bg/c_tg ≈ −1.3) walks the ridge out of the TG window at |Vbg| ≈ 2.7 V — rows beyond that carry no ridge and little else; the price of full BG coverage would be ~+1.2 h for edge-clipped rows. D = 0 reach on this map: |n| up to ~6×10¹² cm⁻² (geometry prior).

**Sensitivities**: sr1–sr3 stay at 2e-5 (card CNP scale; rails above ~4 kΩ — a railed ridge row is expected at larger |D| and the calibration fit handles it via outlier rejection). sr0 bumped 5 mV → **10 mV** for headroom (it sits at 99.7 % of range at full 5 nA; the card's metallic-regime setting).

**Cost** (calibrated on runs 0–3: 2.13 s/pt at delay = 1 → ~2.4 s/pt at fast_delay = 1.2): 61 × 121 = 7 381 pts ≈ 4.9 h + ~15 min row turnaround → **~5–5.5 h** (overnight run; done ≈ 03:00). Checkpoints: first 3 rows (~15 min in — leakage, railing, dead channel), then mid-run.

Preconditions asserted in-cell: T < 2 K, |B| < 0.05 T, Si at 0 V, gates at 0. Gates park at 0 on completion.
