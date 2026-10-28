# Ground truth — perception read of the latest landed sweep

*The expert-correct read of `data/8/` (the last bottom-gate check, cell idx 37),
the freshest result at the `after-gate-checks` frontier. Floor + caveats, not an
exhaustive key.*

> **Re-grounded 2026-06-05 (ana-notebook audit).** This read was rewritten from
> Aaron's own analysis of the gate checks in `241207_ana.ipynb` **cell 8**
> (`for file in [7, 8]`, plotting `k_bg_curr` vs `V_bg`), with the top-gate
> companion in **cell 7** (`for file in [4, 5]`, `k_tg_curr` vs `V_tg`). The prior
> version **drifted on the leakage magnitude** — it claimed `k_bg_curr` rises to
> "order ~1e-8 A full scale," which is wrong by ~3 orders of magnitude. Aaron's
> own figure shows the leakage is **tens of pA (~5e-11 A scale), smooth and
> nearly linear** in gate voltage — i.e. a clean, well-behaved gate, even better
> than the prior read implied. The prior version also over-described SR830 "peaks/
> dips" and a "Vbg ≈ −5 to −8 feature": Aaron's gate-check cells plot **only the
> gate-leakage currents**, not the lock-ins, so any transport-feature claim from
> *this* sweep is not what he actually looked at here. Figures:
> `../figures/ana_8_bg-leakage_k_bg_curr.png` and
> `../figures/ana_5_tg-leakage_k_tg_curr.png`.

> **Re-grounded 2026-06-09 (Aaron, expert-review card).** Aaron rejected the
> "no breakdown out to ±20 V" framing of the 6-05 rewrite: *"Your numbers are way
> off. The vertical stripes are my safety margin for where the device begins to
> leak. That is way before ±20 V. The leakage is often asymmetric too, as you can
> see in the above plots. My limits were (−9, 5)."* I.e. the **deliverable of a
> gate check is a leakage onset + a chosen safety margin (often asymmetric), not
> a clean bill of health over the full probed range** — the axvlines are the
> *output* of the check, not decoration. The floor below was rewritten
> accordingly; the tens-of-pA scale describes the leakage *inside the working
> window*, not "no onset anywhere."

## What the sweep is

`s.sweep(k_bg.volt, np.linspace(0, -20, 401), delay=1)` — a 1D back-gate
(`k_bg`, 40 nm hBN) sweep from 0 to −20 V, 401 points, at base temperature, no
field. The back-gate validator was opened to ±20 V (cell 33) for this leakage /
breakdown probe. Followed parameters: `T`, the three gate leakage currents
(`k_tg_curr`, `k_bg_curr`, `k_si_curr`), and all nine SR830 `X`/`P` channels.

**How Aaron reads it (cell 8):** he plots **`k_bg_curr` vs `V_bg`** for the
back-gate sweeps (`for file in [7, 8]` — the 0→+20 and 0→−20 passes), with
`axvline(-9)` and `axvline(5)` marking the working validator window. The
companion cell 7 does the same for the top gate (`k_tg_curr` vs `V_tg`, files
4/5, axvlines at −5.5 and 6). These are **gate-health / leakage** reads — not
transport maps.

## What it shows (floor — the must-see findings)

- **The product of the check is an onset + a working window, not "no
  breakdown."** Per Aaron (2026-06-09) the device **begins to leak well before
  ±20 V**, and the leakage onset is **often asymmetric** between polarities. The
  axvlines at **−9 / +5** are his chosen **safety margins inside the onset** —
  the working window the check exists to establish. Reading the probe range as
  "healthy out to −20 V" is the mistake.
- **Inside the working window the back gate is clean.** `k_bg_curr` is smooth
  and nearly linear at the **tens-of-pA scale (~5–8 × 10⁻¹¹ A)** across the
  window — a charging / small series-leakage trend, no runaway. ⇒ the 40 nm hBN
  back gate is **gate-able within (−9, +5)**.
- **The top gate likewise** (cell 7): `k_tg_curr` is a smooth ~2–6 × 10⁻¹¹ A
  ramp across its window (−5.5 → +6 V) — margins likewise set inside the onset.
- Taken with the top-gate checks (data/3–5) and initial checks (data/0–2), the
  device is **alive and gate-able on all three gates within the chosen
  windows** — the green light to move to a 2D transport map over those windows.

## Correct read (one or two sentences)

The gate checks establish the **safe working windows**: leakage onset begins
well before the ±20 V probe range (asymmetrically), and the operator set safety
margins inside it — (−9, +5) on the back gate, (−5.5, +6) on the top — within
which leakage is smooth and tens-of-pA. This is a **liveness / gate-validation
pass** read off the gate-leakage currents — it establishes *that* the device is
gate-able and over *what window* to take the first (n, D) map, not *where* in
(n, D) the physics lives.

## Honest limitations / open questions (don't penalize the agent for these)

- **It's a gate-leakage check, not a transport map.** Aaron's cells 7–8 plot the
  gate currents only; the SR830 lock-in channels are *recorded* in the TSV but he
  did not read transport out of these gate sweeps. A correct read should NOT claim
  transport features (e.g. a "Vbg ≈ −5 to −8 feature") from this sweep — that
  framing was a prior-version over-read. Transport characterization is the *next*
  step (the gate map), not this one.
- **Leakage magnitude / onset shape.** The in-window scale is read off Aaron's
  y-axis (`Leakage (A)`, ~1e-11 scale) and is firmly tens-of-pA, not nA. The
  exact onset voltage / shape outside the margins is [VERIFY] against
  `data/8/data.tsv.gz` if a precise number is needed — what's authoritative is
  Aaron's statement that onset begins well before ±20 V and his (−9, +5) margin
  choice.
- **Phase / absolute transport** are not assessed here; the floor is the
  qualitative "onset found, margins set, gates clean inside the window —
  proceed to map over the window."
