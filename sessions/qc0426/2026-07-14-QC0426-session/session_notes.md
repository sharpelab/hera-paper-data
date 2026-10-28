# Session notes — QC0426 / VTI

Operational log (not a science notebook).

## 2026-07-14 — autonomy grant
- 13:2x PT: operator (Zack) gave "go for autonomy" — E1 engaged per brief.
  Consent-gated: DC205 ramp pacing. Banned: safety-surface edits, blocklisted recipes.

## Gate C findings (runs 0-3)
- TOOLING — meas_config['bias_voltage'] froze sr1.amplitude() at bring-up (4 mV residual)
  before Cell A set 0.5 V: hera-watch I_bias header reads 40 pA, R division off x125.
  Fix: refresh bias_voltage/sens keys in meas_config after setting drive, before next station build.
- TOOLING — hera-watch digests lock-in _X channels only; gate-current (Keithley curr)
  safety reads need a direct TSV read. Consider --channels support for non-lockin columns.
- Device: TG leaks on negative side — exponential onset ~-3.5/-4 V, -517 pA at -6.0 V
  (run 1). Positive TG clean to +7 V (32 pA max, run 0). BG+ clean to +4.5 V (run 2,
  ~-100 pA constant Keithley offset floor at nplci=10, not leakage). Operator ruling
  needed on TG negative operating range (gate-leakage-survey is blocklisted).
- Device: sr0 drain channel railed at X=21.8 mV (2e-2 sens) over much of runs 0/2; drain
  current exceeds nominal 0.5V/100MOhm=5 nA ceiling (7->21.8+ nA) — Ithaco gain dial vs
  card (-1e6) or bias-resistor value discrepancy; operator rack check requested.

## E0 drop (operator withdrawal)
- FEEDBACK — Zack withdrew the E1 grant after gate C: TG reached +1.3 nA at +7 V before
  the leg ended; his read: ~1 nA is a lot for a leakage test, possible device stress.
  I had verdict-ed it stop-and-report but only after the full leg ran. E0 until explicit re-grant.
- PROTOCOL — in E1 the recipe's "watch the live plot, interrupt on gross turn-up" maps to
  nothing: hera-watch digests exclude gate-current channels, so the mid-leg abort criterion
  was unmonitorable. Need either per-leg mid-run TSV gate-current checks or hera-watch
  --channels support for non-lockin columns (see TOOLING above).
- RECIPE FIX — gate-current-sanity-check: consider a per-leg current abort threshold in the
  cell itself (e.g. break/park when |I-I0| > 200 pA sustained), so the safety read doesn't
  depend on who is watching. Also: first-rows-only checkpointing misses late-V turn-ups by
  construction on 0->limit legs; periodic checkpoint should include the safety channel.

## Operator ruling — TG operating limit narrowed to [-3.0, +3.0] V
- FEEDBACK — Zack ruling (2026-07-14, after gate C + health re-check): TG design/operating
  range for the campaign is +/-3.0 V (was card [-6.0, +7.0]). Basis: leakage onset measured
  at +4.45/-4.30 V (runs 0/1); +/-3 keeps <~20 pA excess with n(D=0) reach +/-6.4e12 cm-2
  (worst-case scale -15%: +/-5.4e12), comfortably covering the FS-count model window (3.5e12).
  Device card updated (gate-limits table + session-findings block). Fresh session to be
  built from the updated card.
- Aaron verified the Ithaco preamp is set appropriately (gain matches card -1e6). The
  drain-current scale inconsistency is therefore NOT the preamp: sr0 railed at 21.8 nA
  (2e-2 V sens) vs nominal 0.5 V/100 MOhm = 5 nA ceiling. Prime suspect: bias-resistor
  value / drive chain. 30-s test queued for next session (unclip sr0, read I at heavy
  doping: I_max ~ 0.5V/R_bias).
- TOOLING/bring-up — measured lock-in front panels differ from card: sr0 tau=0.1s sens 2e-2;
  sr1 tau=0.1s sens 2e-2 (!! CNP signals ~7e-6 V = 0.03% FS -> the observed quantization/
  dropouts); sr2 tau=1s (under-settled at 1.2 s dwell) sens 1e-3; sr3 tau=0.3s sens 1e-4.
  Card: tau 0.3s all, sens ~2e-5 voltage channels for CNP/gate-map. Set panels per card at
  next bring-up before the gate map.

## Session close / handoff
- State reset cell run by operator (measure cell 37): nplci 1, lock-ins tau 0.3 s / 24 dB,
  sens 2e-5 (sr1-3) / 1e-2 (sr0), drive 0.5 V @ 13.14 Hz, gates/Si/field parked. Readback clean.
- Device card updated (TG limit [-3,+3], blinded) for the fresh session build. History
  retained here + ana notebook only.
- Open items for next bring-up: (1) sr0 clips >= ~11 nA at 1e-2 sens — consider 5e-2 until
  the bias chain is identified; (2) 30-s bias-chain test at heavy doping (I_max ~ 0.5V/R_bias);
  (3) session ended in E0 (grant withdrawn post-gate-C, not re-granted).
