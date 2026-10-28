# vti-02 — stacking-order plan (reconstructed + extended at the handoff, 2026-08-23)

Goal: region-resolved ABAB / ABCA / ABCB call on vti-02 (tetralayer graphene),
evidence-cited, or a calibrated "cannot tell". One live Rxx pair (`sr1` = B_1−B_2),
source T_0 → drain B_3; no Hall pair, no mux.

*(The original plan file did not survive the handoff; steps 0–3b below are
reconstructed from the measure-notebook markdown + `hera_scratch/md_*.md`.
Step 4 onward is this instance's.)*

## Step 0 — Gate C liveness (`gate-current-sanity-check`) — DONE, runs 0–3
1D legs through each gate at B = 0. Alive, no leakage, Rxx 60–330 Ω.
**Established:** the provided configuration conducts; **two** resistance maxima per
leg ⇒ two series regions of different intrinsic doping.

## Step 1 — 0 T gatemap → CNP + (n, D) calibration (`gatemap`, `cnp-and-dline-calibration`) — DONE, run 5 (run 4 aborted, railed)
**Established:** two *parallel* CNP ridges (A dominant, B ≈ 0.19 V lower in V_tg,
electron-doped by 0.43×10¹² vs A) ⇒ a series mosaic of two domains with the same
lever arms. c_bg/c_tg = 0.773 (data), c_tg = geometry prior (9.5 nm hBN),
n_offset = −0.089×10¹², D_offset = −0.013 V/nm from the R_CNP(D) symmetry vertex.
R_CNP 240 Ω at D ≈ 0 → ~2.4 kΩ at D ≈ +0.25 V/nm: a D-tunable gap, **not** a
stacking read (all three parents gap under D).
Realized D = 0 window inside the validators: **n = −1.27 … +3.27×10¹²** (TG-limited).

## Step 2 — feasibility model table — DONE (paper)
At n = 3.2×10¹²: F_Luttinger = 33.1 T (full density, 4-fold).
ABAB → two Fermi surfaces, F ≈ 7.5 / 25.6 T; ABCA → one, F = 33.1 T.
*(ABCB row still owed — see Step 4's read table below.)*

## Step 3 / 3b — SdH spot checks (`sdh-spot-check`) — DONE, runs 6 (e, n=+3.2) / 7 (h, n=−1.2)
**Established (this instance's read, `hera_scratch/ana_spot.py`):** SdH is strong and
**onsets below 1 T** (0.40 T censored at the record edge, run 6; 0.65 T, run 7),
amplitude 20–100 Ω pk-pk on a 12–460 Ω background, point noise ≈ 27 nV (2.7 Ω)
**independent of the sensitivity setting** (same in Ω at 50 and 100 µV FS).
Run 6 tones: 7.1 T (strongest low-B survivor) + 14.1 / 22.2 / 29.5 / 57.9 / 89.2 T.
The tone ladder is ambiguous between (a) one anharmonic fundamental at 7.1 T with
harmonics and (b) two Fermi surfaces (7.1 + 22.2 ≈ 29.3 ≈ F_L within the lever-arm
prior's ~10 % error). **A 1D FFT cannot settle this** — which is exactly what the
fan does. *This is the hinge that makes Step 4 the decisive measurement.*

## Step 4 — Landau fan at D = 0 (`landau-fan`) — NEXT (this proposal)
Rxx(n, B): B slow 0 → 10 T at 0.25 T (41 rows), n fast −1.25 … +3.25×10¹² at
0.040×10¹² along the D = 0 line (113 pts), sr1 500 µV. ETA ≈ 3 h 10 m.
**Establishes:** the number of independent fan families and the density partition
between them — harmonics cannot fake a family, because a harmonic of a tone lies on
the *same* n-intercept-at-B=0 family with subdivided spacing, while a second Fermi
surface is a family with its own dn/dB slope set and its own carrier fraction.

| read | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed) |
|---|---|---|---|
| fan families at D = 0 | **two**, ratio of carrier fractions ≈ 2.6 (λ = 2cos(π/5) : 2cos(2π/5)) | **one**, carrying the full density | **two**, unequal ratio ≠ 2.6 (Dirac-like + bilayer-like) |
| dominant filling sequence | 8-fold at low n (two 4-fold sets overlaid), splitting to 4 | 4-fold, F = F_L | mixed; the light branch is Dirac-like |
| CNP at D = 0, high B | ν = 0 develops, moderate | strong (flat band, large DOS) | asymmetric / already gapped at D = 0 (no inversion symmetry) |
| consistency | ΣF_i = F_L(n) at every n | F = F_L(n) | ΣF_i = F_L(n) |

Sum rule Σν_i = n·h/eB at every B is the closure test, and it re-calibrates the
absolute lever arm (c_tg is still the 9.5 nm geometry prior) — the fan is the
lever-arm calibration as well as the stacking read.
**Mosaic caveat:** sr1 measures A and B in series, so expect the *same* family
template twice, offset by Δn = 0.43×10¹² (B's lines shifted, ×1.13 in density).
Two fan origins in n ⇒ mosaic; two slope families sharing one origin ⇒ two bands.
**Would change my mind / abort:** whole n window railed (sensitivity), leak trip,
or no resolvable fan structure by B ≈ 5 T (then the read is disorder/T_e-limited and
the fallback is Step 5a, not more field).

## Step 5 — contingent on the fan
- **5a (if the fan is clean, families ambiguous):** temperature dependence at 2–3
  fixed n, `set_both(T, ratio=0.95)` ladder to ~20 K → Lifshitz–Kosevich masses.
  Masses are the second, independent stacking discriminator (ABAB pair 0.028/0.061 mₑ
  vs ABCA ≈ 0.074 mₑ and strongly n-dependent). Expensive (descents are
  passive-cooling-limited, τ ≈ 27 min) — only if the fan does not close it.
- **5b (if the fan is clean and families resolved):** a second, shorter fan at
  finite D (≈ +0.2 V/nm, where run 5 shows the gap) over a narrower n window, to
  test the D-evolution of the family split — the ABCA gap grows monotonically and
  symmetrically, ABAB's two sets respond differently.
- **5c (if the fan is featureless):** re-price. The limit would be T_e ≈ 8 K, not
  fixable this session.

## Step 6 — the call
Final cell of the ana notebook, per the brief's output contract: per-region verdict
(one line per measured pair — here one pair, plus the A/B mosaic read), evidence
with run ids and numbers, confidence + hedges.

## Running output-contract debt
- ana notebook is **missing runs 6 and 7** (raw + analysis). Land during the fan's
  first checkpoint window — `hera_scratch/ana_spot.py` is the working script.
