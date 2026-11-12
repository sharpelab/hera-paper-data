# Session notes — vti-01 / VTI

Operational log (not a science notebook).

## 2026-08-18 — E1 grant
- Operator Zack: "go for autonomy" after gates A+B operator-run and VERIFY landed (conditional grant per brief).
- Kernel probe (cell 31, exec 16): KERNEL-BINDING: OK — bound to instrument-carrying kernel 2b0dd53a.
- VERIFY (cell 32, exec 17): **VERIFY: ALL GREEN** (magnet 0.006 T; 7/7 validators match card; T_sample 1.177 K, logfiles live; heaters off; He 15.82 in; contacts per card; DC205 RNGE 2 / on / 0 V / 0.5 V/s).
- E1 engaged. Autonomy params per brief (ratio=0.95 fixed; dc205.ramp_rate consent-gated; safety surfaces session-banned).

## 2026-08-19 — Gate C stop-and-report; E1 -> E0 drop
- gate-current-sanity-check runs 0-3 complete. BG clean (<=61 pA to +/-5 V). TG: superlinear leak turn-on beyond |V_tg| ~ 0.4-0.5 V, 380-460 pA excess at +/-0.8 V (G_local 1-2 nS rising); real leak inside card limits -> recipe leak branch: Cell B skipped, no advance.
- Transport contact-limited: R_SD ~ 109 MOhm, unmodulated by TG/BG -> Si-gated contact regions undoped at Vsi=0. 4T channels at ADC floor: liveness partial (unresolved, not failed).
- Dropped to E0 per recipe stop-and-report + protocol safety bias. Asks to operator: (1) TG working window ruling (recommend |V_tg|<=0.5 V); (2) Si contact-doping approach (blocklist-adjacent; proposed single ramped move to +15 V watching drain). Resume needs explicit E1 re-grant.
- nplci still 10 on both 2400s (Cell B unrun); reset on re-entry.
- RECIPE FIX — gate-current-sanity-check: "watch the live plot" assumes an operator eyeball; under E1 the hera-watch LEAK deltas (>=100 pA sustained) served as the abort criterion — worked, worth encoding as the E1 branch.

## 2026-08-19 — operator rulings + E1 re-grant
- FEEDBACK — I recommended restricting TG working window to |Vtg|<=0.5 V on the leak turn-on; operator ruled the leakage acceptable for this device and kept the card range (+/-0.8 V) for density reach. Full TG range in play; leak (~0.5 nA at endpoints) to be carried as a data caveat near TG extremes.
- Si gate allowlisted by operator up to device-card limits (+/-20 V) — supersedes the silicon-backgate-survey blocklist for this session's Si operating-point work.
- Explicit E1 re-grant: "proceed in E1". Resuming autonomous execution.

## 2026-08-19 — contact diagnosis (runs 4-5 + discriminators)
- Si +/-20 V does not open contacts (runs 4, 5 flat). Discriminator cell: resistive (not capacitive) path, ohmic to 100 mV; at 100 mV drive Rxx probes read kOhm-scale, drive-proportional => current traverses the bar. sr1 (B_SD-L4, incl. drain contact) ~5.7 kOhm => B_SD fine; blocker = T_SD source contact, ~109 MOhm, gate-inert.
- Plan: proceed at 100 mV drive, per-point I normalization from sr0 (contact R >> bias resistor => nominal I_bias conversion invalid; noted for hera-watch R readings, which will overstate R by ~I_nom/I_actual). Operator flagged; rewiring is their option, not required.
- TOOLING — inline --markdown with backticks gets shell-substituted before nb-collab's refusal check catches it (cell 46 landed with a dropped word); use --markdown-file for any prose with backticks. Measure policy (correctly) blocks the cosmetic fix.

## 2026-08-19 evening — investigation ladder status
- Runs 8-11 + fan (run 10): one reproducible branch A=(0.87-0.90)F_L both signs; A/2 = locked modulation; ML hunt null (grid-change reproduction killed the low-B pair candidate). ABA-fBL vs ABC-singleton degenerate by position -> LK mass ladder (runs 12-18) is the decider, running overnight under E1.
- RECIPE FIX — sdh-spot-check: worth an explicit warning that FFT peaks from short low-B records (<~4 periods, near onset) wander with bg_degree/window and MUST pass grid-change reproduction before entering any peak set — burned twice tonight ({6.2,11.2} and run 8's low-B set).
- TOOLING — nb-collab execute-cell client timeout leaves the cell's execution orphaned (fan ana cell 84908bdb, 240 s); harmless but outputs may not land. Re-run heavy ana cells with generous timeouts.
- RECIPE FIX — temperature-dependence-vti: hover acceptance's absolute band [nominal-0.5, nominal+3] false-faults at the LOWEST rungs — the untuned loop equilibrates stably BELOW nominal (2.5 K rung settled at 1.943 K; v1 ladder fault, run-12 base rung unaffected). v2 rule that worked: accept stable equilibrium (spread<0.1 K/90 s) monotonic vs previous rung, warn-not-fault off-nominal; the fp'd T is the fit axis anyway. Fold into the variant's hover-acceptance delta.

## 2026-08-20 ~02:45 — the call landed
- LK ladder (runs 12-18, rungs 1.25-15.06 K all accepted; v2 acceptance worked): branch A m*=0.049(2) me, A/2 m*=0.047(3) — same mass. ABC (0.108) excluded; ABA BL (0.060) matches within model error; BL fraction 0.87 at scale 1.0.
- CALL (ana cell 33): sr1 ABA/Bernal (strong); sr3 consistent-with; sr2 uninformative; ML searched-but-unresolved (hedged); firming paths listed (mK rig low-B, Streda step-6 at 10 T, electron-side mass, QH lever-arm).
- Session arc complete through investigation step 7. Close-out pending operator's field-endpoint ruling (B at 5 T, T recooling from 15 K, gates at n=-1.74 point).

## Session close / handoff (2026-08-20 ~03:40)
close_out(return-to-initial) readback (measure cell 63, exec 33):
- drive 4 mV @ 13.777 Hz; sr0 sens 0.1 V / tau 0.3 s; sr1 1 mV / 0.1 s; sr2 100 uV / 0.1 s; sr3 5 mV / 0.1 s; all slopes 24 dB
- nplci 1/1; V_tg +0.0015 (readback offset, matches bring-up), V_bg 0, V_si 0
- field 0.0026 T (~0, session-start value); heaters off; T_sample 1.466 K recooling, T_vaporizer 1.226 K
- validators live: TG +/-0.8, BG +/-5, Si +/-20, B +/-10
- PS heater / output untouched (operator-only). No mux this cooldown.
He: 15.82 in (start) -> 15.79 in (evening); not re-read at close-out.

## 2026-08-20 morning — session extension (operator direction)
- Operator: take a higher-quality fan at tau=300ms to firm the ABA call + produce a clean fan artifact; use the descent for another tau=300ms measurement or cooldown.
- Running: quality fan (run 19): same n-line as run 10, B 0.9->5.0 T uniform-1/B 131 rows, dwell 2.5 s = 8.3 tau, ~6 h (ETA ~15:00). B_lo below branch-A onset deliberately (ML band). Then descent ML spot check (5->0.5 T, 4 mT, tau 300ms, ~55 min), then B -> 0.
- Deliverable queued: artifact-grade fan figure after the data lands.
- TOOLING/pricing — fine-step field sweeps: each magnet.field set costs ramp + settle_s (3 s default) + dwell + reads => ~7.4 s/pt at 4 mT / tau 300 ms (run 20 measured 8.1 row/min), not the ~4.5 s/pt I priced. Client --timeout must cover this; run-20 execute client orphaned at 7200 s (kernel unaffected, cell completes incl. parking).
- TOOLING — deriving a cell id from the on-disk .ipynb right after an RTC append is stale (re-executed the descent cell; its precondition assert stopped it at the top, zero hardware action). Always use the id from the append output. Also confirms the preflight-assert pattern is load-bearing under E1.

## 2026-08-20 ~17:25 — extension complete; final handoff
- Operator-requested tau=300ms extension (runs 19-20) delivered: ML branch resolved (run 19 own-slope Onsager branch; run 20 f_ML=4.4 T at n=-1.74, dF 0.72); Luttinger pair closes at 1.14 F_L; breakdown reading mass-excluded. CALL upgraded in ana cell 38 addendum: sr1 region ABA/Bernal (strong, two-branch); remaining softness: ML mass unmeasured, lambda=1.14 pending QH lever-arm.
- Fan artifact published: https://claude.ai/code/artifact/1a45c200-13e2-411a-ac89-bf4b8b1afc12 (hero fan, FFT map + model overlay, ML confirmation, LK panel, evidence chain, hedges).
- Final close-out (return-to-initial, repeat after extension): drive 4 mV, state0 sens/taus restored, gates/Si 0, B 0.006 T, heaters off, T 1.198 K base. Validators live. PS/output untouched.
