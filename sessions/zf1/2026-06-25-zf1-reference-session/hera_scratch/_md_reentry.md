## HERA — Gate C: re-entry baseline (constant-D n-cut, D = −0.64)

Bring-up passed: instruments connected & reading (magnet −0.015 mT, probe MC 33.8 mK, all lock-ins/gates/DC205 alive); SAFETIES committed in-kernel = device-card limits (TG −7/+6, BG −4/+4.2) + |B|≤100 mT + heater ≤6.5 V; probe (Probe2/rotator) logfile fresh to ~13 s, fridge logs advancing — **not** the stale-logfile trap. (n,D) calibration roundtrips the optimum exactly (n=−5.0, D=−0.64 → V_tg=−5.365, V_bg=+3.987).

**This cell** is the re-entry check before the campaign: a fast n-linecut at fixed **D=−0.64** (the provisional widest-point), n from −4.0→−6.0×10¹¹ (0.05 step, 41 pts), AC 1 nA, 4T sens 1 mV. Expect Rxx(4T, 30-31)→~0 near n≈−5.0×10¹¹ with normal/metallic flanks both sides — i.e. the dome survived handover. Coverage: this brackets the dome core into normal on both sides but is **1D** (Fig 1 does the 2D zoom next); it does not probe the high-|D| flank.

**Preconditions printed at top — eyeball before trusting the run:** T<60 mK, |B|<5 mT, heater=0, and gates reported (expected ~at the dome from the prior handoff). Cell asserts on T/B/heater.

**~1–1.5 min** (41 pts × ~1.2 s + a few-second gate ramp from the dome). Ends by parking gates **at the optimum** (V_tg=−5.365, V_bg=+3.987) so we're positioned for Step 0 (B_eff0). I'll read the result from disk and compare to runs 5–8 before proposing Step 0.
