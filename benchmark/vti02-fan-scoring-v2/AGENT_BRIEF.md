# Shared brief for the overnight investigation agents (2026-09-23)

Read these first:
- `/home/zack/sharpelab/measurement-env/hera/docs/fan-design-scoring-v2.md`: the frozen
  scoring proposal. **Read-only. Do not edit it.**
- `/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check/REPORT.md` and its scripts:
  the live-fan FFT, noise, clipping and settling study. Reuse `load.py`, `fft_q1.py` and
  the rest instead of rewriting them.
- `roi.py`, `band.py`, `summary.py` in `/data/sharpelab/hera-data/vti02-fan-scoring-v2/`:
  the current band scorer over every dev-set extraction.
- `/home/zack/sharpelab/measurement-env/hera/models/tetralayer_fs_count/README.md` and its
  code (`fs_count_b0.py`, `synth_fan.py`, `synth_eval.py`): the corpus forward model.
- `/home/zack/sharpelab/measurement-env/hera/docs/tetralayer-stacking-extraction-survey.md`:
  the physics survey behind the model.
- Live sessions: `/home/zack/sharpelab/measurement-env/hera/docs/notes/2026-08-2{1..5}-vti-02-session/`.
  Each holds session_notes.md, device_card.md, ana/measure notebooks, hera_scratch and data.
  Use the `nb` CLI, or read the notebook JSON selectively; never dump whole notebooks.
- Fixture fans with their extracted designs:
  `/data/sharpelab/hera-data/frontier/calibration/vti02-live/*`.
  Dev-set replay extractions:
  `/data/sharpelab/hera-data/replay/runs/vti02-fan-design-*/*/episodes/*/grades/fan-design/*/output.json`.

Rules:
- Read-only everywhere except your own output dir,
  `/data/sharpelab/hera-data/vti02-fan-scoring-v2/<your-topic>/`.
- No edits to the repo, no git, no hera-replay / hera-grade / agent episodes, no network
  writes. Web search and reading papers (arXiv) are fine.
- Python via `uv run --no-project --with numpy --with scipy [--with matplotlib ...] python3 ...`.
  Never pip or venv.
- Numbers, not narrative. State every assumption and every free parameter you fit.
  Separate fitted from held-out.
- Your final message is your report: markdown with tables and conclusions, at most ~1500
  words, plus the paths of the artifacts you wrote. The lead saves it next to your
  artifacts. Flag anything that contradicts the proposal.
