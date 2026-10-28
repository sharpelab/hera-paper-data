"""Benchmark runner for HERA trajectory engine.

Ports the full feature set of ``hera-replay`` (``src/hera/replay.py``) onto the
``ReplayEngine`` CAS from ``hera.trajectory``. Every benchmark run produces a
trajectory graph: checkpoint snapshot -> prompt -> agent response.

Single-turn ("what's next?") is Phase 1. Multi-turn is designed but deferred.
"""

from __future__ import annotations

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
from typing import Any

import yaml

from hera.trajectory import ReplayEngine

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


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

_STATE_DATA = (
    "The measurement notebook ({notebook}) holds every cell that has run **so "
    "far**, with outputs preserved. The most recent sweep that landed is "
    "**data/{latest_fileid}/**; earlier sweeps are in the other `data/<id>/` "
    "directories (each has a `metadata.json` with the sweep function + "
    "parameters, a TSV, and a `plot.png`). Rendered cell plots are in `images/`."
)

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


# ---------------------------------------------------------------------------
# BenchmarkRunner
# ---------------------------------------------------------------------------

class BenchmarkRunner:
    """Offline replay driver that uses ReplayEngine for state management.

    Ports every feature of ``hera-replay`` onto the trajectory CAS. Each run
    produces a trajectory graph in the workdir so that any decision point can
    be forked and re-evaluated.
    """

    def __init__(self, checkpoint: Path, repo: Path):
        self.checkpoint = checkpoint.resolve()
        self.repo = repo.resolve()

    # ------------------------------------------------------------------
    # Checkpoint construction
    # ------------------------------------------------------------------

    @staticmethod
    def _read(path: Path) -> str:
        return path.read_text(encoding="utf-8")

    @staticmethod
    def _parse_frontmatter(text: str) -> tuple[dict, str]:
        if not text.startswith("---"):
            sys.exit("frontier file has no YAML frontmatter (--- block)")
        parts = text.split("---", 2)
        if len(parts) < 3:
            sys.exit("frontier file frontmatter not terminated by a second ---")
        fm = yaml.safe_load(parts[1]) or {}
        return fm, parts[2]

    def _resolve_frontier(self, slug: str | None) -> tuple[str, dict]:
        fdir = self.checkpoint / "frontiers"
        if not fdir.is_dir():
            sys.exit(f"{self.checkpoint}/frontiers/ not found — is this a checkpoint with frontiers?")
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
        fm, _ = self._parse_frontmatter(self._read(path))
        for key in ("cut_index", "included"):
            if key not in fm:
                sys.exit(f"{path.name} frontmatter missing required key: {key}")
        return path.stem, fm

    def _measure_notebook(self) -> Path:
        cands = sorted(self.checkpoint.glob("*measure*.ipynb"))
        if not cands:
            sys.exit(f"no *measure*.ipynb in {self.checkpoint}")
        return cands[0]

    @staticmethod
    def _crop_notebook(src: Path, dst: Path, cut_index: int) -> int:
        nb = json.loads(src.read_text(encoding="utf-8"))
        nb["cells"] = nb.get("cells", [])[: cut_index + 1]
        dst.write_text(json.dumps(nb, indent=1), encoding="utf-8")
        return len(nb["cells"])

    @staticmethod
    def _link_or_copy(src: Path, dst: Path) -> None:
        try:
            os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)

    @staticmethod
    def _link_tree(src: Path, dst: Path) -> None:
        try:
            shutil.copytree(src, dst, copy_function=os.link)
        except (OSError, shutil.Error):
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

    def _build_workdir(self, fm: dict, workdir: Path) -> dict:
        """Assemble the working copy from the checkpoint specification."""
        workdir.mkdir(parents=True, exist_ok=True)
        cut_index = fm["cut_index"]
        included = fm.get("included") or {}
        manifest: dict = {"included_files": [], "data_dirs": [], "images": []}

        card = self.checkpoint / "device_card.md"
        if card.exists():
            shutil.copy2(card, workdir / "device_card.md")
            manifest["included_files"].append("device_card.md")

        src_nb = self._measure_notebook()
        n = self._crop_notebook(src_nb, workdir / src_nb.name, cut_index)
        manifest["included_files"].append(f"{src_nb.name} (cropped to {n} cells)")

        (workdir / "data").mkdir(exist_ok=True)
        for did in included.get("data", []):
            src = self.checkpoint / "data" / str(did)
            if not src.is_dir():
                sys.exit(f"allowlist names data/{did} but it does not exist")
            self._link_tree(src, workdir / "data" / str(did))
            manifest["data_dirs"].append(str(did))

        (workdir / "images").mkdir(exist_ok=True)
        for img in included.get("images", []):
            src = self.checkpoint / "images" / img
            if not src.exists():
                sys.exit(f"allowlist names images/{img} but it does not exist")
            self._link_or_copy(src, workdir / "images" / img)
            manifest["images"].append(img)

        return manifest


    # ------------------------------------------------------------------
    # Prompt assembly
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_goal_quote(goal_text: str) -> str:
        for line in goal_text.splitlines():
            s = line.strip()
            if not s.startswith(">"):
                continue
            body = s.lstrip("> ").strip()
            if body.startswith("\u2014") or len(body) <= 3:
                continue
            return body.strip('"')
        return "Characterize the device per the campaign goal."

    def _load_brief(self, slug: str, variant: str) -> str:
        path = self.checkpoint / "briefs" / slug / f"{variant}.md"
        if not path.exists():
            avail = (
                sorted(p.stem for p in (self.checkpoint / "briefs" / slug).glob("*.md"))
                if (self.checkpoint / "briefs" / slug).is_dir()
                else []
            )
            sys.exit(
                f"brief '{variant}' not found for frontier '{slug}'; "
                f"available: {', '.join(avail) or '(none)'}"
            )
        text = re.sub(r"<!--.*?-->", "", self._read(path), flags=re.S)
        text = re.sub(r"^\s*#\s*Brief.*?\n", "", text, count=1)
        return text.strip()

    def _build_prompt(
        self,
        fm: dict,
        brief_text: str | None = None,
        recipes_dir: Path | None = None,
    ) -> str:
        if brief_text is not None:
            goal_heading = "Your brief (handed down from the strategic layer)"
            goal_body = brief_text
        else:
            goal_heading = "Campaign goal"
            goal_body = "Characterize the device per the campaign goal."
            gp = self.checkpoint / "goal.md"
            if gp.exists():
                goal_body = self._parse_goal_quote(self._read(gp))

        notebook = self._measure_notebook().name
        latest = fm.get("latest_fileid")
        cold = latest in (None, "", "none")
        state_block = (_STATE_COLD if cold else _STATE_DATA).format(
            notebook=notebook, latest_fileid=latest
        )
        if not cold and fm.get("cooldown_drift"):
            state_block += _DRIFT
        read_section = (_READ_COLD if cold else _READ_DATA).format(latest_fileid=latest)
        resources_block = _RESOURCES.format(recipes=recipes_dir) if recipes_dir else ""

        parts = self.checkpoint.name.split("-")
        device = parts[3] if len(parts) > 3 else self.checkpoint.name
        return _TASK_TEMPLATE.format(
            device=device,
            user=fm.get("user", "operator"),
            goal_heading=goal_heading,
            goal_body=goal_body,
            state_block=state_block,
            read_section=read_section,
            resources_block=resources_block,
            repo=self.repo,
        )

    # ------------------------------------------------------------------
    # Agent invocation
    # ------------------------------------------------------------------

    @staticmethod
    def _build_claude_cmd(
        workdir: Path,
        recipes_dir: Path | None,
        prompt: str,
        model: str | None,
    ) -> list[str]:
        cmd = [
            "claude", "-p", prompt,
            "--add-dir", str(workdir),
            "--allowedTools", "Read", "Bash", "Glob", "Grep",
            "--output-format", "json",
        ]
        if recipes_dir:
            cmd += ["--add-dir", str(recipes_dir)]
        if model:
            cmd += ["--model", model]
        return cmd

    @staticmethod
    def _result_obj(parsed):
        if isinstance(parsed, dict):
            return parsed
        if isinstance(parsed, list):
            for item in reversed(parsed):
                if isinstance(item, dict) and item.get("type") == "result":
                    return item
            for item in reversed(parsed):
                if isinstance(item, dict):
                    return item
        return {}

    @staticmethod
    def _extract_run_meta(data: dict) -> dict:
        meta: dict[str, Any] = {
            "total_cost_usd": data.get("total_cost_usd"),
            "num_turns": data.get("num_turns"),
            "duration_ms": data.get("duration_ms"),
            "usage": data.get("usage"),
        }
        model = data.get("model")
        if not model:
            mu = data.get("modelUsage")
            if isinstance(mu, dict) and mu:
                model = ",".join(mu.keys())
        meta["model_resolved"] = model
        return {k: v for k, v in meta.items() if v is not None}

    def _invoke_samples(
        self,
        cmd: list[str],
        workdir: Path,
        engine: ReplayEngine,
        checkpoint_event_id: str,
        dest_dir: Path,
        n_samples: int,
        timeout: int,
        prompt_text: str = "",
        env: dict | None = None,
    ) -> tuple[list[dict], int]:
        """Run ``claude -p`` ``n_samples`` times. Each sample branches from
        ``checkpoint_event_id`` — independent draws, not a sequential chain.
        Stores prompt/response content in event metadata for replayability."""
        samples, rc = [], 0
        for i in range(1, n_samples + 1):
            dest = dest_dir if n_samples == 1 else dest_dir / f"sample-{i}"
            dest.mkdir(parents=True, exist_ok=True)
            tag = "" if n_samples == 1 else f" [sample {i}/{n_samples}]"
            print(f"\ninvoking claude -p{tag} (cwd={workdir}, timeout={timeout}s) ...")

            # Branch from the checkpoint snapshot — independent draws
            prompt_event_id = engine.log_event(
                action={"type": "AgentPrompt", "sample": i},
                metadata={
                    "n_samples": n_samples,
                    "timeout": timeout,
                    "prompt_text": prompt_text[:2000],
                    "prompt_file": str(dest / "prompt.md"),
                },
                parent_id=checkpoint_event_id,
            )

            (dest / "prompt.md").write_text(prompt_text, encoding="utf-8")

            try:
                res = subprocess.run(
                    cmd, cwd=workdir, capture_output=True, text=True,
                    timeout=timeout, env=env,
                )
            except subprocess.TimeoutExpired:
                sys.exit(f"claude -p timed out after {timeout}s")

            rc = rc or res.returncode

            (dest / "result.json").write_text(res.stdout, encoding="utf-8")
            if res.stderr.strip():
                (dest / "stderr.txt").write_text(res.stderr, encoding="utf-8")

            output_text, run_meta = res.stdout, {}
            try:
                data = self._result_obj(json.loads(res.stdout))
                output_text = data.get("result", res.stdout)
                run_meta = self._extract_run_meta(data)
            except json.JSONDecodeError:
                print("warning: could not parse claude -p json output; saved raw stdout")

            (dest / "output.md").write_text(output_text, encoding="utf-8")

            # Response is child of the prompt event
            engine.log_event(
                action={"type": "AgentResponse", "sample": i,
                        "exit_code": res.returncode},
                metadata={
                    "output_file": str(dest / "output.md"),
                    "response_summary": output_text[:2000],
                    **run_meta,
                },
                parent_id=prompt_event_id,
            )

            samples.append({"sample": i, "dest": str(dest), **run_meta})
            print(
                f"  exit={res.returncode}  -> {dest / 'output.md'}  "
                f"(model={run_meta.get('model_resolved')}, "
                f"cost=${run_meta.get('total_cost_usd')})"
            )
        return samples, rc

    # ------------------------------------------------------------------
    # A/B across commits
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_ref(git_repo: Path, ref: str) -> tuple[str, str]:
        res = subprocess.run(
            ["git", "-C", str(git_repo), "rev-parse", "--verify", f"{ref}^{{commit}}"],
            capture_output=True, text=True,
        )
        if res.returncode != 0:
            sys.exit(
                f"--ref {ref!r}: not a valid commit in {git_repo} "
                f"({res.stderr.strip()})"
            )
        label = re.sub(r"[^A-Za-z0-9._-]", "_", ref)
        return res.stdout.strip(), label

    @staticmethod
    def _ensure_worktree(git_repo: Path, pool: Path, sha: str) -> Path:
        pool.mkdir(parents=True, exist_ok=True)
        wt = pool / sha[:12]
        if wt.is_dir():
            return wt
        res = subprocess.run(
            ["git", "-C", str(git_repo), "worktree", "add", "--detach", str(wt), sha],
            capture_output=True, text=True,
        )
        if res.returncode != 0:
            sys.exit(f"git worktree add failed for {sha[:12]}: {res.stderr.strip()}")
        return wt

    @staticmethod
    def _write_comparison(
        run_root: Path,
        checkpoint: Path,
        frontier_name: str,
        fm: dict,
        model: str | None,
        samples_per_ref: int,
        ref_results: list[dict],
    ) -> None:
        out = []
        out.append(f"# A/B replay comparison — {checkpoint.name}")
        out.append("")
        out.append(
            f"- **Frontier:** `{frontier_name}` (cut_index={fm['cut_index']}, "
            f"latest=data/{fm.get('latest_fileid')})"
        )
        out.append(f"- **Model:** {model or '(default)'}  \u2022  "
                    f"**Samples/ref:** {samples_per_ref}")
        out.append(f"- **Run root:** `{run_root}`")
        out.append("")
        out.append("## Pinning audit")
        out.append("")
        out.append("| ref | sha | recipes (pinned to worktree) | PYTHONPATH | pinned |")
        out.append("|---|---|---|---|---|")
        for r in ref_results:
            rec, wt = r.get("recipes_dir"), r.get("worktree")
            pinned = "\u2705" if (rec and wt and str(rec).startswith(str(wt))) else "\u2014"
            out.append(
                f"| `{r['label']}` | `{r['sha'][:12]}` | `{rec}` | "
                f"`{r.get('pythonpath')}` | {pinned} |"
            )
        out.append("")
        out.append("## Cost")
        out.append("")
        out.append("| ref | total $ | per-sample $ |")
        out.append("|---|---|---|")
        for r in ref_results:
            per = (
                ", ".join(str(s.get("total_cost_usd")) for s in r.get("samples", []))
                or "\u2014"
            )
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
        out.append(
            "> Phase 0a: pinning audit + cost + raw side-by-side. Science-axis "
            "extraction (sensitivity / settling / N_B\u00d7N_n) is Phase 0b."
        )
        (run_root / "comparison.md").write_text("\n".join(out) + "\n", encoding="utf-8")
        (run_root / "comparison.json").write_text(
            json.dumps(
                {
                    "checkpoint": str(checkpoint),
                    "frontier": frontier_name,
                    "samples_per_ref": samples_per_ref,
                    "model": model,
                    "refs": ref_results,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    # ------------------------------------------------------------------

    def run_single(self, *, slug: str, fm: dict, config: str | None,
                   brief_text: str | None, recipes: bool, model: str | None,
                   samples: int, timeout: int, dry_run: bool) -> int:
        """Single replay on the current checkout (no --ref)."""
        config = config or (f"brief-{brief_text}" if brief_text else "baseline")
        recipes_dir = (self.repo / "hera" / "recipes") if recipes else None
        if recipes_dir and not recipes_dir.is_dir():
            recipes_dir = None

        ts = time.strftime("%Y%m%d-%H%M%S")
        run_dir = self.checkpoint / "runs" / slug / f"{config}-{ts}"
        workdir = run_dir / "workdir"
        manifest = self._build_workdir(fm, workdir)
        prompt = self._build_prompt(fm, brief_text=brief_text, recipes_dir=recipes_dir)

        _latest = fm.get("latest_fileid")

        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")

        # Initialize trajectory in the workdir and capture the checkpoint snapshot
        engine = ReplayEngine(workdir)
        engine.init()
        checkpoint_event_id = engine.log_event(
            action={"type": "CheckpointSnapshot"},
            metadata={
                "checkpoint": str(self.checkpoint),
                "frontier": slug,
                "cut_index": fm["cut_index"],
                "latest_fileid": _latest,
                **manifest,
            },
        )

        base_manifest: dict[str, Any] = {
            "config": config,
            "frontier": slug,
            "brief": brief_text,
            "recipes": bool(recipes_dir),
            "cut_index": fm["cut_index"],
            "latest_fileid": fm.get("latest_fileid"),
            "model_requested": model,
            "checkpoint": str(self.checkpoint),
            "trajectory_checkpoint_event": checkpoint_event_id,
            **manifest,
        }
        (run_dir / "manifest.json").write_text(
            json.dumps(base_manifest, indent=2), encoding="utf-8"
        )

        if dry_run:
            print("\n--- DRY RUN: prompt ---\n")
            print(prompt)
            return 0

        cmd = self._build_claude_cmd(workdir, recipes_dir, prompt, model)
        samples_list, rc = self._invoke_samples(
            cmd, workdir, engine, checkpoint_event_id, run_dir, samples, timeout,
            prompt_text=prompt,
        )
        base_manifest["samples"] = samples_list
        costs = [s.get("total_cost_usd") for s in samples_list if s.get("total_cost_usd")]
        base_manifest["total_cost_usd"] = round(sum(costs), 4) if costs else None
        (run_dir / "manifest.json").write_text(
            json.dumps(base_manifest, indent=2), encoding="utf-8"
        )
        print(f"\n{samples} sample(s); total cost ${base_manifest['total_cost_usd']}")
        return rc

    def run_ab(
        self,
        *,
        slug: str,
        fm: dict,
        refs: list[str],
        worktree_root: Path,
        max_parallel: int,
        brief_text: str | None,
        recipes: bool,
        model: str | None,
        samples: int,
        timeout: int,
    ) -> int:
        """A/B-across-commits: pin each --ref to a worktree, run full flow per side."""
        ts = time.strftime("%Y%m%d-%H%M%S")
        run_root = self.checkpoint / "runs" / slug / f"ab-{ts}"

        # Resolve all refs first
        ref_ctx: list[dict] = []
        for ref in refs:
            sha, label = self._resolve_ref(self.repo, ref)
            wt = self._ensure_worktree(self.repo, worktree_root, sha)
            ref_ctx.append({"ref": ref, "sha": sha, "label": label, "worktree": wt})

        # Build tasks — one per (ref, sample)
        tasks: list[dict] = []
        for ctx_ in ref_ctx:
            recipes_dir = (ctx_["worktree"] / "hera" / "recipes") if recipes else None
            if recipes_dir and not recipes_dir.is_dir():
                recipes_dir = None
            pythonpath = str(ctx_["worktree"] / "src")
            env = {**os.environ, "PYTHONPATH": pythonpath}
            prompt = self._build_prompt(fm, brief_text=brief_text, recipes_dir=recipes_dir)

            for n in range(1, samples + 1):
                dest = (
                    run_root / ctx_["label"] / f"sample-{n}"
                    if samples > 1
                    else run_root / ctx_["label"]
                )
                dest.mkdir(parents=True, exist_ok=True)
                workdir = dest / "workdir"
                self._build_workdir(fm, workdir)



                tasks.append({
                    "dest": dest,
                    "workdir": workdir,
                    "checkpoint": self.checkpoint,
                    "fm": fm,
                    "prompt": prompt,
                    "recipes_dir": recipes_dir,
                    "model": model,
                    "label": ctx_["label"],
                    "sample": n,
                    "timeout": timeout,
                    "env": env,
                })

        # Collect ref metadata
        for ctx_ in ref_ctx:
            recipes_dir = (ctx_["worktree"] / "hera" / "recipes") if recipes else None
            if recipes_dir and not recipes_dir.is_dir():
                recipes_dir = None
            pythonpath = str(ctx_["worktree"] / "src")
            ctx_["recipes_dir"] = str(recipes_dir) if recipes_dir else None
            ctx_["pythonpath"] = pythonpath
            ctx_["samples"] = []

        # Execute tasks in parallel
        results: list[dict] = []
        with ThreadPoolExecutor(max_workers=max(1, max_parallel)) as ex:
            futs = [ex.submit(_run_ab_worker, t) for t in tasks]
            for fut in as_completed(futs):
                results.append(fut.result())

        # Aggregate
        overall_rc = 0
        for ctx_ in ref_ctx:
            sams = sorted(
                (r for r in results if r["label"] == ctx_["label"]),
                key=lambda r: r["sample"],
            )
            for r in sams:
                overall_rc = overall_rc or r.get("exit") or (1 if r.get("error") else 0)
            ctx_["samples"] = sams
            costs = [r.get("total_cost_usd") for r in sams if r.get("total_cost_usd")]
            ctx_["total_cost_usd"] = round(sum(costs), 4) if costs else None
            (Path(ctx_["dest"]) / "manifest.json").write_text(
                json.dumps(ctx_, indent=2, default=str), encoding="utf-8"
            )

        self._write_comparison(run_root, self.checkpoint, slug, fm, model, samples, ref_ctx)
        n_err = sum(1 for r in results if r.get("error") or r.get("exit"))
        print(
            f"\nA/B complete \u2014 {len(results)} run(s), {n_err} failed \u2014 "
            f"comparison at {run_root / 'comparison.md'}"
        )
        return overall_rc


# ---------------------------------------------------------------------------
# A/B worker (module-level, picklable for ThreadPoolExecutor)
# ---------------------------------------------------------------------------

def _run_ab_worker(task: dict) -> dict:
    """One cwd-isolated A/B worker: builds its OWN workdir and runs claude -p."""
    dest = task["dest"]
    workdir = task["workdir"]
    label, n = task["label"], task["sample"]
    cmd = BenchmarkRunner._build_claude_cmd(
        workdir, task["recipes_dir"], task["prompt"], task["model"]
    )
    print(f"  [start] {label} sample {n} (cwd={workdir})")

    # Initialize trajectory for this worker's workdir
    engine = ReplayEngine(workdir)
    engine.init()
    checkpoint_evt = engine.log_event(
        action={"type": "CheckpointSnapshot", "ref": label},
        metadata={"sample": n, "checkpoint": str(task.get("checkpoint", ""))},
    )
    prompt_evt = engine.log_event(
        action={"type": "AgentPrompt", "ref": label, "sample": n},
        metadata={
            "prompt_text": task["prompt"][:2000],
            "prompt_file": str(dest / "prompt.md"),
        },
        parent_id=checkpoint_evt,
    )
    (dest / "prompt.md").write_text(task["prompt"], encoding="utf-8")

    try:
        res = subprocess.run(
            cmd, cwd=workdir, capture_output=True, text=True,
            timeout=task["timeout"], env=task["env"],
        )
    except subprocess.TimeoutExpired:
        (dest / "stderr.txt").write_text(
            f"claude -p timed out after {task['timeout']}s", encoding="utf-8"
        )
        print(f"  [TIMEOUT] {label} sample {n}")
        return {"sample": n, "label": label, "dest": str(dest), "error": "timeout"}

    (dest / "result.json").write_text(res.stdout, encoding="utf-8")
    if res.stderr.strip():
        (dest / "stderr.txt").write_text(res.stderr, encoding="utf-8")

    output_text, meta = res.stdout, {}
    try:
        data = BenchmarkRunner._result_obj(json.loads(res.stdout))
        output_text = data.get("result", res.stdout)
        meta = BenchmarkRunner._extract_run_meta(data)
    except json.JSONDecodeError:
        print(f"  [warn] {label} sample {n}: unparseable claude -p json output")

    (dest / "output.md").write_text(output_text, encoding="utf-8")

    engine.log_event(
        action={"type": "AgentResponse", "ref": label, "sample": n,
                "exit_code": res.returncode},
        metadata={
            "output_file": str(dest / "output.md"),
            "response_summary": output_text[:2000],
            **meta,
        },
        parent_id=prompt_evt,
    )

    print(
        f"  [done]  {label} sample {n}  exit={res.returncode}  "
        f"cost=${meta.get('total_cost_usd')}"
    )
    return {"sample": n, "label": label, "dest": str(dest),
            "exit": res.returncode, **meta}
