# vti-02 — stacking-order plan (`ABAB` / `ABCA` / `ABCB`)

*Reconstructed at the handoff (2026-08-23) from the notebooks, `session_notes.md`
and `data/0–7`; the pre-handoff instance left no `plan.md` (see PROTOCOL note in
session notes). Steps 0–3 are done; step 4 is the current move.*

## The discriminators, and what measures each

Tetralayer at D = 0, in decreasing order of decisiveness on this rig:

| # | Observable | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed) |
|---|---|---|---|---|
| D1 | **Number + partition of Fermi surfaces vs n** (SdH tones) | **two** bilayer-like bands, m\* ≈ 0.028 / 0.061 mₑ → two tones, ΣF = n·h/4e | **one** FS carrying the full density → single tone F = n·h/4e | two tones, but a *different* partition ratio (monolayer-like + trilayer-rhombo-like) |
| D2 | **Zero-LL manifold width at the CNP** (ν of the first flanking gap) | band-overlap semimetal: coexisting e+h pockets near CNP, crossing fan lines | clean 4N-fold zero LL, single-carrier fan on each side | asymmetric / intermediate |
| D3 | **R_CNP(D)** at B = 0 | weakly D-tunable, stays metallic | strongly gapped by D | intermediate |
| D4 | effective masses (LK vs T) | 0.028 / 0.061 mₑ | ≈ 0.074 mₑ at n = 3.2e12 | mixed |

D1 + D2 are the call; D3 is context; D4 is the confirmatory follow-up.

## Steps

- **Step 0 — gate C liveness** (runs 0–3, `gate-current-sanity-check`). **Done.**
  Alive, no leakage. Surfaced the confound that shapes everything downstream:
  **two CNPs in series** between B_1 and B_2 → two regions of different intrinsic
  doping.
- **Step 1 — 0 T gatemap** (run 5, `gatemap`; run 4 aborted, railed). **Done.**
  Two *parallel* CNP ridges → series mosaic, same lever arms, Δn = 0.426e12.
- **Step 2 — (n, D) calibration** (`cnp-and-dline-calibration`, from run 5). **Done.**
  c_bg/c_tg = 0.773 (data), c_tg = 9.5 nm hBN prior, n_offset −0.0894e12,
  D_offset −0.013 (from the R_CNP(D) symmetry vertex). **Absolute scale is still
  the geometry prior** — the lever-arm check is owed, and step 4 pays it.
  D3 read: R_CNP 240 Ω at D≈0 → ~2.4 kΩ at D = +0.25 V/nm, saturating. D-tunable
  but not h/e²-scale: *suggestive, not a call*.
- **Step 3 — SdH spot checks** (runs 6, 7, `sdh-spot-check`). **Done.**
  Signal is strong and the fan is viable: onsets 0.30 T (n = +3.2e12) / 0.71 T
  (n = −1.2e12), tone SNR 20–120. But **single-density FFT cannot close D1**:
  at n = +3.2e12 the high-B window resolves only ΔF = 4.3 T while the contested
  candidates are 25.6 (ABAB-heavy) / 29.5 (4× the 7.1 T tone — a harmonic) /
  33.1 T (ABCA full density). A 7.1 T tone with harmonics to 4× is
  indistinguishable from a 7.1 + 26 T two-band pair **at one density**.
- **Step 4 — Landau fan at D = 0** (`landau-fan`). **CURRENT.** The step that
  separates them, because the confound is density-dependent:
  - a **real band**'s F is ∝ its share of n → a straight line through the origin
    in the (n, F) tone map, positive slope;
  - a **harmonic** is pinned at k × F₁ for all n (slope = k × the fundamental's);
  - an **aliased** harmonic (2F > F_Nyq) runs with *negative* slope.
  Plus D2 directly (fan-line counting at the apex), plus the owed lever-arm
  calibration (fan-line slope dn/dB = ν·e/h fixes the absolute n scale), plus
  the mosaic cross-check (two fans offset by 0.426e12 = 11.5 fast steps).
- **Step 5 — follow-up, chosen by what step 4 says.** Either an LK
  temperature ladder at a fixed n (D4, masses) if the tone count is ambiguous,
  or a D-dependence fan if the apex structure is the discriminating feature.
- **Step 6 — the call** in the ana notebook, per the brief's output contract;
  then `return-to-initial` close-out.

## Step 4 design (what is being run now)

- **Geometry.** Slow = `magnet.field` (traversed **once**, 0 → 10 T — the rig
  card's "never re-traverse"); fast = co-swept `(k_tg.volt, k_bg.volt)` along
  the D = 0 line via `multimegasweep`. Field is *held* during each fast row, so
  every fixed-n column is a clean B-record.
- **Fast axis.** n = −1.221 … +3.219e12, 121 pts, Δn = 0.037e12, **n = 0 exactly
  on-grid** (index 33). The ends are the TG-limited ends of the realized D = 0
  window; margins +17.0 / +10.9 mV inside the TG validator.
- **Slow axis, 79 rows, hybrid** — the grid is chosen for physics, not FFT
  convenience (`sdh_fft` interpolates arbitrary spacing; the binding constraint
  is local Nyquist Δ(1/B) < 1/2F_max, not uniformity):
  - 4 **apex** rows 0.25 / 0.50 / 0.75 / 1.00 T — visual low-field fan only,
    **excluded from the FFT window by construction** (they are badly
    under-Nyquist for a 30 T tone).
  - 55 **core** rows 1.2 → 5.0 T uniform in 1/B, Δ(1/B) = 0.0117 → F_Nyq 42.6 T.
  - 20 **high** rows 5.25 → 10.0 T at 0.25 T uniform in B (F_Nyq 57.8 T) — pure
    1/B spacing would put only *one* row between 9 and 10 T, gutting the
    QH-minima read where it is sharpest.
  - FFT window 1.2–10 T → **ΔF = 1.36 T**, vs 4.29 T for run 6's best window.
    That splits 25.6 / 29.5 / 33.1 at a single density; the F(n) line fit over
    121 densities does far better.
- **Resolution budget.** 4-fold LL spacing in n is 0.116e12 @1.2 T /
  0.484 @5 T / 0.967 @10 T → 3.1 / 13.0 / 25.9 fast points per LL.
- **Coverage trade (stated).** The FFT window starts at **1.2 T, above the
  measured onsets** (0.30 / 0.71 T). Extending uniform-1/B sampling down to
  0.3 T at F_Nyq = 42 T costs ~225 extra rows ≈ **+13 h** — not affordable, and
  the low-B decade is not where D1 or D2 is decided. The 4 apex rows give a
  visual (non-FFT) look at that region for ~11 min.
- **Sensitivity trade (stated).** sr1 at **200 µV = 20 kΩ FS** — 38× the largest
  R seen at 10 T (587 Ω, run 7) so a QH-gapped ν = 0 at the apex has headroom
  (run 4's lesson: size for the corner that rails, not the peak you have seen),
  while keeping 0.6 Ω quantization against the ~15 Ω low-B oscillations. If the
  apex still rails, that is itself a read and a short CNP-column re-run at 1 mV
  is cheap.
- **Price.** 121 × 1.25 s + 8.5 s = 160 s/row × 79 rows = 210 min, + the 73 min
  bare 0 → 10 T ramp folded into the blocking slow sets = **≈ 4 h 45 m**
  (bracket 4 h 45 m – 5 h 30 m; session evidence says actuals run 5–10 % over).
  Rate calibrated on run 5 (1.17 s/pt at fast_delay 1.0, nplci 1, 7 fp) + one
  magnet readback + one extra co-swept Keithley write.
- **fast_delay = 1.0 s** (3.3τ at τ = 0.3 s / 24 dB) — knowingly under the
  settling floor, same as run 5 so the timing calibration transfers. It is the
  right bend *here* specifically because the FFT runs along the **slow** axis:
  every row samples a given n at the identical point in the fast sweep, so the
  lag is common-mode in each column and the 1/B record is undistorted. The cost
  is an n-axis offset (≲ 1 step, constant across rows — slopes untouched) and
  some attenuation of n-structure at the lowest fields.

### What would change my mind

- **Abort the fan** if by B ≈ 3 T (row ~30, ≈ 1 h 40 m in) the re-formed map
  shows no n-dispersing minima *and* the column FFTs show no tone above the
  noise floor — then the read is resolution-limited at this T_e and the
  remaining 3 h buys nothing; pivot to an LK ladder or a D-cut instead.
- **Revise the calibration** if the fan-line slopes disagree with the geometry
  prior's absolute scale by more than ~10 % — the fan wins; c_tg gets re-anchored
  and every density in the session is restated.
- **Two tones with ΣF = n·h/4e, both with positive dF/dn** ⇒ D1 says ABAB or
  ABCB; the *ratio* then picks between them.
- **One tone with F = n·h/4e across the whole window** ⇒ D1 says ABCA — and
  then the 7.1 T content of run 6 must be harmonic/mosaic, which the tone map
  shows directly.
- **Neither** (tones that do not sum, or fan lines of both signs at the same n)
  ⇒ compensated e/h pockets, the ABAB semimetal signature (D2).
