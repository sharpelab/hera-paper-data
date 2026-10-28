# Analysis-reproduction ground truth (test type A′) — b1c2 `after-idc-vs-n`

*Re-grounded 2026-06-05 (ana-notebook audit). Captures Isaac's actual analysis
convention for the sweeps around this frontier so a future harness can pose the
second test: **given a raw sweep, can HERA (a) reproduce the analysis Isaac did,
and (b) produce the result he drew from it?***

Isaac's convention (consistent across `20260415_ana.ipynb`, this cooldown's
`bottom device` wiring): the **current channel is `sr830_1`**
(`Ixx = sr830_1_X / sr1_gain`, sr1_gain = −1e6, so Ixx ≈ 1 nA AC). Transport is
formed as a ratio:

```
Rxx2 = (sr830_4_X / 1e2) / Ixx     # four-probe Rxx (sr4 = 30-31)
Rxx  = (sr830_2_X / 1e2) / Ixx     # two-probe-ish (sr2 = 28-4)
Rxy  = (sr830_3_X / 1e2) / Ixx     # off-diagonal  (sr3 = 5-30)
```

The `/1e2` is the SR830 voltage-channel gain (sr2/3/4_gain = 100). Bias:
`bias_resistor = 1e8 Ω`, so dc205 ±15 V → **Idc ≈ ±150 nA** (`Idc[nA] = dc205[V]·10`).

| Input | His method | Expected figure | Result (what it shows) |
|---|---|---|---|
| `data/84` | `method_84.py` (his convention; no dedicated cell — see provenance note) | `ana_84_idc-vs-n_Rxx_sr830_4.png`, `ana_84_idc-vs-n_Rxx-traces_sr830_4.png` | `Rxx(Idc, n)` along the density line at fixed D: a low-Rxx (~0–1 Ω) SC-like **diamond centered at Idc = 0**, widest mid-window (frames ~15–30) and narrowing toward both density ends → a **density-dependent critical current** (peaks at ±40…±90 nA). See `../reading.md`. |
| `data/85` | `method_85.py` (cells 34+35, **verbatim**) | `ana_85_B-vs-idc_Rxx_sr830_4.png` | **Next move.** `Rxx(Idc, B)`: the critical-current diamond is **maximal at B ≈ −6.8 mT (the trapped-flux null) and suppressed by perpendicular field** on both sides, closing by ~−2 / ~−11 mT — a field-suppression discriminator *consistent with* (not confirming) superconductivity; true confirmation needs phase coherence, e.g. a Fraunhofer-like pattern (Aaron, 2026-06-06). *Post-cut — answer-key only.* |

**Leakage note:** `data/85` is post-cut (the answer-key B-vs-Idc map). It belongs
to the analysis-reproduction ground truth and the human review card, **never** to
the served (≤ cut) workdir. `data/84` is the pre-cut latest sweep (in the
`after-idc-vs-n` frontier allowlist).

## Correction history (what drifted)
The pre-audit `reading.md` was authored from the raw measure-notebook inline
overlay (`images/cell274_out53.png`: T + raw sr830_{1..4}_X vs dc205), not from
Isaac's ana figures. It (a) called **raw `sr830_4_X` the "clearest signal"** and
**`sr830_1_X` a "featureless / railed dead contact"** — but `sr830_1` is the
**current** (denominator) and `sr830_4` is the Rxx **voltage** (numerator); the
quantity to read is `Rxx = (sr830_4_X/1e2)/Ixx`, not raw sr830_4. (b) Reported
the critical-current peaks at **"±8 in dc205"** — that is ±8 V dc205 = **±80 nA**,
not ±8 nA (off by the 10 nA/V bias factor). (c) Said the **density dependence was
"not directly legible"** — the 2D `Rxx(Idc, n)` map makes it plainly legible (the
Ic dome). Same wrong-current-channel / wrong-units drift class as the other
audited fixtures.
