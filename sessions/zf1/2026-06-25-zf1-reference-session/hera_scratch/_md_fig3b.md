## HERA — Figure 3 (corrected) · **supersedes cell 43 — run THIS**

Bug fix only: cell 43's n-line dropped a `*1e11` (passed n in 1e11-units to `nD_to_V`, which expects cm⁻²), so the points landed at the CNP at D=−0.64 → V_bg≈4.29 V > the 4.2 cap → the validator assert fired (correctly — it caught a bad gate target before any hardware moved). Fixed: `nD_to_V(n_line*1e11, −0.64)` → V_tg∈[−5.47,−5.29], V_bg∈[3.90,4.05], all in range.

**Identical otherwise:** R(T,n) at D=−0.64, B=B_eff0, heater descending 480→34 mK (100 uniform 4.4 mK steps, measure-while-cooling), n-line fast 126 pts, AC 1 nA, 4T 0.1 mV, slow_delay 90 s, init_delay=False, ~7 h, ends heater-off at base. Heater is still at the 6.5 V ceiling from the warm-up (precondition asserts that). **Run this cell; ignore cell 43.** Same checkpoints (first steps, then ~hourly); watch the fridge MC.
