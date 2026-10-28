# Adding a grader

A grader scores one decision point of a replayed HERA session. It is two files in
`hera/graders/<name>/`: a prompt an LLM extractor follows, and a `grade.py` that turns
the extractor's output into scores without a model call. The physics lives next to the
grader that uses it. One grader per decision point: a spot check is not a fan, a fan is
not a gate survey.

```
hera/graders/
  BASE.md                  prepended to every prompt; do not edit per grader
  <name>/
    prompt.md              what to extract, and the exact output file
    grade.py               check + score; every threshold lives here
    <physics>.py           a sibling module grade.py imports (scorer, polygon, …)
    context/               optional extras the extractor may read
```

## How a grade runs

`hera-grade <episode-dir> --grader <name>` (or `hera-replay grade <run-dir>`, which
calls it for every finished episode) does this per extraction:

1. Starts a container from the image the episode ran in. `session/` is mounted
   read-only at `/episode`, which is the working directory. The extractor has `nb`,
   the venv (`python` is the image's), `hera.analysis`, `sharpelab_nb`. It has no
   network access to anything but the API, no write access outside `/grade-run`,
   and never sees `grades/`, `episode.json`, or the episode's `.claude/`.
2. Sends `BASE.md` + your `prompt.md` on stdin with `{OUTPUT_PATH}` and
   `{SCRATCH_DIR}` substituted.
3. The extractor writes the output file and runs `submit_output`, which runs your
   `grade.py check` on it. Rejections go back to the extractor verbatim; on accept
   it stops.
4. On the host, `grade.py score <output.json> --archive <session> -o scores.json`.

Everything lands in `<episode-dir>/grades/<name>/<stamp>/`.

## prompt.md

Say what the answer is (usually the trailing appended cell(s) of the measure notebook),
name **one** quantity per field, and give the output file's exact shape with an example.
The extractor never sees thresholds and must not need them. Rules that hold for every
grader are already in `BASE.md`: use `nb`, evaluate expressions in the venv rather than
by eye, write `cannot_extract` with a reason rather than guess.

Two kinds, stated in the prompt: **extract** (the LLM never sees the reference answer;
the script scores) and **judge** (the LLM sees a key; the script tallies).

## The output file

Flat JSON. The values the score needs, plus on every file:

- `status`: `"extracted"` or `"cannot_extract"`
- `flags`: `[{"kind", "severity": "egregious"|"minor", "note"}]`, usually empty; errors
  plain on the face of the answer, not judgements of the design
- `notes`: one to three sentences on where the values came from

Prefer the quantity that is easiest to extract reliably (a density over a gate voltage,
a linspace's three numbers over 500 values). If the natural form varies, allow the
alternatives explicitly (`B_values` for a stitched vector) and handle each in `grade.py`.

## grade.py

```
grade.py check <output.json>                              exit 0, or 1 with reasons on stdout
grade.py score <output.json> --archive <dir> [-o out]     scores.json
```

- `check` is shape and sanity only. It never computes a score, so the extractor cannot
  tune toward one. Reject with reasons the extractor can act on.
- `score` is deterministic. Every threshold, constant, window and unit convention is a
  named constant in this file or its sibling module. A threshold change is a commit here.
  Per-device values live in `devices.toml`, read with `devices.device_params(archive, ...)`.
  Per-case values live in the grader's `cases.toml`, keyed by replay case name.
- `scores.json` carries `grader`, `status` (`graded` | `cannot_extract` | `no_output` |
  `invalid`), `ok`, the per-scorer diagnostics, `flags` and `notes` passed through, and
  `versions`.
- Imports: numpy, the sibling module and `graders/devices.py`, both by path. Nothing from
  the `hera` package.

## Adding one

1. Pick the decision point and the archived session that has the expert's answer for it.
2. Write `prompt.md` against that answer. Run the extractor on it once (`hera-grade`,
   about $0.30–0.50) and read `output.json` and the transcript: did it find the values
   by evaluating the cell, or by guessing?
3. Write `grade.py` and the physics module. Unit-test `score` on a hand-written
   `output.json` that mirrors the expert's answer, and `check` on the rejections you
   care about (`tests/hera/test_grading.py` has the pattern).
4. Run `hera-grade <episode-dir> --grader <name> --n 3` on the expert's answer. Three
   identical `output.json`s, and `scores.json` says what you expect. If the three
   disagree, the prompt is underspecified, not the model.
5. Name it in the case file: `grader: <name>`. A decision point without a grader is
   `grader: null`; do not point another grader at it.

## What not to do

- No manifest, no shared schema, no parameter plumbing between graders.
- No score in `check`.
- No physics in the prompt. If the extractor needs a threshold to decide what to
  report, the prompt is asking for the wrong quantity.
- No grader that covers two decision points. Split it.
