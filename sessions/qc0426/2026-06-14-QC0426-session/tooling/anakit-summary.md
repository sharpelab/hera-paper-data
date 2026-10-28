# Tooling subtask — ana-kit (triage round 3)

Branch: `subtask/triage-r3-anakit` (off `hera`). Draft only — not merged, not pushed.

Two session-kit items from the 2026-06-14 QC0426/VTI session.

---

## T-7 (IMPLEMENTED) — ana-notebook data path no longer assumes kernel cwd

### Problem
The ana template's helper cell defined the data dir relative to the kernel's
cwd — either `file_path = './data'` or `file_path = os.path.join('.', 'data')`.
The ana kernel's working directory is **not** guaranteed to be the measurement
dir, so `load_meta`/`load1d`/`sl.pload` raised `FileNotFoundError`. The
2026-06-14 agent worked around this by hardcoding absolute Windows paths into
ana cells repeatedly — a recurring paper-cut.

### Fix
Replace the bare `file_path = ...` line with a `_resolve_data_dir()` helper that
derives the data dir from the **notebook's own location** rather than `'.'`:

1. Prefer `globals()['_dh'][0]` — IPython sets `_dh` to a list whose first entry
   is the notebook's startup cwd (the dir holding the notebook). This survives
   jupyter-collaboration/RTC and any later `%cd`, so it is the most robust
   handle on the notebook dir without `__file__` (notebooks have none) and
   without adding the `ipynbname` dependency (not installed in the env).
2. Fall back to `Path.cwd()`.
3. From each candidate, walk up checking for a `data/` subdir, so loading still
   works if the kernel happened to start inside `./data/<id>/`.
4. **Stop before the filesystem root** so an unrelated top-level `data/` dir
   (e.g. `/data` exists on dev boxes) can never be matched — this was a real
   hazard caught during testing.

```python
def _resolve_data_dir():
    candidates = []
    dh = globals().get("_dh")
    if dh:
        candidates.append(Path(dh[0]))
    candidates.append(Path.cwd())
    for base in candidates:
        base = Path(base).resolve()
        for d in [base, *base.parents]:
            if d == d.parent:  # filesystem root
                break
            cand = d / "data"
            if cand.is_dir():
                return str(cand)
    return str((Path(candidates[0]) / "data").resolve())

file_path = _resolve_data_dir()
```

A `from pathlib import Path` import was added to the import header of notebooks
that lacked it.

### Notebooks touched (5)
- `templates/toploader_ana.ipynb`        (canonical, was `'./data'`)
- `templates/vti_ana.ipynb`              (canonical, was `os.path.join(".", "data")`)
- `hera/templates/QC0426/20260610_ana.ipynb`   (was `os.path.join(".", "data")`)
- `hera/templates/QC0426-round2/ana.ipynb`     (was `os.path.join(".", "data")`)
- `hera/templates/b1c2/toploader_ana.ipynb`    (was `'./data'`)

Edited via `nbformat` read/modify/write (no hand-editing of JSON); all five
re-parse cleanly as nbformat v4.

### Validation
A standalone harness exercised the resolver from a cwd **different** from the
simulated notebook dir:
- **A** `_dh` set, cwd elsewhere → resolves to `<nbdir>/data` ✓
- **B** no `_dh`, cwd == nbdir → resolves via cwd ✓
- **C** cwd == `<nbdir>/data/<id>` → search-up finds `<nbdir>/data` ✓
- **D** nothing found → falls back to `<base>/data`, does **not** climb to root ✓
- **E** deep subdir, no `_dh` → still finds the right `data/` without hitting `/data` ✓

Then the **actual patched cell source** from `vti_ana.ipynb` was `exec`-ed with
`_dh` set and `os.chdir('/tmp')` (kernel cwd ≠ measurement dir); `file_path`
resolved correctly and `load_meta(5)` successfully read a real
`metadata.json` — i.e. the end-to-end load path that previously failed now works.

---

## T-8 (BACKLOGGED — written proposal, not implemented) — instrument snapshot stores `time_constant`/`filter_slope` as `None`

### Disposition
**Backlogged.** Root cause confirmed, but every viable fix crosses a contract
boundary the brief reserves for a human ruling (the `measureme` submodule or the
measure-notebook). There is **no in-this-repo seam** that does not touch one of
those, so no code was changed for T-8.

### Root cause (confirmed)
The snapshot is built in the `measureme/sweep` submodule:

`lib/measureme/sweep/sweep.py:381`
```python
"snapshot": inst.snapshot(),   # no update= → defaults to update=False
```

QCoDeS `InstrumentBase.snapshot_base(update=False, ...)` reports each
parameter's **cached** value and never queries the hardware. The SR830 driver
(QCoDeS built-in `qcodes.instrument_drivers.stanford_research.SR830`) defines
`time_constant` (`OFLT?`) and `filter_slope` (`OFSL?`) as ordinary gettable
params with no `snapshot_get=False` — they are fully snapshot-able. But during
a run only `X` (the followed/read param) is ever `get()`-ed; `time_constant`
and `filter_slope` are never read, so their cache stays `None` and serializes
as `null` in `metadata.json`. The lock-in τ is therefore not recoverable from
disk (hurts reproducibility + post-hoc settling checks).

Demonstrated against a mock QCoDeS instrument (no hardware):
- `snapshot(update=False)` on a never-read param → `value: None`
- `snapshot(update=True)` → forces the getter → `value: 0.1`
- manual `param()` once, then `snapshot(update=False)` → `value: 0.1`

So the param works; it is simply never queried before the cache is serialized.

### Where the fix belongs + concrete proposals
Two clean options, each crossing a boundary that needs a human call:

1. **`measureme` submodule** — change `sweep.py:381` to
   `inst.snapshot(update=True)`. Pro: fixes it for *all* instruments/params at
   once. Con: forces a hardware `get()` of **every** parameter of **every**
   followed instrument at each sweep init — slower, and risky for params with
   expensive/side-effecting/write-only-ish getters. Could also be scoped via
   `params_to_skip_update` to update only safe params, but that adds policy to
   the generic sweep layer. **Touches the measureme submodule + the
   measure-side snapshot contract → human ruling required.**

2. **Measure notebook (bring-up)** — after instantiating the SR830s, call the
   getters once so the cache is warm before the first sweep, e.g. in the
   lock-in bring-up cell:
   ```python
   for srs, _ in sr830s:
       srs.time_constant(); srs.filter_slope()
   ```
   Pro: minimal, low-risk, only reads the two params we care about, no change to
   sweep semantics. Con: lives in `templates/toploader_measure.ipynb` (the
   measure-notebook contract) and must be remembered for every rig/device
   variant. **Touches the measure-notebook contract → human ruling required.**

**Recommendation:** option 2 (cache-warm in measure bring-up) is the lowest-risk
fix and keeps the generic sweep layer untouched; promote it to a standard line
in the lock-in bring-up cell of the canonical measure template once a human
signs off. If broad correctness across all instruments is preferred over
narrow risk, option 1 with an explicit `params_to_skip_update` allowlist is the
alternative. Either way this is a backlog item, not landed here.

---

## Net line delta

T-7: **+29 logical source lines per ana notebook × 5 = net +145** code-cell
source lines (resolver function + `pathlib` import, replacing the 1-line
`file_path` assignment). T-8: **0** (no code change — written proposal only).
Plus this summary doc.

## Caveats
- `_dh` is an IPython/Jupyter construct; under a plain (non-IPython) kernel it
  is absent and the resolver falls through to `Path.cwd()` — acceptable, since
  these are Jupyter ana notebooks.
- The diff appears large in `git diff --stat` (~190 lines) because notebook JSON
  stores cell source as escaped strings; the logical source delta is +145.
- T-8 left for human ruling per the brief; no measureme/measure-notebook edits.
