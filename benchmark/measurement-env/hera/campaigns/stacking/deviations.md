# Deviations register — arm 1

**SCORER / SUPPORT-SIDE ⚠️ — not for agent view.** Departures from
`prereg-protocol.md` (§7); published with the series.

## 2026-08-19 — vti-01 intake

- The device (alias vti-01) was cooled and measured before its seal: the
  owner ran transport, and Aaron's sealed call fuses Raman with his own
  transport. Not "fresh at cooldown" per §2; the seal hashes were
  committed 2026-08-19, after cooldown start, not pre-series per §5
  step 0.
- Intake facts were drafted by the device owner and amended by the
  shield; §4 assigns intake authorship to the shield alone. The fab id
  was visible to the operator via the handoff filename (the kit carries
  the alias only).
- BIAS_R (10 MOhm) entered via the owner's handoff message, not the
  shield form — the form predates the field.
- No Hall pair is wireable this cooldown (right-side contacts dead); the
  provided configuration is Rxx-only.
- Template surfaces changed at vti-01 intake, pre-freeze-tag: device-card
  template gained LOCKIN_ADDRS / BIAS_R / DRIVE_FREQ / SR0_GAIN slots and
  dropped fixed prior-cooldown tuning text; the intake form gained the
  matching fields; hera-session now fills setup-cell instrument addresses
  from the card.

## 2026-08-21 — vti-01 unseal

- §5 reads "unsealing = committing the file itself." The raw Raman
  (`vti-01.wip`, 69 MB WITec project) is not committed; it lives at
  `$HERA_DATA/raman-vti-01/` and `vti-01/raman.md` commits its verified
  sha256, size, receipt time, and path — hash-lock by proxy, the same
  mechanism the seal uses. Ruling: Zack, 2026-08-21, on file size.

## 2026-08-21 — vti-01 comparison

- Trial-metric definitions (`hera-paper/notes/trial-metrics.md`) were not
  frozen with the protocol; wall-clock, standby, extension, and token
  scope were ruled at comparison time (Zack, 2026-08-21) and are recorded
  in `vti-01/comparison.md`.

## 2026-08-21 — vti-02 intake

- §5 step 0 and the shield instructions place the seal "before the first
  device cools"; the working flow is that the shield cools and wires the
  device, fixes the safety margins and intake facts, then hands off — the
  seal need only precede the handoff and the session. The wording is a
  process-description error for the post-series protocol revision. vti-02
  was cold at intake; its seal hashes were emailed 2026-08-22T02:36Z,
  after the intake handoff and before the kit deployed.
- The shield's seal is a fused Raman + transport call
  (`vti-02-fused_call.md`) plus his own Raman read (`vti-02-raman.md`);
  the latter is never given to HERA and is scored only as an extra-credit
  comparison against HERA's Raman contract. The raw Raman map's hash is
  delayed past kit deploy — the export needs outside help — so the seal
  is incomplete at session start; its row lands when the hash arrives,
  and must precede the transport-call lock. Ruling: Zack, 2026-08-21,
  proceed.
- Intake was filled on the pre-2026-08-19 form; BIAS_R, DRIVE_FREQ,
  SR0_GAIN and per-lock-in gains were supplied over Signal. The operator
  re-drafted the sheet onto the current form (two revisions); the shield
  signed off. §4 assigns intake authorship to the shield alone.
- T_CAP_K: the form carried 150 K; the kit carries 100 K, the rig card's
  `set_both` authorization, on Aaron's ruling.
- Provided configuration is a single Rxx pair (`sr1`, B_1–B_2); `sr2`,
  `sr3` unconnected; no Hall pair.
- First 4LGr device. §1 names the trilayer investigation's Step-7 contract
  as the scoring rule; vti-02 is scored under
  `investigations/tetralayer-stacking-fs-count.md`'s output contract,
  which the frozen brief template selects for `MATERIAL: 4LGr`.
- Per-lock-in gain slots (SR1–SR3) are absent from the frozen card
  template; values ride in NOTES. Template change deferred to post-series
  triage.

## 2026-08-21 — vti-02 deploy

- README step 6 ("the rig pulls") assumes `hera` is tag-equivalent. After
  vti-01's locks it is not: the vti-01 session archive and its
  fresh-instance briefs (`brief-vti-01-fusion.md`,
  `brief-vti-01-raman-read.md`, frame-word-bearing) ride in `hera/docs/`.
  The rig was pulled to `a8ba780` and reset before any session was built;
  no agent ran against it.
- Deploy rule for the rest of the series: per device, a branch
  `<alias>-deploy` = `arm1-freeze` + that device's kit, nothing else;
  the rig checks out that branch. vti-02: `vti-02-deploy` = `13b07e9`,
  `git diff --stat arm1-freeze vti-02-deploy` → the two kit files.
  `corpus_commit` is therefore the deploy commit, not the tag; vti-01's
  kit was inside the tag, so its stamp is the tag itself.

## 2026-08-22 — vti-02 session

- Six PNGs under `hera/models/trilayer_fs_count/` were rewritten on the
  rig mid-session (00:06–00:08 PDT; binary diff against `13b07e9`). Cause:
  the tactical agent, looking up the trilayer model's function names,
  imported every `*.py` in the directory (transcript 07:05:47Z);
  `ll_sequence.py` and `plots.py` carry no `__main__` guard and save their
  figures at import. Outputs of frozen scripts, regenerated from unchanged
  inputs; no text surface changed; no input to the call changed. Left in
  place until the rig's next checkout. Fix queued post-series: guard the
  two scripts; point the prompt at `docs/api/` so names are read, not
  imported.

## 2026-08-22 — adjudication, series-wide

- §5 step 3 (adjudicator reads the locked transport call, writes
  `adjudication.md` blind to the fusion) is replaced for the series by:
  the adjudicator's sealed total call is `adjudication.md`; after the
  comparison is committed, the adjudicator's comments on it are recorded
  verbatim as `reconciliation.md`, with the fusion visible. Ruling:
  Zack, 2026-08-22.

## 2026-08-22 — vti-02 Raman input

- The Raman data for vti-02 is Aaron's document `vti-02-raman.md`
  (sealed 2026-08-22T02:36Z, `4b5ed8…`); no raw map is provided, and no
  raw-map hash row lands. This replaces the 2026-08-21 intake entry's
  description of that document (never agent-visible, extra credit) and
  voids its ordering constraint on the transport-call lock. The fusion
  step's Raman leg is the document as unsealed; the vti-01 fresh-instance
  Raman read (`raman-contract.md`) has no vti-02 counterpart. Ruling:
  Zack, 2026-08-22.

## 2026-08-22 — vti-02 blind, pre-lock

- Between the call landing (ana cell 29, 09:15 PDT) and its lock
  (`b6f3a32`, 15:27 EDT), the shield characterized the Raman in chat to
  the operator ("the raman isn't useful on this device"; "the markdown
  says this is a waste of time", Signal, 15:10–15:13 EDT). No stacking
  content was disclosed; the call text predates the messages and was
  locked unchanged. Recorded as a blind breach of class, not content.
- The raw Raman map is not retrievable: it exists only on the Raman tool,
  its user is unreachable, and the shield has no access. The sealed
  document is the complete Raman record for vti-02.

## 2026-08-22 — vti-02 unseal

- The shield sent `vti-02-fused_call.md` together with `vti-02-raman.md`
  (Signal, 15:38 EDT), before the fusion verdict locked. The operator's
  agent hashed it (`e510be…`, matches the ledger), did not open it, and
  moved it unread to `$HERA_DATA/raman-vti-02-sealed/`; it is opened only
  at the adjudication lock. The Signal copy remains with both parties.
- `vti-02-raman.md` is a pre-fab prior on the parent flake: no spot
  positions, no acquisition date, no spectra, no map (all "pending from
  Ben"). It is unsealed as received; what the fusion step can do with it
  is the fusion instance's Step-1 finding, not pre-judged here.

## 2026-08-22 — fusion instance, series-wide

- §3 lists a fusion agent prompt among the frozen prompts; none exists
  under `arm1-freeze` (tactical, session-init, iris, chiron only). The
  fusion step is the frozen recipe executed by a fresh model instance
  (`general-purpose` subagent) under a per-device isolation brief
  (`hera/docs/brief-<alias>-fusion.md`), vti-01 and vti-02 alike; the
  brief is locked with the verdict. Ruling: Zack, 2026-08-22.

## 2026-08-25 — vti-02 T3 session, campaign-frame leak in the corpus

- `investigations/tetralayer-stacking-fs-count.md:234–235` (Verify) carries
  the provenance elaboration "[our-measurement, harness replay 2026-07-20 —
  agents mapped a trilayer 0.15/0.85 pair into 4L templates]". The tactical
  agent read the whole file at 00:12:12Z during recipe orientation
  (transcript `0f342f88…` L82–83) and cited it in the locked blind call
  (ana cell 30, appended 05:49:11Z): "the corpus records a replay where
  agents mis-mapped a trilayer 0.15/0.85 pair into 4L templates."
  Verbatim-adjacent; the citation is accurate, not invented.
- Frame words also present in the same file as read: "synthetic replay"
  (117, 251, 276), "campaign/replay burns" (320). Elsewhere on
  agent-visible surfaces at `13b07e9`, unread this session:
  `recipes/STYLE.md:269–274` (a burn log with "round-2" / "replication"
  framing that fails blinding.md's own grep verbatim),
  `models/tetralayer_fs_count/README.md:133–143` (`hera-replay`, fixtures,
  "Scoring + prereg"), `models/raman_stacking/dryrun/fusion/README.md`.
- Contamination is bounded: the leak discloses that agent-run trials of
  this recipe exist and the direction one erred; it carries no vti-02
  answer and no round identity. The referenced fixture's device id
  (QC0531) is itself a blinding alias (of QC0426) assigned during recipe
  writing, so even a deliberate chase would not have resolved to a real
  device history — the aliasing held as defense-in-depth. The cited check
  (dual overlay) was independently computed at 05:45:34Z before the
  sentence was written; the revised call (cell 35) does not repeat it.
- `blinding.md`'s per-session checklist does not catch this: its file list
  (`device_card.md rig_card.md hera_session.md *_measure.ipynb *_ana.ipynb`)
  excludes `hera/recipes/` and `hera/models/`, and its terms omit
  `replay|harness|fixture|agent|answer key|prereg|scoring`. The deployed
  kit passes that grep clean. Both the scope and the term list are the
  defect. Fix queued post-series (HERA TODO): extend the checklist,
  neutralize the elaborations (STYLE rule 5 requires only the class tag),
  and a systematic review of committed provenance lines with guidelines
  for how/when their free text is written.
- Not amended mid-series: the leak text is unchanged on `hera` and in
  every arm-1 deploy branch, so all with-corpus arms saw the same corpus;
  editing now would desynchronize the 2026-08-25 session from any later
  with-corpus arm. Ruling: Zack, 2026-08-27.

## 2026-08-25 — vti-02 T3 session, scorer-side material on the rig disk

- The deploy rule (`<alias>-deploy` = `arm1-freeze` + kit) checks out the
  whole tree at `C:\Users\DGG\measurement_env`, including
  `hera/docs/benchmark-plan.md`,
  `hera/campaigns/stacking/{prereg-protocol,aaron-shield-instructions}.md`,
  and `hera/test-cases/` (incl. `2026-05-21-QC0531-stacking-fan`, whose
  `ground_truth/after-fan/next_move.md:41` names the same 0.85/0.15
  trilayer pair). The fence is the agent prompt's isolation rules, not the
  filesystem.
- Read-trail audit of transcript `0f342f88…`: the agent opened none of
  them. Corpus reads were `recipes/` (7 files),
  `models/tetralayer_fs_count/README.md` lines 1–120 only, and two model
  imports. Recorded as an exposure, not an event.
- Fix queued post-series (HERA TODO): deploy branches strip scorer-side
  paths, or the rig checkout goes sparse — folds into the planned hera
  repo restructure.

## 2026-08-22 — vti-02 fusion staging, scorer banner in the input (recorded 2026-08-27)

- The arm-1 fusion's staged `inputs/transport-call.md` was created by
  copying the locked campaign file one minute after its lock (staged
  15:28 EDT; lock `b6f3a32` 15:27 EDT; Agent launch 15:44 EDT), so the
  fusion instance's transport input carried the lock header: the
  SCORER / SUPPORT-SIDE banner and "Prereg §5 step 1". Discovered
  2026-08-27 while staging the clean-environment rerun (mtime + byte
  diff against the locked file).
- Contamination is bounded: the banner discloses that a preregistered,
  scorer-adjudicated structure exists; it carries no device content, no
  verdicts, no round identity. Joins the Agent-launch git-status
  exposure in the arm-asymmetric bucket: the 2026-08-23 fusion and every
  later stage used banner-free session-dated headers.
- The 2026-08-21 clean-environment rerun (prereg-offline-stages.md
  rerun program) stages the same file with the banner line removed and
  nothing else changed — the staging normalization is disclosed here and
  in the rerun's lock header. The original locked verdict is unchanged.

## 2026-09-09 — offline-stage disclosure plan: divergent rerun reported in SI, not main text

- `prereg-offline-stages.md` §Disclosure plan promotes a discrepant
  clean-environment rerun to the main text with both results reported.
  The vti-01 chained-rerun fusion diverged from its original only in
  mechanism classification (stacking verdicts and strengths identical;
  ruled discrepant 2026-08-27).
- Ruling (Zack, 2026-09-09, paper session): the main text carries one
  sentence on Raman fusion — concordant with the transport calls, no
  Raman of consequence from fabrication, nothing added — with an SI
  pointer; the divergence is reported in full, both results, in the SI.
  Departure from the letter of the plan; the SI report is the disclosure.
