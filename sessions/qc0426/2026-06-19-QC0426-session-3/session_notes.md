# Session notes — QC0426 / vti

Operational log (not a science notebook). Entries as they happen.

## 2026-06-19

- TOOLING — Read tool returned "wasted call — file unchanged since your last Read"
  on the FIRST read of rig_card.md / device_card.md / the investigation recipe this
  session (no prior read in context). Worked around with `cat` via Bash for cards +
  recipes. If reproducible it defeats the dedicated Read path for reference files.
- BRING-UP — Gate A green (all setup cells exec [2]–[16] in one kernel; magnet status
  0.003 T / PS on / output enabled; sample_T 1.167 K; sr0–3 + QSwitch ser37 fw2.0
  connected). Gate B green (SAFETIES exec [11]: TG[-6,7] BG[-4.5,4.5] Si[-50,50]
  B_cap 8.0 — all match device card; field cap on magnet.mag.vals). Awaiting grant.
- GRANT — operator: "go for autonomy" (2026-06-19). E1 engaged. Re-entry after any
  E0 drop requires a fresh explicit grant.
- RECIPE FIX — gatemap.md (base): its fp list says "fp temperature(s)", but on the VTI
  that means `s.fp(heater.sample_temperature)` polls the LS335 per-point — the rig card's
  documented dual-master quirk (Grafana logger + kernel) -> VISA contention. Killed run 1
  (the gate map) on KRDG? A timeout ~row 0-1; the 2-min locator (run 0) survived by luck.
  FIX: never fp the LS335 on VTI. Read sample_T ONCE at cell top into the comment; rely on
  Grafana for the per-point T log. The landau-fan-vti variant already defers to the card on
  this ("follow the rig card's instrument-polling rules"); the base gatemap does not — the
  card wins. (run 1 failed, no data dir written; gates left mid-position, re-park before re-run.)
- STEP 1 DONE — run 0 (1D CNP locator) + run 1 (0T map, v2) -> (n,D) calibration on the device
  card. CNP line V_tg = -1.2923 V_bg + 0.149; ratio 1.2923 (geom 1.300, 0.6%); n_off -1.581e15;
  D_off 0 (assumed). Both Rxx metallic ~50-70Ω across D~0 (-11.4..+11.0 e12); leakage clean.
  Ana notebook cells 10-13 (raw map, fit/cal, take). CNP R low at D~0 (~1kΩ) -> held lightly.
- PROCESS — caught my own n_offset SIGN bug (density() ADDS n_offset) via the closure check
  (|n| was 2x the offset, constant not scatter -> tell-tale). The Verify closure step earned its
  keep; always run it before trusting n=0 placement.
- NOTE — ana notebook runs in its OWN kernel (6edc2948), separate from the measure/instrument
  kernel; it has the menv env (hera.analysis ok). nb-collab execute-cell on ana works.
- TIMING — field sweeps run ~8.7 s/pt (not my 5.7 s est): 8 mT blocking magnet ramp (3.5 s) +
  2.2 s dwell + ~3 s overhead (10 fp channels threaded read + magnet readback). A 501-pt 0->4T
  spot check is ~70 min, not 48. Price field sweeps at ~8.5-9 s/pt at 8 mT/2.2 s dwell.
- RECIPE FIX / sdh-spot-check — adaptive lock-in sensitivity sized off the B=0 reading (2.2x
  headroom) UNDER-RANGES on a device with strong positive MR: run 2 (hole, n=-5e12) Rxx rose
  33->71 Ohm by 1.8 T (x2.1) and was at ~81% of the 2e-6 scale, headed for a clip above ~2.4 T.
  FIX: size fixed sensitivity for the EXPECTED HIGH-FIELD max R (e.g. 5e-6 to cover ~250 Ohm),
  not the B=0 value; or autorange (ok on a 1D field sweep, unlike a 2D fast gate row). Applies
  to the electron spot check + the fan. (Spot check left running; mid/low-field window is clean.)
- TOOLING — `nb-collab execute-cell --timeout` bounds the CLIENT wait, not the kernel: when it
  expires the client exits non-zero ("failed") but the KERNEL CELL KEEPS RUNNING (sweep continues,
  data keeps landing, hera-watch still sees it). Benign, but the spurious "failed" is alarming.
  FIX: set --timeout > full expected run time + margin (run 2: 70 min run vs my 3600 s timeout ->
  false alarm). Real completion signal is hera-watch (or nb-collab wait). Confirmed clip: sr1/sr2
  pinned 109 Ohm from ~2.6 T (2e-6 saturation) -> usable FFT window [onset, ~2.5 T].
- MODEL TEMPLATE (fs_count_b0, D=0) — ABA = dominant BL tone ~F_L + SMALL ML partner
  (f_ML=1.5T, f_BL=29.5T at n=3e12; f_ML grows super-linearly, plausibly ~8T at 5e12);
  ABC = SINGLE tone at F_L, no partner. Discriminator = presence of the small ML partner
  + partition f_ML+f_BL=F_L. Hole run 2: 8.5+44=52.5~F_L is ABA-consistent (ML amplitude-
  dominant, but freqs classify, not amplitudes). Onsager OVERLAY clamps >3.5e12 -> the FAN
  must reach n<=3.5e12 for ML/BL curve-shape labeling (Step 5). Electron run 3 = clean test.
- STEP 4/5 + CALL — run 4 fan (electron, n=1.0-4.5e12 x B 0.4-4T, 8mT, fast_delay 1.0s, 7.7h,
  complete, leakage clean). High-F ridge disperses linearly (F=8.76*n), detrend-stable, tracks
  Onsager f_BL/F_tot ~0.89 F_L. Low-F (~5T) artifact-contaminated -> ML resolved only in the
  clean spot checks. CALL: QC0426 = ABA (Bernal), STRONG hedged — two pockets (8+44=F_L) on
  both Rxx pairs + both density signs; ABC excluded. Hedges: ML frac ~2x SWMcC nominal (lever-arm
  fork); LK mass split unavailable (temperature-dependence blocklisted). Ana cells 17-22; call
  cell 22; device card "Stacking result" section. n-scale geometry-prior (QH upgrade pending).
- LESSON — fan fast_delay 1.0s (amplitude-for-time trade) cost low-F SNR: the small ML partner
  (model 0-2T at n<=3.5e12) sank into a low-F detrend artifact band, so the FAN could not
  independently resolve ML — only the full-settling spot checks (n=5e12, ML~8T clear of artifact)
  carried it. For a future ABA/ABC fan where the ML partner is the target, settle the fan at the
  floor (cost) OR rely on high-n spot checks for ML and use the fan for BL dispersion only.
- CLOSEOUT (2026-06-20) — restored instruments to session-start (measure cell 48): bias 0.5V/5nA,
  sens sr0=0.05/sr1=2e-5/sr2=2e-5/sr3=1e-4, tau 0.3/24dB (untouched), gates 0, B=0 (PS on), T base.
  QSwitch left on the provided contact config (qsw.reset forbidden; Si 16/11 closed). Session done.
