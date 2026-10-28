#!/usr/bin/env bash
# Build the HERA paper snapshot from the lab's working repos and data store.
#
# Re-runnable: wipes and regenerates every content directory, leaves README.md,
# TODO.md, tools/ and .git alone. Every directory it writes is listed in MANIFEST.md with
# the source path and commit it came from.
set -euo pipefail

ME=/home/zack/sharpelab/measurement-env       # code + corpus + session archives
HQ=/home/zack/sharpelab/hera-quality          # expert grading (Pass A / Pass B)
HP=/home/zack/sharpelab/hera-paper            # paper repo (analysis/ only is taken)
HD=/data/sharpelab/hera-data                  # Raman evidence, agent stage outputs
OUT=${OUT:-/home/zack/sharpelab/hera-paper-data}

# The frozen corpus the blinded trial ran on: arm1-freeze (d8e1337) + the vti-02
# kit (brief + device card). Sessions on vti-02 stamped this commit.
CODE_COMMIT=13b07e9898b973aa34066587c27ac61db13c26cc
SESS_REF=hera                                  # session archives are read from this branch tip
SESS_COMMIT=$(git -C "$ME" rev-parse "$SESS_REF")
HQ_COMMIT=$(git -C "$HQ" rev-parse HEAD)
HP_COMMIT=$(git -C "$HP" rev-parse HEAD)
# The replay benchmark (vti-02 fan-design matrix). BENCH_COMMIT is the commit
# that declared the pre-registration (hera/campaigns/vti02-fan-design/prereg.md,
# 2026-09-29); the harness, grader, case files, briefs and masks are read from it.
# The runs of record are the run directories the analysis of record lists.
BENCH_COMMIT=58d02e641961fd33ae744eb6e271fea08ead7a92
BENCH_SCORING=$HD/vti02-fan-scoring-v2
BENCH_ANALYSIS=$BENCH_SCORING/final/analysis.json
BENCH_FRONTIER=vti02-fan-request-0822

# Session archives in scope, grouped by device. Names are the archive dir names
# under measurement-env/hera/docs/notes/ (kept verbatim so runs.yaml resolves).
QC0426=(
  2026-06-10-QC0426-session 2026-06-14-QC0426-session 2026-06-16-QC0426-session
  2026-06-17-QC0426-session 2026-06-19-QC0426-session 2026-06-19-QC0426-session-2
  2026-06-19-QC0426-session-3 2026-06-20-QC0426-session 2026-06-21-QC0426-session
  2026-06-21-QC0426-session-2
  2026-07-14-QC0426-session 2026-07-14-QC0426-session-2-full 2026-07-16-QC0426-session-3
  2026-07-17-QC0426-capstone-2 2026-07-17-QC0426-raman-fusion
  2026-07-18-QC0426-session-full 2026-07-25-QC0426-prefab-raman
)
ZF1=(
  2026-06-20-zf1-session 2026-06-21-zf1-session 2026-06-22-zf1-session
  2026-06-23-zf1-session-full 2026-06-24-zf1-session 2026-06-25-zf1-session
  2026-06-25-zf1-reference-session
)
VTI01=(2026-08-18-vti-01-session)
VTI02=(
  2026-08-21-vti-02-session 2026-08-22-vti-02-session 2026-08-23-vti-02-session
  2026-08-24-vti-02-session 2026-08-25-vti-02-session
)

# hera-data directories to mirror (name-for-name). `inputs/` subdirs are copies
# of the raw Raman files already under raman-qc0426 / raman-vti-01 and are
# dropped; so are the multi-GB video intermediates of the brief test.
HERA_DATA_DIRS=(
  raman-qc0426 raman-qc0426-fusion-2026-07-25 raman-qc0426-fusion-brieftest-2026-08-12
  raman-qc0426-registration
  raman-vti-01 raman-vti-01-read raman-vti-01-read-20260824 raman-vti-01-fusion
  raman-vti-01-fusion-20260824 raman-vti-01-20260818-read raman-vti-01-20260818-fusion
  raman-vti-01-20260818-fusion-b
  raman-vti-02-sealed raman-vti-02-fusion raman-vti-02-20260821-fusion
  raman-vti-02-20260822-fusion raman-vti-02-20260823-fusion raman-vti-02-20260823-fusion-run1
  raman-vti-02-20260824-fusion raman-vti-02-20260825-fusion
  tetralayer-synth-validation
)
# Not mirrored: read-keys-review (replay answer keys, not used by the paper),
# tetralayer-replay-3b (replay pilot notes).
# Not mirrored: hera-session-transcripts (raw bring-up transcripts carrying a
# live Jupyter token and other users' notebook paths), tetralayer-rpl19-validation
# (re-analysis of another group's device from the private lab mirror).

# Paths inside the frozen measurement-env tree that are not published. Used both
# to prune the extracted tree and to exclude the same paths from every corpus
# patch, so the patches still apply to the pruned tree.
DROP_PATHS=(
  hera/docs/notes                              # session archives: published under sessions/ instead
  hera/docs/papers                             # third-party paper PDFs
  docs/manuals                                 # third-party instrument manuals
  hera/docs/vti/refs/ncomms14518.pdf           # third-party paper PDF
  hera/docs/vti/refs/ncomms14518-reference-fan.png  # figure panel extracted from that paper
  hera/vti/cernox-cal/X225149/X225149.pdf      # vendor calibration certificates (the curve data stays)
  hera/vti/cernox-cal/X225150/X225150.pdf
  ZACK-TODO.md                                 # dev residue
  REVIEW_NOTES_2026-03-03.md                   # dev residue
  hera/test-cases                              # replay fixtures: excluded from patches only (3 MB of data churn); the tree keeps them
)
# Scope policy: the snapshot is the corpus, the agent prompts, the tools, the
# session archives, the grading and the metrics code. Design notes, proposals,
# backlogs of other rigs, literature surveys, dev specs and material for devices
# outside the paper are chopped here. Session briefs, the fix log
# (triage-changelog / scoreboard / eng-backlog) and the operator's live-session
# logs stay: they are inputs to or records of the sessions.
CHOP_PATHS=(
  FEEDBACK_SPEC.md REPLAY-SPEC.md TODO.md fan_smear_scratch hera/scratch
  docs/plans docs/dependabot-triage-2026-06.md docs/launcher-library-extraction.md
  docs/nb-collab-stdin-proposal.md docs/rotator-servo.md docs/rotator-servo-feedback.md
  docs/rotator-servo-example.py
  hera/nb-collab/PLAN.md hera/nb-collab/PLAN-edit-execute.md hera/nb-collab/PERF-optimization.md
  hera/nb-collab/sync-resolution-spec.md
  hera/docs/aaron-handoff.md hera/docs/benchmark-plan.md hera/docs/benchmark-rubrics.md
  hera/docs/brief-qswitch-transient-2026-06-18.md
  hera/docs/campaign-readiness-2504.06972.md hera/docs/campaign-readiness-2504.06972-workstream.md
  hera/docs/campaign-readiness-qswitch-transient.md hera/docs/classifier-build-plan.md
  hera/docs/hera-utilization-design.md hera/docs/hera-v0.md hera/docs/iris-mining-followups.md
  hera/docs/iris hera/docs/notebook-indexes hera/docs/phase-b-proposal.md
  hera/docs/pink-template-notes.md hera/docs/preflight-QC0426.md hera/docs/preflight-zf1.md
  hera/docs/prior-art-evaluation.md hera/docs/replay-variance.md
  hera/docs/sharpelab-nb-extension-proposal.md hera/docs/sharpelab-nb-lift-open-questions.md
  hera/docs/sharpelab-nb-reference.md hera/docs/stacking-extraction-survey.md
  hera/docs/tetralayer-stacking-extraction-survey.md hera/docs/strategic-layer.md
  hera/docs/vti/refs hera/docs/vti/photos hera/docs/vti/vision hera/docs/vti/vti-rig-backlog.md
  hera/docs/vti/preflight-runbook.md hera/docs/vti/round2-preflight.md hera/docs/vti/round3-preflight.md
  hera/docs/vti/2026-06-18-qswitch-live-session-log.md
  hera/rig-cards/pink.md
  .claude/agent-memory/subtask_agent
)
# Chopped like CHOP_PATHS but not named in MANIFEST.md: td-01 is redacted from the deposit
# (see the td-01 block below), so the manifest must not list its paths either.
CHOP_PATHS_SILENT=(
  hera/docs/brief-td-01.md hera/templates/td-01
)
# Pending exposure decisions (see TODO.md): add paths here to drop them.
DROP_PATHS_PENDING=(
)
# Out of scope at the benchmark commit, on top of DROP_PATHS and CHOP_PATHS.
BENCH_CHOP_PATHS=(
  hera/evaluations                       # earlier frontier-sampling pipeline and its results; not reported
  hera/experiments                       # ablation experiment definitions outside the paper
  hera/docs/feldman-set                  # separate project
  hera/docs/replay-fresh-start-plan.md   # dev plan
)
HERA_DATA_FILES=(
  fusion-run2-launch.json vti01-fusion-run.json vti01-raman-run.json
  raman-vti-01-20260818-fusion-b-launch.json raman-vti-01-20260818-fusion-launch.json
  raman-vti-01-20260818-read-launch.json raman-vti-02-20260821-fusion-launch.json
  raman-vti-02-20260822-fusion-launch.json raman-vti-02-20260824-fusion-launch.json
  raman-vti-02-20260825-fusion-launch.json
)

cd "$OUT"
rm -rf measurement-env corpus-variants sessions campaigns grading metrics hera-data benchmark MANIFEST.md CHECKSUMS.sha256
MAN=MANIFEST.md
{
  echo "# MANIFEST"
  echo
  echo "Generated $(date -u +%Y-%m-%dT%H:%MZ) by tools/build_snapshot.sh. Source path, source commit, and what was dropped, per directory."
  echo
  echo "| snapshot path | source | commit | notes |"
  echo "|---|---|---|---|"
} > $MAN

# ---------------------------------------------------------------- code + corpus
mkdir -p measurement-env
git -C "$ME" archive "$CODE_COMMIT" | tar -x -C measurement-env
for p in "${DROP_PATHS[@]}" "${CHOP_PATHS[@]}" "${CHOP_PATHS_SILENT[@]}" "${DROP_PATHS_PENDING[@]}"; do
  [ "$p" = hera/test-cases ] && continue
  rm -rf "measurement-env/$p"
done
# Replay fixtures symlink their notebooks/data into hera/docs/notes, which now
# lives under sessions/; the links dangle here, so they go (the targets are the
# session archives of the same date).
find measurement-env -xtype l -delete
echo "| measurement-env/lib/measureme | vendored copy of https://github.com/sharpelab/measureme, branch sharpelab | 7bb45403c7314d7e5a8d96748624e46ae739af8e (tag hera-paper-freeze) | GPL-3.0; byte-identical to that commit apart from uv.lock |" >> $MAN
echo "| measurement-env/lib/measurebot | vendored copy of https://github.com/sharpelab/measurebot, branch main | 0810c0e | MIT; identical to that commit apart from uv.lock and the Slack-id example redacted in alerts.py |" >> $MAN
echo "| measurement-env/ | ~/sharpelab/measurement-env (git archive) | $CODE_COMMIT (vti-02-deploy = arm1-freeze + vti-02 kit) | dropped: $(printf '%s, ' "${DROP_PATHS[@]}" "${DROP_PATHS_PENDING[@]}" | sed 's/hera\/test-cases, //; s/, $//') (session archives are under sessions/; the rest are third-party PDFs, a figure crop, vendor certificates, dev residue). Chopped as out of scope (design notes, proposals, other rigs, dev specs): $(printf '%s, ' "${CHOP_PATHS[@]}" | sed 's/, $//') |" >> $MAN

# ---------------------------------------------------------------- corpus variants
# Every other corpus commit a session ran on, as a patch against the frozen
# tree. Session data, third-party PDFs and replay fixtures are excluded from the
# patches; the timeline file records which session used which commit.
mkdir -p corpus-variants
PATCH_PATHSPEC=(.)
for p in "${DROP_PATHS[@]}" "${CHOP_PATHS[@]}" "${CHOP_PATHS_SILENT[@]}" "${DROP_PATHS_PENDING[@]}"; do PATCH_PATHSPEC+=(":!$p"); done
emit_patch() {  # label commit
  local label=$1 c=$2 short
  short=$(git -C "$ME" rev-parse --short=7 "$c")
  git -C "$ME" -c core.abbrev=7 diff --binary "$CODE_COMMIT" "$c" -- "${PATCH_PATHSPEC[@]}" > "corpus-variants/$label-$short.patch"
  git -C "$ME" diff --stat=120 "$CODE_COMMIT" "$c" -- "${PATCH_PATHSPEC[@]}" > "corpus-variants/$label-$short.diffstat"
}
TL=corpus-variants/corpus-timeline.md
{
  echo "# Corpus commit per session"
  echo
  echo "The frozen tree in measurement-env/ is \`$CODE_COMMIT\`. Each patch in this directory turns that tree into the corpus a session actually ran on (apply with \`git apply\` or \`patch -p1\` from inside measurement-env/). Patches exclude session archives, third-party PDFs and the replay fixture tree (hera/test-cases)."
  echo
  echo "Sessions from 2026-07-17 onward stamp their corpus commit in \`corpus_provenance.json\`. Earlier sessions did not; for those the commit is the last commit on the \`hera\` branch before the session transcript's first timestamp, which is the best available reconstruction of what the rig checkout could have been, not a record of what it was."
  echo
  echo "| session | corpus commit | stamped? | patch |"
  echo "|---|---|---|---|"
} > $TL
declare -A SEEN
for d in "${QC0426[@]}" "${ZF1[@]}" "${VTI01[@]}" "${VTI02[@]}"; do
  src="$ME/hera/docs/notes/$d"
  if [ -f "$src/corpus_provenance.json" ]; then
    c=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['corpus_commit'])" "$src/corpus_provenance.json")
    stamped=yes
  else
    ts=$(ls "$src"/transcripts/*.jsonl 2>/dev/null | head -1 | xargs -r head -c 200000 | grep -o '"timestamp":"[^"]*"' | head -1 | cut -d'"' -f4 || true)
    if [ -n "$ts" ]; then
      stamped="no (inferred from transcript start $ts)"
    else
      ts=$(date -u -d "$(echo "$d" | cut -c1-10) 12:00 -0700" +%Y-%m-%dT%H:%M:%SZ)
      stamped="no (no transcript; inferred from the archive date, noon PDT)"
    fi
    c=$(git -C "$ME" log -1 --format=%H --until="$ts" "$SESS_REF" --)
  fi
  short=$(git -C "$ME" rev-parse --short=7 "$c")
  if [ "$c" = "$CODE_COMMIT" ]; then
    patch="(frozen tree)"
  else
    label="corpus"; patch="corpus-$short.patch"
    if [ -z "${SEEN[$c]:-}" ]; then emit_patch "$label" "$c"; SEEN[$c]=1; fi
  fi
  echo "| $d | \`$short\` | $stamped | $patch |" >> $TL
done
echo "| corpus-variants/ | git diff $CODE_COMMIT..<commit> (measurement-env) | per session, see corpus-timeline.md | one patch per distinct corpus commit |" >> $MAN

# ---------------------------------------------------------------- sessions
take_sessions() {  # group dir...
  local group=$1; shift
  mkdir -p "sessions/$group"
  for d in "$@"; do
    git -C "$ME" archive "$SESS_COMMIT" "hera/docs/notes/$d" | tar -x -C "sessions/$group" --strip-components=3
    rm -rf "sessions/$group/$d/.transcripts"     # byte-identical hidden duplicate of transcripts/
    rm -rf "sessions/$group/$d/.claude"          # Claude Code runtime lock files
  done
}
take_sessions qc0426 "${QC0426[@]}"
take_sessions zf1    "${ZF1[@]}"
take_sessions vti-01 "${VTI01[@]}"
take_sessions vti-02 "${VTI02[@]}"
# The model column counts the measurement agent's transcript only. The
# hera-session setup agent runs from the shared measurement_env checkout and
# its jsonl is archived next to the session's in several archives; the two are
# told apart by the cwd of their entries, as metrics/tool does with the
# manifest's rig_session_dir.
python3 - "$TL" sessions/INDEX.md <<'EOF'
import glob, json, os, re, sys, collections
tl, out = sys.argv[1], sys.argv[2]
commits = {}
for line in open(tl, encoding="utf-8"):
    cells = [c.strip() for c in line.split("|")]
    if len(cells) > 3 and cells[2].startswith("`"):
        commits[cells[1]] = cells[2].strip("`")
rows = []
for g in ("qc0426", "zf1", "vti-01", "vti-02"):
    for p in sorted(glob.glob(f"sessions/{g}/*/"), key=lambda p: os.path.basename(p.rstrip("/"))):
        d = os.path.basename(p.rstrip("/"))
        n_session = n_setup = 0
        models = collections.Counter()
        setup_models = collections.Counter()
        for f in sorted(glob.glob(os.path.join(p, "transcripts", "*.jsonl"))):
            cwds = collections.Counter()
            seen = collections.Counter()
            for line in open(f, encoding="utf-8", errors="replace"):
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if e.get("cwd"):
                    cwds[os.path.basename(e["cwd"].replace("\\", "/"))] += 1
                if e.get("type") == "assistant":
                    m = e.get("message", {}).get("model")
                    if m and m != "<synthetic>":
                        seen[m] += 1
            is_setup = cwds and cwds.most_common(1)[0][0] == "measurement_env"
            if is_setup:
                n_setup += 1
                setup_models.update(seen)
            else:
                n_session += 1
                models.update(seen)
        model = ", ".join(f"{m} ({n})" for m, n in models.most_common())
        if not model and setup_models:
            model = "— (lost; setup agent " + ", ".join(f"{m} ({n})" for m, n in setup_models.most_common()) + ")"
        tcol = str(n_session) + (f" (+{n_setup} setup)" if n_setup else "")
        rows.append(f"| {g} | {d} | {model or '—'} | {tcol} | `{commits.get(d, '')}` |")
with open(out, "w", encoding="utf-8") as fh:
    fh.write("# Sessions\n\n")
    fh.write("Model and corpus commit per session. Model = the `model` field of the assistant entries in the measurement agent's transcript (all values seen, most frequent first; `<synthetic>` entries are harness messages; the transcript field drops the `[1m]` context suffix). Transcripts = number of the session's own jsonl files, plus the `hera-session` setup agent's jsonl where it was archived alongside (told apart by the `cwd` of the entries: the setup agent runs from the shared `measurement_env` checkout). 0 means the measurement agent's transcript was lost; what survives instead is listed in the archive's `transcripts/recovered/README.md` and in metrics/runs.yaml caveats.\n\n")
    fh.write("| device | session | model | transcripts | corpus commit |\n|---|---|---|---|---|\n")
    fh.write("\n".join(rows) + "\n")
EOF
echo "| sessions/<device>/<archive> | measurement-env/hera/docs/notes/<archive> (git archive) | $SESS_COMMIT (hera) | dropped .transcripts/ (duplicate of transcripts/); partial archives 2026-07-14-QC0426-session-2 and 2026-07-18-QC0426-session superseded by their -full re-archives; Jupyter server tokens redacted |" >> $MAN

# ---------------------------------------------------------------- campaigns
mkdir -p campaigns
git -C "$ME" archive "$SESS_COMMIT" hera/campaigns/stacking | tar -x -C campaigns --strip-components=2
rm -rf campaigns/stacking/read-keys     # replay answer keys: not used by the paper, still under expert review
# td-01 (RMG01): a pre-lock rehearsal of the session kit on another rig, not in the paper; its seal row and
# its one mention in the deviations register leave every copy of the campaign directory.
# (benchmark/measurement-env/ gets the same treatment where it is built, below.)
redact_td01() {
  sed -i '/^| td-01 |/d' "$1/raman-hashes.md"
  sed -i "s/ td-01's kit predates these surfaces\.//" "$1/deviations.md"
}
for d in campaigns/stacking measurement-env/hera/campaigns/stacking; do redact_td01 "$d"; done
echo "| campaigns/stacking/ | measurement-env/hera/campaigns/stacking | $SESS_COMMIT (hera) | prereg, deviations register, per-device calls/verdicts; read-keys/ excluded |" >> $MAN

# ---------------------------------------------------------------- grading
mkdir -p grading
git -C "$HQ" archive "$HQ_COMMIT" | tar -x -C grading
rm -f grading/raters/sandesh/slack-draft.md            # private recruitment message, not a grading artifact
echo "| grading/ | ~/sharpelab/hera-quality (git archive, tracked files only) | $HQ_COMMIT | gitignored files (blind-map.secret.yaml, passb-predictions.secret.md, cards/figs) are not included |" >> $MAN

# ---------------------------------------------------------------- metrics
mkdir -p metrics
git -C "$HP" archive "$HP_COMMIT" analysis | tar -x -C metrics --strip-components=1
rm -rf metrics/drafts metrics/mock-report-qc0426-r3.md   # superseded drafts (the mock carries a known cost error)
echo "| metrics/ | ~/sharpelab/hera-paper/analysis | $HP_COMMIT | runs.yaml manifest, runs.csv, per-run metrics/messages/reports from hera-metrics |" >> $MAN
# The extractor that produced metrics/ is read from the session-archive commit,
# not the corpus freeze: it has moved since (transcript selection, lost-session
# overrides) while measurement-env/ stays the frozen tree the sessions ran on.
mkdir -p metrics/tool
git -C "$ME" archive "$SESS_COMMIT" src/tools/run_metrics.py src/tools/hera_utilization.py hera/docs/run-metrics-spec.md | tar -x -C metrics/tool
mv metrics/tool/src/tools/*.py metrics/tool/hera/docs/run-metrics-spec.md metrics/tool/ && rm -rf metrics/tool/src metrics/tool/hera
echo "| metrics/tool/ | measurement-env src/tools/run_metrics.py, src/tools/hera_utilization.py, hera/docs/run-metrics-spec.md | $SESS_COMMIT (hera) | the hera-metrics extractor and spec at the version that produced metrics/ (the copy under measurement-env/ is the corpus-freeze version) |" >> $MAN

# ---------------------------------------------------------------- hera-data
mkdir -p hera-data
for d in "${HERA_DATA_DIRS[@]}"; do
  rsync -a --exclude inputs/ --exclude intermediates/ --exclude __pycache__ --exclude .stfolder "$HD/$d/" "hera-data/$d/"
done
for f in "${HERA_DATA_FILES[@]}"; do cp -a "$HD/$f" hera-data/; done
find hera-data \( -name 'video_*.npz' -o -name 'fusion_videos.npz' \) -delete   # video-frame stacks, regenerable from the .wip files
echo "| hera-data/ | /data/sharpelab/hera-data (rsync, not versioned) | n/a (snapshot $(date -u +%Y-%m-%d)) | dropped: inputs/ (copies of the raw Raman files), intermediates/ (video-frame npz), feldman-set (separate project), raman-public-data (third-party Zenodo sets, cited in measurement-env/hera/docs/raman-public-data.md), test-cases (replay runs, not in the paper), triage-dryruns, r4g-*-deposit |" >> $MAN

# ---------------------------------------------------------------- benchmark
# The harness, grader, pre-registration, analysis script, case files, briefs
# and masks, as one tree at the pre-registration commit. The two container
# images the arms ran in were built from commits already in this snapshot: the
# corpus arm from the frozen tree (measurement-env/), the no-corpus arm from
# corpus-variants/corpus-039b0f5.patch applied to it.
mkdir -p benchmark/measurement-env
git -C "$ME" archive "$BENCH_COMMIT" | tar -x -C benchmark/measurement-env --exclude=hera/docs/notes
for p in "${DROP_PATHS[@]}" "${CHOP_PATHS[@]}" "${CHOP_PATHS_SILENT[@]}" "${DROP_PATHS_PENDING[@]}" "${BENCH_CHOP_PATHS[@]}"; do
  [ "$p" = hera/test-cases ] && continue
  rm -rf "benchmark/measurement-env/$p"
done
find benchmark/measurement-env -xtype l -delete
redact_td01 benchmark/measurement-env/hera/campaigns/stacking
echo "| benchmark/measurement-env/ | ~/sharpelab/measurement-env (git archive) | $BENCH_COMMIT (hera: fan-design pre-registration declared) | the same drops and chops as measurement-env/, plus: $(printf '%s, ' "${BENCH_CHOP_PATHS[@]}" | sed 's/, $//') |" >> $MAN

# The runs of record: every run directory final/analysis.json lists, pruned of
# container residue. The frozen state (cut/) is identical across runs apart from
# its episode.json timestamp, so it is published once; each run keeps its own
# cut/episode.json. Per episode, session/data is a copy of the cut's, stubs/ is
# a copy of src/hera/replay/stubs, and the Codex home keeps its rollouts and
# config only.
BR=benchmark/runs/$BENCH_FRONTIER
mkdir -p "$BR"
mapfile -t BENCH_RUNS < <(python3 -c "import json,sys;print('\n'.join(sorted(json.load(open(sys.argv[1]))['run_dirs'])))" "$BENCH_ANALYSIS")
cut_digest() { (cd "$1" && find . -type f ! -name episode.json -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -c1-16); }
CUT0=$(cut_digest "${BENCH_RUNS[0]}/cut")
rsync -a --exclude episode.json "${BENCH_RUNS[0]}/cut/" "$BR/cut/"
for rd in "${BENCH_RUNS[@]}"; do
  [ "$(cut_digest "$rd/cut")" = "$CUT0" ] || { echo "cut differs: $rd" >&2; exit 1; }
  case=$(basename "$(dirname "$rd")"); stamp=$(basename "$rd")
  dest="$BR/$case/$stamp"
  mkdir -p "$dest/cut"
  cp -a "$rd/cut/episode.json" "$dest/cut/episode.json"
  for ep in "$rd"/episodes/*/; do
    diff -rq "$rd/cut/session/data" "$ep/session/data" >/dev/null || { echo "episode data differs from the cut: $ep" >&2; exit 1; }
  done
  rsync -a --exclude '/cut/' \
    --exclude 'episodes/*/tmp/' --exclude 'episodes/*/mnt/' --exclude 'episodes/*/stubs/' \
    --exclude 'episodes/*/session/data/' --exclude 'episodes/*/session/.jupyter_ystore.db' \
    --exclude 'episodes/*/session/.ipynb_checkpoints/' \
    --include 'episodes/*/codex-home/sessions/***' --include 'episodes/*/codex-home/config.toml' \
    --include 'episodes/*/codex-home/hooks.json' --include 'episodes/*/codex-home/hook-log.jsonl' \
    --exclude 'episodes/*/codex-home/*' \
    "$rd/" "$dest/"
done
python3 - "$BENCH_ANALYSIS" "$BR/INDEX.md" <<'EOF'
import json, sys, collections
a = json.load(open(sys.argv[1]))
rows = collections.OrderedDict()
for e in a["episodes"]:
    case, stamp, _ = e["key"].split("/")
    r = rows.setdefault((case, stamp), collections.Counter())
    r[e["ending"]] += 1
with open(sys.argv[2], "w") as f:
    f.write("# Runs of record\n\nThe run directories `vti02-fan-scoring-v2/final/analysis.json` lists, with each episode's ending as the analysis of record classifies it (`fan` is graded; the rest are censored). `cut/` is the frozen state every run started from; each run's own `cut/episode.json` records when it was materialized.\n\n| case | run | episodes | fan | spot check | B = 0 | nothing landed |\n|---|---|---|---|---|---|---|\n")
    for (case, stamp), c in rows.items():
        f.write(f"| {case} | {stamp} | {sum(c.values())} | {c.get('fan',0)} | {c.get('spot check',0)} | {c.get('B = 0',0)} | {c.get('nothing landed',0)} |\n")
EOF
echo "| benchmark/runs/$BENCH_FRONTIER/ | /data/sharpelab/hera-data/replay/runs/<case>/<stamp> (rsync) | n/a (the ${#BENCH_RUNS[@]} run dirs final/analysis.json lists; snapshot $(date -u +%Y-%m-%d)) | cut/ published once (each run keeps cut/episode.json); per episode dropped: tmp/, mnt/, stubs/ (= src/hera/replay/stubs), session/data (= cut/session/data), session/.jupyter_ystore.db, session/.ipynb_checkpoints, codex-home/ except sessions/, config.toml, hooks.json, hook-log.jsonl. Not included: the 2026-10-03 medium-effort runs (exploratory) and the development frontiers |" >> $MAN

# The analysis of record and the grader-development record.
rsync -a --exclude '*.zref' --exclude __pycache__ --exclude effort-medium/ "$BENCH_SCORING/" benchmark/vti02-fan-scoring-v2/
echo "| benchmark/vti02-fan-scoring-v2/ | /data/sharpelab/hera-data/vti02-fan-scoring-v2 (rsync) | n/a (snapshot $(date -u +%Y-%m-%d)) | final/ is the analysis of record (analysis.json, episodes.json, audit, reads); the rest is the grader-development record. Dropped: *.zref boards, effort-medium/ (exploratory arm) |" >> $MAN
echo "| figures/ | kept in this repository, not rebuilt | n/a | the paper's figure scripts; figures/out/ is gitignored |" >> $MAN

# ---------------------------------------------------------------- redaction
# In-place substitutions that keep line counts, applied to the tree AND the
# corpus patches so the patches still apply. Targets: Jupyter server tokens,
# Slack member ids, personal email addresses and mail thread ids, the lab's
# tailnet id, the wiki credentials-page link, the on-disk location of an
# InfluxDB token.
REDACT='
  s/token=[0-9a-f]{48}/token=REDACTED/g;
  s/\btoken *: *[0-9a-f]{48}/token: REDACTED/g;
  s/\b(U02HE4J1279|U07JPR2G9M3)\b/U0123456789/g;
  s/\b(aaronlsharpe|aa88767)\@gmail\.com/[personal email redacted]/g;
  s/bingcheng\@stanford\.edu/user\@example.edu/g;
  s/\b(19fc416210b6f9ea|1a017d4ab96fc45a)\b/[thread id redacted]/g;
  s/tail737ca5/[tailnet]/g;
  s#https://wiki\.sharpelab\.science/doc/credentials-[A-Za-z0-9]+#[wiki credentials page, link redacted]#g;
  s#`~/Documents/GitHub/influx/writetoinflux/influx\.py`#[path redacted]#g;
'
grep -rlE 'token=[0-9a-f]{48}|token *: *[0-9a-f]{48}|U02HE4J1279|U07JPR2G9M3|aaronlsharpe@gmail|aa88767@gmail|bingcheng@stanford|19fc416210b6f9ea|1a017d4ab96fc45a|tail737ca5|credentials-AnLfoWDpb2|writetoinflux' \
  measurement-env corpus-variants sessions campaigns grading metrics hera-data benchmark 2>/dev/null | while read -r f; do
  perl -pi -e "$REDACT" "$f"
done

# ---------------------------------------------------------------- checksums
find measurement-env corpus-variants sessions campaigns grading metrics hera-data benchmark figures -path figures/out -prune -o -type f -print0 | sort -z | xargs -0 sha256sum > CHECKSUMS.sha256
echo >> $MAN
echo "CHECKSUMS.sha256 covers every file under the directories above." >> $MAN
echo "Built: $(du -sh --exclude=.git . | cut -f1) total."
