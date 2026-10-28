# Ground truth — next move at the frontier (cut idx 32)

*What Isaac actually did in the next section (idx 33–40 / source cells
276–283). This is **one** expert path, not **the** answer — used to route the
replay to human review, never as an exact-match score. See benchmark-plan.md
"Imitation is a screen, not a score."*

## The move: `# B vs Idc`

Isaac's next experiment was a **magnetic-field × DC-bias map** at the fixed
(n, D) operating point where the SC-like feature lives:

- `mag.field(-0.012)` — park field at the start of the ramp.
- `s.megasweep(mag.field, np.linspace(-0.012, -0.002, 51), dc205_1.volt, np.linspace(-15, 15, 301), …)`
  → **`data/85/`**. Slow axis: out-of-plane field, −12 mT → −2 mT, 51 points.
  Fast axis: DC bias, −15 → 15 V (dc205), 301 points. Gates held at the
  Idc-vs-n operating point.
- `mag.field(-0.0068)` afterward — parks the field near the feature center.

## Why this is the right next step

The prior three sections established *that* there is a candidate superconducting
feature (a zero-bias differential-signal suppression with symmetric
critical-current-like peaks; see `reading.md`) and *where* it sits in density
and temperature. The open question for "characterize the superconducting state"
is then: **is it actually superconducting?** Field response is one discriminator
— a true SC critical current is suppressed by an out-of-plane magnetic field,
whereas a generic normal-state nonlinearity is not. Mapping the zero-bias
feature / Ic vs B is *consistent with* SC and gives a rough critical field.

> **Aaron, 2026-06-06:** field suppression alone does **not confirm** SC. The
> usual confirmation is evidence of phase coherence — a Fraunhofer-like
> interference pattern in Ic(B). Aaron would typically reach for a fixed-gate
> Ic-vs-B cut or the temperature dependence of Ic (Ic→0 at Tc) here. So treat
> Isaac's B-vs-Idc map as a reasonable move, not as the SC-confirming step.

## Class for judging

- **Same experiment:** propose a field (B) × DC-bias map at the SC operating
  point. (Exact field range / step count is parameter-level, not the decision.)
- **Same class, different params:** field dependence by another cut — e.g. a
  1D zero-bias-resistance vs B, or Ic-vs-B extracted differently.
- **Different but reasonable:** other legitimate SC-confirmation moves —
  temperature dependence of Ic (Ic→0 at Tc), Fraunhofer / current-phase if a
  junction geometry, finer Idc-vs-n to localize the feature before field work.
  A reviewer may rate these equivalent-or-better.
- **Divergent / worse:** abandoning SC characterization, re-running an already
  completed map with no new axis, or a move that ignores the field test
  entirely.

## Notes

- This is the SC-characterization goal proper. The subsequent
  `# find 90 degrees theta` section (idx 41+) is a calibration tail and is
  *not* the expected next move — if HERA proposes angle calibration here, that's
  a divergence from the stated goal, not a match.
