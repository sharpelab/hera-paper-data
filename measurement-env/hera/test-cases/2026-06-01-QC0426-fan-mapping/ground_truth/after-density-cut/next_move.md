# Ground truth — next move at the frontier (cut idx 180)

*What the operator (Qingrui) actually did in the next sections
(`# B-n sweep at D=0.25` … `D=-0.5`, cells 181-200 → `data/80-84`). This is
**one** expert path used to route the replay to human review, not an exact-match
score. See benchmark-plan.md "Imitation is a screen, not a score."*

## The move: sweep the density cut into a Landau fan, then map the fan across D

Having confirmed the reconfigured contacts with a clean 0-field density cut along
the D = 0.25 line (`data/79`), the operator **adds the field axis and sweeps the
Landau fan across a series of displacement fields**:

- **D = 0.25** (`data/80`): the same `vtg ∈ [1, 5]`, `vbg = vtg/1.3 − 2` line, now
  swept vs **B (8 → 0 T, 161 steps)** at finer density resolution (201 points) —
  i.e. the density cut turned into a **B-n Landau fan**.
- **D = 1** (`data/81`): line `vtg ∈ [5, 7.5]`, `vbg = vtg/1.3 − 8`, B 0 → 8 T.
- **D = −1** (`data/82`): line `vtg ∈ [−6.5, −4]`, `vbg = vtg/1.3 + 8`, B 8 → 0 T.
- **D = −0.25** (`data/83`): line `vtg ∈ [−1.6, 2.4]`, `vbg = vtg/1.3 + 2`.
- **D = −0.5** (`data/84`): line `vtg ∈ [−3, 1]`, `vbg = vtg/1.3 + 4` — **this
  last fan was interrupted ~halfway** (79 of 161 B-steps).

Each fan is a `multimegasweep([magnet.mag], [...], [dc205_volt, k_bg.volt],
[vtg_vec, vbg_vec])` — B as the slow axis, the constant-D gate-line as the fast
axis — read as `Rxx = sr{1,2}_X / I`, `Rxy = sr3_X / I`. Figures:
`figures/ana_8x_fan_*.png`.

## Why this is the right next step

The density cut (79) established that the D = 0.25 gate-line is clean and crosses
the CNP, but a single 0-field line carries **no Landau-level information** — and
the campaign's whole purpose is to **classify the stacking order (ABA vs ABC)**,
whose fingerprint is precisely the **Landau-fan structure and its
displacement-field dependence**. The natural move is therefore to (1) add the
field axis to the line just verified, producing the **D = 0.25 Landau fan**, and
(2) **repeat across a spread of displacement fields** (D = 1, −1, −0.25, −0.5):
ABA (Bernal) and ABC (rhombohedral) trilayer differ in how the Landau levels
disperse and how the bands respond to D, so mapping the fan across D is the
discriminating measurement, not just generic coverage. The zoomed D-fans
(e.g. `data/82`, D = −1) resolve clean Landau diagonals radiating from the CNP
that the wide-range D = 0 fan (27) only hinted at — confirming the focused
per-D fan is the productive measurement (even though, at the VTI's ~1.2 K, the
fans stay too washed out for a *definitive* ABA/ABC call — Qingrui's suspicion is
ABA).

## Class for judging

A clear-answer **coverage** decision (Qingrui did not treat it as contested):

- **Same move (expected):** take the Landau fan at the just-verified D = 0.25 line
  (add the B axis) and **extend the fan measurement across a D-series**. Exact D
  values, order, B range (0-8 T), and density windows are parameter-level.
- **Same class, different params:** a different but equivalent coverage of the
  same axis — e.g. a denser or coarser D grid, fewer/more D points, fan to a
  different max field, or building a 2D `Rxx(n, D)` map at a fixed B (e.g. the
  6 T map already taken) as the coverage vehicle. Equivalent.
- **Different but reasonable:** drilling deeply into the **single D = 0.25 fan
  first** (high-resolution, symmetrization, LL gap extraction) before sweeping the
  rest of D is defensible if well-argued, though it postpones the D-coverage the
  goal calls for. Re-checking the contacts/CNP once more is weak but harmless.
- **Divergent / worse:** abandoning the fan/QHE goal (e.g. jumping to temperature
  dependence, a bias-spectroscopy series, or warming up) **before** any
  field-resolved fan exists; or re-running the same 0-field density cut unchanged.

## Notes

- **The interrupted D = −0.5 fan (84)** is a real campaign detail — the series was
  cut short partway through the last D point. An agent is not expected to predict
  the interruption; it is preserved as honest ground truth.
- **Contacts were reconfigured** for this block (`sr0` on 42, `sr1 = 09-01`,
  `sr3 = 09-12`) before the density cut — already in hand at the cut, so choosing
  the fan does not require a contact change.
- The two earlier decisions in this campaign (0 T map → first fan; D = 0 fan →
  introduce the Si gate) are separate frontiers (`after-0T-gatemap`,
  `after-D0-fan`); proposing *those* here would be re-deciding already-settled
  steps.
