## HERA — Gate C: cheap liveness check (`gate-current-sanity-check`, first-session branch)

Bring-up is green: setup ran in-kernel (probe MC **33.7 mK**, all instruments connected), SAFETIES committed (cell 16, exec [8]) with card-exact validators — `k_tg ∈ (−7,+6)`, `k_bg ∈ (−4,+4.2)`, **|B|≤0.1 T** on `magnet.field` — and `magnet.field()` reads **−0.04 mT** (≈0). [VERIFY] all green.

This is the **liveness-only** branch: the gate operating limits are *provided* (device card) and *already committed* as validators, and the range-finding family is blocklisted this session — so no iterate-then-bless loop, no Cell B. One small TG excursion (0 → **+1 V**, deep inside the +6 V validator) with `k_bg` parked at 0, watching three things:

- **Lock-in X** on `sr1`(5-4, current), `sr2`(5-4, 2T), `sr3`(30-31, **4T longitudinal Rxx**) — nonzero, smooth → device alive, contacts read clean, the 4T channel is live.
- **`k_tg.curr`** (active gate) — stays in pA → no leakage at the operating point.
- **`k_bg.curr`** (parked) — at floor → no cross-gate path.

`nplci=10` on the gate-current channels for pA-floor readback (reset to 1 in the `finally`). AC drive set to **0.1 V → ~1 nA** at the device (device card, 100 MΩ bias R). Magnet untouched — the Step-1 survey map is still pristine-field.

**Precondition asserts** at top (state this cell assumes but does not set): base T, B≈0. Gates are parked by the cell, so their start value only costs ramp time.

**Cost:** ~1.5–2 min (51 pts × ~1 s + the 5 mV/step ramps). **Read after it lands:** if all three reads are clean I advance to the Step-1 axis-aligned survey gatemap (does double duty as the cap-ratio calibration); any flat/saturated channel or nA gate current stops me per the failure-mode catalog.
