# HERA SdH/fan analysis fix — verification plan

*My take + the gap, written as the benchmark answer-key. A collaborator is doing
this work; grade theirs against this. The question being answered:* **"Have I
fixed the issues that caused a bad fan and SdH analysis?"** *(QC0426 session-3,
2026-06-19.)*

## Operator notes from running these by hand — from Claude

*Hard-earned while running the A/B/C/D replays manually this session (2026-06-20).
These are the friction points and traps a built tool should absorb; until then,
they're the checklist. Written by Claude at Zack's request.*

- **`PYTHONPATH=src` or you're testing the wrong commit.** `python -m hera.replay`
  binds to the **installed** package (the main checkout), not the worktree you
  `cd` into. `repo = parents[2]` of the loaded module → the agent's recipes
  (`--add-dir`) *and* its `import hera.analysis` both follow the install. This
  silently ran B on current hera instead of my worktree. **Always pass
  `PYTHONPATH=src`, and verify `runs/.../prompt.md`'s "recipe corpus is at …"
  line points at the intended worktree before trusting a result.** A built tool
  must pin the commit explicitly, not via cwd/install.
- **Verify no Bash escape.** The agent's Bash isn't confined to `--add-dir`; it
  can `cat` the main checkout (B read `field_invB` that way). After a run,
  `grep result.json` for foreign paths (`/measurement-env/hera/recipes` vs your
  worktree). Real fix is the sandbox (full-tier req #2).
- **A/B-across-commits is ~6 fiddly steps per commit by hand**: worktree at the
  commit → copy the fixture in (it postdates old commits) → edit if testing a
  recipe change → `PYTHONPATH=src` run → verify pinning → verify no escape →
  extract the axes → diff. That's the whole argument for the high-SNR one-flag
  invocation (req #1): `replay <fixture> --frontier X --commit A --commit B`
  should do all of it and hand back the comparison.
- **Leak terms grep the cropped notebook *including outputs*.** Generic numeric
  tokens collide with output noise (`"451"` tripped a false leak). Use
  distinctive post-cut-only strings (recipe slugs, sweep-call names, section
  labels), and verify against the actual cropped `.ipynb`, not just the source
  cells.
- **Trim `workdir/` before keeping a run.** Each run drops a regenerable
  `workdir/` (hardlinked data + notebook) that dominates the size; the keepers
  are `output.md` / `result.json` / `prompt.md` / `manifest.json`.
- **Cost per run** ≈ \$1.3–1.7, a few minutes (opus-4-8). Cheap enough that —

  **From Zack:** *n = 3 and run them in parallel should be the standard practice
  once the thing is built.* (The driver already has `--samples N`; carry it
  through, and parallelize across commits too — variance/CI for free, and it
  removes the "one sample, was it luck?" caveat that dogs every result above.)

## Run discipline — preregister + score (the norm, not a hard rule)

Treat replays as experiments: each run should state a **hypothesis** (directional,
per axis — e.g. "cost-floor gate → cost down, rest unchanged-or-better") and its
**points of interest** up front, and be scored against a **standard rubric** tied
to the frontier's `ground_truth` axes. Not a hard requirement — the norm, so "did
it help?" is a measurement rather than a vibe. (Worked instances: the A/C/B/D
runs below.)

Two tiers. The cheap offline replay (built, used below) is the **screen**; a more
expensive **full replay** is the **confirmation tier**, deployed only after a fix
clears the cheap stage. This is the answer-key for the collaborator — minimum is
"extend the offline replay and report"; the **target is to build the full tier**;
stretch is surprising judgement/results (e.g. catching a harness artifact, as
the 1/B finding below did).

**What the full tier is.** Resume the *real session transcript* at the cut and
run the agent **in a sandbox**, instead of feeding a synthesized frozen-state
prompt. Higher fidelity to what the live agent actually saw; costs more, so it
runs second.

**Requirements (hard):**
1. **High-SNR invocation.** One command/skill/agent; the ratio (result tokens /
   setup tokens) must be high — cheap for both Zack and Claude to fire. Form is
   free (skill `/hera-replay-full <fixture> <frontier>`, a shim, or an agent) so
   long as setup is ~one line and the result is the comparison, not a transcript
   dump. A/B-across-commits should be one flag, not two manual worktrees.
2. **Sandbox.** Filesystem/network confinement (container/bwrap): only `workdir`
   + recipes mounted, Bash cannot reach the uncropped notebook / `ground_truth/`.
   Turns the leak guarantee from *trusted* (today's replay TODO) into *enforced*.
3. **Transcript resume.** Reconstruct the agent's real context at the cut from
   the archived session `.jsonl` transcripts, not the synthesized frozen-state
   prompt — start from the real conversation state.
4. **Backtested for accuracy (hard).** Validate the full replay by resuming a
   frontier whose real next-move is recorded, and checking the replay reproduces
   the **real agent's actual decision** within tolerance. Report a fidelity
   score; a replay that doesn't match real runs isn't trustworthy.

**Bonus:** `--samples N` → decision variance / agreement-rate / CI (the offline
driver already has `--samples`; carry it through).

**Extra credit — classify replay fidelity.** Three-way: real run vs
full-sandbox-replay vs offline-replay. Quantify how well the *cheap* tier tracks
the *expensive* tier and the real run; if offline meaningfully diverges, improve
the offline harness. (Live motivation below: the offline run surfaced a
tooling-import asymmetry and a docstring-induced hallucination — a sandbox +
transcript-resume would constrain both.)

## A/B RESULT — layer-B fan-proposal replay (2026-06-20)

> **CORRECTION (methodology bug).** The B run did **not** execute on the commit
> intended. `python -m hera.replay` *without* `PYTHONPATH=src` loaded the
> **installed** package (the main checkout, at `7d488f6` = current hera, which
> includes the landed **1/B-sweep change**), so B's recipes (`--add-dir`) and
> `import hera.analysis` both resolved to current hera — **not** my worktree
> `85a174c`. A was launched with `PYTHONPATH=src` and ran correctly on the
> pre-fix worktree (`82883a9`). Consequences: (1) `field_invB` was **real**, not
> hallucinated — current hera's `sdh-spot-check.md` defines/cites it and B read
> it; the "fabricated citation" claim is retracted. (2) The **1/B change WAS in
> the test**, on the B side. (3) **B = `7d488f6`, not `85a174c`.** The
> fan-design findings below still hold (the burn #7/#8 guards are in both bases).
> **Harness lesson:** the worktree A/B is fragile — tooling binds to the
> *installed* package and `repo = parents[2]` of the loaded module, so the lever
> silently follows what's installed, not what's checked out. Pin the commit
> explicitly (and sandbox) — see the full-tier requirements above.

Ran the real two-worktree `hera-replay` at the `after-sdh-spot-checks` frontier
(cut after the electron spot-check, before the fan). Fixture:
`hera/test-cases/2026-06-19-QC0426-stacking/`. Same harness, same model
(opus-4-8). **Effective bases: A = `82883a9` (pre-fix), B = `7d488f6` (current
hera).** **Question: does HERA propose a fan without the two acquisition faults —
under-ranged sensitivity (clipping) and shaved fast-axis dwell (under-settling)?**

| Axis | A — pre-fix (`82883a9`, no guards) | B — post-fix (current, guards) | Winner |
|---|---|---|---|
| **Sensitivity** (avoid low-n/high-B clip) | `1e-5` inherited from the metallic spot-check, asserts "no clip 0–4 T" — but its n-line spans to +1e12, so it **reproduces the burn-#7 clip fault** | `5e-5`, explicit *"worst corner = low-n × high-B; data/2 clipped"* — **sized to the worst corner, no clip** | **B** ✅ |
| **Fast-axis settling** | `fast_delay=2.2 s` = **7τ, full floor** (inherited the spot-check dwell) | `fast_delay=1.2 s` = **4τ**, rationalized as "the floor" (under-spec for 24 dB/oct) | **A** ✅ |

### Three-way result (A / C / B) — added the clean middle run

Ran **C** = the guards-but-pre-1/B base (`85a174c`), correctly pinned with
`PYTHONPATH=src` (verified: recipes = the worktree, no main-checkout escape, no
`field_invB`). With "4τ is fine for a 1/B/FFT fan," the picture resolves:

| Axis | A — `82883a9` (no guards) | C — `85a174c` (guards, no 1/B) | B — `7d488f6` (guards + 1/B) |
|---|---|---|---|
| **Sensitivity** | `1e-5` inherited → **clips** (fault) | **`1e-3`, explicit `R(n_min,B_max)` = CNP-R×MR arithmetic** (best) | `5e-5`, qualitative worst-corner bump (good, less rigorous) |
| **Settling** | `2.2 s`/7τ — by *blind inheritance*, no reasoning | **`1.2 s`/4τ, explicit "do not shave for amplitude-for-time"** (guard bites) | `1.2 s`/4τ (fine) |
| **B sampling** | uniform-B 8 mT | uniform-B 8 mT + **trim n for cost** (recipe's measurement-dominated branch) | **uniform-1/B** (`field_invB`, defined in the measure-notebook template — runs fine) — best sampling |
| **Sweep cost** | ~12 h (501 B × 41 n; also offered a 16 mT/251-row coarsen — mild anti-pattern) | **~12 h** (501 B × 61 n, held 8 mT, trimmed n — recipe-correct) | **~24 h** (400 B × 151 n to +8e12) — **2× for marginal gain (serious ding)** |

**Conclusions (correcting the half-confirmed framing above):**
- **The guards work — C is the clean proof.** Guards + no-1/B confound, properly
  pinned → HERA addressed **both** faults, and on sensitivity *more rigorously
  than B* (it did the recipe's explicit `R(n_min,B_max)` arithmetic → `1e-3`,
  where B only qualitatively bumped to `5e-5`). Zack's hope — "both τ and sens
  addressed" — is met.
- **Settling guard DID bite (earlier "backfire" retracted).** With 4τ
  acceptable, C *held* 4τ and explicitly refused to shave it (citing the
  amplitude-for-time mistake). A's 7τ was blind inheritance, not reasoning.
- **A reproduces the sensitivity fault** (`1e-5` inherited, clips).
- **Cost is a first-class axis (and it sinks B here).** B's `n_max = +8e12`
  (151 n-points, to resolve the high-n ML partner *beyond* the Onsager-overlay
  validity ≤3.5e12) drove the fan to **~24 h — 2× A/C** for marginal, partly
  out-of-validity gain, and it only cleared prefer-1/2 (not 1/3). C got the same
  correctness at **~12 h** by holding 8 mT and trimming n (the recipe's
  measurement-dominated branch). **Any acquisition-design criterion must price
  the cost delta** — a "better" fan that doubles fridge time for an
  out-of-validity corner is not better.
- **The 1/B change (B vs C):** the uniform-1/B *sampling* is the right idea and
  `field_invB` is real (defined in the measure-notebook template — B's cell
  runs). But it did *not* improve the two acquisition-fault axes (B's sensitivity
  reasoning was weaker than C's), and B bundled it with the cost overreach. Net:
  good sampling idea, orthogonal to the faults, and not worth a 2× cost on its
  own.
- **Docstring worry retired.** C (my worktree, my `sdh_fft` docstring, no 1/B
  recipe) did **not** invent `field_invB` or propose 1/B sweeping → `field_invB`
  in B came purely from the real recipe on `7d488f6`, not my docstring. The
  earlier "tighten the docstring" actionable is withdrawn.

**Net answer to the question:** the SdH/fan fix (the guards) **works** — a
properly-pinned guards run (C) designs the fan without either fault **and**
without a cost blowup. The separable **1/B-sweep change** is a sound sampling
improvement (helper lives in the notebook template today; should move to
`hera.analysis` — new subtask), but it's orthogonal to the two faults and must
not be allowed to inflate sweep cost.

**Harness/tooling findings from this run (the "surprise" class):**
- **The B base silently followed the install, not the worktree** (see the
  correction banner). B = `7d488f6` (current hera, *with* the 1/B-sweep change),
  not the `85a174c` I launched from. So this run accidentally bundled the 1/B
  change into B — to run the *guards-only, no-1/B* test Zack wants, B must be
  pinned to `e5654b5`/`85a174c` (force `PYTHONPATH=src` + a worktree at that
  commit). The 1/B change should be A/B'd *separately* (`85a174c` vs `7d488f6`).
- **`field_invB` is real on current hera** and B used it correctly — the
  uniform-1/B fan B proposed is the landed recipe behavior, not an invention. (My
  earlier hallucination claim was an artifact of checking my stale worktree.)
- **Tooling lever was asymmetric:** B (current hera) imported + used `sdh_fft` +
  `sdh_onset`; A (`82883a9`) **hand-rolled** the FFT (`np.polyfit` 1/B detrend +
  `interp` + `np.fft.rfft`), using `hera.analysis` only to load. So the
  spot-check *read* difference isn't cleanly attributable to the sdh_fft code
  version — and **both still got the two-pocket ABA read**. That B used the
  helper traces to the recipe pointing at it (a recipe win).
- **Unsandboxed Bash is a live risk:** the agent's `Bash` is not confined to
  `--add-dir`, so even with a correctly-pinned worktree it can `cat` the main
  checkout. Enforced sandboxing (full-tier requirement #2) is necessary, not
  theoretical.

(Outputs: the fixture's `runs/after-sdh-spot-checks/{prefix,postfix}-*/output.md`.)

## The question, made precise

A "fix" has to be demonstrated on two layers, not asserted:

- **Layer A — perception.** Does the corrected tooling *read the SdH/fan FFT
  right*? Concretely: on the run-3 electron spot-check, do the three tones
  resolve with a near-F_L tone dominant over the spurious 8 T; on the run-4
  fan, does the ML ridge appear across density without having to hide a low-F
  band.
- **Layer B — decision.** Given that corrected read, does **HERA's next move**
  at the relevant decision point improve? This is the thing that actually
  matters — perception is necessary, not sufficient.

"Have I fixed it" = **yes on A, and A flows through to a better B at the point
where the bug bit.**

## Root cause (what made the fan + SdH analysis bad)

The SdH FFT helper detrended in **1/B space** (polynomial of the resampled 1/B
signal). The magnetoresistance background is smooth in **B**, not 1/B, so a
1/B-space detrend leaves background residual that piles into the low-frequency
FFT bins and **inflates the slowest tones**. Two concrete harms in session-3:

- **Spot-check (run 3):** the ~8 T (monolayer) tone was artificially made
  *dominant*, muddying the ML+BL+F_L tone structure.
- **Fan (run 4):** to suppress the low-F residual the in-session analysis had to
  crank the detrend to **order 7** *and* **hide the `<6 T` band** (see the
  session's own `ana_cell_fan_fft2.py`: *"stronger detrend (order 7) to suppress
  the ~5 T low-F residual band"*, *"ML partner (~8 T) sits in the hidden low-F
  band → see spot checks for it"*). The fan FFT therefore **could not show the
  ML ridge across density** — the partition read was deferred to the spot checks
  and the fan under-delivered.

Net: the stacking read was muddier than the data supports. (The session call was
not a hard wrong binary — it held "ABA, or ABA+ABC mixed; ABC-singleton
excluded" and deferred the partition — but the tooling kept the fan from
settling it.)

## The fix (what changed)

Landed on `hera` (and `subtask/qc0426_archive`):

- **`hera.analysis.sdh_fft` → B-space background subtraction** before the 1/B
  step (degree-5 polynomial in B, mean-subtracted), replacing the 1/B detrend.
  Knob renamed `detrend` → `bg_degree`. No back-compat.
- **Conditional 1/B resample**: decide uniform-in-1/B vs uniform-in-B from the
  spacing distribution; FFT directly when already uniform in 1/B, else
  interpolate. No uniform-ΔB assumption baked anywhere.
- **`hera.analysis.sdh_onset`** (+ `SdhOnset`): low-B edge of the usable window
  via a consensus-frequency band + sustained-from-top walk; returns the onset,
  the high clip edge, and the SNR(B)/peak-freq curves so a caller picks its own
  cutoff. Robust to the non-monotonic SNR(B) curve (a spurious low-B spike).
- **Recipe corpus**: `sdh-spot-check.md` now points at the helpers (API +
  `SdhOnset` fields) and states that the FFT low-field cutoff sits *above* the
  bare onset (low-B residual inflates the slowest tones). `trilayer-stacking-id.md`
  marked deprecated (superseded by `trilayer-stacking-fs-count.md`, the live
  FS-counting investigation). STYLE rule 15 added (recipe cross-references point
  sideways/down, never up to an investigation).

## How to verify — the harness

### The two commits = the A/B knob

- **A (BEFORE)** = `82883a9` — session-3 archived *as-run*; `sdh_fft` is the old
  1/B-space `detrend`.
- **B (AFTER)** = `e5654b5` (or current `hera`) — B-space `sdh_fft` + `sdh_onset`
  + updated recipes.
- `fan_grids` / `resistance_grids` are **byte-identical across both** → the only
  thing that changes is the detrend space. Clean controlled swap.
- A commit bundles **both** levers `hera-replay` cares about: analysis tooling
  (`hera.analysis`) **and** the recipe corpus (`hera/recipes`). Since the fix
  spans code *and* recipe, "commit A vs B" is the right single knob. Realize it
  by running from a **worktree checked out at A** vs **a worktree at B**.

### The runs (mind the fixture conflation)

- **`tests/hera/fixtures/qc0426-sdh-electron`** is **run 3 — the SdH
  spot-check**, *not* the fan. Its layer-A A/B is already documented (B-space
  flips 8 T → BL dominance at window [1.5, 4] T).
- **"The landau fan step" is run 4** — 2D electron fan (D=0, n=1.0–4.5e12 ×41,
  B=0.4–4.0 T ×451 at 8 mT). This is where the band-hiding harm lives. Data is
  committed in the session-3 archive at `82883a9`.

### Layer-A precursor (cheap, no agent)

Numerical FFT A/B, old vs new `sdh_fft`, on run 3 (spot-check) and run 4 (fan).
Expected, if the fix works:

- **Run 3:** near-F_L (BL ~48 T) dominates the 8 T at the [1.5, 4] T window under
  B-space; the old 1/B detrend keeps 8 T dominant.
- **Run 4 (verified — more nuanced than "all fixed"):** under B-space at the
  **default `bg_degree=5`** the BL/F_L diagonal ridge (~0.89·F_L) resolves
  cleanly — reaching what the old 1/B detrend only got with the **order-7 +
  `<6 T` band-hiding workaround**. So the "bad fan" was largely a
  *tooling-workaround* artifact, and the fix makes the usable fan read the
  default. **But:** the **ML ridge (~0.11·F_L, ~1–5 T) does not cleanly resolve
  in the fan under any method** — it is intrinsically congested in the low-F
  band at the fan's [1,4 T] window/resolution, so the ML partner reads off the
  spot checks (by design), not the fan. And **F_L (ABC) vs 0.89·F_L (BL) are
  ~11 % apart — borderline at the fan's frequency resolution**, which is the
  crux of the mixed call. Grade the fix on *removing the workaround*, not on the
  fan resolving ML or splitting F_L/0.89·F_L — those are intrinsic limits, not
  tooling bugs.

![[attachments/qc0426-run4-fan-fft-ab.png]]
*Run-4 fan FFT A/B (sr1, per-n normalized, window [1,4] T). Left → right: old
detrend=3 (residual smear), old detrend=7 (the workaround), new B-space bg=5.
B-space at default reaches the workaround's diagonal; the ML band (green,
~0.11·F_L) stays congested in all three.*

This is the *necessary condition*: if perception doesn't change, the next move
can't. It also supplies the evidence behind the fixture's `ground_truth/reading.md`.

### Layer-B replay (the real test)

`hera-replay` (`src/hera/replay.py`) freezes the session at a **frontier**
(decision point X), builds a leakage-safe workdir, and asks a HERA-shaped agent
for its next move. Run it from **worktree@A** and **worktree@B**, diff the
next-move proposals.

- **Decision point X**: cut **after the SdH spot-checks, before the fan** (does
  HERA propose the right fan / read two-vs-three tones?), or **after the fan,
  before the stacking call**. The first is the cleaner "did the tooling change
  the move" test.
- **Judge**: HERA@A's move vs HERA@B's move against the corrected read (three
  tones → mixed), not HERA-vs-human.

## The gap (what the collaborator must build)

1. **A session-3 frontier fixture** under `hera/test-cases/` per the authoring
   spec (`test-cases/README.md`): crop the measure notebook at X, allowlist the
   pre-cut `data/` dirs, set `leak_terms`, write `ground_truth/{reading,next_move}.md`.
   This is the bulk of the work. (Reference fixture:
   `2026-05-06-b1c2-sc-characterization/`.)
2. **Pick X** and justify it (the decision where the tooling bug actually bit).
3. **A/B run-mode**: confirm the replayed agent imports `hera.analysis` from the
   *worktree it runs in* (not a globally-installed `hera`), or the A/B is fake.
   Likely a `PYTHONPATH` / editable-install detail per worktree — pin it.
4. **Judge the A-vs-B pair** (`hera-judge` / pairwise), axis = HERA@A vs HERA@B
   against the correct read.
5. **Ground truth** for session-3: correct read (ML+BL+F_L resolved → mixed) +
   the correct next move. The session's own take + the corrected tooling give it.

## Success criteria (how to grade)

- **Layer A passes** if the run-3 and run-4 FFT A/B show the expected
  perception change (above) — quantified, not eyeballed.
- **Layer B passes** if, at frontier X, HERA@B's next move is judged at least as
  good as HERA@A's *and* the improvement traces to the corrected read (not luck /
  prompt noise). Equivalent-or-better with a clear perception reason = the fix
  helped.
- **The honest null result** is also a pass for the *evaluation*: if A and B
  produce the same next move, the fix didn't change HERA's decision at X — say
  so, and that's a real finding about whether the bug actually drove behavior.

## Pointers

- Commits: A = `82883a9` (`archive QC0426 .3 session`), B = `e5654b5`
  (`deprecate trilayer-stacking-id`) / current `hera`. SdH port = `1a30b30`.
- Runs (session-3 archive `hera/docs/notes/2026-06-19-QC0426-session-3/data/`):
  3 = electron spot-check, 4 = electron fan, 2 = hole spot-check.
- In-session analysis scratch: `…/hera_scratch/ana_cell_fan_fft2.py` (the
  detrend-7 + band-hiding fan FFT), `ana_take_step3.md` (the deferred call).
- Harness: `src/hera/replay.py`, `hera/docs/benchmark-plan.md`,
  `hera/test-cases/README.md`.
- Live investigation for the call logic: `trilayer-stacking-fs-count.md`
  (FS-counting; ABC singleton at F_L, ABA pair summing to F_L, mixed = both).
