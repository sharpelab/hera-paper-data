## HERA — ramp magnet 0.30 T → 0 T (VERIFY + Step-1 prep)

Bring-up read shows the magnet sitting at **0.303 T**. Session-start VERIFY wants 0 T, and Step 1 (the B = 0 (n, D) gate map / CNP calibration) needs B = 0 — so this ramps to zero.

**Cost:** 0.303 T ÷ 0.137 T/min ≈ **2.2 min**, blocking. `magnet.field()` blocks through the whole ramp; per the rig card, interrupting the *cell* does **not** stop the supply (recovery is another `field()` call), so abort at the instrument if ever needed. No data dir written.

**Precondition:** sample T at base; PS heater on / output enabled (else `field()` raises). If the 0.30 T is intentional, don't run this — tell me why and I'll re-plan.
