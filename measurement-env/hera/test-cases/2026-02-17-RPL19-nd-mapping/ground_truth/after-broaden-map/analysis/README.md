# Analysis-reproduction ground truth (test type A′) — after-broaden-map

*Staged 2026-06-08. This frontier's analysis layer is about **reading a
data-quality artifact**, not extracting a physics quantity. The decision being
tested (re-sweep D-first to kill streaks) follows directly from correctly seeing
the n-first streaking in `data/1945`.*

| Input | Method | Expected figure | Result (what it shows) |
|---|---|---|---|
| `data/1945` | `../../after-rough-nd-map/analysis/method_1945.py` (Aaron's verbatim cell 141) | `../figures/ana_1945_broaden-map-nfirst_streaky.png` | **Latest sweep at the cut.** The broaden map, swept **n-first**, full range `n ∈ [0.2,1.8]`, `D ∈ [−0.4,1.065]`. Charge-neutrality line near D ≈ −0.1, constant-D feature lines, low-n/positive-D corner — but the high-Rxx positive-D corner **streaks along the fast (n) axis**. See `../reading.md`. |
| `data/1946` | `method_1946.py` (re-render of the same pipeline; Aaron re-swept rather than re-analyzed) | `../figures/ana_1946_dfirst-rough_destreaked.png` | **The next move.** The same landscape re-rastered **D-first** (coarse 101×101, positive-D). The streaks are gone; constant-D feature lines resolve cleanly — confirming the artifact was sweep-ordering, not physics. *Post-cut — answer-key only.* |

**Leakage note:** `data/1946` (and `1947`/`1948`) are post-cut and belong only to
the answer-key / review card — never the served (≤ cut) workdir. `data/1945` is
pre-cut (in the `after-broaden-map` allowlist). The on-disk `data/1945/plot.png`
is the gate-leakage monitor, not the transport map; the streak read comes from
re-forming `Rxx = sr830_{1,2,3}_X / sr830_4_X`.

## Note on figures
Both figures here were generated 2026-06-08 by re-running Aaron's pipeline
(`sl.pload` → `Rxx = Vxx/I` with sr830_4 as current → `calculate_n_D` axes →
`raster.pcolorize_data` → SymLog `pcolormesh`) on the local source data, since he
re-swept D-first rather than producing a verbatim ana cell for 1946. They are
faithful to his convention but are renders, not extracted ana-cell outputs.
