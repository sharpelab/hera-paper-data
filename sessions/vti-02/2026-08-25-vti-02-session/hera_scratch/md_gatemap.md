## HERA — first 0 T gate map (the load-bearing measurement)

`recipe: measurements/gatemap.md`. Preceded by `gate-current-sanity-check` Cell B
(nplci reset) in the cell above.

**What Gate C established** (runs 0–3, four legs, 151/151 each, none interrupted,
T flat at 1.175 K): gates safe on both polarities, the provided hardwired
configuration fully live (sr0 and sr1 clean and resistive, sr2/sr3 at the n.c.
floor), and `sr1` never above 3% of full scale. And **two resistance ridges, not
one**, along each gate axis:

| ridge | V_tg at V_bg = 0 | V_bg at V_tg = 0 | implied c_bg/c_tg |
|---|---|---|---|
| A | −0.2152 V (322 Ω) | −0.2642 V (303 Ω) | 0.814 |
| B | +0.1121 V (242 Ω) | +0.1284 V (265 Ω) | 0.873 |

geometry prior: 0.864.

Both ridges return a ratio consistent with the prior and with each other to
within ~6–7%, which says they are **parallel** — two CNP lines, i.e. two regions
of differing intrinsic doping in series along the B_1−B_2 span, separated by
roughly 0.6×10¹² cm⁻². (My first pass at this, from raw argmax, gave 0.830 and
0.958 and I read it as *non*-parallel; smoothing plus parabolic refinement moved
ridge B from 0.958 to 0.873 and reversed the conclusion. The two-point estimate
is too sensitive to peak-picking to carry a claim — which is the argument for
this map.)

**Why that matters more than it looks.** If B_1−B_2 spans two domains at
different densities, then at any gate setting the two regions carry different n,
and each contributes its own SdH frequency. **Two tones from two doping domains
would masquerade as two Fermi surfaces** — precisely the ABAB signature the
investigation is looking for. This is a confound that has to be resolved before
any FS count means anything, and it is not the stacking-domain case the
investigation discusses (that one shares a common gated density); here the
densities themselves differ.

**What this map decides**, and why it is worth 1.6 h of zero-field time before
any magnet time:

1. **Both ridges' slopes, properly fitted** — per-row argmax with continuity
   enforcement, robust line fit, residuals reported (`cnp-and-dline-calibration`
   Step 1–2). Parallel to within residuals ⇒ two doping domains. Non-parallel ⇒
   band structure, and one of the two is not a CNP. A ridge at *constant V_bg*
   (infinite slope) would instead mean a region the top gate does not cover.
2. **The data-calibrated c_bg/c_tg**, replacing the geometry prior — ratio
   data-grade, absolute scale still prior-grade until a quantum-Hall lever arm
   lands (Step 5 upgrade path).
3. **Each ridge's resistance at D = 0.** The Gate C peak heights are all at
   finite D — ridge A sits at ~2× ridge B's |D| and reads higher, and both read
   higher at D < 0 than D > 0, so the height difference may be pure |D| effect.
   A tetralayer CNP that is semimetallic rather than insulating is weak evidence
   about stacking, but only if read at D ≈ 0, and only as consistent-with
   (survey §5: three candidate parents for an insulating CNP).

**Grid and the coverage trade.** V_tg fast, [−0.3, +1.0] × 101 (13 mV);
V_bg slow, [−1.3, +1.3] × 37 (72 mV); 3737 points. The full committed TG window
is used because the ridges sweep across all of it (ridge A reaches V_tg ≈ +1.03
at V_bg = −1.3) and because the D = 0 line needs V_tg = 1.0 to reach n ≈
+3.3×10¹² cm⁻², where the ABAB and ABCA templates separate. **Excluded:
V_bg ∈ (1.3, 2.0]** — Gate C run 2 shows R falling smoothly there with no new
ridge, and it is high-D electron side, off the D ≈ 0 operating point. Adding it
back is ~10 rows ≈ 25 min if the map argues for it.

**Top-gate leakage, stated on the page.** Gate C run 0 shows I_tg flat at −97 pA
to V_tg ≈ 0.62 V, then a sharp turn-on reaching −10 pA at +1.0 V: **+88 pA of
voltage-dependent gate current with an onset at 0.62 V**, TG-positive only. Below
the recipe's 1 nA abort and just under its 100 pA surface-it line. I am running
to the committed +1.0 V because capping at 0.6 V would drop the reachable
electron density from 3.3 to 1.9×10¹² — below where the templates separate, i.e.
it would cost the campaign its answer. The operating limit is the operator's;
Zack has been pinged with the number and can cap it. `hera-watch` warns at ≥100 pA
excess sustained, and the fast axis crosses the onset every row so any growth
shows immediately.

**Pricing, from measured overhead.** Gate C ran 1.79 s/pt at `nplci = 10`
(33.5 rows/min, calibrating run 0). Dropping the gate-current NPLC to 1 removes
~0.30 s/pt → ~1.49 s/pt: 3737 pts ≈ 1.55 h, plus 37 row-flybacks
(1.3 V / 5 mV × 6 ms + 1 s slow_delay ≈ 2.6 s) ≈ 1.6 min. **ETA 1h45m** with the
5–10% over-run margin this rig's session evidence warrants.

**Checkpoints.** First rows — leakage, railing, dead channel, and a re-price of
s/pt against the 1.49 estimate; then periodically as rows land, with the CNP
ridge trackable from the first few rows onward.
