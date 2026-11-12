# vti-02 — plan (stacking order of tetralayer graphene: ABAB / ABCA / ABCB)

*Reconstructed + carried forward at the 2026-08-23 handoff. Steps 1–4 ran under the
previous instance; step 5 is the current move.*

## The discriminator

Min–MacDonald chiral decomposition of a 4-layer stack — the low-energy spectrum
splits into chiral subsystems whose chiralities sum to N = 4:

| stacking | decomposition | Fermi surfaces at D = 0 | minority share of n |
|---|---|---|---|
| **ABAB** (Bernal) | 2 + 2 (two bilayer-like) | **two** | γ₁ splitting λ∓ = (√5∓1)/2 → **≈ 0.28** |
| **ABCA** (rhombohedral) | 4 (one chirality-4) | **one** | — (single tone at F_L) |
| **ABCB** (mixed) | 1 + 3 (Dirac + rhombo-trilayer) | **two, strongly asymmetric** | **≈ 0.07** (at n = 3.2×10¹²) |

Each Fermi surface gives an SdH tone F_i = n_i·h/4e. The **calibration-free** read is
the *set of fractions* x_i = F_i/ΣF_j, not the absolute frequencies (our absolute n
scale is still a geometry prior). Additional ABCB tell: broken inversion → gap at
D = 0 and electron–hole asymmetry.

Model at n = +3.24×10¹² (F_L = 33.5 T): ABCA → {33.5}; ABAB → {9.2, 24.3};
ABCB → {2.5, 31.0}. (Step-2 table in `md_spot_e.md` gave ABAB {7.5, 25.6} from
quoted masses — same qualitative bracket.)

## Steps

1. **Gate C — `gate-current-sanity-check`** (runs 0–3, done). Four 1D gate legs to
   the card limits at B = 0. Established: contacts live, no leakage, two resistance
   peaks on the TG leg (→ two regions in series).
2. **`gatemap`** (runs 4 aborted / 5, done). 0 T map TG × BG. Established the CNP
   line, the (n, D) calibration (`cal_run5.json`: ratio c_bg/c_tg = 0.773 data-fit,
   c_tg = geometry prior, D_offset from the R_CNP(D) symmetry vertex), the realized
   D = 0 window **n = −1.27 … +3.27×10¹²**, and a **second parallel ridge (region B,
   +0.43×10¹² relative to A)** — a series mosaic, i.e. a known source of duplicate
   tones at ×1.13.
3. **`sdh-spot-check`** (runs 6, 7, done — analysis landing this turn). Electron spot
   n = +3.2×10¹² (0→10 T) and hole spot n = −1.2×10¹² (10→0.3 T). Established:
   **oscillations onset at 0.3–0.7 T**, fully developed LLs (minima reach R ≈ 0),
   SNR ≈ 40–120. Run 6 tone set {7.1, 14.1, 22.2, 29.5} is consistent with either a
   **harmonic ladder of 7.4 T** *or* a **two-surface pair {7.1, 22.2}** (ABAB-like,
   x = 0.24) *or* **{4.2, 29.5}** (ABCB-like, x = 0.13). **Undecided at one density —
   this is what the fan resolves.**
4. **Calibration sanity** — folded into step 2; absolute n still a geometry prior,
   so all calls rest on fractions, not absolute F.
5. **`landau-fan` — CURRENT.** R_xx(B, n) at D = 0, B slow (0.7 → 10 T, uniform in
   1/B with a 0.40 T cap on ΔB), (V_tg, V_bg) fast along the D = 0 line,
   n = −1.24 … +3.24×10¹². Establishes, at *every* density simultaneously:
   - **F_i(n) slopes.** A real second surface has dF₂/dn = x₂·h/4e with x₁+x₂ = 1; a
     harmonic has dF/dn exactly k× the fundamental's. Over the full n range these
     separate by ≫ δF = 0.75 T.
   - **Landau-line families.** One family of uniformly spaced lines converging on the
     CNP (ABCA, or a symmetry-broken single surface — uniform Δν) vs **two
     incommensurate families with crossings** (ABAB / ABCB).
   - **e–h asymmetry and the D = 0 CNP gap** (ABCB tell).
   - Free check: the lines' convergence point validates the run-5 n calibration.
6. **Next, decided by the fan** (fan ends at 10 T — ride the field down, never
   re-traverse):
   - If two tone families resolve → **`lk-mass`**: T-dependence at one or two
     densities to get m*₁/m*₂, which separates ABAB (0.38 mass ratio, both massive)
     from ABCB (Dirac-like minority, m ∝ √n). Rides 10 T down or holds.
   - If one family only → a **D-dependence fan slice** to test the gap's D-response
     and the e–h asymmetry.
7. **Call** — per-region verdict + evidence + hedges as the final ana cell;
   `return-to-initial` close-out.

## What would change my mind

- Fan lines that are uniformly spaced in ν across the whole window at all n → single
  Fermi surface → ABCA (and the run-6 tone zoo was harmonics + the region-B mosaic).
- Two families whose fractions track {0.28, 0.72} → ABAB; {0.07, 0.93} → ABCB.
- Fractions that do **not** sum to 1 against the measured F_L → the absolute n scale
  (geometry prior on c_tg) is wrong; fall back to ratios only, and say so.
- Region-A/region-B mosaic tones (×1.13 pairs) masquerading as a second surface →
  identified by a *fixed 13 % ratio independent of density partition*; if they
  dominate, the verdict degrades to `cannot tell` for the pair.

## Banned / out of scope

Gate-limit probing; standalone Si survey; any safety-surface edit.
