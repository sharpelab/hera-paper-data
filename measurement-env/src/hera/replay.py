"""hera-replay — offline replay driver for the HERA measurement-suggestion benchmark.

Freezes a fixture at a declared frontier, builds a leakage-safe working copy that
contains only what a live operator would have seen up to the cut, and runs a
HERA-shaped agent (headless Claude Code) against it. The agent emits its read of
the latest sweep + the next experiment it would propose. Output is captured under
``<fixture>/runs/<slug>/<config>-<ts>/`` for hand- or LLM-judging against
``ground_truth/<slug>/``.

Per benchmark-plan.md: tools restricted to Read / Bash / Glob / Grep (read-only;
no nb-collab append, no kernel).

Leakage control is **declared, not heuristic**. Each frontier file
(``frontiers/<slug>.md``) carries YAML frontmatter:

    ---
    slug: after-idc-vs-n
    cut_index: 32              # inclusive, fixture-relative, 0-based
    latest_fileid: 84          # the freshest sweep at the cut
    included:
      data: [75, 76, ...]      # ALLOWLIST of pre-cut data dirs (authoritative)
      images: [cell254_out2.png, ...]
    leak_terms: ["mag.field", "B vs Idc", ...]   # must not appear in the workdir
    forward_scan: "..."        # human attestation that kept cells were scanned
    ---

The driver copies *only* the allowlisted data/images, then greps the assembled
workdir for every ``leak_term`` and **aborts** if any hit. Goal + framing are
injected via a generated prompt built from the safe Isaac quote + device card;
the fixture's scaffolding files (goal.md, README.md, cell-to-fileid.md, the full
hera_session.md, the post-hoc ana notebook) — all of which name post-cut
sections — are never copied.

Usage:
    uv run hera-replay <fixture-dir> [--frontier SLUG] [--config NAME]
                       [--model M] [--dry-run]
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml

# Workdir files to scan for leak_terms (data TSVs are excluded — bulk data, and
# the allowlist already controls which data dirs are present).
_SCAN_SUFFIXES = {".md", ".ipynb", ".json", ".txt", ".py"}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split a frontier file into (frontmatter dict, body)."""
    if not text.startswith("---"):
        sys.exit("frontier file has no YAML frontmatter (--- block)")
    parts = text.split("---", 2)
    if len(parts) < 3:
        sys.exit("frontier file frontmatter not terminated by a second ---")
    fm = yaml.safe_load(parts[1]) or {}
    return fm, parts[2]


def _resolve_frontier(fixture: Path, slug: str | None) -> tuple[str, dict]:
    fdir = fixture / "frontiers"
    if not fdir.is_dir():
        sys.exit(f"{fixture}/frontiers/ not found — is this a frontier'd fixture?")
    files = sorted(fdir.glob("*.md"))
    if not files:
        sys.exit(f"no frontier files in {fdir}")
    if slug is None:
        if len(files) != 1:
            avail = ", ".join(f.stem for f in files)
            sys.exit(f"--frontier required; available: {avail}")
        path = files[0]
    else:
        path = fdir / f"{slug}.md"
        if not path.exists():
            avail = ", ".join(f.stem for f in files)
            sys.exit(f"frontier '{slug}' not found; available: {avail}")
    fm, _ = _parse_frontmatter(_read(path))
    for key in ("cut_index", "included", "leak_terms"):
        if key not in fm:
            sys.exit(f"{path.name} frontmatter missing required key: {key}")
    return path.stem, fm


def _measure_notebook(fixture: Path) -> Path:
    cands = sorted(fixture.glob("*measure*.ipynb"))
    if not cands:
        sys.exit(f"no *measure*.ipynb in {fixture}")
    return cands[0]


def _crop_notebook(src: Path, dst: Path, cut_index: int) -> int:
    nb = json.loads(_read(src))
    nb["cells"] = nb.get("cells", [])[: cut_index + 1]
    dst.write_text(json.dumps(nb, indent=1), encoding="utf-8")
    return len(nb["cells"])


def _link_or_copy(src: Path, dst: Path) -> None:
    """Hardlink a file (cheap, no duplication when src and workdir share a btrfs
    subvolume); fall back to a copy when os.link raises (EXDEV across a
    subvolume/filesystem boundary — e.g. a fixture whose binary layer is
    symlinked to $HERA_DATA on a machine where runs/ is not co-located). Copy,
    not symlink: the workdir must stay self-contained so the agent cannot reach
    un-allowlisted data outside it — that is the leakage guarantee."""
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def _link_tree(src: Path, dst: Path) -> None:
    """Hardlink a directory tree (cheap, no duplication); fall back to a copy
    across a subvolume/filesystem boundary. Copy not symlink — see _link_or_copy."""
    try:
        shutil.copytree(src, dst, copy_function=os.link)
    except (OSError, shutil.Error):
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)


def _build_workdir(fixture: Path, workdir: Path, fm: dict) -> dict:
    """Assemble the leakage-safe working copy from the frontier allowlist."""
    workdir.mkdir(parents=True, exist_ok=True)
    cut_index = fm["cut_index"]
    included = fm["included"] or {}
    manifest: dict = {"included_files": [], "data_dirs": [], "images": []}

    card = fixture / "device_card.md"
    if card.exists():
        shutil.copy2(card, workdir / "device_card.md")
        manifest["included_files"].append("device_card.md")

    src_nb = _measure_notebook(fixture)
    n = _crop_notebook(src_nb, workdir / src_nb.name, cut_index)
    manifest["included_files"].append(f"{src_nb.name} (cropped to {n} cells)")

    (workdir / "data").mkdir(exist_ok=True)
    for did in included.get("data", []):
        src = fixture / "data" / str(did)
        if not src.is_dir():
            sys.exit(f"allowlist names data/{did} but it does not exist")
        _link_tree(src, workdir / "data" / str(did))
        manifest["data_dirs"].append(str(did))

    (workdir / "images").mkdir(exist_ok=True)
    for img in included.get("images", []):
        src = fixture / "images" / img
        if not src.exists():
            sys.exit(f"allowlist names images/{img} but it does not exist")
        _link_or_copy(src, workdir / "images" / img)
        manifest["images"].append(img)

    return manifest


def _leak_check(workdir: Path, leak_terms: list[str]) -> list[tuple[str, str]]:
    """Grep the assembled workdir for any leak term. Returns (file, term) hits."""
    terms = [(t, t.lower()) for t in leak_terms]
    hits: list[tuple[str, str]] = []
    for path in workdir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in _SCAN_SUFFIXES:
            continue
        try:
            blob = path.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        rel = str(path.relative_to(workdir))
        for orig, low in terms:
            if low in blob:
                hits.append((rel, orig))
    return hits


_TASK_TEMPLATE = """\
# HERA offline replay — {device} / {user}

You are HERA, the in-session measurement advisor for the Sharpe Lab toploader
cryostat. This is an **offline replay**, not a live session: the data below is a
**frozen, complete-up-to-now** measurement directory. There is no running
kernel and no live notebook to append to — do **not** propose `nb-collab`
cells, and do not try to execute anything. Your job is judgment, not actions.

## {goal_heading}
{goal_body}

## Where you are
{state_block}
{resources_block}
## What to produce (markdown, two sections)

{read_section}

### 2. Next experiment
Given the state above, what is the single best **next experiment**? Give:
(a) a one-line statement of the experiment, (b) the rationale tied to the
goal/brief and to what the data does or doesn't yet show, and (c) the concrete
sweep cell you would land (the `s.<sweep>(...)` call with axes/ranges), as you
would write it in the notebook.

Tools available: Read, Bash (incl. `uv run --project {repo} nb ...` to navigate
the notebook), Glob, Grep — all read-only. Be concise and specific.
"""


def _parse_goal_quote(goal_text: str) -> str:
    """The full blockquote (a wrapped quote spans several `> ` lines), minus the
    attribution. The attribution line starts with an em-dash (`> — Name`); the
    quote may legitimately contain em-dashes mid-sentence, so test the leading
    char only."""
    parts: list[str] = []
    for line in goal_text.splitlines():
        s = line.strip()
        if not s.startswith(">"):
            if parts:
                break            # blockquote ended
            continue
        body = s.lstrip("> ").strip()
        if body.startswith("—"):  # attribution
            break
        if len(body) <= 3:        # empty quote line
            continue
        parts.append(body)
    if parts:
        return " ".join(parts).strip('"')
    return "Characterize the device per the campaign goal."


def _load_brief(fixture: Path, slug: str, variant: str) -> str:
    """Load a brief variant body (strip the leading HTML comment + '# Brief' head)."""
    path = fixture / "briefs" / slug / f"{variant}.md"
    if not path.exists():
        avail = sorted(p.stem for p in (fixture / "briefs" / slug).glob("*.md")) \
            if (fixture / "briefs" / slug).is_dir() else []
        sys.exit(f"brief '{variant}' not found for frontier '{slug}'; "
                 f"available: {', '.join(avail) or '(none)'}")
    text = re.sub(r"<!--.*?-->", "", _read(path), flags=re.S)      # drop comment header
    text = re.sub(r"^\s*#\s*Brief.*?\n", "", text, count=1)         # drop '# Brief' heading
    return text.strip()


_STATE_DATA = (
    "The measurement notebook ({notebook}) holds every cell that has run **so "
    "far**, with outputs preserved. The most recent sweep that landed is "
    "**data/{latest_fileid}/**; earlier sweeps are in the other `data/<id>/` "
    "directories (each has a `metadata.json` with the sweep function + "
    "parameters, a TSV, and a `plot.png`). Rendered cell plots are in `images/`."
)
# Appended only when the frontier declares cooldown_drift: true (e.g. b1c2,
# where the device card is a different cooldown than the data). Most fixtures are
# same-cooldown, so this is off by default.
_DRIFT = (
    "\n\n**Device-card drift (real, not a trick):** `device_card.md` describes a "
    "*different* cooldown than the data on disk (same chip). Treat it as \"fresh "
    "device summary, older data\" — flag it if it matters."
)
_STATE_COLD = (
    "The measurement notebook ({notebook}) shows the session **setup only** — "
    "instrument instantiation, `meas_config`, gate ramps and validators — and "
    "**no sweeps have run yet**. You are at the very start of the campaign. What "
    "the device is and what is wired for this run are in `device_card.md`."
)
_READ_DATA = (
    "### 1. Read of the latest sweep\n"
    "Open and read **data/{latest_fileid}/** (its `plot.png`, `metadata.json`, "
    "and the TSV if useful). State plainly what it shows and what it means for "
    "the goal: what's the sweep, what's the signal, is there a feature, what does "
    "it establish, what's still open. Note any limitation of how it's plotted."
)
_READ_COLD = (
    "### 1. Starting point\n"
    "No sweeps have landed yet. Briefly state what you know about the device from "
    "`device_card.md` and the notebook setup (gates + safe ranges, what's wired, "
    "intended config), and what you most need to find out first."
)


_RESOURCES = (
    "\n## Resources (same as a live session)\n"
    "The lab's measurement **recipe corpus** is at `{recipes}` — canonical "
    "how-to for gatemaps, nD-maps, field sweeps, etc., each with the real "
    "`s.megasweep(...)` / `s.multisweep(...)` API, sensible default parameters, "
    "timing, and a `## Next` branching section. **Consult the relevant recipe** "
    "for the correct sweep call and parameters, exactly as you would live — do "
    "not guess the API.\n"
)


def _build_prompt(fixture: Path, fm: dict, repo: Path, brief_text: str | None = None,
                  recipes_dir: Path | None = None) -> str:
    if brief_text is not None:
        goal_heading = "Your brief (handed down from the strategic layer)"
        goal_body = brief_text
    else:
        goal_heading = "Campaign goal"
        goal_body = "Characterize the device per the campaign goal."
        gp = fixture / "goal.md"
        if gp.exists():
            goal_body = _parse_goal_quote(_read(gp))
    notebook = _measure_notebook(fixture).name
    latest = fm.get("latest_fileid")
    cold = latest in (None, "", "none")
    state_block = (_STATE_COLD if cold else _STATE_DATA).format(
        notebook=notebook, latest_fileid=latest)
    if not cold and fm.get("cooldown_drift"):
        state_block += _DRIFT
    read_section = (_READ_COLD if cold else _READ_DATA).format(latest_fileid=latest)
    resources_block = _RESOURCES.format(recipes=recipes_dir) if recipes_dir else ""
    parts = fixture.name.split("-")
    device = parts[3] if len(parts) > 3 else fixture.name
    return _TASK_TEMPLATE.format(
        device=device, user=fm.get("user", "operator"),
        goal_heading=goal_heading, goal_body=goal_body,
        state_block=state_block, read_section=read_section,
        resources_block=resources_block, repo=repo,
    )


def _result_obj(parsed):
    """`claude -p --output-format json` may return the final result dict directly
    or the full event array; return the terminal `type=="result"` object."""
    if isinstance(parsed, dict):
        return parsed
    if isinstance(parsed, list):
        for item in reversed(parsed):
            if isinstance(item, dict) and item.get("type") == "result":
                return item
        # fall back to the last dict
        for item in reversed(parsed):
            if isinstance(item, dict):
                return item
    return {}


def _extract_run_meta(data: dict) -> dict:
    """Best-effort pull of model + cost + usage from a claude -p result object."""
    meta = {"total_cost_usd": data.get("total_cost_usd"),
            "num_turns": data.get("num_turns"),
            "duration_ms": data.get("duration_ms"),
            "usage": data.get("usage")}
    model = data.get("model")
    if not model:
        mu = data.get("modelUsage")
        if isinstance(mu, dict) and mu:
            model = ",".join(mu.keys())
    meta["model_resolved"] = model
    return meta


# NOTE: Read is confined to --add-dir, but Bash is not — a determined agent could
# `cat` the full uncropped notebook or ground_truth/ and defeat the leakage
# control. For now we trust the agent (prompted as a frozen replay) and monitor
# outputs; the real fix is sandboxing claude -p (container/bwrap with only workdir
# + recipes mounted, or a restricted Bash). TODO: hera/docs/benchmark-plan.md
# "Open questions" — sandbox the replay (Phase 1 of the operationalization plan).
def _build_claude_cmd(workdir: Path, recipes_dir: Path | None, prompt: str,
                      model: str | None) -> list[str]:
    cmd = ["claude", "-p", prompt, "--add-dir", str(workdir),
           "--allowedTools", "Read", "Bash", "Glob", "Grep",
           "--output-format", "json"]
    if recipes_dir:
        cmd += ["--add-dir", str(recipes_dir)]
    if model:
        cmd += ["--model", model]
    return cmd


def _invoke_samples(cmd: list[str], workdir: Path, dest_dir: Path, n_samples: int,
                    timeout: int, env: dict | None = None) -> tuple[list[dict], int]:
    """Run ``claude -p`` ``n_samples`` times against a read-only workdir, capturing
    each. ``samples == 1`` lands directly in ``dest_dir``; otherwise in
    ``dest_dir/sample-<i>/``. Returns (sample-meta list, first non-zero rc)."""
    samples, rc = [], 0
    for i in range(1, n_samples + 1):
        dest = dest_dir if n_samples == 1 else dest_dir / f"sample-{i}"
        dest.mkdir(parents=True, exist_ok=True)
        tag = "" if n_samples == 1 else f" [sample {i}/{n_samples}]"
        print(f"\ninvoking claude -p{tag} (cwd={workdir}, timeout={timeout}s) ...")
        try:
            res = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True,
                                 timeout=timeout, env=env)
        except subprocess.TimeoutExpired:
            sys.exit(f"claude -p timed out after {timeout}s")
        rc = rc or res.returncode

        (dest / "result.json").write_text(res.stdout, encoding="utf-8")
        if res.stderr.strip():
            (dest / "stderr.txt").write_text(res.stderr, encoding="utf-8")
        output_text, run_meta = res.stdout, {}
        try:
            data = _result_obj(json.loads(res.stdout))
            output_text = data.get("result", res.stdout)
            run_meta = _extract_run_meta(data)
        except json.JSONDecodeError:
            print("warning: could not parse claude -p json output; saved raw stdout")
        (dest / "output.md").write_text(output_text, encoding="utf-8")
        samples.append({"sample": i, "dest": str(dest), **run_meta})
        print(f"  exit={res.returncode}  -> {dest/'output.md'}  "
              f"(model={run_meta.get('model_resolved')}, cost=${run_meta.get('total_cost_usd')})")
    return samples, rc


def _resolve_ref(git_repo: Path, ref: str) -> tuple[str, str]:
    """Resolve a committish to (full sha, path-safe label)."""
    res = subprocess.run(
        ["git", "-C", str(git_repo), "rev-parse", "--verify", f"{ref}^{{commit}}"],
        capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit(f"--ref {ref!r}: not a valid commit in {git_repo} "
                 f"({res.stderr.strip()})")
    label = re.sub(r"[^A-Za-z0-9._-]", "_", ref)
    return res.stdout.strip(), label


def _ensure_worktree(git_repo: Path, pool: Path, sha: str) -> Path:
    """Materialize (or reuse) a detached worktree at ``sha`` under ``pool``.
    Keyed by sha so A/B sides and repeat runs share one checkout. Never
    ``uv sync``'d — the agent runs the main venv interpreter with the worktree's
    ``src`` pinned on PYTHONPATH, so submodules stay uninitialized and unused."""
    pool.mkdir(parents=True, exist_ok=True)
    wt = pool / sha[:12]
    if wt.is_dir():
        return wt
    res = subprocess.run(
        ["git", "-C", str(git_repo), "worktree", "add", "--detach", str(wt), sha],
        capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit(f"git worktree add failed for {sha[:12]}: {res.stderr.strip()}")
    return wt


def _write_comparison(run_root: Path, fixture: Path, slug: str, fm: dict,
                      args, ref_results: list[dict]) -> None:
    """Phase 0a comparison: pinning audit + cost + raw side-by-side links.
    Science-axis extraction (sensitivity / settling / N_B×N_n) is Phase 0b."""
    out = []
    out.append(f"# A/B replay comparison — {fixture.name}")
    out.append("")
    out.append(f"- **Frontier:** `{slug}` (cut_index={fm['cut_index']}, "
               f"latest=data/{fm.get('latest_fileid')})")
    out.append(f"- **Model:** {args.model or '(default)'}  •  "
               f"**Samples/ref:** {args.samples}")
    out.append(f"- **Run root:** `{run_root}`")
    out.append("")
    out.append("## Pinning audit")
    out.append("")
    out.append("| ref | sha | recipes (pinned to worktree) | PYTHONPATH | pinned |")
    out.append("|---|---|---|---|---|")
    for r in ref_results:
        rec, wt = r.get("recipes_dir"), r.get("worktree")
        pinned = "✅" if (rec and wt and str(rec).startswith(str(wt))) else "—"
        out.append(f"| `{r['label']}` | `{r['sha'][:12]}` | `{rec}` | "
                   f"`{r.get('pythonpath')}` | {pinned} |")
    out.append("")
    out.append("## Cost")
    out.append("")
    out.append("| ref | total $ | per-sample $ |")
    out.append("|---|---|---|")
    for r in ref_results:
        per = ", ".join(str(s.get("total_cost_usd")) for s in r.get("samples", [])) or "—"
        out.append(f"| `{r['label']}` | {r.get('total_cost_usd')} | {per} |")
    out.append("")
    out.append("## Outputs (raw side-by-side)")
    out.append("")
    for r in ref_results:
        out.append(f"### `{r['label']}` ({r['sha'][:12]})")
        for s in r.get("samples", []):
            rel = Path(s["dest"]).relative_to(run_root)
            out.append(f"- sample {s['sample']}: [`{rel}/output.md`]({rel}/output.md)")
        if not r.get("samples"):
            out.append("- (no samples — dry-run or failed)")
        out.append("")
    out.append("> Phase 0a: pinning audit + cost + raw side-by-side. Science-axis "
               "extraction (sensitivity / settling / N_B×N_n) is Phase 0b.")
    (run_root / "comparison.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (run_root / "comparison.json").write_text(
        json.dumps({"fixture": str(fixture), "frontier": slug,
                    "samples_per_ref": args.samples, "model": args.model,
                    "refs": ref_results}, indent=2), encoding="utf-8")


def _run_legacy(args, fixture: Path, repo: Path, slug: str, fm: dict,
                brief_text: str | None) -> int:
    """Single replay on the current checkout (no --ref). Unchanged behavior:
    recipes + hera.analysis follow whatever is installed/checked out."""
    config = args.config or (f"brief-{args.brief}" if args.brief else "baseline")
    recipes_dir = (repo / "hera" / "recipes") if args.recipes else None
    if recipes_dir and not recipes_dir.is_dir():
        recipes_dir = None

    ts = time.strftime("%Y%m%d-%H%M%S")
    run_dir = fixture / "runs" / slug / f"{config}-{ts}"
    workdir = run_dir / "workdir"
    manifest = _build_workdir(fixture, workdir, fm)
    prompt = _build_prompt(fixture, fm, repo, brief_text=brief_text, recipes_dir=recipes_dir)

    # Mandatory leak-check — abort before spending a run if anything leaked.
    hits = _leak_check(workdir, fm.get("leak_terms", []))
    _latest = fm.get("latest_fileid")
    _latest_str = f"data/{_latest}" if _latest not in (None, "", "none") else "cold start (no data)"
    print(f"frontier:  {slug}  (cut_index={fm['cut_index']}, latest={_latest_str})")
    print(f"run dir:   {run_dir}")
    print(f"data dirs: {manifest['data_dirs']}")
    print(f"images:    {manifest['images']}")
    if hits:
        print("\n❌ LEAK CHECK FAILED — answer-key terms found in workdir:")
        for rel, term in hits:
            print(f"   {rel}: '{term}'")
        print("Aborting. Fix the allowlist or the fixture; workdir left for inspection.")
        return 2
    print(f"leak-check: clean ({len(fm.get('leak_terms', []))} terms scanned) ✅")

    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")
    base_manifest = {"config": config, "frontier": slug, "brief": args.brief,
                     "recipes": bool(recipes_dir), "cut_index": fm["cut_index"],
                     "latest_fileid": fm.get("latest_fileid"),
                     "model_requested": args.model, "fixture": str(fixture), **manifest}
    (run_dir / "manifest.json").write_text(json.dumps(base_manifest, indent=2),
                                           encoding="utf-8")

    if args.dry_run:
        print("\n--- DRY RUN: prompt ---\n")
        print(prompt)
        return 0

    cmd = _build_claude_cmd(workdir, recipes_dir, prompt, args.model)
    samples, rc = _invoke_samples(cmd, workdir, run_dir, args.samples, args.timeout)
    base_manifest["samples"] = samples
    costs = [s["total_cost_usd"] for s in samples if s.get("total_cost_usd")]
    base_manifest["total_cost_usd"] = round(sum(costs), 4) if costs else None
    (run_dir / "manifest.json").write_text(json.dumps(base_manifest, indent=2),
                                           encoding="utf-8")
    print(f"\n{len(samples)} sample(s); total cost ${base_manifest['total_cost_usd']}")
    return rc


def _run_worker(task: dict) -> dict:
    """One cwd-isolated A/B worker: builds its OWN workdir under ``task['dest']``
    and runs a single ``claude -p``. Runs in a thread pool, so it never
    ``sys.exit``s — failures come back as ``error``/``exit`` fields on the result
    dict. cwd isolation (own workdir per worker) is the parallel-collision fix;
    the shared ~/.claude session is reused, not isolated."""
    dest, fixture, fm = task["dest"], task["fixture"], task["fm"]
    workdir = dest / "workdir"
    _build_workdir(fixture, workdir, fm)            # own workdir → no cross-worker races
    cmd = _build_claude_cmd(workdir, task["recipes_dir"], task["prompt"], task["model"])
    label, n = task["label"], task["sample"]
    print(f"  [start] {label} sample {n} (cwd={workdir})")
    try:
        res = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True,
                             timeout=task["timeout"], env=task["env"])
    except subprocess.TimeoutExpired:
        (dest / "stderr.txt").write_text(f"claude -p timed out after {task['timeout']}s",
                                         encoding="utf-8")
        print(f"  [TIMEOUT] {label} sample {n}")
        return {"sample": n, "label": label, "dest": str(dest), "error": "timeout"}

    (dest / "result.json").write_text(res.stdout, encoding="utf-8")
    if res.stderr.strip():
        (dest / "stderr.txt").write_text(res.stderr, encoding="utf-8")
    output_text, meta = res.stdout, {}
    try:
        data = _result_obj(json.loads(res.stdout))
        output_text = data.get("result", res.stdout)
        meta = _extract_run_meta(data)
    except json.JSONDecodeError:
        print(f"  [warn] {label} sample {n}: unparseable claude -p json output")
    (dest / "output.md").write_text(output_text, encoding="utf-8")
    print(f"  [done]  {label} sample {n}  exit={res.returncode}  "
          f"cost=${meta.get('total_cost_usd')}")
    return {"sample": n, "label": label, "dest": str(dest), "exit": res.returncode, **meta}


def _run_ab(args, fixture: Path, driver_repo: Path, slug: str, fm: dict,
            brief_text: str | None) -> int:
    """A/B-across-commits: pin each --ref's recipe corpus + hera.analysis to a
    per-commit worktree (recipes via --add-dir path, analysis via PYTHONPATH), so
    the levers follow the commit, not the installed package. The fixture is read
    from its canonical HEAD location; each (ref × sample) worker builds its OWN
    workdir (cheap hardlinks) so parallel workers don't collide on cwd. The `nb`
    helper stays on the synced driver repo — its version is irrelevant to the
    science. Concurrency is bounded by --max-parallel (default 1 = serial)."""
    pool = (Path(args.worktree_root).resolve() if args.worktree_root
            else Path(tempfile.gettempdir()) / "hera-replay-worktrees")
    # nb tooling runs from the synced main checkout (the git-common-dir's parent),
    # never a pool worktree (whose submodules are uninitialized) — nb's version is
    # irrelevant to the science, only recipes + hera.analysis follow the ref.
    common = subprocess.run(["git", "-C", str(driver_repo), "rev-parse",
                             "--git-common-dir"], capture_output=True, text=True)
    main_checkout = Path(common.stdout.strip()).resolve().parent if common.returncode == 0 else driver_repo
    ts = time.strftime("%Y%m%d-%H%M%S")
    run_root = fixture / "runs" / slug / f"ab-{ts}"
    run_root.mkdir(parents=True, exist_ok=True)
    leak_terms = fm.get("leak_terms", [])
    print(f"A/B frontier: {slug}  (cut_index={fm['cut_index']})")
    print(f"run root:     {run_root}")
    print(f"worktree pool:{pool}")
    print(f"nb project:   {main_checkout}")
    print(f"max-parallel: {args.max_parallel}")

    ref_ctx, tasks = [], []
    for ref in args.ref:
        sha, label = _resolve_ref(driver_repo, ref)
        wt = _ensure_worktree(driver_repo, pool, sha)
        recipes_dir = (wt / "hera" / "recipes") if args.recipes else None
        if recipes_dir and not recipes_dir.is_dir():
            sys.exit(f"--ref {ref}: {recipes_dir} missing in worktree "
                     f"(does {sha[:12]} predate the recipe corpus?)")
        pythonpath = wt / "src"
        ref_dest = run_root / f"{label}-{sha[:12]}"
        prompt = _build_prompt(fixture, fm, main_checkout, brief_text=brief_text,
                               recipes_dir=recipes_dir)

        # Pre-flight leak-check per ref (fail fast before spending any run) on a
        # throwaway workdir; the per-worker builds are identical so they need no
        # re-check.
        pf = run_root / f".preflight-{label}-{sha[:12]}"
        manifest = _build_workdir(fixture, pf / "workdir", fm)
        hits = _leak_check(pf / "workdir", leak_terms)
        shutil.rmtree(pf, ignore_errors=True)
        print(f"\n=== ref {label} ({sha[:12]}) ===")
        print(f"worktree:   {wt}")
        print(f"recipes:    {recipes_dir}")
        print(f"PYTHONPATH: {pythonpath}")
        print(f"dest:       {ref_dest}")
        if hits:
            print("❌ LEAK CHECK FAILED — answer-key terms in workdir:")
            for rel, term in hits:
                print(f"   {rel}: '{term}'")
            sys.exit("Aborting A/B — fix the allowlist or the fixture.")
        print(f"leak-check: clean ({len(leak_terms)} terms) ✅")

        ref_dest.mkdir(parents=True, exist_ok=True)
        (ref_dest / "prompt.md").write_text(prompt, encoding="utf-8")
        # Pin hera.analysis to the worktree's src (PYTHONPATH prepended → wins over
        # the editable install; the agent's Bash inherits it so a bare `python`
        # follows the commit). Bare `python` must be the driver's interpreter (the
        # synced main venv), so prepend its bin to PATH ahead of /usr/bin.
        env = dict(os.environ)
        venv_bin = str(Path(sys.executable).parent)
        env["PATH"] = f"{venv_bin}{os.pathsep}{env.get('PATH', '')}"
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (f"{pythonpath}{os.pathsep}{existing}" if existing
                             else str(pythonpath))

        ctx = {"ref": ref, "sha": sha, "label": label, "worktree": str(wt),
               "recipes_dir": str(recipes_dir) if recipes_dir else None,
               "pythonpath": str(pythonpath), "config": "ab", "frontier": slug,
               "brief": args.brief, "recipes": bool(recipes_dir),
               "cut_index": fm["cut_index"], "latest_fileid": fm.get("latest_fileid"),
               "model_requested": args.model, "fixture": str(fixture),
               "dest": str(ref_dest), **manifest}
        ref_ctx.append(ctx)

        if not args.dry_run:
            for i in range(1, args.samples + 1):
                wdest = ref_dest if args.samples == 1 else ref_dest / f"sample-{i}"
                tasks.append({"fixture": fixture, "fm": fm, "dest": wdest, "sample": i,
                              "label": label, "recipes_dir": recipes_dir, "prompt": prompt,
                              "model": args.model, "timeout": args.timeout, "env": env})

    if args.dry_run:
        for ctx in ref_ctx:
            ctx["samples"], ctx["total_cost_usd"] = [], None
            (Path(ctx["dest"]) / "manifest.json").write_text(json.dumps(ctx, indent=2),
                                                             encoding="utf-8")
        _write_comparison(run_root, fixture, slug, fm, args, ref_ctx)
        print("\n(dry-run: prompts + workdirs built, claude not invoked)")
        return 0

    # Run every (ref × sample) worker, cwd-isolated, bounded by --max-parallel.
    print(f"\nlaunching {len(tasks)} worker(s), max-parallel={args.max_parallel} ...")
    results = []
    with ThreadPoolExecutor(max_workers=max(1, args.max_parallel)) as ex:
        futs = [ex.submit(_run_worker, t) for t in tasks]
        for fut in as_completed(futs):
            results.append(fut.result())

    overall_rc = 0
    for ctx in ref_ctx:
        sams = sorted((r for r in results if r["label"] == ctx["label"]),
                      key=lambda r: r["sample"])
        for r in sams:
            overall_rc = overall_rc or r.get("exit") or (1 if r.get("error") else 0)
        ctx["samples"] = sams
        costs = [r["total_cost_usd"] for r in sams if r.get("total_cost_usd")]
        ctx["total_cost_usd"] = round(sum(costs), 4) if costs else None
        (Path(ctx["dest"]) / "manifest.json").write_text(json.dumps(ctx, indent=2),
                                                         encoding="utf-8")

    _write_comparison(run_root, fixture, slug, fm, args, ref_ctx)
    n_err = sum(1 for r in results if r.get("error") or r.get("exit"))
    print(f"\nA/B complete — {len(results)} run(s), {n_err} failed — "
          f"comparison at {run_root/'comparison.md'}")
    return overall_rc


def main(argv=None):
    ap = argparse.ArgumentParser(description="Offline HERA replay driver.")
    ap.add_argument("fixture", type=Path, help="fixture directory")
    ap.add_argument("--frontier", default=None,
                    help="frontier slug (default: the only one, if unambiguous)")
    ap.add_argument("--config", default=None,
                    help="config label for the run dir (default: brief variant, or 'baseline')")
    ap.add_argument("--brief", default=None,
                    help="brief variant under briefs/<slug>/ to use in place of the "
                         "campaign-goal framing (e.g. directive-short)")
    ap.add_argument("--ref", action="append", default=None,
                    help="git committish to pin recipes + hera.analysis to for an "
                         "A/B-across-commits run; repeat per side (--ref A --ref B). "
                         "Omit for a single replay on the current checkout.")
    ap.add_argument("--worktree-root", default=None,
                    help="pool dir for per-commit worktrees "
                         "(default: $TMPDIR/hera-replay-worktrees)")
    ap.add_argument("--max-parallel", type=int, default=1,
                    help="max concurrent A/B workers; default 1 = serial. Each worker "
                         "is cwd-isolated (its own workdir); the shared ~/.claude session "
                         "is reused, not isolated.")
    ap.add_argument("--model", default=None, help="model for claude -p")
    ap.add_argument("--samples", type=int, default=1,
                    help="number of independent samples (captures run-to-run variance); "
                         "carried through every --ref in an A/B run")
    ap.add_argument("--no-recipes", dest="recipes", action="store_false", default=True,
                    help="ablate recipe-corpus access (lever #3); default is ON, "
                         "matching a live session")
    ap.add_argument("--dry-run", action="store_true",
                    help="build workdir + leak-check + prompt, do not invoke claude")
    ap.add_argument("--timeout", type=int, default=900,
                    help="claude -p timeout (s); classification-grade per-column "
                         "FFT reads run ~10 min/sample, so the floor is 15 min")
    args = ap.parse_args(argv)

    fixture = args.fixture.resolve()
    driver_repo = Path(__file__).resolve().parents[2]
    slug, fm = _resolve_frontier(fixture, args.frontier)
    brief_text = _load_brief(fixture, slug, args.brief) if args.brief else None

    if args.ref:
        return _run_ab(args, fixture, driver_repo, slug, fm, brief_text)
    return _run_legacy(args, fixture, driver_repo, slug, fm, brief_text)


if __name__ == "__main__":
    raise SystemExit(main())
