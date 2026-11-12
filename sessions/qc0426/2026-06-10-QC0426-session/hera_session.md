# QC0426 / VTI / 2026-06-10 — live HERA session brief

*Session context for the first live agent-driven measurement session on the
VTI. This file is the `hera-vti` agent's first message — it names the goal,
activates the recipes, and carries the session-specific facts. The physics
method lives in the recipes; this brief deliberately does not restate it.*

*Supersedes the 2026-06-09 IRIS-style brief. The contract has flipped:
HERA drives.*

---

## Contract

- **HERA (agent, `hera-vti`)** — drives the session arc: decides what to
  measure next, reads every sweep from disk, commits to a direction, and
  lands paired markdown+code cells via `nb-collab append`. Protocol,
  gates, and boundaries: `hera_vti.md` (your agent prompt) — this brief
  does not repeat them.
- **Qingrui — operator.** At the physical keyboard. Executes every cell;
  running a cell IS the approval handshake; declining is the veto. Owns
  every instrument write and all physical rig actions. New to this flow:
  agent cells land *un-executed* at the bottom of the notebook — review,
  edit if needed, run or skip. Overriding the agent is normal and is
  feedback we want.
- **Zack — remote supervisor.** Same RTC notebook via SSH tunnel + the
  agent terminal. Talks to Qingrui out-of-band; his input arrives through
  the operator or the terminal.

## Campaign goal

**Determine the stacking order of QC0426 (trilayer graphene): ABA
(Bernal) vs ABC (rhombohedral).** The prior campaign on this device
mapped fans across displacement field but did not record a stacking
conclusion in the notebooks; this session's job is an independent,
evidence-cited, region-resolved call — or a calibrated "cannot tell."

**Active recipes** (read the actual files before proposing the
corresponding actions):

1. `~/measurement_env/hera/recipes/investigations/trilayer-stacking-id.md`
   — the decision procedure. The session follows its ladder: mine the
   disk → CNP-vs-D → channel triage → D≈0-region fan hunt → iterate →
   output contract. Its Verify section (signed chain detection, aliasing
   robustness, superposed-fan alternative) is mandatory for any feature
   claim.
2. `~/measurement_env/hera/recipes/measurements/landau-fan.md` — fan
   mechanics (toploader-flavored; sweep API and magnet facts below and
   in the device card take precedence on this rig).
3. Technique paper, ingested:
   `~/measurement_env/hera/docs/papers/ncomms14518/paper.md` (+ figure
   crops alongside). Cite its panels when claiming discriminating
   features.

**Tool**: the ABA forward model — `~/measurement_env/hera/models/aba_trilayer/`
(SWMcC LL spectrum with the paper's fitted parameters; predicted
crossing loci for any (n, B) window; `compare_qc0426.py` is the worked
overlay example; `uv run --no-project --with numpy --with scipy --with
matplotlib --with pillow`). This is the primary arc-reading method —
overlay predicted loci on TSV re-forms, single global density rescale
allowed (see recipe Verify). Works mid-fan: overlay on however many
B-rows have landed. Raw-render vision and untemplated ridge detection
are both demonstrated-unreliable on these features — model-overlay
first, always.

## Device + rig pointers

- **Device card**: `./device_card.md` in the measurement directory —
  gate stack, validators, channel conventions, contact map, field cap.
  Resolve its `[VERIFY]` markers with the operator before the first
  measurement cell.
- **Notebook set**: `20260610_measure.ipynb` (append_only),
  `20260610_ana.ipynb` (edit_no_exec), `hera_scratch/` (edit_exec).
- **Data**: each sweep writes `data/<id>/{data.tsv.gz, metadata.json,
  plot.png}`. Ids start at 0 in this directory. `plot.png` is the live
  monitor, not the measurement — re-form maps from the TSV (rendered
  images are not classification-grade evidence; recipe Verify).
- **Magnet**: parked nominally at 0 T (set value) after the prior
  campaign's last fan. Confirm before bring-up. Ramp-time arithmetic and
  no-re-traverse discipline per `hera_vti.md`.

## Reference pack — your ONLY prior data

**This is a fresh run.** Do not read other campaign directories — no
prior measurement data, notebooks, or analysis beyond what is in this
measurement directory. Your designated references (Gate C and
otherwise) are exactly:

- `./device_card.md` — gate stack, validators, capacitances/CNP-line
  constants, contact map, channel conventions (current = sr0_X/gain,
  gain −1e6; sr1/sr2 = Rxx pairs probing *different device regions* —
  triage them separately per the recipe; sr3 = Rxy in this wiring).
- `./reference/` — curated baseline snippets provided by the team: two
  B = 0 density cuts (D = ±0.25 V/nm, session wiring) with per-channel
  Rxx, plus a README stating the four re-entry comparisons (resistance
  scale, CNP position, shape, drain current). Compare your Gate C
  baselines against these; disagreement is stop-and-report.
- The recipes and ingested paper named above.

The recipe's "mine what's already on disk" step applies to *this
directory's* `data/` as the session accumulates runs — there is nothing
prior here by design. If you believe you need reference material beyond
the pack, ask the operator for it by name; do not go looking.

## Session arc

Gates A→C per `hera_vti.md` first (setup run, SAFETIES vs device card,
re-entry baselines: a 1D `k_bg` sweep and a short density cut vs the
designated references).

Then the recipe ladder, with the session-shaped emphasis:

1. **CNP-vs-D first — it is minutes, not hours.** Recipe step 1 does
   not need a full gate map: a single 1D co-swept gate line along the
   CNP at B = 0 (the device card's CNP-line constants, offset family
   collapsed to one sweep with n ≈ 0 and D varying across the full safe
   range) yields Rxx_CNP(D) directly at ~1.2 s/pt. Land the analysis
   (per channel, log-scale dynamic range over D) before any field work.
   This is the cheapest discriminator and it shapes everything after.
2. **Iteration-1 fan: the agent's call**, made against the recipe's
   logic and priced in wall-clock. Considerations (not exhaustive):
   - **D ≈ 0 is the regime where crossing chains are unambiguous**
     (recipe Why) — the natural first fan.
   - Electron side first; B to the session field cap; grid coarse
     enough to finish, dense enough that the ν-ray family is not
     near-Nyquist in the hunt window (recipe Verify, aliasing).
   - If the CNP-vs-D read was dramatic (strong gap growth), a fan at
     modest |D| watching the ν = 0 gap evolve is a complementary
     follow-up — but crossings at finite D no longer count as ABA
     evidence (recipe Why).
3. **Mid-fan reads**: re-form the partial fan from TSV as B-rows land
   and overlay the forward model's predicted crossing loci; flag early
   whether the fan is developing features or is washed out — abandoning
   a dead fan after 20 min beats discovering it after 90. Analysis
   continues through the operator-absence window.
4. **Post-fan**: full recipe Verify on any claimed feature (signed
   chains, robustness, superposed-fan alternative, lever-arm
   quantization), then iterate (recipe step 4: densify the feature
   window / change D / change contact pair) or close.
5. **The call**: the recipe's five-part output contract, landed in the
   ana notebook. *Cannot-tell with reasons is a successful outcome;
   a confident call without feature-level evidence is a protocol
   violation.*

## Timing + logistics

- Sweep arithmetic from the prior campaign's metadata: **~1.2 s/pt +
  ~30 s per B-row.** A 33-row × 101-pt fan ≈ 1 h 25 m; price every
  proposal (`hera_vti.md` wall-clock discipline).
- **Operator gap: Qingrui is away ~2–4 pm.** Plan the long iteration-1
  sweep to *start before* the gap and run through it; nothing can be
  approved/executed while he's away, so analysis-only during that
  window.
- Session budget ≈ 4–5 h including slack. Helium/schedule budget:
  `[VERIFY]` with operator.
- The device is wanted for a future toploader cooldown — it is not
  expendable. SAFETIES and validator discipline are hard.

## [VERIFY] with the operator at session start

- [ ] Magnet actually at 0 T (set value vs readback) before bring-up.
- [ ] Contact wiring unchanged since run 84 (D-series block:
  sr1=09-01, sr2=12-20, sr3=09-12, drain on 42)?
- [ ] Si gate value for new sweeps: +50 V (D-series convention) or
  other? k_2410 safe range?
- [ ] FastBi1K5: confirm the set call blocks and the session field cap
  (device card SAFETIES).
- [ ] Helium / schedule budget for ~5 h.
- [ ] Base temperature holding ≈ 1.2–1.3 K.

## Session notes

Maintain `session_notes.md` per `hera_vti.md` (RECIPE FIX / TOOLING /
PROTOCOL / FEEDBACK entries). This is the first live run of the
investigation recipe and the ABA forward model — gaps you hit are primary
deliverables of the day, not distractions.
