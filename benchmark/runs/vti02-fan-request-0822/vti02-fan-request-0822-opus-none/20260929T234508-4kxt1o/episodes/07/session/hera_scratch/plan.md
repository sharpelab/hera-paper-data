# vti-02 — stacking-order plan (HERA, 2026-08-22/23)

Goal: region-resolved call ABAB / ABCA / ABCB (or calibrated "cannot tell") on
tetralayer vti-02, D = 0 accessible window, single hardwired pair `sr1 = B_1 - B_2`.

> Reconstructed + extended at the 2026-08-23 handoff (the file was not on disk;
> steps 0-3 are what the notebooks show was actually done). TOOLING note filed.

## What discriminates (the physics this plan buys)

At D = 0 the three candidates differ in **how the total density is partitioned over
Fermi surfaces**, and that is exactly what a Landau fan measures:

| stacking | low-energy decomposition | SdH tones at D = 0 | zero-LL degeneracy |
|---|---|---|---|
| ABCA (rhombohedral) | one chirality-4 (quartic) band | **one** tone, F = n·h/4e | 16 (4 orbital x 4 sv) |
| ABAB (Bernal) | two bilayer-like (J = 2) subbands, different masses | **two** tones, F1 + F2 = n·h/4e, ratio ~ m1/m2 | 8 + 8, two families |
| ABCB (mixed) | J = 1 + J = 3 (monolayer-like + rhombohedral-trilayer-like) | **two** tones, strongly unequal | 4 + 12 |

Two readouts of the same fan:
- **LL-line slopes** in (n, B): minima follow n = nu·eB/h. The set of nu, and whether
  the families converge on one CNP, gives degeneracy and band count.
- **F(n)** per n-column (FFT in 1/B): tone count and the sum rule Sum F_i = n·h/4e.

**The confound to separate:** run 5 found a *second CNP ridge* (region B, electron-doped
by 0.43e12 vs region A) in series along this pair. Two *regions* produce LL families with
**equal slopes, offset n-intercepts**; two *bands* produce **different slopes converging on
one CNP**. The fan separates them; a single-n spot check cannot.

## Steps

- [x] **0 — Gate C liveness** (`gate-current-sanity-check`, runs 0-3). 1D legs, B = 0.
      Pair alive, R(D=0 CNP) <= 330 Ohm, no leakage.
- [x] **1 — 0 T gatemap** (`gatemap`, run 4 aborted / run 5 good). CNP line, two ridges.
- [x] **2 — (n, D) calibration** (`cnp-and-dline-calibration`, ana on run 5).
      ratio c_bg/c_tg = 0.773 (data), c_tg = geometry prior, n_offset = -0.089e12,
      D_offset = -0.013 V/nm (R_CNP(D) vertex). D = 0 window inside validators:
      **n = -1.27 .. +3.27e12** (TG-limited both ends).
- [x] **3 — SdH spot checks** (`sdh-spot-check`, run 6 e-side n = +3.2e12; run 7 h-side
      n = -1.2e12). Establish that oscillations exist and where they start.
      **Read (this session, ana pending):** run 6 onset 0.30 T (censored at the record
      edge), robust tones from 1.3 T, tone set {3.0, 4.2, 5.2, 7.1} T with a clean
      harmonic ladder 7.1 / 14.1 / 22.2 / 29.5; F_Luttinger(3.2e12) = 33.1 T. Run 7
      onset 0.71 T, tones {4.7, 6.6, 8.5, 9.4, 12.3, 14.8} T; F_L(1.2e12) = 12.4 T.
      **Conclusion: not decidable from spot checks.** A fixed-n trace cannot tell a
      genuine second Fermi surface from a harmonic of the first, nor a second *region*
      from a second *band*. -> the fan is required. Tones do fix the design: oscillations
      from ~1 T, F up to ~33 T (sets the 1/B Nyquist), SNR 40-120 (sets the noise budget).
- [ ] **4 — Landau fan at D = 0** (`landau-fan`, this step). B slow 0 -> 10 T x n fast
      -1.25 .. +3.25e12 along D = 0. The decisive measurement. ~4h45m, ends at 10 T.
- [ ] **5 — CNP dynamic-range follow-up at 10 T** (`cnp-cut-highB`). The fan is sized for
      the LL lines (sr1 500 uV = 50 kOhm FS); if the CNP column clips at high B, a short
      gate cut across the CNP at 10 T at a larger FS recovers the nu = 0 / zero-LL region.
      Costs gate time only (magnet already at 10 T), ~15 min.
- [ ] **6 — D-dependence, riding the magnet down** (`fan-vs-D` or `dline-cuts`). Whatever
      step 4 leaves ambiguous: if two families are seen, their D-dependence separates
      band-splitting (D-tunable) from region-mosaic (D-insensitive offset).
- [ ] **7 — call** in the ana notebook, per the brief's output contract.

## What would change my mind

- **One tone tracking F = n·h/4e across the whole n window, single nu = 4N family**
  -> ABCA, strong.
- **Two families, different slopes, converging on one CNP**, F1 + F2 = n·h/4e
  -> ABAB (near-equal partition) or ABCB (strongly unequal). The m*-ratio from the
  partition, plus the zero-LL count (16 vs 4+12), separates those two.
- **Two families, equal slopes, offset intercepts** -> region mosaic, not a band read;
  re-read on whichever region dominates and hedge the call.
- **No resolvable LL lines below 10 T at T_e ~ 8 K** -> "cannot tell", resolution-limited,
  with the T_e-vs-gap arithmetic stated.

## Budget / envelope notes

- Magnet is the expensive axis (0.137 T/min): never re-traverse. Fan goes up 0 -> 10 T
  (magnet sits at 0), leaves the field at 10 T for step 5; step 6 rides it down.
- Field cap 10 T, gates [-0.3, +1.0] / [-1.3, +2.0] V, Si at 0 (banned as a standalone
  survey). Everything at base T; no heater use planned.
