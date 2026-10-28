# vti-02 stacking call — plan (recreated 2026-08-23, post-handoff)

Goal: ABAB vs ABCA vs ABCB, region-resolved (one wired pair: sr1 = B_1−B_2), per output contract.

## Done
1. **Gate C** — runs 0–3: liveness + leakage green (ana cell [6]).
2. **Gatemap + (n,D) cal** — run 5 (run 4 aborted, sens rail): ratio c_bg/c_tg = 0.773,
   c_tg = 2.796 mF/m² (9.5 nm geometry prior), n_offset = −0.089e12, D_offset = −0.013 V/nm
   (`hera_scratch/cal_run5.json`). Single CNP ridge; no second ridge → one region visible on this pair.
3. **SdH spot checks at D = 0** — run 6 (e, n = +3.2e12, 0→10 T): fundamental F ≈ 7.1 T + harmonics
   14.1/22.1/29.5, onset < 0.3 T; F_full = 33.1 T → visible pocket ≈ 21% of n. Light+heavy two-band
   picture (ABAB-like); ABCA singleton excluded *at this spot* unless the 7.1 T tone is something else.
   Run 7 (h, n = −1.2e12, 10→0.3 T): multi-tone 4.7/6.6/8.5/12.3 T; 12.3 ≈ F_full = 12.4 T.

## Now
4. **Landau fan at D = 0** (this step; operator-requested): n fast −1.25…+3.25e12 (121 pts, co-swept
   TG+BG line, run-5 cal), B slow 1.2→10 T uniform in 1/B (97 rows, Δ(1/B) = 0.0076 → F_Nyq 65 T,
   ΔF 1.4 T). Establishes F(n) branches on both carrier signs — the decisive stacking evidence:
   - ABAB: two branches per sign, F_light(n) + F_heavy(n) partial slopes summing to h/4e·|n − n₀|;
     light branch ≈ 20–25% share on e-side (run 6 anchor).
   - ABCA: single branch at the full-density slope (33 T at +3.2e12), no light pocket.
   - ABCB: monolayer-like (F ∝ n, 2-fold or 4-fold light Dirac cone) + heavy remainder; distinguished
     from ABAB by the light branch's share/slope and LL-crossing pattern.
   Analysis: per-column FFT in 1/B (`sdh_fft`), F vs n overlay against full-density Luttinger line +
   two-band partitions; visual fan (LL fan lines, ν=0 stripe).
5. **Verdict** — ana final cell per output contract. If F(n) is ambiguous (branch attribution unclear),
   the fallback discriminator is T-dependence (LK masses) at fixed n, high B — priced separately if needed.

## Would change my mind
- A light branch on the e-side that tracks the FULL density slope → not ABAB.
- Fan lines from two CNPs / split ridge → multi-domain; region-resolve becomes "mixed on this pair".
- Railed/insulating stripes beyond ν = 0 (gaps at symmetric fillings) → weigh even-integer gap
  pattern (ABAB semimetal vs ABCA gapped CNP at D = 0).

## Standing facts
- Magnet 0.137 T/min, blocking sets; never re-traverse. Now at 0 T → fan ascends 1.2→10 T, ends at 10 T.
- sr1 sens for fan: 100 µV (10 kΩ FS, 17× run-7 high-B max 590 Ω; ν=0 stripe may rail — accepted).
- τ = 0.3 s / 24 dB; fast_delay 1.0 s (3.3τ, run-5-proven on quasi-continuous gate steps); magnet
  settle 3 s = 10τ per row.
- Timing cal: 1.17 s/pt (run 5, fast_delay 1.0); fan priced 5.1 h → headline 5 h 45 m.
