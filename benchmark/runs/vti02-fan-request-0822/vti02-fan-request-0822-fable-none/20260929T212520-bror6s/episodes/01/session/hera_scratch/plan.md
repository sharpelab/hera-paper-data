# vti-02 stacking-order campaign — plan (reconstructed 2026-08-23 at handoff)

*(The first instance ran steps 1–3 without leaving `plan.md` on disk — reconstructed
here from the notebooks and session notes; PROTOCOL note filed. Kept current from
here on.)*

**Goal:** ABAB vs ABCA vs ABCB call for tetralayer vti-02, evidence-cited, per the
output contract (final ana cell). One measured pair: sr1 = B_1–B_2 (Rxx only; no
Hall channel this cooldown).

## Done

1. **Gate C — liveness + gate-current sanity** (runs 0–3): all four gate legs clean
   (|I_gate| ≲ 0.2 nA transients), device conducts, two-peak structure in 1D legs.
2. **0 T gatemap + (n, D) calibration** (runs 4 aborted / 5; ana cells 12–13):
   ratio c_bg/c_tg = 0.773 (data), c_tg anchored on 9.5 nm prior, n_offset
   −0.089×10¹², D_offset −0.013 V/nm. CNP ridge gap grows with |D| (not by itself
   a stacking call — three candidate parents). Second parallel ridge B: mosaic
   region electron-doped +0.43×10¹² vs A. Realized D = 0 window: n = −1.27 …
   +3.27×10¹² (TG-limited). Cal in `hera_scratch/cal_run5.json`.
3. **SdH spot checks at D = 0** (runs 6 e-side, 7 h-side; ana cells 14–15): e side
   is a two-band metal — F_l ≈ 7.1 T + F_h ≈ 30.0 T with breakdown comb; sum 37.1 T
   vs prior-scale F_total 33.1 T → n scale likely +12% vs prior (c_tg thinner-hBN
   error; consistent with run 5's ratio shift). h side harmonic-rich multi-tone.
   Anti-ABCA lean (two bands), ABAB vs ABCB open.

## Now

4. **Landau fan along D = 0** (the money measurement, ~6 h): fast axis co-swept
   (V_tg, V_bg) along D = 0, n = −1.25 … +3.20×10¹² (151 pts); slow axis B =
   1.0 → 10.0 T, 100 mT (91 rows); sr1 500 µV (50 kΩ FS — CNP at high B may rail;
   accepted, gap region is qualitative there), fast_delay 1.0 s (run-5-calibrated
   1.1 s/pt). Establishes: (a) F(n) branches per carrier sign — light+heavy band
   partition vs single band vs monolayer-like linear branch; (b) LL fan filling
   factors: ν-line slopes calibrate n absolutely (lever-arm check of the +12%
   read); (c) degeneracy pattern of strong minima (which ν are principal gaps) —
   the ABAB / ABCA / ABCB discriminator; (d) ν = 0 / CNP insulator vs B.
   Ends at 10 T, gates at n = +3.2×10¹².
   - Checkpoints: first rows (~15 min: rails/leak/signal); ~3 T (row ~20) interim
     re-form + partial read; ~6 T. Abort on rail-everywhere, leak trip, dead channel.

## Next (data-dependent)

5. **Targeted follow-ups** as the fan demands (choose after step 4 read):
   - LK mass at 2–3 (n, B) points on the dominant branches (T ladder via
     `set_both`, hover-acceptance per rig card) if masses are needed to separate
     ABAB's two bilayer-like masses from ABCB's monolayer+bilayer partition.
   - Short D ≠ 0 fan slice or fixed-n D sweep at fixed B if band-edge behavior
     vs D is the remaining discriminator (ABCA flat band gaps strongly with D; ABAB
     semimetallic robust).
   - Ride the field down through any of these (never re-traverse).
6. **Verdict** — final ana cell per output contract (per-region: A, and mosaic B
   where separable; strength words; run-id-cited evidence; hedges).
7. **Close-out** — `return-to-initial` cell: B → 0, gates → 0 at committed pacing,
   heater ranges off, readback printed and recorded in session_notes.

## What would change my mind / watchpoints

- ν-line slopes disagreeing with the +12% rescale → redo n calibration before
  interpreting F(n).
- The region-B mosaic producing a second CNP fan shifted by +0.43×10¹² — expect
  doubled features; separate by the two CNP positions before calling degeneracies.
- A single F(n) branch tracking n·h/4e exactly → ABCA back on the table.
- Leakage above ~1 nA sustained anywhere in the box → stop, notify.
