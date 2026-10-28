## HERA — thermal-machinery validation: base → 3 K → 10 K → 50 K → base-ish (E0 — operator runs)

Per operator ruling (session notes): `temperature-dependence` unblocked; `heater.set_both(T, ratio=0.99)` is the sanctioned control call; ranges authorized to 50 K. This cell validates the machinery before the LK ladder: three plateaus covering both heater-range bands — **3 K, 10 K** (range 1) and **50 K** (range 2) — each settle-verified against the worker logfile (never GPIB polling), then `heater.off('both')` and a monitored drift back to **≤ 1.5 K**.

**What it checks per plateau**: settle time (feeds ladder pricing), stability over a 60 s hold (tol = max(50 mK, 0.5 %·T)), and vaporizer tracking (setpoint ratio 0.99 — a lagging/runaway T_vap is the old failure mode and aborts the cell). Gates parked at 0 first; magnet stays at 8 T (envelope: consideration zone needs > 10 T *and* > 15 K — not entered; Cernox field error at 3 K/8 T is tens-of-mK systematic, fine for a machinery check).

**Abort safety**: all waits are `interruptible_sleep`; any exception or interrupt lands in the `finally`, which turns **both heaters off** — the safe state (drift to base).

**Cost (this cell is the calibrator — no prior thermal excursion this session)**: plateaus ~5–10 min each incl. climbs, cooldown 50 → 1.5 K is the unknown (est. 30–60 min on He flow) → **~1.5–2 h total**, generous timeouts throughout. Settle-time summary printed at the end. No run dir (control cell — the record is the cell output; the ladder's runs will carry the data).
