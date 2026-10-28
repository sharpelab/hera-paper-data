# vti-02 — fused stacking verdict (Raman × transport)

Offline fusion, 2026-08-27. Analysis only — no rig, nothing re-measured.

**Headline.** The fused verdict for the one wired channel is **ABCA (rhombohedral),
moderate** — numerically and evidentially unchanged from the transport call alone.
The two legs are *nominally* concordant, but the concordance carries almost no
information: the Raman leg attaches to the parent flake before stacking, cannot be
registered to the measured span, and reports at a granularity (ABC vs ABA) that is
blind to the one alternative the transport call is actually uncertain about (ABCB).
It corroborates the part transport had nailed down (not Bernal) and is silent on the
part transport left open. **The concordance is therefore not grounds to promote the
call to `strong`, and I have not promoted it.**

---

## 1. Per-channel table

| transport channel | transport verdict + strength | Raman verdict + strength + build stage it attaches to | **fused verdict + strength** | stated basis for the fused row |
|---|---|---|---|---|
| **sr1 = B_1 – B_2** (Rxx; the only four-terminal pair wired this cooldown) | **ABCA — rhombohedral**; **moderate**. Four evidence lines on the measured span: R_CNP rises 10.4× (296 → 3074 Ω) to D/ε₀ = +0.307 V/nm; gap minimum at D = 0.000 ± 0.008 V/nm (base-T R_CNP) and +0.016 ± 0.004 V/nm (activation); D-driven metal→insulator crossover at neutrality (Δ = −0.62 ± 0.17 meV at D ≈ 0 → +1.36 ± 0.14 meV at +0.238 V/nm, dR/dT sign change at +0.126 V/nm); exactly one SdH tone, f ∝ n (f/f_full = 0.835, 0.834 on the two highest-contrast traces). ABAB excluded twice over; ABCB disfavoured but not excluded. | **Rhombohedral / "ABC"**; document self-declares **strong** — **assessed here as weak**. Attaches to **build stage: parent flake, pre-stacking** — and even that stage attribution is internally inconsistent (§3, H2). The leg is a *narrative assertion with no retained evidence*: 0 quantities with units, 0 stated uncertainties, no acquisition date, no instrument/wavelength/spot size, no positions, no domain outline or area fraction, no layer count, and the flakemap/spectra are "not yet in hand — pending from Ben". No Raman exists at any post-stacking stage. | **ABCA — rhombohedral; moderate** | The fused strength is **inherited from the transport leg and not raised by the concordance**. Fusion changes the call only if the second leg adds independent discrimination on the live alternatives; here it adds none. (a) The Raman leg's discriminating content is ABC-family vs ABA-family — exactly the axis transport already closes hardest (two independent disqualifications of ABAB). (b) It never names ABCB and cannot distinguish it from ABCA, so it leaves the transport call's dominant residual untouched — see `artifacts/fig3-odds.png`: the fused ABCA:ABCB odds equal the transport-only odds **for every** assumed survival probability. (c) It describes a pre-stack parent flake that cannot be placed on the same coordinate frame as the B_1–B_2 span (§2). Its net effect is a weak prior nudge away from ABAB, on a hypothesis transport had already driven to ~0.3 % posterior. |
| T_1, T_2, T_3, T_4 | *not measured* — dead contacts, not wired to instruments; not a transport channel this cooldown | no region-resolved Raman exists at any stage, so the leg says nothing about these regions either | **no fused verdict possible** | Neither leg carries region-resolved information here. Both are silent for the same reason (no spatial resolution on either side), so this is an absence of data, not a disagreement. |

Supporting: `artifacts/fig1-discrimination-matrix.png` — which evidence line separates
which hypothesis, per leg. Every Raman row is flat across the ABCA and ABCB columns.

### 1a. A second fused statement the per-channel table does not capture

The table's row answers *"what is the stacking order of the dominant conducting region
between B_1 and B_2?"* There is a second question the fusion raises and neither leg
answers, and it would be dishonest to fold it into the row:

> **Is the B_1–B_2 span phase-pure? Fused verdict: unresolved — both legs empty.**

Three transport observables are individually explained by, and jointly suggestive of,
a residual non-rhombohedral or differently-doped patch conducting in parallel inside
the measured span:

- **R_CNP saturates near 3 kΩ** above D/ε₀ ≈ 0.23 V/nm instead of continuing up. The ana
  notebook reads this as "disorder- and parallel-channel-limited" — a *parallel channel*
  is one of the two named candidates, and 3 kΩ is then an upper bound on the shunt.
- **Δ_max = 1.36 meV is 10–100× below a clean rhombohedral gap** at that field. Ordinary
  for gapped multilayers, but also exactly what a shunt does.
- **7 of 35 map rows (20 %) show a double-peaked neutrality region**, all at low |D|,
  reproducing the same structure seen in run 1 (peaks 297 Ω and ≈272 Ω, 35 % dip
  between, an order of magnitude above the ~3 % noise floor). The notebook's own
  reading: "two areas of slightly different doping between the B_1–B_2 probes."

A Bernal patch in parallel would produce all three. So would ordinary charge disorder,
and the single SdH tone argues against a *comparable-area* second Bernal region (it would
contribute its own density-scaling tones). This is the one place a Raman map would have
been decisive — and it is precisely what the Raman leg cannot supply. The Raman
document's relevant sentence, *"we expect the cut region to contain no ABA"*, is an
**expectation, not an observation**, and I have scored it as carrying no information.

---

## 2. Spatial / temporal correspondence

`artifacts/fig2-stage-timeline.png` renders both panels below.

### Spatial: **no — the two legs cannot be placed on one coordinate frame.** Not partially; not at all.

- The Raman leg lives in parent-flake scan-inspector coordinates (flake 84135). It gives
  **no domain outline, no domain area or coverage fraction, no cut outline, and no
  positions of any kind**.
- The transport leg lives in bond-pad labels (B_1 = pad 12, B_2 = pad 04). It gives **no
  probe separation and no channel width** — the device card carries no Hall-bar geometry,
  which is why every resistance in the call is in ohms and not ohms per square.
- The brief supplies **no frame bridges**: no optical image, no GDS, no build-step list.
  The parent-flake URL in `raman.md` is explicitly not an input and was not fetched.

**What that costs the fusion, bounded.** The strongest statement the Raman leg can
support after registration failure is *flake-level*: "the parent flake contained a
rhombohedral domain, and the fab intent was to cut the device out of it." It cannot
support the *span-level* statement fusion actually needs — "the region between B_1 and
B_2 lies inside that domain, with no domain wall crossing it." Concretely, three
questions stay open that a single registered image would close: (i) does the B_1–B_2
span sit inside the cut domain at all; (ii) does a domain boundary cross it (§1a); (iii)
is the double-peaked neutrality a doping inhomogeneity or a stacking boundary. The only
purely electrical constraint available is indirect and does not locate anything: 297 Ω
at neutrality is ~1/20 of a graphene minimum-conductivity square, so the probes almost
certainly span well under one square — an aspect-ratio inference, not a position.

Note also that **"region-resolved" is one region on both legs**, for different reasons.
Transport has one wired pair (T_1–T_4 dead, sr2/sr3 n.c.; rewiring is operator work at
the breakout). Raman has no map in hand. So the fusion has no spatial degrees of freedom
to compare — there is exactly one cell in the region × modality grid with data in it.

### Temporal: **ordering yes, interval no, bracketing no — and the stage attribution is itself contradictory.**

- **Transport** is fully timestamped: session 2026-08-24 11:36 → 16:53 rig-local (PDT),
  E1 grant 12:08:29, thermal close-out readback 16:51:53, corpus commit `039b0f5`, seven
  runs on disk and re-analysable.
- **Raman** has **no acquisition date at all** and no instrument record. Its stage is
  stated as "pre-stacking, on parent flake", so the *ordering* is known — the read
  precedes stacking, anneal, cut, litho and the cooldown.
- **The interval is unknown**, so nothing bounds how much handling, storage or ageing
  separates the two legs.
- **No conversion-risk step is bracketed.** `raman.md` itself names stacking, anneal,
  cut and litho as ABC→ABA conversion risks, and confirms there is no Raman at any later
  stage (no exposed device layer after gating). There is therefore no "after" read
  anywhere: the entire causal chain between the Raman evidence and the measured device
  is unobserved, in a material whose rhombohedral order is known to be metastable
  against exactly these steps.
- **The stated stage is internally inconsistent.** The header places the read
  pre-stacking on the parent flake and says no further Raman was performed; but the
  document also asserts "the rhombohedral domain survived the cutting process" and that
  "some spectra look like noise due to the laser cutting." A read that predates the cut
  cannot witness survival of the cut, and cannot contain laser-cutting damage. Either
  some spectra postdate the cut (contradicting the header) or "survived" is an inference
  (in which case one of the leg's two positive claims is not evidence). **Unresolvable
  from the supplied inputs**, and it is why the leg's stage attribution is scored
  unreliable rather than merely early.

**What that costs the fusion, bounded.** Temporal non-correspondence converts the Raman
leg from evidence about the device into a *pre-fab prior about the starting material*,
mediated entirely by an unmeasured survival probability `s`. The odds model
(`analysis/fuse_vti02.py`, part C) makes the consequence explicit: `s` moves the fused
ABAB posterior around, but the fused ABCA:ABCB odds are **exactly invariant to `s`** —
6.0 for every value in 0.05 ≤ s ≤ 0.95 — because the leg's claim is flat across those
two hypotheses. No assumption about conversion survival, optimistic or pessimistic,
rescues the Raman leg's relevance to the live question.

---

## 3. Named hedges

**On the fused verdict as a whole**

- **H1 — Concordance here is nearly uninformative, and could be mistaken for
  confirmation.** Both legs say "rhombohedral", but they do not constrain the same
  proposition: the Raman leg discriminates ABC-family from ABA-family on a pre-stack
  parent flake, transport discriminates ABCA from ABCB and ABAB on the measured span.
  Agreement on the axis where one leg is already decisive is not independent support.
  This is the single biggest risk of over-reading this document.
- **H2 — The Raman leg's build stage is contradictory** (pre-stack header vs
  laser-cutting damage in the spectra and a survived-the-cut claim). Whichever
  resolution is right, one of the leg's two positive claims loses its footing.
- **H3 — The Raman leg retains no assessable evidence.** No spectra, no map, no
  positions, no instrument, no date, no uncertainties, no ABC coverage fraction, and an
  acknowledged but unquantified fraction of spectra degraded by the laser cutting. Its
  self-declared `strong` cannot be checked, reproduced, or re-read by anyone; I have
  scored the leg `weak` on that basis, which is a judgement about *what was supplied*,
  not about the fabricator's work.
- **H4 — Vocabulary mismatch.** `raman.md` frames the question as ABC vs ABA — trilayer
  vocabulary, and a binary that does not contain ABCB. The transport call's live
  alternative is a *tetralayer mixed* stack. Even with the raw spectra in hand, resolving
  ABCA from ABCB by 2D-band lineshape in a four-layer stack is a much finer measurement
  than resolving rhombohedral from Bernal, and may not be achievable at all; I am not
  assuming it would be.
- **H5 — Neither leg establishes the layer count.** `raman.md` never states it. Transport
  cannot: the SdH frequency and the Landau ladder both depend only on the product α·g
  (4.78 and 4.67 by two routes), so with no Hall pair wired the absolute density scale
  and the degeneracy are inseparable, and the zero-LL degeneracy counts layers, not
  stacking, in any case. N = 4 rests on the device card and fab record alone. Both legs'
  polytype vocabulary presumes it.

**Inherited from the transport leg (carried, not re-litigated — the underlying analysis
holds up on re-derivation)**

- **H6 — The −D lever arm is 0.26 of +D** (D covered −0.0798 … +0.3068 V/nm), because the
  provided top-gate limit stops at −0.3 V. Inversion symmetry is demonstrated over
  |D| ≤ 0.10 V/nm, not the full range; an ABCB asymmetry developing beyond that is
  invisible. This remains the dominant limitation on the fused row, and the Raman leg
  does nothing to relieve it.
- **H7 — The two gap-minimum locators differ by +0.016 V/nm.** Against the activation
  fit's own bootstrap error alone that is 4.0σ; against the two errors combined it is
  **1.8σ**, i.e. consistent, and the offset is 4.1 % of the accessible D range. I agree
  with the transport call's reading (different observables, fit-noise-only errors), but
  weak inversion-symmetry breaking is not excluded.
- **H8 — The gap's size is not established, only its existence and D-dependence.**
  Δ_max = 1.36 meV with R_CNP flooring near 3 kΩ; see §1a for why this is also a fusion
  hedge and not only a transport one.
- **H9 — A small satellite Fermi pocket is not excluded.** A second pocket carrying under
  ~10 % of the carriers would sit below ~1.5 T and be removed by the degree-5 background
  subtraction. What is excluded is two *comparable* pockets. The hole side reaches only
  n = −0.81 × 10¹² cm⁻², so the pocket count is really established on the electron side.
- **H10 — No absolute density calibration and no Hall-bar geometry**, so every resistance
  is in ohms rather than ohms per square and no mobility or sheet-resistance claim
  exists. Electron temperature ~8 K restricts activation fits to T ≥ 8 K and puts
  correlated states out of reach.

**On this document**

- **H11 — The odds model in `artifacts/fig3-odds.png` is an explicit-judgement device,
  not a measurement.** Its likelihood ratios (ABCB:ABCA = 1:6, ABAB:ABCA = 1:300) are my
  stated reading of the transport evidence, written down so a reader can move them. They
  are swept: over ABCB:ABCA from 1:15 to 1:3 the fused ABCA posterior runs 0.94 → 0.74 —
  which is what "moderate, not strong" means, and none of the sweep changes the
  qualitative conclusion. The one result that is *structural* rather than judged is the
  invariance of the ABCA:ABCB odds to the Raman leg.

---

## 4. What would settle it

For the rows and questions the two modalities leave unresolved or in tension.

**(A) ABCA vs ABCB — the live residual on the fused row (H6, H7).** *Transport side, and
decisive:* extend the top-gate range past −0.3 V to lengthen the −D lever arm toward
symmetry with +D, and re-locate the gap minimum from both R_CNP(D) and Δ(D). A minimum
genuinely displaced from zero → ABCB; a minimum still at zero over a symmetric range →
ABCA at `strong`. This requires a revised gate operating limit (the current one is a
provided limit, not a hardware fence) plus a leakage check on the way out; it is a
consent/limits question, not an analysis one. *Raman side:* obtain the flakemap and
spectra files from Ben and fit the 2D-band lineshape properly — but see H4: this may not
resolve ABCA from ABCB even in principle, so it should not be relied on as the route.

**(B) Whether the Raman leg is admissible evidence at all (H2, H3).** Three questions to
Ben, all cheap: (i) the acquisition date; (ii) the spectrometer, wavelength and spot
size; (iii) which stage each spectrum was taken at — specifically, were any spectra
acquired at or after the laser cut? Plus the flakemap and raw spectra themselves. Until
(iii) is answered the leg's own stage attribution contradicts itself and no strength
above `weak` is defensible.

**(C) Registration — the frame bridge (§2).** One optical image of the finished device
with bond-pad labels, overlaid on (or co-registered with) the parent-flake image and the
cut outline; plus the GDS and the build-step list. This is the minimum that would let
anyone ask whether the B_1–B_2 span lies inside the rhombohedral domain. Without it, no
amount of extra Raman on the parent flake can be attached to the measured channel.

**(D) Phase purity inside the span (§1a).** Three independent probes, in cost order:
(i) a **Hall pair** — rewire sr2 or sr3 at the breakout — giving n = B/(e·R_xy), which
separates α from g and lets the SdH-implied and Hall-implied densities be compared; a
parallel patch shows up as a discrepancy between them. (ii) A **low-field, fine-1/B**
record below ~1.5 T with a gentler background removal, to look for the small satellite
tone H9 leaves open. (iii) A **Raman map with positions**, which is the only direct test
and is unavailable on this device at any stage after gating.

**(E) Region resolution beyond one region.** Both legs are single-region. On the
transport side the fix is operator work at the breakout: B_3 is alive, so wiring B_1–B_3
or B_2–B_3 as a second four-terminal pair would give a genuinely independent span to
compare against, and a disagreement between two spans would be direct evidence of
multi-domain structure. T_1–T_4 are dead and would need rebonding. On the Raman side
there is no route on this device.

**(F) The layer count (H5).** If a Hall pair lands, the absolute density scale follows,
and the width of the ν = 0 insulating wedge in absolute filling factor counts 4N — which
would confirm N = 4 directly rather than inheriting it from the device card. Independent
of transport: AFM step height or the parent-flake Raman layer count, if the raw data
arrive under (B).

---

## Artifacts

| path | what it is |
|---|---|
| `analysis/fuse_vti02.py` | regenerates everything below; parses the ana notebook's printed outputs, never executes it. Part A = transport consistency re-derivations, part B = per-leg evidence inventory, part C = the explicit-judgement odds model + sensitivity sweeps. |
| `artifacts/fig1-discrimination-matrix.png` | which evidence line separates which hypothesis (ABCA / ABCB / ABAB / ABCA + residual patch), per leg |
| `artifacts/fig2-stage-timeline.png` | build-stage timeline with the unbracketed conversion-risk window and the stage contradiction; coordinate-frame panel showing the registration gap |
| `artifacts/fig3-odds.png` | posteriors at each fusion step, and the invariance of the ABCA:ABCB odds to the Raman leg |
| `artifacts/fusion-intermediates.json` | every number in this document in machine-readable form |

Re-run with `python3 analysis/fuse_vti02.py` from the fusion root.

Selected re-derived checks (from `artifacts/fusion-intermediates.json`): accessible D
span 0.3866 V/nm; −D lever arm 0.2601; gap-minimum offset 4.14 % of the span, 1.79σ
joint / 4.00σ activation-only; largest fold-ratio deviation 0.07, i.e. 1.65 combined
noise floors; the two α routes agree to 2.83 %; measured c_tg/c_bg sits 2.46σ above the
geometry prior; double-peaked rows 20 % of the map.

---

## Provenance

Fusion performed offline on 2026-08-27 by a fresh Claude instance with no prior context
on this device. **What I received, and nothing else:** the five files under
`inputs/` — `transport-call.md`, `raman.md`, `20260824_ana.ipynb` (parsed cell-by-cell
with `json`; never executed), `session_notes.md`, `device_card.md`. All five listed
inputs were present; none had to be reconstructed. **I saw no prior fusion attempt,
draft or verdict for vti-02, and no human's read, lean or reaction to either modality's
call.** I did not read `~/sharpelab/measurement-env` or any other repository or notes
directory, did not fetch the parent-flake scan-inspector URL in `raman.md` or any other
web resource, and used no email, chat or wiki. No forbidden material reached me. The
only non-input material consulted was the local `dataviz` skill's palette reference, for
figure colours. The transport leg's verdict wording and the Raman document's verdict
wording were both treated as inputs to be assessed, not conclusions to inherit.
