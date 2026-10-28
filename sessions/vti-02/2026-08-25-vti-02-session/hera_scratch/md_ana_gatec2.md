**Read.**

*Gates.* Safe on both polarities of both gates. BG is flat at its +25 pA readback
offset everywhere, on both legs, and shows no cross-gate tracking. **TG is not
flat**: run 0 holds −97 pA out to V_tg ≈ 0.62 V, then turns up sharply and
reaches −10 pA at +1.0 V — **+88 pA of voltage-dependent gate current with a
distinct onset**, which capacitive charging does not do. It appears only on
TG-positive (run 1, TG-negative, is flat at −100 pA). It sits below the recipe's
1 nA abort and just under its 100 pA surface-it line, so this is a flag, not a
stop; `gate-leakage-survey` is blocklisted this session, so it is recorded rather
than characterised. Consequence for design: the committed +1.0 V is used anyway,
because capping at 0.6 V would drop the reachable D = 0 electron density from
≈3.3 to ≈1.9×10¹² cm⁻² — below where the ABAB and ABCA templates separate.

*Contacts.* The provided hardwired configuration is fully live: sr0 (drain
current on B_3) tracks at 49.2 nA with 0.7% spread across every leg, sr1
(B_1−B_2) gives a clean resistive four-terminal signal at θ ≈ −3°, and sr2/sr3
sit at the n.c. pickup floor. No dead provided contact — nothing to hand back
for rewiring.

*The science.* **Two resistance ridges along each gate axis, not one**, with a
shallow minimum between them near the origin:

| ridge | V_tg at V_bg = 0 | V_bg at V_tg = 0 | implied c_bg/c_tg |
|---|---|---|---|
| A | −0.2152 V (322 Ω) | −0.2642 V (303 Ω) | **0.814** |
| B | +0.1121 V (242 Ω) | +0.1284 V (265 Ω) | **0.873** |
| geometry prior | | | 0.864 |

Both ridges return a lever-arm ratio consistent with the geometry prior and with
each other to ~6–7%, i.e. **the two ridges are parallel** — two CNP lines rather
than one CNP plus a band feature. The leading interpretation is **two regions of
differing intrinsic doping in series along the B_1−B_2 span**, offset by roughly
0.6×10¹² cm⁻².

Method note, because it changed the answer: raw per-point argmax gave 0.830 and
0.958 for the two ridges and I read that as *non*-parallel. Gaussian smoothing
plus parabolic refinement of the peak moved ridge B from 0.958 to 0.873 and
reversed the conclusion. On peaks this broad and this close to the origin, the
ratio is far too sensitive to peak-picking for a two-point estimate to carry a
claim — which is the argument for the gate map, where the slope is fitted across
many rows with residuals.

*Why this is a problem and not a result.* If B_1−B_2 spans two domains at
different densities, then at any gate setting each region carries its own n and
contributes its own SdH frequency. **Two tones arising from two doping domains
would masquerade as the two Fermi surfaces that are exactly the ABAB signature
this campaign is trying to detect.** This is a distinct confound from the mixed
*stacking* domains the investigation discusses — those share a common gated
density and check against a common F_L; these do not. It has to be resolved
before any FS count is meaningful.

*D-dependence, noted not concluded.* All four peak heights are at finite D. Ridge
A sits at ~2× ridge B's |D| and reads higher (322/303 Ω vs 242/265 Ω), and both
ridges read higher at D < 0 than at D > 0. So the height difference between
ridges may be entirely a |D| effect rather than intrinsic. Each ridge's
resistance *at D = 0* — the number that bears on stacking, and then only as
consistent-with — comes from the gate map.

**Next:** the 0 T gate map over the full committed TG window × V_bg ∈ [−1.3, +1.3],
to fit both ridge slopes with residuals, produce the data-calibrated c_bg/c_tg,
and read each ridge at D = 0.
