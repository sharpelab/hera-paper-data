# Ground truth — perception read of the latest landed sweep

*The expert-correct read of `data/26/` (the finite-field B = 3 T TG-BG gate map,
cell 95 of the served notebook), the freshest result at the frontier. Used to
score the perception layer (A) independently of the decision layer (B). Rendered
from the data via the device's own convention — see
`figures/ana_26_gatemap_3T.png` and `analysis/render_maps.py`.*

## What the sweep is

`s.megasweep(k_bg.volt, np.linspace(-5, +4.8, 197), dc205_volt,
spoints(-6.5, +7.5, 281), slow_delay=1, fast_delay=1)` — a **2D TG-BG gate map**
over the full chosen gate box (back gate `k_bg ∈ [−5, 4.8]` × top gate
`DC_bias ∈ [−6.5, 7.5]`, a 197 × 281 grid), taken at **B = 3 T**
(`B field (T) ≈ 3.002`), base T ≈ 1.18 K (VTI). Comment: *"B=3T, DC205 for TG,
K2400 for BG, ground Si, float other contacts."* It is the finite-field repeat of
the 0 T map (`data/25`) that immediately precedes it.

- **What it maps:** `Rxx` across the `(Vtg, Vbg)` plane at fixed field — the
  zero-/finite-field characterization map. Carrier density and displacement field
  follow from the gate axes via the device's capacitance helper
  `calc_nD(Vtg=DC_bias, Vbg=k_bg_volt, c_tg, c_bg)`; constant-n runs along the
  CNP diagonal, constant-D along the orthogonal direction.
- **Channels (this config):** current on **`sr0`** ("drain current on 03",
  gain −1E6); `sr1` carries the longitudinal voltage (`21-28`); `sr2`/`sr3` the
  other contacts. `I = sr0_X / sr0_gain`, `Rxx = sr{1,2,3}_X / I`.
- **Field:** B = 3 T (set-point). **Temperature:** ~1.18 K.

So this is a **finite-field (3 T) TG-BG gate map** — the operator checking the
gate map at field after the 0 T characterization, the last step before adding a
full B axis.

## What it shows (floor — the must-see findings)

(Read directly from the re-formed `Rxx(Vtg, Vbg)` — see `ana_26_gatemap_3T.png`,
with the 0 T companion `ana_25_gatemap_0T.png` for reference.)

- **A sharp charge-neutrality ridge along the diagonal.** A bright high-`Rxx`
  (insulating, tens of kΩ) line runs diagonally across the map, with a low-`Rxx`
  metallic background (→ few hundred Ω) on both sides — the device gaps out at
  charge neutrality and conducts well when doped, across the full gate box.
- **The CNP line is `Vtg ≈ −1.3·Vbg + 0.06`.** The ridge sits on the
  negative-slope diagonal; the overlaid fit line (slope −1.3, the constant-D = 0
  line) lies on it. This is the line the coming Landau fan will co-sweep at
  fixed D = 0.
- **Finite field has not yet opened resolved QHE structure.** At 3 T and ~1.2 K
  the map is still dominated by the single CNP ridge — the diagonal looks much
  like the 0 T map, with at most faint modulation along/around neutrality, **not**
  clean quantum-Hall plateaus or a developed Landau fan. The field-resolved
  structure needs a proper B sweep (and is limited by the warm base T).
- **Good contacts / clean map.** A smooth, single-valued ridge with a well-defined
  CNP and no leakage streaks — the gate ranges are well chosen and the device is
  ready to be swept vs field.

## Correct read (one or two sentences)

A clean **finite-field (3 T) TG-BG gate map** (`Rxx = Vxx/I`, `sr0` = current)
shows a sharp charge-neutrality ridge along the `Vtg ≈ −1.3·Vbg + 0.06` diagonal
on a metallic background — the same CNP line as the 0 T map, now at field. At 3 T
and ~1.2 K the map carries only the CNP ridge, **no resolved Landau-level / QHE
structure**: the device is characterized in the `(n, D)` plane and the obvious
next step is to add the B axis and sweep a B-n Landau fan along the D = 0 line.

## Honest limitations / open questions (don't penalize the agent for these)

- **The disk `plot.png` shows the live monitor, not transport.** `data/26/plot.png`
  is the registered live-monitor view; the `Rxx(Vtg, Vbg)` map requires forming
  `sr{1,2,3}_X / (sr0_X / sr0_gain)` from the TSV and reshaping over the megasweep
  grid (exactly what the device's analysis does). An agent that only looks at the
  PNG sees no CNP ridge — reconstructing Rxx is the correct sub-step; flag, don't
  penalize.
- **2D gate map — in `hera-classify` scope.** Unlike the `after-density-cut`
  latest result (a 1D density cut), this *is* a 2D `(Vtg, Vbg)` transport map and
  the 2D-map classifier applies — though again to the re-formed map, not the
  on-disk PNG.
- **`sr1` vs `sr3` channel roles.** `sr1` is the longitudinal `Rxx`; in the
  field sections `sr3` is read as the Hall channel (`r_xy`). Reading the diagonal
  ridge as the longitudinal CNP line is correct.
- **Absolute n, D are calibration-dependent.** They come from the capacitance
  lever arms (`t_tg = 1.3·t_bg`, `t_bg = 12 nm`, SiO₂ term zeroed); the lever arm
  is approximate until cross-checked against Landau-level filling factors in the
  fan. Don't over-index on exact n / D from the gate axes alone.
- **Field zero / set-point.** "3 T" and "0 T" are magnet current set-points, not
  absolute fields; treat nominal zero as the current null.
- **Classification context.** This cooldown exists to classify the stacking
  (ABA vs ABC), which is read from the *field-resolved* fan, not this gate map —
  so the 3 T map is characterization/setup, not itself the discriminator. Don't
  over-read stacking from `data/26`; and note the VTI's ~1.2 K base left even the
  later fans too warm for a definitive call (Qingrui leans ABA).
