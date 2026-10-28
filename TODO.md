# TODO before the public flip

Scope of this repo: the corpus, the agent prompts, the tools, the session
archives, the grading data, and the code that computes the metrics. Nothing
else. Design notes, proposals, backlogs for other rigs and dev specs are
chopped by `CHOP_PATHS` in `tools/build_snapshot.sh`; the fix log
(`hera/docs/triage-changelog.md`, `triage-scoreboard.md`, `eng-backlog.md`),
the session briefs and the operator's live-session logs stay because they are
inputs to or records of the sessions.

This repo is private until the paper is out. Publishing method:

1. Work the items below on the private repo; ordinary commits are fine here.
2. Before the flip, rewrite history to a **single commit** (`git checkout --orphan`, commit, `git push --force origin master`) so no interim decisions, redactions or this file survive in history. Rerun `tools/build_snapshot.sh` first so `MANIFEST.md` and `CHECKSUMS.sha256` match the tree.
3. Delete this file in that commit; set the license files; fill in the citation.
4. Flip the repo to public. `hera-paper/main.tex` Data availability and Code availability already link `https://github.com/sharpelab/hera-paper-data`; the SDR link there is still `xxx`.
5. Regenerate the deposit (`~/sharpelab/hera-paper-data-deposit/`) from the final tree, upload to the Stanford Digital Repository, replace `xxx` with the DOI.

Findings below come from the three-part exposure review of the built snapshot (2026-09-15), filtered to what is still in the tree. Paths are relative to this directory. After a ruling: add paths to `DROP_PATHS_PENDING` or the `REDACT` block in `tools/build_snapshot.sh`, rerun it, re-check `git apply --check` on every corpus patch, commit. Never hand-edit the content directories.

## 0. Licensing

- [x] `measurement-env/lib/measureme` is GPL-3.0, chosen by its original author Joe Finney (`spxtr`), not the lab; relicensing would need his consent plus Praveen Sriram's. Resolved without relicensing: the vendored copy now equals the public commit tagged `hera-paper-freeze` on `sharpelab/measureme@sharpelab` (recorded in `MANIFEST.md` and `README.md`); our own code goes MIT, which is GPL-compatible, and the README says which license covers what. Nothing changes for users of measureme `main`.
- [ ] Add `LICENSE` (MIT for the code we wrote) and a data license (CC-BY-4.0 is the SDR default).
- [ ] Raman validation figures under `measurement-env/hera/models/raman_stacking/` derive from Zenodo 10931524 (CC-BY-SA 4.0): add the attribution line.
- [ ] `measurement-env/src/hera/models.py` lifts its schema from Nathan's measure4me: add attribution or remove the reference.

## 1. Consent from people who are not authors

- [ ] **Isaac Zheng** (zf1 / b1c2 owner). `sessions/zf1/` (six sessions and the 2026-06-25 reference session) is his device's superconductivity, quantitative in `2026-06-23-zf1-session-full/POSTMORTEM.md`; handle `izheng` in every zf1 `device_card.md` and `measurement-env/hera/templates/zf1/device_card.md`; named as the safety-envelope source in 3 scratch files, 2 notebooks and `session_notes.md`; 4 `measurement-env/hera/crops/**/isaac-*.md`; `measurement-env/hera/test-cases/2026-05-06-b1c2-sc-characterization/` (unpublished I_c dome numbers). Ask. Regardless: `izheng` / "isaac's" → "the device owner's" outside the transcripts.
- [ ] **Qingrui** (QC0426 grower/owner). Named as source of ranges in `sessions/qc0426/2026-06-10-*/20260610_measure.ipynb` and cards; fabrication record in `sessions/qc0426/2026-07-25-QC0426-prefab-raman/` and `hera-data/raman-qc0426/` (GDS, WITec projects, chip photos) with his private stacks path in that README; the T7 contact killed on 2026-06-16 (`session_notes.md`); schedule line in `2026-06-10-*/hera_session.md`; `measurement-env/hera/templates/QC0426/reference/baseline_*` from his prior campaign; `measurement-env/hera/docs/vti/2026-06-12-round2-prep-log.md` names two other users' devices (A25_041, NF03A2). Ask, and tell him about T7. Regardless: redact the private path, the schedule line, and the two device lines.
- [ ] **Jordan** (vti-01 owner + fabricator; Pass B second rater). `OWNER: Jordan` in `campaigns/stacking/vti-01/intake-facts.md`, `sessions/vti-01/*/device_card.md`, `measurement-env/hera/templates/vti-01/device_card.md`; "fabricated by Jordan" + wiki URL carrying the real device slug in `campaigns/stacking/vti-01/adjudication.md`; real device name `JM_R_S_4` in `campaigns/stacking/raman-hashes.md`; `grading/passb/RATER-JORDAN.md`, `RATER-JORDAN-RESULT.md` (κ 0.22). Ask about the device. Anonymize the rater to "rater B", or drop the result file. Drop the OWNER lines.
- [ ] **Sandesh Kalantre** (Pass A second rater). `grading/raters/sandesh/` (pass in flight, no export yet), `grading/PREREG.md`. Anonymize the rater; hold `grading/` until his export lands (§3).
- [ ] **Bingcheng Suo** (VTI rig owner). Verbatim Slack with timestamps in `sessions/qc0426/2026-06-10-*/transcripts/*.jsonl` and `metrics/messages/qc0426-r1.csv`; the "we don't need the bingcheng compliant ladder, aaron has approved the non compliant version" line (same two files); his warm-up procedure in the 06-10 notebook; `measurement-env/hera/crops/**/bingcheng-*` (NF02B1 sweep code and a physics narrative); named idioms in `measurement-env/hera/recipes/measurements/*.md`; `measurement-env/hera/docs/eng-backlog.md` mentions CF01B1. Ask about the Slack quote. Drop the crops; genericize the idioms; redact the name in the csv; leave the transcript intact unless he objects.
- [ ] **Ben** (vti-02 fabricator). "fabricated by Ben", "pending from Ben" in `campaigns/stacking/vti-02/{adjudication,raman}.md`; internal flake-DB URL in `raman.md`. Redact name and URL.
- [ ] **Other lab members**: account rosters in two transcript tool results (`sessions/zf1/2026-06-24-*`, `sessions/vti-02/2026-08-22-*`). Redact the two roster lines.

## 2. Aaron's own devices and words

- [ ] RPL10 / RPL19 feed the in-prep chiral-superconductor paper and are still in the tree as replay fixtures (`measurement-env/hera/test-cases/2024-12-07-RPL10-*`, `2024-12-30-RPL10-*`, `2025-11-03-RPL19-*`, `2026-01-24-RPL19-*`, `2026-02-17-RPL19-*`; the stacking fixture lists its own leak terms "chiral", "cCSC", "quarter-metal"), 18 `hera/crops/**/aaron-RPL_*` excerpts, five real RPL19 figures in `src/hera/assets/exemplar_RPL19_18/`, thicknesses in `src/hera/assets/device_cards.json`, a copy of the private `rmg19_quantumoscillations` analysis in `hera/models/trilayer_fs_count/rmg-fft-snapshot/`, `hera/test-cases/EXTRACT-BRIEF.md` (names the private source tree), and ~1,600 textual mentions quoted from the corpus into 23 of 36 transcripts. Recommend: drop fixtures, crops, assets, snapshot, EXTRACT-BRIEF from the tree (paths ready to paste below); leave transcripts intact and say in the README that recipes cite earlier lab devices by name. Dropping `src/hera/assets` breaks `tests/hera` and the classifier demo.

```
hera/test-cases/2024-12-07-RPL10-first-characterization/
hera/test-cases/2024-12-30-RPL10-qo-discovery/
hera/test-cases/2025-11-03-RPL19-sc-dome-fraunhofer/
hera/test-cases/2026-01-24-RPL19-qo-effmass/
hera/test-cases/2026-02-17-RPL19-nd-map-resolution/
hera/test-cases/2026-02-17-RPL19-stacking-fan/
hera/test-cases/2026-05-06-b1c2-sc-characterization/   # unless Isaac consents
hera/test-cases/EXTRACT-BRIEF.md
hera/test-cases/2026-06-19-QC0426-stacking/SESSION-HANDOFF.md
hera/test-cases/2026-06-19-QC0426-stacking/VERIFICATION-PLAN.md
hera/crops/
hera/models/trilayer_fs_count/rmg-fft-snapshot/
src/hera/assets/exemplar_RPL19_18/
```

- [ ] Candid quotes attributed to Aaron, default keep, paraphrase the two profanities: "look like shit" (`sessions/qc0426/2026-07-14-QC0426-session-2-full/` transcript + `session_notes.md`); "Aaron OVERRODE my B7-death safety flag" (`sessions/qc0426/2026-06-16-*/session_notes.md`, `hera_scratch/aaron_snake.py`); `AS:` critiques in `sessions/zf1/2026-06-23-zf1-session-full/wiki_notes.md`; grading remarks in `grading/dossiers/notes.jsonl` and `grading/scores/*` ("terrible job", "absolute garbage", "ludicrous"); raw chat in `campaigns/stacking/vti-01/reconciliation.md`; Signal quotes in `campaigns/stacking/deviations.md`; "world-class physics expert, moderate software" in `measurement-env/hera/docs/vti/2026-06-16-live-session-log.md`.
- [ ] `campaigns/stacking/aaron-shield-instructions.md` is addressed to Aaron in the second person; prereg §6 commits to publishing it. Retitle and reframe as the expert-shielding protocol with his approval.
- [x] `td-01` = RMG01 (a pre-lock rehearsal of the kit on the toploader, not in the paper): its seal row and deviations mention are redacted from every copy of `campaigns/stacking/` by `tools/build_snapshot.sh` (2026-10-26).

## 3. Blinding and pre-registration

Paper-wording issues as much as file issues; the files are honest.

- [ ] `sessions/vti-02/2026-08-22-vti-02-session/transcripts/*.jsonl` lines 17/28/30: operator queued "quick override, we will be rerunning the vti-02 campaign, go for that". Keep; the paper's blinding claim for the replication session must acknowledge it.
- [ ] `sessions/zf1/2026-06-20-*` transcript: operator told the agent "you are wrong (STRONG). I know that is a superconductor". Keep; frame as prior knowledge injected.
- [ ] `sessions/qc0426/2026-06-14-*/artifacts/device_card.md` headed "round 2 … replication from a cooled start" (agent-visible). Keep; do not claim frame-blindness for that session.
- [ ] `sessions/vti-02/2026-08-25-*/hera_scratch/md_verdict.md` cites "the corpus records a replay where agents mis-mapped…": the replay benchmark fed a live blinded session via the corpus. Disclose in Methods.
- [ ] `grading/dossiers/runs.csv` + `grading/blind-map.yaml` give the pooled-card → run → device/model/corpus chain that `grading/PREREG.md` confines to the gitignored secret map. Expected post-freeze, but Sandesh's Pass A export is pending: hold `grading/` until it lands.
- [ ] `metrics/runs.yaml` has `corpus_commit` empty for every run; back-fill from `corpus-variants/corpus-timeline.md` (inferred for June, stamped from July 17).
- [ ] Read keys (`hera/campaigns/stacking/read-keys/`, `hera-data/read-keys-review/`) are excluded: replay answer keys, not used by the paper, still under expert review. Revisit for the replay paper.

## 4. Remaining clean-up

- [ ] Rewrite the "SCORER / SUPPORT-SIDE ⚠️ — not for agent view" banner on 34 campaign files as "unblinded scorer-side artifact, never an agent input".
- [ ] Replace `wiki.sharpelab.science/doc/<slug>` links (5 session notes, `hera/chiron.md`, `hera/docs/vti/2026-06-17-live-session-log.md`) with "lab wiki (internal)".
- [ ] `measurement-env/hera/docs/vti/2026-06-16-live-session-log.md` proposes a people roster with capability ratings; `2026-06-12-round2-prep-log.md` names two other users' devices. Trim.
- [ ] Trim the "Working with Zack" section of `measurement-env/CLAUDE.md` and the private-repo clone URL in `measurement-env/README.md`.
- [ ] Fix the hardcoded absolute path in `measurement-env/tests/hera/conftest.py`; rewrite `sys.path.insert(0, "/home/zack/...")` in 7 scratch scripts under `sessions/qc0426/2026-07-{17,25}-*`.
- [ ] `.claude/agent-memory/chiron/` is kept as the triage agent's working memory; `rounds.md` has "Zack corrected ~5× this round"-style lines. Read once and decide keep/curate.

## 5. Transcript hygiene (alters the record; recommend leaving as is)

Transcripts are published byte-intact apart from the §7 substitutions. Known noise: 152 verbatim `/loop` prompt turns across four qc0426 sessions, two Anthropic skill prompts in the vti-01 transcript, one "Context Usage" turn listing the operator's connected Gmail/Calendar/Drive tools (`sessions/qc0426/2026-06-10-*`), and the ten `hera-data/*-launch.json` payloads recording the operator's personal Claude Code environment.

- [ ] Decide: drop the launch JSONs (content restated in each stage's `provenance.md`/`result.md`) or keep one exemplar per stage.
- [ ] Decide whether the "Context Usage" turn and the two roster lines are redacted (recommend yes for those three; nothing else).

## 6. Gaps the availability statements assume

- [ ] Figure-generation code for the fan and zf1 PDFs (`fig-main-fan.pdf`, the zf1 figures) is in no repo; it was produced in a paper-side Claude session ("calc_nD + cal_run5.json"). The paper no longer promises it, so this is optional: regenerate into `hera-paper/figures/` and add a `figures/` directory here if wanted. Fig. 5's script is in (`benchmark/fig5_panels.py`).
- [ ] The paper's Data availability promises "the sealed documents": Aaron's sealed transport calls for vti-01 and vti-02 are not in the snapshot yet (only their hashes, in `campaigns/stacking/raman-hashes.md`). Get the sealed files from Aaron, add them under `campaigns/stacking/<device>/sealed/`, verify against the hashes. The zf1 reference session is a separate decision.
- [ ] Benchmark scope rulings. In: the 41 runs of record (300 episodes, 1.7 GB pruned), the harness and grader at `58d02e64`, the scoring directory minus its boards. Out, pending a ruling: the development episodes (`replay/runs/vti02-fan-design-*`, `vti02-pre-fan-*`, `vti02-probe-first-*`; the 27 development fans the pre-registration says the grader was tuned on, ~1 GB raw), the 2026-10-03 medium-effort arm (12 runs, `vti02-fan-scoring-v2/effort-medium/`; exploratory, not in the paper), and N.B.'s earlier frontier-sampling pipeline (`hera/evaluations/`, `hera/experiments/` at the benchmark commit; not reported, but N.B. is credited with building the benchmark, so ask him). `hera-data/test-cases/` (the QC0426 replay fixtures' runs, 989 MB) stays out: the corpus-defect replays are a Methods disclosure, not a result.
- [ ] Codex episodes: `codex-home/sessions/` rollouts are the Codex CLI's own record; no `auth.json` is present in any run (checked), and the harness logs already carry `ANTHROPIC_API_KEY=<redacted>`. The Codex state databases, skills and shell snapshots are dropped.
- [ ] Data availability names sessions, pre-registrations, grading and sealed documents but not the benchmark episodes and grades; propose a clause to Aaron (paper-side, main text rules).
- [ ] Model ids in the corpus (`claude-fable-5[1m]`, `claude-opus-4-8[1m]`, `claude-opus-4-7`, `claude-sonnet-4-6`) and one negative capability note: confirm nothing is under NDA.
- [ ] Citation block in `README.md` once the DOI exists.

## 7. Applied by the build script

Dropped: `hera-data/hera-session-transcripts/` (live Jupyter token, other users' notebook paths), `hera-data/tetralayer-rpl19-validation/` (re-analysis of another group's device that de-anonymizes their published alias), `grading/raters/sandesh/slack-draft.md`, `metrics/drafts/` and `metrics/mock-report-qc0426-r3.md`, video-frame `.npz` intermediates, vendor calibration certificate PDFs, third-party paper and manual PDFs, the `ncomms14518` figure crop, `.claude/` runtime locks in session archives, `.transcripts/` duplicates, dangling fixture symlinks, and everything in `CHOP_PATHS`.

Substituted in place (tree and corpus patches alike): Jupyter server tokens, two Slack member ids, two personal Gmail addresses and two mail thread ids, a work email used as a template example, the tailnet id, the wiki credentials-page link, the on-disk location of an InfluxDB token.

Not touched: instrument LAN addresses (private range, part of the rig cards), rig service-account paths, the InfluxDB endpoint hostname, ntfy handles `ZACKG`/`ASHARPE`, instrument serials in qcodes snapshots.
