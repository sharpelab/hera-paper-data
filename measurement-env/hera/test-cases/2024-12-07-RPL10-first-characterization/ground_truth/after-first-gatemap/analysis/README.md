# Analysis-reproduction ground truth (test type A′)

*Staged 2026-06-05. **Data only — the test harness is a later phase.*** This
captures Aaron's actual analysis of the sweeps around this frontier so a future
harness can pose the second test: **given a raw sweep, can HERA (a) reproduce the
analysis Aaron did, and (b) produce the result he drew from it?** This is the
analysis-layer analogue of the next-move test — one turn back, with Aaron's ana
notebook (`241207_ana.ipynb`) as ground truth.

Each `method_<id>.py` is his **verbatim** ana cell for that input file_id (loads
via `sl.pload`, forms `Rxx = sr830_{ind}_X / sr830_4_X`, plots). The expected
output is the matching figure under `../figures/`. The harness will need plotting
tooling + a data loader (`sweep.sweep_load` / `sl.pload`) wired for HERA — TBD.

| Input | His method | Expected figure | Result (what he concluded) |
|---|---|---|---|
| `data/18` | `method_18.py` (cell 12) | `ana_18_gatemap_sr830_{1,2,3,5,6,7,8}_*.png`, `ana_18_gatemap_current.png` | The interrupted first gate map (landed V_bg ≈ −9…−7.9) resolves a **vertical low-Rxx stripe at V_tg ≈ +0.8 V** across the voltage channels; current steady ≈ 1 nA. He marks the candidate operating point **(V_tg, V_bg) = (0.825, −8.5)** on the stripe. See `../reading.md`. |
| `data/20` | `method_20.py` (cell 14) | `ana_20_dcbias_sr830_{1,2,3,5,6,7,8}_*.png` | **DC-bias line cut at the candidate point**, `Rxx` vs `I_DC` (`xs = data['xs']*10` → nA). Shows a **clear supercurrent signature: a near-zero-Rxx dip about I_DC = 0 flanked by sharp critical-current peaks at I_DC ≈ ±25 nA** (Rxx → ~0 Ω on 13-14; ~90 Ω dip floor on 9-11). This is the evidence the candidate stripe is a genuine SC/critical-current feature. *Post-cut — answer-key only.* |

**Leakage note:** `data/20` is post-cut (the answer-key DC-bias check, file_id 20
in the `# Checking DC on potential superconductor` section). Its method + figures
belong to the analysis-reproduction ground truth and to the human review card,
**never** to the served (≤ cut) workdir. `data/18` is pre-cut (in the frontier
allowlist). Note also that file_id **19** (the first DC-bias pass) has no
dedicated ana cell — Aaron analyzed only the `[20]` pass.

## Method notes (what to reproduce)
- **Current channel insight:** `I = data['sr830_4_X']` (the AC current bias, gain
  −1e6), `Vxx = data['sr830_{ind}_X']`, `Rxx = Vxx / I`. Reading a signal *out of*
  sr830_4 would be the mistake.
- **DC-bias axis:** `xs = data['xs'] * 10` converts the swept `dc205_1.volt` (0→10
  V then 10→−10 V, file 19/20) into `I_DC` in nA via the bias network — the ×10
  factor is Aaron's cooldown-specific volt→nA conversion (see [VERIFY] on the
  bias resistor in the device card).
- **Gate-map view:** zoomed `ylim(-9, -6)` to the landed strip; candidate point
  overplotted as a red dot at (0.825, −8.5).

## Open design question (for the later harness)
The analysis test needs HERA to *run* code (load, reshape, plot), so it requires
a tool surface the next-move test doesn't: a data loader + matplotlib + a way to
compare its figure/result to Aaron's. Scoring is likely "does it form Rxx
correctly (the sr830_4-as-current insight) and does it read the
stripe / supercurrent dip," judged against the result column — not pixel match.
