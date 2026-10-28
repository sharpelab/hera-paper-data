# Session notes — QC0426 / VTI round 2 (2026-06-14)

Operational log. Tagged entries; cite cell idx / file_id / recipe. Points at data, doesn't repeat it.

- **FEEDBACK — operator: use `nb-collab wait` on future measurement cells.** After
  run 0 (contact-survey), operator asked HERA to block on cell completion via
  `nb-collab wait` rather than ending the turn and polling. Adopted from batch 2 on.
- **TOOLING — realized per-point ~0.74 s/pt on the TG screen** (run 0 / file_id 0:
  53 pts, 39.3 s wall incl. initial 0→−6 V ramp). Cheaper than the rig-card 1.2 s/pt
  default; use ~0.74 s/pt for pricing the rest of the survey, recalibrate for the
  gate map (longer dwell likely).
- **DATA — contact-survey-2t run 0 (T1–T7): dead/high-R.** ~0.34 nA flat vs 5 nA
  nominal, gate-independent over TG −6..+7, in-phase (~1.3 GΩ). Not workable; T1/T7
  suspect. Disambiguation in batch 2 (mini-star on T4 + T3–T5 hedge).
- **DATA — batch 2 (file_id 1–6): T1 localized DEAD; T3,T4,T5,T7,B4 alive.** T1 reads
  high-R in both its pairs (T1–T7 #0, T1–T4 #3) while partners T4/T7 conduct ~5 nA
  elsewhere → fault localized to T1. T4-star (T4–T5,T3–T4,T4–T7,T4–B4) and T3–T5 all
  ~5 nA. Avoid T1.
- **RECIPE FIX — contact-survey-2t: current-bias source saturates the 2T current; CNP
  read is 4T, not the drive current.** This rig drives current-bias (0.5 V / 100 MΩ ≈
  5 nA). For any device R ≪ 100 MΩ the measured drive current is pinned at ~5 nA, so
  step-3's "drive amplitude / measured current" returns ~R_bias, NOT device R, and
  there is no CNP dip in the current (mod <1% across TG −6..+7 for all alive pairs).
  The current cleanly separates dead (I≪5 nA) from alive (I≈5 nA) — good enough for
  aliveness/localization — but ranking alive contacts by resistance and seeing the CNP
  require the 4T voltage (V = I·R, recipe 2's gate map). The base recipe is
  rig-agnostic (assumes voltage-bias-like I∝1/R); a VTI/current-bias delta should say
  so. Evidence: file_id 1–6.
- **PROTOCOL — sweep dwell must be derived from the lock-in time constant, not picked.**
  HERA set fast_delay/delay=0.5 s on the survey + gate map as a conservative round
  number matched to the scout, not from τ (dwell ≳5τ @6 dB/oct, ≳7–10τ @24 dB/oct).
  Operator (Qingrui) flagged it. Rule going forward: read sr*.time_constant() +
  filter_slope before pricing any sweep and set dwell from τ. Note: a *uniform*
  fast-axis lag biases only the CNP-line intercept (n_offset), not the slope (cap
  ratio) — so the file_id 17 map's ratio is robust; offset to be pinned by a fwd/back
  cut. Matters most for phase-2 fan dwell.
- **TOOLING — `nb-collab wait` has a ~10 min internal timeout; use `hera-watch` for
  longer runs.** The settled gate map (~19 min, file_id 18) outlived two `nb-collab
  wait` calls (returned `status: timeout`, run unaffected). For >~10 min sweeps,
  background `hera-watch data/<id>` instead — it's the intended long-run monitor and
  exits on completion. (Also: `--wait-for-rerun` errored exit-2 when the watched cell
  was interrupted rather than re-run — don't use it for first-run waits.)
- **TOOLING — instrument snapshot stores time_constant/filter_slope as None.**
  data/16 metadata 'instruments' snapshot has the keys but null values, so τ is not
  recoverable from disk (hurts reproducibility / post-hoc settling checks). Capture
  these at station build.
- **DATA — CNP/D-line calibration (file_id 18, settled 4τ map): c_bg/c_tg = 1.314
  (sr1), 1.309 (sr2), prior 1.300.** c_tg=1.703e-3, c_bg=2.237e-3 F/m²;
  n_offset=−0.225e12 cm⁻², D_offset=0; CNP at (Vtg,Vbg)=(+0.21,0); quality
  ~0.21e12 cm⁻². D envelope ±~1.2 V/nm; |D|≤0.5 covers n∈[−4,4]. Written to device
  card + ana (cells 10–13). **Phase-2 signal**: CNP Rxx rises with |D| (1→78 kΩ) and
  is asymmetric in BG — D-gap-like, a stacking discriminator. Not interpreted.
- **TOOLING — ana kernel cwd ≠ measurement dir.** The ana notebook's cell-1 helpers
  use \`file_path = os.path.join('.', 'data')\`; the ana kernel's '.' isn't the
  measurement dir, so load_meta/load1d raise FileNotFoundError. Fix: set \`file_path\`
  to the absolute data dir in the analysis cell. Template could derive it from the
  notebook path instead of '.'.
- **DATA — phase 2 step 1 (CNP Rxx vs D, from file_id 18): mixed/mosaic-leaning,
  gappable content present.** CNP Rxx grows ×90 (sr1) / ×83 (sr2) with |D| (B=0) over
  D∈[−0.98,+1.15] — ABC-positive D-gap fingerprint in BOTH paths. But D≈0 CNP ~0.8 kΩ
  (near paper 250 Ω ABA benchmark) and ceiling ~80 kΩ (not MΩ) ⇒ consistent-with mixed
  ABA/ABC mosaic, not clean ABC. Per-region call deferred to fans. ana cells 14–16.
- **RECIPE FIX — landau-fan.md is toploader-flavored; needs a VTI delta.** Recipe step
  0/4/5 use \`mag.field\`, \`calculate_gate_voltages(ns,Ds,dtg,dbg)\`,
  \`sweep.AsyncStation\`, \`time.sleep(600)\` field-settle, \`alerts.discord\`. VTI forms:
  \`magnet.mag\` (blocking ramp, no pre-settle sleep needed — set blocks till reached),
  \`sharpelab_nb.gates.calc_gate_voltages(n,D,c_tg,c_bg,n_offset,D_offset)\`,
  \`async_station\`, \`hera-notify\`. Also the cost-model 'fine B nearly free' assumes
  traverse-dominated; at this rig's 1.44 s/pt (4τ) a fan is MEASUREMENT-dominated
  (8 T traverse ~1 h ≪ grid time), so coarse-first still applies. First VTI fan:
  file_id 19 (designed cell 48).
- **FEEDBACK/RECIPE FIX — never per-point fp the Lakeshore on VTI (two-masters
  contention).** HERA put \`s.fp(heater.sample_temperature)\` in the D=0 fan (file_id
  19), polling the LS335 every fast point → VISA contention with the Grafana logger →
  \`VI_ERROR_TMO\` on \`KRDG? A\` killed the run at row 2 (~7 min). The rig card warns
  about this explicitly; the toploader \`landau-fan\` recipe step 6 says "fp
  temperature(s)" — a VTI delta must say DON'T fp the LS335 (rely on the Grafana
  logger; single preflight read only). Re-ran as file_id 20 with T removed from fp.
  Lock-ins (GPIB) are fine — contention is LS335-specific.
- **DATA — D=0 fan (file_id 20) → stacking call: ABC (weak-to-moderate).** Onset
  ~2.5–3 T (moderate mobility). Single clean fan of straight rays; SdH-FFT shows ONE
  frequency (g=4 single band), 0/52 columns two-pocket → against ABA ML+BL. Hall
  classical (no plateaus). Both regions (sr1 T3-T4, sr2 B4-B5) agree → no mosaic
  disagreement. With step-1 D-gap, all resolvable discriminators point ABC. Hedges:
  ABA chain region (n>4) not measured; no plateaus; lever-arm geometry-prior; no LK
  cross-check. 5-part call in ana cell 19. Firming fan queued (file_id 21: high-n
  n=3.5–10, B 8->0, rides magnet home).
- **DATA — firming fan (file_id 21) → call upgraded to ABC (moderate).** Chain region
  (N_M=1≈6.8, N_M=2≈10) now in-window: straight rays, no curved arcs co-locating with
  model chains; single SdH branch across n=3.5–10 in clean B4–8 T window (0/69
  two-pocket). An apparent high-n second pocket (b-range 3–8 T, 8 cols) VANISHED for
  B≥4 T → sub-onset (3–4 T) artifact, not a pocket (STYLE rule 14 fork, tested+killed).
  Both regions agree. Magnet rode home to 0 T. Updated 5-part call in ana cell 19;
  firming figure ana cell 21. Remaining hedges device/rig-inherent (no plateaus, no
  LK-mass cross-check) — strong needs lower T.
- **TOOLING — nb-collab markdown: backtick-wrapped slash-paths can hit bash command
  substitution** (dropped 'hera/models/aba_trilayer' from a cell, intermittently —
  other backtick paths survived same session, so it is flaky). Robust fix: edit-cell
  --source-file (write the cell to a file, no shell quoting). Use --source-file for
  any long/path-heavy cell.
- **PROTOCOL — re-run the fan Nyquist check when n_max changes; don't reuse ΔB.**
  Both fans used ΔB=0.1 T. For file_id 20 (n≤4) the SdH-period check at the worst
  corner (n=4,B≈3 T) gave 2.2 rows/period — marginal-OK, claims confined above onset.
  For file_id 21 I reused 0.1 T without re-checking for n_max=10; period ∝1/n, so at
  n=10,B=4 T it's only 1.5 rows/period (UNDER the ≥2 floor) — n=10 needs B≥5–6 T at
  0.1 T. That under-sampled corner is exactly where the spurious high-n second-pocket
  lived (killed for B≥4 T; robust single-pocket confirmed at b-range (4,8),(5,8),(6,8)
  → 0/69). Conclusion not compromised, but design should have flagged it. Fix for
  high-n fans: finer ΔB (≈0.05 T) with fewer n-points, or floor the high-n claim at
  B≥5–6 T by design. (At 1.44 s/pt these fans are measurement-dominated, so fine B is
  NOT free here — trim n-points, don't coarsen B.)
- **DATA — multi-region D-gap survey (file_id 22,23 + 18) → call upgraded to ABC
  (strong).** 9 contact-pair regions (both edges), B=0 CNP-Rxx-vs-D: ALL gap ×26–505
  with |D|, none flat → device-wide rhombohedral content, not mosaic (resolves the
  step-1 caveat: modest ceiling = moderate mobility/in-gap conduction, not ABA
  shunting). ~35 min, magnet stayed at 0 T, no T fp. ana cell 23.
- **DATA — SdH lever-arm cross-check (analysis only, file_id 20+21): single band,
  scale ~15% high.** Dominant SdH freq vs n_gate is a single line through origin
  across n=0.6–10 (one g=4 band carries full density → single Fermi surface, sum-rule
  form, not just peak count). Slope 85% of g=4 ideal → absolute n/D scale ~15% above
  geometry-prior (ratio 1.314 unchanged); SdH-anchored lever-arm upgrade. ana cell 23.
- **CALL: ABC (strong)** on B=0 + single-particle evidence; decisive (ν=±6 QHE / LK
  mass) needs lower T. Updated 5-part call ana cell 19.
- **PROTOCOL — phase split worked well.** The phase-1/phase-2 gate (exit report +
  operator go) is a clean, natural checkpoint: phase 1 (bring-up + characterize) is a
  self-contained deliverable, and the exit report forces a coherent hand-off rather
  than drifting into magnet work. Recommend keeping it.

---

## Session summary (2026-06-14 → 06-15, operator: qingrui; supervisor: Zack)

**Outcome: both phases complete. Stacking call = ABC (rhombohedral), strong** on the
B=0 + single-particle evidence accessible at 1.2 K (decisive needs lower T).

**Phase 1 (bring-up + characterize):** gate validators committed (TG/BG/Si + B cap);
contact survey (file_id 0–16) localized 5 dead contacts and blessed a workable config
(source T2 / drain T7; sr1=T3–T4, sr2=B4–B5, sr3=T5–B6); CNP/D-line calibration
(file_id 18): c_bg/c_tg=1.314 (geom prior 1.300), n_offset=−0.225, D-line designer.
Exit report → operator go.

**Phase 2 (classify):** D=0 fans (file_id 20, 0→8 T; file_id 21 high-n, 8→0 T) →
single Fermi surface (FFT + SdH lever-arm sum-rule), no crossing chains where the ABA
model places them. Multi-region D-gap survey (file_id 22,23 + 18): 9 regions, all gap
×26–505 with |D| → device-wide rhombohedral, not mosaic. SdH lever-arm anchored the
absolute scale ~15% below geometry-prior. 5-part call in ana cell 19.

**Deliverables:** measure + ana notebooks (record + analysis), device_card.md
(config + calibration written back), session_notes.md (this file).

**Open / next:** decisive ABC confirmation (ν=±6 QHE sequence, LK single mass) needs
lower T → mK campaign (ABC = flat-band/correlated candidate). Cheapest pre-warming
firming: LK-mass temperature series on one SdH branch (not run this session).

**Recipe/tooling fixes logged above:** contact-survey-2t current-bias saturation;
landau-fan VTI delta (magnet.mag, no LS335 per-point fp, measurement-dominated cost);
fan Nyquist re-check on n_max change; nb-collab wait 10-min cap / use hera-watch;
nb-collab markdown backtick-path substitution / use --source-file; ana kernel cwd;
dwell must be TC-derived (4τ).

**Rig left:** magnet 0 T, gates parked to 0 (park cell), device contacts grounded
(mux.park), Si closures 16/11 held all session, base T holding.
