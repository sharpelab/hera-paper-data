## HERA — Gate C: gate-current sanity / device liveness (gate-current-sanity-check)

**Why now.** Bring-up is green: setup ran clean in this kernel, magnet at ~5.5 µT (≈0), probe MC 33.9 mK with the Probe2 logfile *advancing* (not the frozen-bridge case the rig card flags), and SAFETIES committed exactly to the device-card limits (TG (−7,+6), BG (−4,+4.2), |B|≤100 mT). The one open VERIFY item is contact wiring / a live 4-terminal Rxx — this cell establishes it. Per `sc-characterization` Step-1 prerequisites, this liveness pass gates everything downstream, so it runs before the pristine-field map.

**What runs (Cell A).** Four legs — k_tg→+6, k_tg→−7, k_bg→+4.2, k_bg→−4 — each from 0 with the other gate parked at 0, 251 pts, delay 1 s, gate-current readback at nplci=10 (pA floor). Each leg is its own run/slug. The card limits sit well inside the geometry ceiling (~±11.8 V TG, ±10 V BG), so sweeping to them is safe.

**Watch live, per leg:**
- `sr830_3.X` (4T Rxx, 30‑31): nonzero, smoothly varying ⇒ device alive on the 4-terminal channel. `sr830_1.X` (current, 5‑4) and `sr830_2.X` (2T, 5‑4): sensible, not flat-zero or all-equal (the grounded-device tell).
- swept gate `*.curr`: stays in pA on the capacitive charging slope to the limit ⇒ clean.
- parked gate `*.curr`: at the readback floor ⇒ no cross-gate path.

A gross turn-up off the charging slope = a leak → **Kernel Interrupt** (the `finally` parks the swept gate), then stop and report — skip Cell B.

**Cost:** ~20–25 min (≈5–6 min/leg at nplci=10 + ramp-backs); first real timing calibration for this dir. **Handshake:** you run Cell A, watch the plots, report per-leg; I won't propose the map until you do. Run **Cell B** (reset nplci → 1) only if every leg looked clean.

*(Note on mode: the brief's Autonomy section sets E1 this round on your "go for autonomy" once VERIFY/SAFETIES are green — they now are — while the Session-arc line reads "E0 throughout." This liveness check is human-run either way; flagging the wording mismatch for you to resolve before I'd execute anything autonomously.)*
