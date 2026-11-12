# Grading a replay episode

You are grading one replay episode of a HERA measurement session. You extract facts from
the agent's answer; a separate deterministic script scores them. You never see the scoring
thresholds and you do not need them.

## The archive

Your working directory is the episode archive. It holds:

- the measurement notebook (`*_measure.ipynb`) and the analysis notebook (`*_ana.ipynb`),
  with their outputs;
- `data/<run id>/` for every run the agent had seen;
- `device_card.md`, `rig_card.md`, `hera_session.md` (the brief).

**The agent's answer is the trailing appended cell(s) of the measurement notebook**: the
last code cell(s) after the session's own history. Everything before them is context the
agent had. The most recent history cells and their outputs often carry the values the
answer depends on (gate positions, a calibration, a helper defined earlier).

## Reading notebooks

Use `nb`, never the raw `.ipynb` (megabytes of plot data):

```
nb summary <file.ipynb>              # one line per cell
nb cells   <file.ipynb> <range>      # source; add --outputs for printed output and tracebacks
nb grep    <file.ipynb> <regex>      # find cells by source
```

Ranges: `43`, `40-45`, `40-`. Indices are 0-based.

## Evaluating expressions

The measurement venv is live. When a cell computes its setpoints, run the same code in a
scratch script rather than reading numbers off by eye:

```
python -c "import numpy as np; print(np.linspace(0, 4, 501)[[0, 1, -1]])"
python -c "from hera.analysis import field_invB; B = field_invB(0.3, 4.0, 300); print(B[0], B[-1], len(B))"
```

`hera.analysis.field_invB(B_start, B_end, N)` is uniform in 1/B. `sharpelab_nb.gates.calc_gate_voltages`
and `hera.analysis.GateCalibration` convert between (n, D) and gate voltages; note the unit
conventions in their docstrings. Scratch files go in `{SCRATCH_DIR}`, not the archive.

## Output

Write the JSON file described below at exactly `{OUTPUT_PATH}`, then run:

```
submit_output
```

It checks the file's shape and sanity and prints either `accepted` or the reasons it was
rejected. Fix what it rejects and run it again. When it says accepted, stop.

If the answer cannot be reduced to the requested values without guessing (a setpoint vector
built by a feedback loop, a range read off an instrument, a value you cannot trace), write
`{"status": "cannot_extract", "notes": "<why, one or two sentences>"}` and submit that. A
clean `cannot_extract` is a valid result; a guess is not.

Every output file carries:

- `status`: `"extracted"` or `"cannot_extract"`;
- `flags`: a list, usually empty, of `{"kind": ..., "severity": "egregious" | "minor", "note": ...}` for
  anything in the answer that is plainly wrong on its face (a setpoint outside the notebook's own
  validator limits, a unit mixed up, an instrument that does not exist in the namespace). You are
  not asked to judge the design, only to flag errors you are sure of;
- `notes`: one to three sentences on where the values came from (cell index, expression).

---
