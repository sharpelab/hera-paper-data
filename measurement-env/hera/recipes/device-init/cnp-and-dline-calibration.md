# CNP-line and D-line calibration

*Base recipe, rig-agnostic. Mostly analysis: it consumes the cooldown's
first 0 T gate map and produces the validated (n, D) conversion and the
constant-D line designer that every coordinate-claiming recipe downstream
(`landau-fan`, `nD-map`, feature positions) inherits. The house
conversion is the capacitance form — `sharpelab_nb.gates`:
`stack_capacitance` / `calc_nD` / `calc_gate_voltages` — with the
device's numbers in the device card. (The legacy thickness-parametrized
`calculate_n_D` is the single-dielectric special case of the same
helpers; older notebooks also carry inline equivalents — use those only
to replot their own runs.)*

## What
From a 0 T gate map: locate the charge-neutrality ridge per channel, fit
the CNP line in (V_tg, V_bg), refine the gate-capacitance **ratio** from
its slope (a fitted CNP slope dV_tg/dV_bg *is* −c_bg/c_tg), set the
density offset from its intercept, and emit constant-D gate-voltage
lines clipped to the validators. Output is a calibration contract
written to the device card: per-channel fits, the chosen (c_tg, c_bg)
with provenance split — **ratio: data-calibrated; absolute scale:
geometry prior until a quantum-Hall lever-arm check upgrades it** — the
offsets, a residual quality number, and the D-line designer parameters.

## When
After `gate-range-finding` (validators committed) and a first `gatemap`
that shows the CNP crossing the swept window. Re-run when:
- the operating point of a screening gate changes (the CNP intercept
  shifts with it; the slope usually survives — verify, don't assume);
- `reentry-baseline` shows feature-position drift across a handover;
- quantum-Hall data lands and enables the lever-arm upgrade (step 5).

No new sweeps are required if the gatemap is adequate; if the CNP exits
the window or is clipped (step 1 guard), this recipe specifies the map
extension and hands back to `gatemap`.

## Why
Every (n, D)-coordinate claim downstream inherits this calibration:
wrong capacitances tilt a fan's co-swept fast axis (the "fixed D" line
silently varies in D), shift every filling-factor assignment, and move
feature positions between sessions. The CNP slope is the cheapest
precise calibration in the corpus — one polyfit on a map you already
have — and it measures exactly the quantity the conversion needs
(c_bg/c_tg). What it does **not** measure is the absolute scale: slope
and intercept are invariant under c → λc, so n and D magnitudes carry
the geometry prior's uncertainty until ray slopes (dn/dB = ν·e/h) or
SdH frequencies pin the scale. Keep the two tiers separate in every
write-back; an absolute-n claim quoted at ratio-grade precision is a
provenance error (STYLE rule 5).

## Recipe

**Step 0 — inputs.** Re-form the gate map from the TSV per channel
(`plot.png` is the live monitor, not the measurement), with the device
card's channel arithmetic — including any mandatory gain division on the
current channel. Pull the dielectric-stack prior from the card and form
prior capacitances: `c = stack_capacitance([(t_nm, kappa), ...])` per
gate (series stacks — e.g. hBN over SiO₂ — are first-class).

**Step 1 — extract the CNP ridge, per channel.** For each four-terminal
channel separately (a 2T argmax is pulled off the CNP by contact features
and the V_bg≈0 stripe; never average channels — on a mosaic device the
channels disagree and the disagreement is signal, not noise): along each
gate-map row, locate the Rxx maximum across the fast axis. Smooth before
argmax when noisy (a 1D gaussian along the fast axis is the corpus
idiom). Three guards:
- **edge-clipped rows**: a row whose maximum sits at the swept-window
  edge has not located the CNP — exclude it from the fit and report the
  surviving row coverage; many clipped rows means the map is inadequate
  (see When).
- **competing maxima**: away from the CNP, contact-driven features or
  secondary peaks can outrun the CNP maximum. Restrict the argmax to a
  window around the visually-continuous ridge, or enforce continuity
  row-to-row; a ridge that jumps discontinuously is two features, not
  one line.
- **railed / glitch rows**: a 4T channel can rail at its sensitivity
  ceiling along a gapped CNP, flat-topping the argmax. Fit robustly —
  iterative outlier rejection (drop rows >~2σ off the line and refit)
  recovers the slope from the surviving rows; report the surviving
  coverage.

**Step 2 — fit, per channel.** Linear fit (`np.polyfit`) of ridge
position vs row coordinate; report slope and intercept per channel with
fit residuals. **State the axis orientation with the fit**: the
`c_bg/c_tg = −slope` reading in step 3 assumes the ridge position is
V_tg (fast axis) fitted against V_bg rows — a transposed map yields the
*inverted* ratio (e.g. 1.3 ↔ 0.77) with no other symptom until the
Verify geometry check; name which gate was which axis in the write-back. Read the residuals before trusting the line: structured
curvature (quantum capacitance, screening nonlinearity) makes a linear
slope window-dependent — if present, fit over the operating window the
campaign will actually use and say so. Cross-channel check: slopes
agreeing to a few percent → one calibration for the device *(heuristic
threshold — n = 1 device to date; better: compare the disagreement
against the per-channel fit residuals and say which bound you used)*;
disagreement beyond that is real spatial variation — keep per-channel
calibrations, flag it, and carry the channel question forward (it feeds
channel triage in the stacking/feature recipes; this recipe records the
disagreement, it does not interpret it).

**Step 3 — update the conversion.** From the chosen fit:
- **ratio**: `c_bg/c_tg = −slope`. Hold the better-constrained gate's
  capacitance at its stack prior and set the other from the ratio
  (heuristic — usually the simple single-dielectric gate is the anchor;
  state which you anchored).
- **density offset**: choose `n_offset` so the fitted line maps to
  n = 0: with `b` the V_tg intercept at V_bg = 0,
  `n_offset = -calc_nD(b, 0, c_tg, c_bg)[0]`.
- **D offset**: leave 0 unless the device exhibits a feature that
  physically locates D = 0 (e.g. a symmetric response in ±D); if you
  set it, cite the feature. An unexamined D_offset = 0 is itself a
  stated assumption — say it.
- **closure check**: `calc_nD` along the fitted ridge must return
  n ≈ 0; quote the max |n| residual as the calibration quality number.

**Step 4 — design constant-D lines.** Generate gate vectors with
`calc_gate_voltages(ns, D0*ones, c_tg, c_bg, n_offset=...)` and **clip
to the committed validators by dropping out-of-range points, not
clamping them** (clamping bends the line in (n, D); dropping shortens
it). Report the *realized* n-window per D after clipping — at large |D|
it can be much narrower than requested, and a fan designed to the
requested window would silently lose rows. Design-time guards per STYLE
rule 12: point density along n sized to the finest expected feature,
stated in the proposing cell. Any run executed under this recipe (a
confirmation cut along a designed line) tags
`s.add_comment('cnp-and-dline-calibration')`.

**Step 5 — write back.** Device card gets: per-channel slope/intercept
(+ run id of the source map), chosen (c_tg, c_bg) with the two-tier
provenance, offsets, residual quality, realized D-line table, and the
explicit upgrade path: *absolute scale pending quantum-Hall lever-arm
check* — when field data exists, ray slopes must quantize
(dn/dB = ν·e/h); a non-integer Δν spacing means the scale is wrong and
every ν claim inherits the error (recalibrate before classifying).

## Verify
- **Roundtrip**: designed D-line vectors → `calc_nD` → D constant to
  numerical precision and n monotonic across the realized window.
- **Overlay**: fitted line drawn over the re-formed per-channel map —
  the ridge and the fit must track by eye; a fit that misses the ridge
  passed the math and failed the extraction (step 1 guards).
- **Geometry sanity**: compare the fitted ratio against the stack
  prior's ratio; agreement is confirmation, disagreement at the tens-of-
  percent level means a wrong thickness/κ in the card or a wrong gate
  assignment in the map axes — resolve before writing back.
- **Lever-arm upgrade** (when field data exists): the step-5 check.

## Examples
- `vti/qingrui/20260601-QC0426-3LGr` *(our-measurement)* — the worked
  chain this recipe encodes. Measure cells 81–88: the 0 T TG–BG
  megasweep pair (197-pt back-gate rows). Analysis cells 10–11: the
  per-row argmax + `polyfit` extraction, cell 11 adding
  `gaussian_filter1d` smoothing — yielding `Vtg = −1.3·Vbg + 0.06`
  per the Rxx channels. Analysis cell 15: `sanitize_tg_bg`, the
  clip-by-dropping D-line designer this recipe's step 4 generalizes.
  Analysis cell 24: the inline capacitance `calc_nD` (t_tg = 15.6 nm,
  t_bg = 12 nm, κ_hBN = 3) — now canonical in `sharpelab_nb.gates`; on
  this device the geometry ratio (15.6/12 = 1.3) and the fitted slope
  agreed exactly, the happy case of the Verify geometry-sanity check.
  The campaign's D-line offset table (line constant ≈ −8·D) is device
  card content, consumed by the fan-design cells (analysis 50/58/61).
- Toploader corpus *(citation)*: `gatemap.md` defers CNP extraction to
  a then-unwritten recipe, and `landau-fan.md` names an SdH-frequency
  `cap-ratio-calibration` (still deferred) as the independent
  cross-method. This recipe is the CNP-slope method; the SdH method,
  when written, refines the same (c_tg, c_bg) from fan data and slots
  into step 5's upgrade path.

## Next
- Default: the campaign's first designed measurement — the D-lines feed
  `landau-fan` fast axes and `nD-map` polygons; the realized-window
  table from step 4 is the input to their wall-clock pricing.
- Quantum-Hall data lands: run the lever-arm check (step 5); on failure,
  recalibrate and re-emit the D-line table before any ν assignment.
- Per-channel slopes disagree: carry the per-channel calibrations into
  the campaign's channel-triage step (`trilayer-stacking-id` step 2 or
  equivalent); do not average them away.
- CNP clipped or absent in the map: extend the `gatemap` window (or
  revisit `silicon-backgate-survey` — a screening-gate operating point
  can move the CNP into reach), then re-enter at step 1.
