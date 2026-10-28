# Analysis-reproduction ground truth (test type A′)

*Staged 2026-06-05. **Data only — the test harness is a later phase.*** This
captures Aaron's actual analysis of the sweeps around this frontier so a future
harness can pose the second test: **given a raw sweep, can HERA (a) reproduce the
analysis Aaron did, and (b) produce the result he drew from it?** This is the
analysis-layer analogue of the next-move test — one turn back, with Aaron's ana
notebook (`241207_ana.ipynb`) as ground truth.

Each `method_<id>.py` is his **verbatim** ana cell for that input file_id. The
gate-check analysis is a leakage read: load via `sl.pload`, plot the gate
**leakage current** (`k_bg_curr` / `k_tg_curr`) vs the swept gate voltage. The
expected output is the matching figure under `../figures/`.

| Input | His method | Expected figure | Result (what he concluded) |
|---|---|---|---|
| `data/8` | `method_8.py` (cell 8) | `ana_8_bg-leakage_k_bg_curr.png` | Back-gate (40 nm hBN) leakage `k_bg_curr` vs `V_bg` for both passes (files 7 & 8): **smooth, near-linear, tens of pA (~5e-11 A), no breakdown** out to −20 V; working window (−9/+5) marked. The back gate is healthy. See `../reading.md`. |
| `data/5` | `method_5.py` (cell 7) | `ana_5_tg-leakage_k_tg_curr.png` | Top-gate (26 nm hBN) leakage `k_tg_curr` vs `V_tg` (files 4 & 5): smooth ~2–6e-11 A linear ramp across −5.5 → +6 V, no breakdown; working window marked. Top gate healthy. *Prior subsection (the `## Top gate` checks) — its result figure is the card's "what came before."* |

**Leakage note:** all inputs here (`data/4,5,7,8`) are **pre-cut** (gate-check
section, in the `after-gate-checks` allowlist) — no post-cut leakage to guard at
this frontier. Aaron's gate-check cells plot the **gate leakage currents only**,
not the SR830 lock-ins; the transport story starts at the gate map (next move).

## Method notes (what to reproduce)
- The reproduction target is a **gate-leakage read**, not an Rxx map: `data['k_bg_curr']`
  / `data['k_tg_curr']` vs `data['xs']`, with the working-window validators drawn
  as `axvline`s. The judgment is "gates healthy, leakage small, no breakdown."
- **Next move has no dedicated ana cell.** The first gate map (the `# Gatemap`
  next move → `data/9`) is not analyzed in its own cell; Aaron's gate-map cells
  load files 11, 14, and 18 (later passes of the same section). So there is no
  `method_9.py` — the next-move analysis surfaces at the `after-first-gatemap`
  frontier (`method_18.py`).

## Open design question (for the later harness)
The analysis test needs HERA to *run* code (load + plot), so it requires a tool
surface the next-move test doesn't: a data loader + matplotlib + a way to compare
its figure/result to Aaron's. Scoring is likely "does it plot the gate leakage
and conclude gates-healthy/no-breakdown," judged against the result column — not
pixel match.
