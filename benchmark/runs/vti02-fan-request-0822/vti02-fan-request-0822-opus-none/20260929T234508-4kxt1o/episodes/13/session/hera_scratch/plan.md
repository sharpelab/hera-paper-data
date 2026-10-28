# vti-02 — stacking-order campaign plan

*Goal: region-resolved ABAB / ABCA / ABCB call (or calibrated "cannot tell") on
vti-02 tetralayer graphene. Reconstructed and carried forward at the 2026-08-23
handoff (the pre-handoff instance left no `plan.md` — see session_notes
PROTOCOL).*

## Discriminator logic — what actually decides the call

At fixed density, the Fermi-surface content and the Landau-level degeneracy
sequence differ by stacking:

| | ABAB (Bernal ×2) | ABCA (rhombohedral, χ=4) | ABCB (mixed) |
|---|---|---|---|
| bands at D=0 | two bilayer-like subbands → **two** SdH frequencies, F₁+F₂ = nh/4e | one quartic band → **one** frequency = nh/4e | hybrid (bilayer-like + dimer-like) → two, with a different ratio |
| LL fan | two interpenetrating ray families, different slopes, **crossings** | single 4-spaced family | two families, asymmetric |
| zero-LL at CNP | 8+8 (two χ=2 manifolds, energy-offset) | 16-fold single manifold | mixed |
| CNP vs D | gap opens, moderate | gap opens strongly | intermediate |

The **fan is the discriminator**: ray *slopes* give ν directly (n = νeB/h),
independent of the geometry-prior density scale, and the number of ray families
plus the CNP step separates the candidates.

## Steps

1. **DONE — gate C liveness** (runs 0–3, `gate-current-sanity-check`). Alive on
   the provided contacts, no leakage, Rxx 60–330 Ω. Surfaced **two CNPs in
   series** between B_1 and B_2 → two regions (A, B) of different intrinsic
   doping. Carried forward as a series-mosaic confound *and* as a second,
   independent region to call.
2. **DONE — 0 T gatemap → (n, D) calibration** (run 5, `cnp-and-dline-calibration`;
   run 4 railed, aborted). Ridge A and a parallel ridge B (0.19 V lower in V_tg).
   c_bg/c_tg = 0.773 (data), c_tg = 2.796 mF/m² (9.5 nm **geometry prior — absolute
   n scale still uncalibrated**), n_offset −0.089e12, D_offset −0.013 V/nm.
   Region B is electron-doped by 0.43e12 vs A. D = 0 window inside the
   validators: n = −1.28 … +3.26e12.
3. **DONE — SdH spot checks** (runs 6, 7, `sdh-spot-check`). Strong oscillations
   both signs; onset ≲ 0.7 T; minima reach ~0 Ω. Electron side (run 6) shows a
   ladder 7.8 / 14.4 / 22.2 / 30.0 T whose minima spacing is Δ(1/B) ≈ 0.033 → a
   single ~30 T periodicity with a 4-grouped amplitude modulation. **Ambiguous at
   fixed n**: harmonics of one frequency, a two-band pair, and a
   degeneracy-resolved single band all fit. This is exactly what the fan breaks.
4. **NOW — Landau fan at D = 0** (`landau-fan`, step 4). B 0 → 10 T slow × n
   −1.28 → +3.26e12 fast along the calibrated D = 0 line. Establishes:
   - ν assignment from ray slopes → **absolute density calibration**, independent
     of the 9.5 nm prior (fixes the c_tg scale);
   - the degeneracy sequence (Δν = 1 / 2 / 4 / 8) on each side;
   - the number of ray families and whether they cross (ABAB) or not (ABCA);
   - the CNP step (4χ) for region A **and** region B — the two CNPs sit at
     n = 0 and n ≈ −0.43e12 on the same fast axis, so one fan reads both regions.
   - **What would change my mind:** a single 4-spaced family with a 16-step at
     CNP → ABCA; two families with crossings and two zero-LL manifolds → ABAB;
     an asymmetric pair → ABCB. No resolvable rays by 5 T → the read is
     resolution/T_e-limited, and the call degrades to "cannot tell".
5. **NEXT (planned) — CNP vs B ride-down.** The fan ends at 10 T; the magnet must
   return to 0 T anyway. Ride it down as a 1D cut parked at the CNP (and a second
   at the region-B CNP if the fan says they are separable) at high sr1
   sensitivity, to read the ν = 0 insulating state's onset field — the direct
   zero-LL-degeneracy probe. Cost: ~35 min over the bare ramp the session needs.
6. **CONDITIONAL — fan or cuts at finite D.** Only if step 4 leaves the families
   ambiguous: ABCA's gap is strongly D-tunable, ABAB's much less. Run 5 already
   has R_CNP(D) at B = 0 (240 Ω → 2.4 kΩ by D ≈ +0.25 V/nm), so this is a
   fan-at-finite-D question, priced at another ~5 h — a **detour**, flagged
   before it lands.
7. **Close-out** — `return-to-initial` per the brief, then the call as the final
   ana cell.

## Standing constraints

- Banned: probing/extending gate operating limits; standalone Si-gate survey.
- Consent-gated: any `ratio ≠ 0.95` in `set_both`; DC205 ramp_rate; any safety-surface edit.
- No prior-campaign data; only this session's `./data/`.
