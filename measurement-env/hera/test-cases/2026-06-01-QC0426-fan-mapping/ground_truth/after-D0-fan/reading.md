# Ground truth — perception read of the latest landed sweep

*The expert-correct read of `data/27/` (the B-n Landau fan at the D = 0 line,
cell 102 of the served notebook), the freshest result at the frontier. Used to
score the perception layer (A) independently of the decision layer (B). Rendered
from the data via the device's own convention — see `figures/ana_27_fan_D0.png`
and `analysis/render_fans.py`.*

## What the sweep is

`s.multimegasweep([magnet.mag], [np.linspace(0, 8, 401)], [dc205_volt, k_bg.volt],
[vtg_new_vec, vbg_new_vec])` — a **B-n Landau fan** at the **charge-neutral D = 0
line**, base T ≈ 1.15 K (VTI). Comment: *"B-n sweep at D=0, DC205 for TG, K2400
for BG, ground Si, float other contacts."*

- **What it maps:** a 2D `Rxx(n, B)` Landau fan — the constant-D = 0 gate-line
  (`vtg ∈ [−6.5, 6.17]`, `vbg = vtg/1.3 + const`, 182 points, fast axis) co-swept
  versus **B (0 → 8 T, 401 steps, slow axis)**. Density `n` is computed from the
  gate-line via `calc_nD(Vtg=DC_bias, Vbg=k_bg_volt, c_tg, c_bg)`, `n_12cm =
  n·1e-16`; the gate-line follows the CNP D-line `Vtg ≈ −1.3·Vbg + 0.06` fit from
  the 0 T map.
- **Channels (this config):** current on **`sr0`** ("drain current", gain −1E6);
  voltages on `sr1 = 21-28`, `sr2 = 28-12`, `sr3 = 12-20`. `I = sr0_X / sr0_gain`,
  `Rxx = sr{1,2}_X / I`, `sr3` the Hall channel. Si **grounded**.
- **Field:** 0 → 8 T. **Temperature:** ~1.15 K.

So this is the **first field-resolved fan** of the campaign — the operator turning
the D = 0 gate-line into a Landau fan to see what quantum-Hall structure the device
shows.

## What it shows (floor — the must-see findings)

(Read directly from the re-formed `Rxx(n, B)` — see `ana_27_fan_D0.png`.)

- **A bright, near-vertical charge-neutrality stripe at n ≈ 0.** A tall insulating
  ridge (→ several ×10⁴ Ω) sits at the CNP across the whole field range, confirming
  the gate-line crosses neutrality and the device gaps out there; it is roughly
  field-independent in position.
- **Metallic away from neutrality.** `Rxx` falls to a low background (hundreds of Ω
  and below) on both the electron (n > 0) and hole (n < 0) sides out to the
  n ≈ ±13 ×10¹² edges of the gate-line — the device conducts well across the doping
  range.
- **Only faint, washed-out Landau structure.** The fan shows at best weak,
  smeared modulation fanning out from the CNP with field; **no sharp Landau-level
  diagonals or clean QH minima are resolved**. This is the key finding: the fan
  *works* but is **too washed out at ~1.2 K to read the stacking** — consistent
  with the campaign's "VTI didn't get cold enough" outcome.
- **`sr3` is the Hall channel.** As elsewhere in the cooldown, `sr3` carries the
  transverse (`Rxy`) component, not a clean longitudinal `Rxx`; the longitudinal
  fan is read from `sr1`/`sr2`.

## Correct read (one or two sentences)

A first **B-n Landau fan at D = 0** (Rxx = Vxx/I, sr0 = current, Si grounded) shows
a sharp insulating charge-neutrality stripe at n ≈ 0 and a metallic background on
both sides, but **only faint, washed-out Landau modulation — no resolved
Landau-level diagonals** at the VTI's ~1.2 K. The fan technique is established and
the D = 0 line is well-placed, but the fan is too featureless to read the
ABA/ABC stacking, so the productive next step is to make the fan cleaner /
extend control (add Si screening, push field, or move on to the D-series) rather
than to call the stacking from this map.

## Honest limitations / open questions (don't penalize the agent for these)

- **The disk `plot.png` shows the live monitor, not transport.** `data/27/plot.png`
  is the registered live-monitor view; the `Rxx(n, B)` fan requires forming
  `sr{1,2}_X / (sr0_X / sr0_gain)` from the TSV and reshaping row-major
  `(B, gate-line)` (exactly what the device's analysis does). An agent that only
  looks at the PNG sees no fan — reconstructing Rxx is the correct sub-step; flag,
  don't penalize.
- **Washed-out ≠ featureless device.** The lack of sharp LLs is a *temperature*
  limitation (~1.2 K), not evidence the device is bad; the same fan re-taken with
  Si screening at 13 T (run 31, post-cut) resolves more structure. Don't conclude
  "no quantum Hall" from this single warm fan.
- **Absolute D value is calibration-dependent.** D = 0 is the CNP line from the
  0 T map; the capacitance lever arms (`t_tg = 1.3·t_bg`, `t_bg = 12 nm`) are
  approximate until cross-checked against Landau-level filling factors
  (`ν` from `n = ν·e·B/h`) — which this washed-out fan does not cleanly permit.
- **Field zero is the magnet set-point, not an absolute B.** As elsewhere on these
  rigs, treat "0 T" as the current null.
- **Classification context.** This cooldown exists to classify the stacking
  (ABA vs ABC), read from the *field-resolved D-dependence* of the fan — not from a
  single D = 0 fan. Don't over-read stacking from `data/27`; the VTI's ~1.2 K base
  left even the later fans too warm for a definitive call (Qingrui leans ABA).
