# vti-02 stacking-order campaign — plan (2026-08-23 refresh, post-handoff)

Goal (brief): call the stacking of tetralayer vti-02 — ABAB vs ABCA vs ABCB —
region-resolved (one wired pair: sr1 = B_1−B_2), evidence-cited, into the ana
notebook's final cell. Written at handoff pickup; reconstructs the prior
instance's arc (this file was owed from session start — noted in
session_notes) and carries the remaining steps.

## Discriminants (what the call rests on)

At D = 0 the three stackings differ in Fermi-surface topology and band masses:

- **ABAB (Bernal)**: decomposes into two bilayer-like subbands (light ~0.028 mₑ,
  heavy ~0.061 mₑ) → **two fundamental SdH frequencies** at fixed n, both
  dispersing with n, F_light + F_heavy ≈ n·h/(4e); no gap at CNP at D = 0.
- **ABCA (rhombohedral)**: single very flat band at low E → **one fundamental**
  carrying the full density (F ≈ n·h/(4e)); heavy mass (LK-dead at our
  T_e ≈ 8 K at low n); interaction gaps near CNP.
- **ABCB (mixed)**: monolayer-Dirac-like + bilayer-like mix → two-ish pockets
  with a light Dirac-like component and intrinsic e–h asymmetry; gapped or
  semimetallic CNP depending on parameters.

A Landau fan at D = 0 measures F(n) per tone family (slopes → per-pocket
degeneracy and density fraction) and the filling-factor lines (ν where Rxx
minima sit, n = ν·eB/h) — together these separate one-pocket from two-pocket
band structure and give the density partition, the primary stacking read.

## Steps

1. **[done] Gate C liveness** — runs 0–3 (`gate-current-sanity-check`): all
   4 provided contacts alive, leakage at noise floor (≲200 pA transients).
2. **[done] 0 T gatemap + (n, D) calibration** — run 5 (run 4 railed, lesson
   noted): CNP ridge; c_bg/c_tg = 0.773 (data), scale = geometry prior;
   n_offset = −0.089×10¹², D_offset = −0.013 V/nm → `cal_run5.json`.
3. **[done] SdH spot checks at D = 0** — run 6 (electron, n = +3.2×10¹²,
   B 0→10 T): strong fundamental 7.1 T + harmonics 2×/3×/4×, plus low-F
   cluster 3.0/4.2/5.2 T; nothing at the one-pocket F_L = 33.1 T →
   **multi-pocket, rules against a single-band read at this n**. Run 7
   (hole, n = −1.2×10¹², B 10→0.3 T): fundamentals ~4.7 and 6.6 T +
   harmonics; F_L = 12.4 T. Both signs show ≥2 tone families.
   Ana landing of runs 6–7 was owed at handoff — landing now.
4. **[now] Landau fan at D = 0** (`landau-fan`) — operator-requested, the
   campaign's central measurement. Fast axis: n = −1.25 → +3.24×10¹²
   (validator-limited on the hole side), 151 pts co-swept (V_tg, V_bg) along
   the run-5-calibrated D = 0 line. Slow axis: B rows [0, 0.25, 0.5, 0.75] +
   128 rows uniform in 1/B from 1 → 10 T (Nyquist F_max = 70 T; per-column
   FFT gets an already-even 1/B record). sr1 100 µV (10 kΩ FS — accepts a
   possible narrow rail at the CNP columns at high B), fast_delay 0.9 s
   (3τ at τ = 0.3 s/24 dB — knowing bend; run 5 clean at 1.0 s), leak guard
   1 nA. ≈ 7¼ h. Ends at 10 T, gates parked 0.
   **Analysis:** re-form via fan_grids/resistance_grids; (i) per-column FFT →
   F(n) ridge map, tone-family slopes dF/dn → degeneracy g per pocket and
   density partition; (ii) Rxx(n, B) fan → ν-line assignment from CNP
   (which ν are strong/missing → LL degeneracy structure); (iii) e–h
   asymmetry of both.
5. **[conditional] Follow-ups, priced after the fan read:**
   - LK T-ladder at 1–2 fixed (n, D=0) spots riding the field down (masses →
     light/heavy assignment; discriminates ABAB pair vs ABCB Dirac+BL).
   - D ≠ 0 fixed-B cut or small fan (CNP gap opening vs D: ABCA/ABCB gap,
     ABAB stays semimetallic) — cheap at fixed B on the way down.
6. **Verdict** — final ana cell per the output contract (per-region verdict +
   strength, evidence with run ids and numbers, hedges). Then close-out
   (`return-to-initial`): B→0 (73 min from 10 T — price it), gates→0,
   heaters off, readback into session_notes.

## What would change my mind

- Fan shows a **single** tone family with F ≈ n·h/(4e) across n (spot-check
  low-F cluster turns out to be harmonics/magneto-intersubband artifacts) →
  leans ABCA; then the LK ladder (step 5) becomes decisive, not optional.
- Strong e–h asymmetry in pocket count (e.g. two families on electrons, one
  on holes) → leans ABCB; check ν-line parity structure.
- Filling-factor lines from CNP showing g = 4 steps with two interleaved
  families whose densities sum to n → ABAB two-BL read.
- A CNP that becomes strongly insulating at high B at D = 0 (ν = 0 gap ≫)
  is consistent with correlated ABCA/ABCB, weak for ABAB — supporting, not
  decisive.
- Calibration risk: the n-scale is geometry-prior (only the tg/bg *ratio* is
  data-calibrated). The fan itself recalibrates it: total ν-line slopes give
  n(V) absolutely — cross-check c_tg against QH slopes before trusting
  F_L comparisons in the verdict.
