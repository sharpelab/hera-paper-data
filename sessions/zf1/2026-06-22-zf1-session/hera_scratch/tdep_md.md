## HERA — Run 7: T-dependence — Ic(T), the final hallmark (heat up LAST)

Four hallmarks in hand (Rxx→0, Ic≈18 nA lobe, reference Ic, field-kill B_c⊥≈2.5 mT/flat normal) → strong SC. This is the decisive thermal test: **Ic(T)** — the supercurrent lobe should melt continuously to Ic→0 at Tc. I chose the bias×T map over plain Rxx(T) because watching the dV/dI lobe collapse is the definitive "supercurrent melts at Tc" (and gives Ic(T) for the writeup), at only ~2 min/step over Rxx(T).

**Design (heater discipline — first heater use this session):**
- **Stepped warm-up** to 6 V (~423 mK) in 1 V increments with 60 s holds, then 300 s equilibration (device-card rule: ≤1 V steps, no thermal shock). Heater current printed to confirm it draws (open-line check).
- **Measure while cooling:** `megasweep` slow = `heater.volt` **6→0 V (11 steps)**, `slow_delay=300 s` thermalization per step; fast = `dc205_1.volt` ±3 V (**Idc ±30 nA**, 63 pts, step <0.1 V so no DC205 10 s settle). T read back from the `T` column (heater V is uncalibrated; approx 423→30 mK).
- Gates fixed at the optimum, field at nominal 0 (effective-zero region), 1 nA AC. fp `temperature`, `heater.volt`, `heater.curr`, `magnet.field`, gates, lock-ins.

**Cost ~85 min** + ~1 h re-cool afterward. **Checkpoint @ ~35 min** (via the armed `hera-watch` + a TSV T-read): confirm T descending monotonically, heater drawing current, and the dV/dI lobe beginning to appear as T drops — continue / adjust thermalization / abort.

**Preconditions** asserted: base T start, gates/field in place. `finally`: heater→0 (start re-cool), dc205→0, gates→0. **Read after:** Ic vs T → Tc (where Ic→0; %-of-normal / threshold convention, stated). If Ic is already 0 at the 423 mK top, Tc<423 mK (captured); if Ic still finite at the top, Tc>423 mK — note and extend toward the 6.5 V ceiling.
