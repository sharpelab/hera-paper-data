# Analysis-reproduction ground truth (test type A′)

*Staged 2026-06-05. **Data only — the test harness is a later phase.*** This
captures Aaron's actual analysis of the sweeps around this frontier so a future
harness can pose the second test: **given a raw sweep, can HERA (a) reproduce the
analysis Aaron did, and (b) produce the result he drew from it?** This is the
analysis-layer analogue of the next-move test — one turn back, with Aaron's ana
notebook (`20251103_ana.ipynb`) as ground truth.

Each `method_<id>.py` is his **verbatim** ana cell for that input file_id (loads
via `sl.pload`, forms `Rxx = sr830_{3,5}_X / sr830_4_X`, plots). The expected
output is the matching figure under `../figures/`. The harness will need plotting
tooling + a data loader (`easyload`/`sl.pload`) wired for HERA — TBD.

| Input | His method | Expected figure | Result (what he concluded) |
|---|---|---|---|
| `data/134` | `method_134.py` (cell 12) | `ana_134_sc-dome-gatemap_sr830_{3,5}.png` | A low-Rxx **dome ridge** in (V_bg, V_tg); optimum pinned at (−5.2, 0.47); 7 candidate Fraunhofer points laid along the ridge. |
| `data/145` | `method_145.py` (cell 17) | `ana_145_dome-vs-field_sr830_{3,5}.png` | The dome in (V_tg, B): low-Rxx (~10 Ω) region **suppressed by perpendicular field, closing by ~8–10 mT**; consistent on both voltage channels. See `../reading.md`. |
| `data/150` | `method_150.py` (cell 19) | `ana_150_fraunhofer_sr830_{3,5}.png` | **Fraunhofer / Ic-vs-B⊥** map in (I_dc, B): a critical-current lobe centred at I_dc ≈ 0, spanning ≈ −25…+22 nA, **centred in field at B ≈ +7 mT** (evidence the perpendicular null is offset ~7 mT). *Post-cut — answer-key only.* |
| `data/151` | `method_151.py` (cell 20) | `ana_151_fraunhofer-rev_sr830_{3,5}.png` | Fraunhofer repeated with field swept the other direction (hysteresis / sweep-direction check). *Post-cut.* |

**Leakage note:** `data/150` and `data/151` are post-cut (the answer-key
Fraunhofer). They belong to the analysis-reproduction ground truth and to the
human review card, **never** to the served (≤ cut) workdir. `data/134` and
`data/145` are pre-cut (in the frontier allowlist).

## Open design question (for the later harness)
The analysis test needs HERA to *run* code (load, reshape, plot), so it requires
a tool surface the next-move test doesn't: a data loader + matplotlib + a way to
compare its figure/result to Aaron's. Scoring is likely "does it form Rxx
correctly (the sr830_4-as-current insight) and does it read the dome/field-
suppression," judged against the result column — not pixel match.
