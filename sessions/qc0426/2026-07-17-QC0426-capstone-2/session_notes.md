# Session notes — QC0426 / vti

Operational log (not a science notebook).

## 2026-07-17 — E1 grant
- Operator grant: **"go for autonomy"** (Zack, chat, 2026-07-17 ~18:4x local),
  conditional per brief. Kernel-binding probe: OK (measure cell 30, exec 17).
  VERIFY executed by HERA (measure cell 28, exec 18): **VERIFY: ALL GREEN**
  (16/16 checks; magnet 0.0034 T, base T 1.170 K, logfile cadence 5 s live,
  He 16.1 in). E1 engaged.

## Gate C + gatemap
- Gate C (gate-current-sanity-check, runs 0-3): PASS. |I_gate| <= 47 pA all
  legs; CNP near (0,0), R ~ 1-3 kOhm; metallic tens of Ohm at limits both
  signs. Si leg deferred (no DC205 current readback; not in near arc).
- TOOLING — hera-watch digests don't carry Keithley gate-current channels;
  first-rows leakage checkpoint read the partial data.tsv directly (fine, but
  a --channels option covering non-lock-in fp columns would close the gap).
- Timing: liveness legs ran 2.13-2.28 s/pt at NPLC=10+delay=1 (predicted
  1.3-1.7); rig-card serialize-all-reads model fits (~25-30 ms/read x 15
  cols + 4x167 ms Keithley NPLC=10). Gatemap priced from this at 4.2-4.6 h.
- Gatemap (run 4, 'gatemap' slug): 0 T, TG fast [-3,+3] x101, BG slow
  [-4.5,+4.5] x101, 5 nA bias, sens sr1-3 2e-4, started ~19:2x. E1 auto.

## Calibration + spot checks
- Run 4 gatemap: CNP calibration ratio 1.2863 (data), n_off -0.052e12,
  D_offset 0 (R_CNP min at Vbg~0). Written to device_card.md. R_CNP
  D-tunable >10x both channels — ABC-leaning hint, fed forward only.
- PROTOCOL — settle_s (FastBi post-ramp dwell) set 3.0 -> 1.2 s for
  fine-step field sweeps (= 4*tau card dwell floor); not operator-owned per
  rig card, stated in the proposing cell. Flag for Chiron: rig card could
  name settle_s ownership explicitly.
- Spot check H (run 5): n=-3.0e12 D=0, B 0.7->8 T uniform 5.26 mT
  (1/3-Nyquist on F_L=31 T), 20 nA, sens 5e-5. ~100 min priced.

## Spot checks + fan
- Run 5 (hole -3e12): onset 0.77 T; f_ML ~4 T + heavy band 27-28 breaking
  harmonic envelope + ~33 T tone. Run 6 (electron +3e12): stable singleton
  33.2 T (+2f), fixes lambda ~1.07; low-F/22-29 content window-unstable ->
  fork. Cross-side tension noted in ana (single-scale discipline).
- RECIPE FIX — sdh-spot-check: sdh_onset on run 6 returned the *heavy
  tone's* SNR edge (3.3-3.9 T) as onset_b while oscillations run from
  ~1.5 T; recipe Verify could warn that onset_b is per-dominant-tone, and
  window-stability sweeps must extend below it for light-tone hunts.
- TOOLING — sr1 soft-read to 2.73 kOhm on nominal 2.5 kOhm sens (SR830
  ~109% headroom): hera-watch/clip detection didn't flag; worth a
  soft-clip warning in sdh_onset/clip_high_b.
- Run 7 fan launched (landau-fan-vti): hole D=0, 141 (1/B-uniform
  0.77-8 T) x 101 (n -0.5..-3.5e12), 20 nA, sens sr1 5e-4/sr2 2e-4/sr3
  5e-4, ~6.8-7.5 h priced from measured 16.3 rows/min fp-set rate.

## Fan + LK ladder
- Run 7 fan complete (5.8 h, clean; low-|n| corner soft-clip flagged, 9/15
  cols excluded). Analysis in ana cells 24-28: lambda=1.069 Luttinger pin
  (device card scale upgraded), ABA template on hole side, e-side
  non-discriminating (model: e-side ML 1.5 T unresolvable).
- RECIPE FIX — trilayer-stacking-fs-count: fs_count_b0 is electron-only
  (E_F >= 0); hole-side Onsager overlay impossible — flag the p-h caveat in
  the recipe / extend the model (README TODO already tracks m*; add E_F<0).
- Run 8-13 LK ladder launched (temperature-dependence-vti): base/6/10/15/
  22/32 K at hole spot, B 1.5<->8 T alternating, guard set per variant.
  settle_s stays 1.2 s.

## LK ladder + call (2026-07-18)
- Runs 8-13: 6 rungs base/6/10/15/22/32 K, all hover-accepted, held to
  <0.26 K/rung, 54 min/rung as priced. Guard set exercised cleanly (no
  runaway fires, no stale-logfile fires).
- LK masses: m_ML 0.019-0.021, m_BL 0.037-0.064 (channel spread = BL-window
  harmonic contamination — systematic, stated), m_FL ~0.05. Two distinct
  masses -> ABA confirmed.
- **Session call: QC0426 = ABA (strong), per-region (sr1 T3-T4, sr2 B4-B5
  both), F_L-tone = breakdown-consistent (fork carried on ABC-domain).**
  Full contract in ana nb final cell.
- FEEDBACK — none: no operator overrides this session (fully autonomous
  E0->E1 arc from bring-up to call).
- Rig end state: gates 0/0/0, B = 8 T (flagged to operator), heaters off,
  T descending from 32 K. settle_s left at 1.2 (noted in cells).
