# Ground truth — next move at the frontier (cut idx 95)

*What the operator (Qingrui) actually did in the next section (`# B-n sweep at
D = 0`, cells 96-102 → `data/27`, then extended in cells 111-115 → `data/31`).
This is **one** expert path used to route the replay to human review, not an
exact-match score. See benchmark-plan.md "Imitation is a screen, not a score."*

## The move: go to field — take the B-n Landau fan at the D = 0 line

Having characterized the device in the `(n, D)` plane (0 T gate map, plus a 3 T
gate map that still shows only the CNP ridge), the operator **adds the field axis
and sweeps the first Landau fan along the charge-neutral D = 0 line**:

- **Set up the D = 0 line.** Cell 97 records the CNP fit from the 0 T map,
  `Vtg = −1.3·Vbg + 0.06`, and cell 100 builds `(vtg_vec, vbg_vec)` along that
  constant-D = 0 line, clipped to the validators with an inline `sanitize_tg_bg()`
  helper.
- **D = 0 fan to 8 T** (`data/27`): `s.multimegasweep([magnet.mag],
  [np.linspace(0, 8, 401)], [dc205_volt, k_bg.volt], [vtg_vec, vbg_vec],
  slow_delay=5, fast_delay=1)` — **B as the slow axis (0 → 8 T, 401 steps)**, the
  constant-D = 0 gate-line as the fast axis — read as `Rxx = sr{1,2}_X / I`,
  `Rxy = sr3_X / I`.
- **Extended to 13 T** (`data/31`): the same D = 0 line swept **13 → 0 T**
  (261 steps), reaching the magnet's full field (this run also steps the Si gate
  to +60 V — the start of the Si-screening test that is the *next* frontier).

Figures: `figures/ana_27_fan_D0.png` (8 T), `figures/ana_31_fan_D0_13T.png` (13 T).

## Why this is the right next step

The gate maps (0 T and 3 T) place the CNP and fix the D = 0 line, but a gate map
carries **no Landau-level information** — and the campaign's whole purpose is to
**classify the stacking order (ABA vs ABC)**, whose fingerprint is the
**Landau-fan / quantum-Hall structure and its displacement-field dependence**.
You cannot read that off a zero-/few-tesla gate map; you have to go to field. The
natural move is therefore to **add the B axis to the just-characterized D = 0
line and sweep a B-n Landau fan** — establishing the fan technique at the
charge-neutral line first (where the LL sequence radiating from the CNP is the
cleanest handle on the stacking), before later introducing the Si gate and
sweeping the fan across a D-series. The 3 T map already hinted that finite field
alone doesn't resolve the structure at this base T; a full B sweep to 8 T (then
13 T) is what begins to bring the Landau diagonals out — though, at the VTI's
~1.2 K, the fans stay washed out (the CNP ridge dominates and the LL structure is
faint), which is exactly why the campaign could not make a *definitive* ABA/ABC
call (Qingrui leans ABA).

## Class for judging

A clear-answer **decision** (Qingrui did not treat it as contested):

- **Same move (expected):** go to field and measure a **B-n Landau fan along the
  D = 0 (CNP) line** — add the B axis to the characterized gate-line. Exact max
  field (8 vs 13 T), B step count, density window, and which channel is read as
  `Rxx` / `Rxy` are parameter-level.
- **Same class, different params:** a different but equivalent first field-resolved
  QHE probe — e.g. a gate-vs-B map at a fixed filling, a fan over a narrower n
  window, or fanning to a different max field. Equivalent. (Introducing the Si
  gate *together with* the first fan is also reasonable, though the campaign did
  the bare D = 0 fan first and added Si next.)
- **Different but reasonable:** more zero-field characterization first — a finer
  0 T map, four-probe symmetrization, or a re-check of the contacts/CNP — before
  going to field, is defensible if well-argued, though it postpones the
  field-resolved measurement the goal actually needs. Going to field but taking a
  fixed-gate `Rxx(B)` line instead of the CNP-line fan is weaker but on-axis.
- **Divergent / worse:** abandoning the field/QHE goal before any field-resolved
  fan exists — jumping to temperature dependence, bias spectroscopy, or warming
  up — or re-running the same 0 T / 3 T gate map unchanged. Sweeping the *D-series*
  of fans now (the `after-density-cut` answer) skips the prerequisite step of
  getting the D = 0 fan working in the first place.

## Notes

- **`data/31` carries the Si gate.** The 13 T extension also sets `Si = +60 V`,
  which is properly the *next* decision (introduce the Si gate — the `after-D0-fan`
  frontier). The bare D = 0 fan to 8 T (`data/27`) is the clean answer to *this*
  frontier; the 13 T run is preserved as the field-extension / answer-key context.
- **Contacts unchanged.** This block uses the characterization contact set
  (`sr0` "drain on 03", `sr1 = 21-28`, …); the later reconfiguration (`sr0` on 42)
  belongs to the 6 T / D-series block, not here.
- The two later decisions in this campaign (introduce the Si gate; sweep the fan
  across a D-series) are separate frontiers (`after-D0-fan`, `after-density-cut`);
  proposing *those* here jumps ahead of getting the first fan working.
