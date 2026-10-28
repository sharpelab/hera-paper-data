**Gate C verdict — liveness PASS; TG range restriction found (stop-and-report).**

- **Alive**: every channel responds — sr1/sr2 show strong, smooth gate response
  with neutrality-like maxima near 0 V on both gates; sr3 (Hall) sits at noise
  floor at B = 0 as expected; drain passes current in all conditions. No dead
  pairs, no shared-node short.
- **TG leaks on both polarities**: |I_tg − offset| exceeds 100 pA beyond
  **+4.45 V / −4.30 V**, reaching **+1.29 nA at +7.0 V** and **−0.53 nA at
  −6.0 V** — exponential turn-up, leakage, not charging (charging floor is
  ~15–25 pA). Runs 0/1.
- **BG clean** to ±4.5 V both sides (< 100 pA above the flat −100 pA channel
  offset; runs 2/3). Offsets at nplci = 10: BG channel ≈ −100 pA, TG ≈ +20 pA
  — read leakage relative to these.
- **sr0 railed** at X = 21.8 mV (2e-2 V sensitivity) over much of runs 1–3 —
  drain-current trace clipped. Implied I ≥ 22 nA is inconsistent with the
  nominal 0.5 V / 100 MΩ = 5 nA chain: Ithaco gain dial vs the recorded −1e6,
  or the bias-resistor value, needs a rack check. Liveness read unaffected.
- **Recommendation pending operator ruling** (`gate-leakage-survey` is
  blocklisted this session): design all sweeps within **TG ∈ [−4.0, +4.0] V**
  (leakage < ~60 pA there), BG full ±4.5 V. SAFETIES validators stay as
  committed — this is a design cap, not a safety-surface change. Cell B
  (nplci reset) held until the ruling.
