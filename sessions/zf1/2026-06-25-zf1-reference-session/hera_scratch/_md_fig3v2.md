## HERA — Figure 3 (re-do) — R(T,n) at D=−0.64, B=B_eff0: 1τ-dwell, small-step ascending

The fix, your prescription: **~1τ dwell per step + small steps**. At 1τ each step is ~63% thermalized; the un-thermalized remainder is ~0.37×(step), which is tiny because the steps are small → the sample tracks T. No zero-dwell, no full-settle, **no up/down averaging**.

- **τ ≈ 3.5 min** — from the warm-up's own 1 V settles (probe dT/dt<1 mK/min reached in ~510–780 s).
- **slow_delay = 210 s (~1τ)**, **120 uniform-T steps (~3.7 mK each)** → residual per-step lag **~1.4 mK**.
- **Single ascending traverse**, base→480 mK. Ascending from base (we're cooling there now) needs no re-warm, and the 1τ dwell lets T reach the top cleanly. n-line fast at D=−0.64 (126 pts), AC 1 nA, 4T 0.1 mV.

**~12.5 h** (120 × (210 s dwell + ~164 s n-sweep)); waits for base first. This supersedes the dynamic run 4 (which I'll keep as the diagnostic). vs run 4: 90 s dwell (<1τ, under-thermalized) + only 100 pts (bigger steps) → that's what gave the ~80 mK lag.

**Verification (no ambiguous processing):** I'll check the lag directly — compare this run's Tc(optimum) to the prior settled value (~280 mK) and to run 4 (223 mK). If it lands near ~280 with small per-row T-drift, the lag is the few-mK we expect → ship. **Preconditions asserted** (B=B_eff0, gates at optimum, heater off). `fp`'s T/heater and plots heater.curr + T + R live. **Watch the fridge MC.** Checkpoints: first few steps (heater drawing, T tracking, n-line clean), then ~hourly. Run when ready.
