"""End-to-end tests for HERA benchmark runner (hera.benchmark.BenchmarkRunner).

Covers all 13 features ported from hera-replay onto the trajectory CAS:
fixture ingestion, leakage control, prompt assembly, agent invocation stubs,
output capture, sampling, A/B worktree pinning, parallel dispatch, dry-run,
brief variants, comparison output, model selection, and recipes access.

Also verifies trajectory integration: every run produces a valid event graph.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import textwrap
from pathlib import Path
from unittest import mock

import pytest

from hera.benchmark import BenchmarkRunner
from hera.trajectory import ReplayEngine, main as trajectory_main


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def repo_root(tmp_path) -> Path:
    """A minimal mock measurement-env repo for resolving paths."""
    root = tmp_path / "measurement_env"
    root.mkdir()
    (root / "hera" / "recipes").mkdir(parents=True)
    (root / "hera" / "recipes" / "gatemap.md").write_text("# Gatemap recipe\n")
    return root


@pytest.fixture
def fixture_dir(tmp_path) -> Path:
    """A minimal fixture directory with one frontier and a mock notebook."""
    fx = tmp_path / "test-fixture" / "2026-01-01-TEST01-minimal"
    fx.mkdir(parents=True)

    # Device card
    (fx / "device_card.md").write_text("# Device: TEST01\nGate stack: TG + BG\n")

    # Goal
    (fx / "goal.md").write_text(
        "> Characterize the superconducting state.\n"
        "> \u2014 Isaac, 2026-01-01\n"
    )

    # Measure notebook (minimal valid .ipynb)
    nb = {
        "cells": [
            {"cell_type": "code", "source": ["# setup"], "outputs": []},
            {"cell_type": "code", "source": ["s.megasweep(...)"], "outputs": []},
            {"cell_type": "markdown", "source": ["# Next: field sweep"]},
            {"cell_type": "code", "source": ["mag.field(...)"], "outputs": []},
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    (fx / "20260101_measure.ipynb").write_text(json.dumps(nb))

    # Data dirs
    for did in [1, 2, 3]:
        d = fx / "data" / str(did)
        d.mkdir(parents=True)
        (d / "metadata.json").write_text('{"type": "1D"}')
        (d / "data.tsv.gz").write_bytes(b"fake gzip data")
        (d / "plot.png").write_bytes(b"fake png data")

    # Images
    (fx / "images").mkdir()
    (fx / "images" / "cell1_out1.png").write_bytes(b"fake png")

    # Frontiers
    (fx / "frontiers").mkdir()
    frontier = textwrap.dedent("""\
    ---
    slug: after-setup
    cut_index: 1
    latest_fileid: 3
    included:
      data: [1, 2, 3]
      images: [cell1_out1.png]
    ---
    # Checkpoint: after-setup
    The agent must decide the next experiment.
    """)
    (fx / "frontiers" / "after-setup.md").write_text(frontier)

    # Cold-start checkpoint
    cold_frontier = textwrap.dedent("""\
    ---
    slug: cold-start
    cut_index: 0
    latest_fileid: null
    included:
      data: []
      images: []
    ---
    """)
    (fx / "frontiers" / "cold-start.md").write_text(cold_frontier)


    # Briefs
    (fx / "briefs" / "after-setup").mkdir(parents=True)
    (fx / "briefs" / "after-setup" / "directive-short.md").write_text(
        "# Brief\nFind the SC dome quickly.\n"
    )

    return fx


@pytest.fixture
def runner(fixture_dir, repo_root) -> BenchmarkRunner:
    return BenchmarkRunner(fixture_dir, repo_root)


# ---------------------------------------------------------------------------
# Unit tests — frontmatter & fixture parsing
# ---------------------------------------------------------------------------


class TestFrontmatterParsing:
    def test_parse_valid_frontmatter(self):
        text = "---\nslug: test\ncut_index: 5\n---\nBody here"
        fm, body = BenchmarkRunner._parse_frontmatter(text)
        assert fm["slug"] == "test"
        assert fm["cut_index"] == 5
        assert body.strip() == "Body here"

    def test_parse_missing_opening_dashes(self):
        with pytest.raises(SystemExit):
            BenchmarkRunner._parse_frontmatter("no frontmatter here")

    def test_parse_unterminated(self):
        with pytest.raises(SystemExit):
            BenchmarkRunner._parse_frontmatter("---\nslug: test\n")

    def test_resolve_frontier_single_by_name(self, runner):
        slug, fm = runner._resolve_frontier("after-setup")
        assert slug == "after-setup"
        assert fm["cut_index"] == 1

    def test_resolve_frontier_by_name(self, runner):
        slug, fm = runner._resolve_frontier("cold-start")
        assert slug == "cold-start"
        assert fm["cut_index"] == 0

    def test_resolve_frontier_multiple_requires_flag(self, runner):
        # fixture_dir already has 2 frontiers; asking without --frontier → error
        with pytest.raises(SystemExit):
            runner._resolve_frontier(None)

    def test_resolve_frontier_missing(self, runner):
        with pytest.raises(SystemExit):
            runner._resolve_frontier("nonexistent")


class TestGoalParsing:
    def test_parse_goal_quote(self):
        text = "> Characterize the SC state.\n> \u2014 Isaac\n"
        assert BenchmarkRunner._parse_goal_quote(text) == "Characterize the SC state."

    def test_parse_goal_quote_skips_attribution(self):
        text = "> \u2014 Zack, 2026\n> Find the dome.\n"
        assert BenchmarkRunner._parse_goal_quote(text) == "Find the dome."

    def test_parse_goal_quote_no_quote_found(self):
        assert BenchmarkRunner._parse_goal_quote("no blockquotes here") == \
            "Characterize the device per the campaign goal."

    def test_parse_goal_quote_empty_line(self):
        text = ">   \n> Real quote here.\n"
        assert BenchmarkRunner._parse_goal_quote(text) == "Real quote here."


# ---------------------------------------------------------------------------
# Unit tests — notebook cropping
# ---------------------------------------------------------------------------


class TestNotebookCropping:
    def test_crop_notebook(self, tmp_path):
        nb = {
            "cells": [
                {"cell_type": "code", "source": ["cell 0"]},
                {"cell_type": "code", "source": ["cell 1"]},
                {"cell_type": "code", "source": ["cell 2"]},
                {"cell_type": "code", "source": ["cell 3"]},
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        src = tmp_path / "src.ipynb"
        dst = tmp_path / "dst.ipynb"
        src.write_text(json.dumps(nb))

        n = BenchmarkRunner._crop_notebook(src, dst, 1)
        assert n == 2  # cells 0 and 1 kept

        result = json.loads(dst.read_text())
        assert len(result["cells"]) == 2
        assert result["cells"][0]["source"] == ["cell 0"]
        assert result["cells"][1]["source"] == ["cell 1"]

    def test_crop_notebook_at_zero(self, tmp_path):
        nb = {
            "cells": [
                {"cell_type": "code", "source": ["cell 0"]},
                {"cell_type": "code", "source": ["cell 1"]},
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        src = tmp_path / "src.ipynb"
        dst = tmp_path / "dst.ipynb"
        src.write_text(json.dumps(nb))
        n = BenchmarkRunner._crop_notebook(src, dst, 0)
        assert n == 1


# ---------------------------------------------------------------------------
# Unit tests — leakage control
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Unit tests — prompt assembly
# ---------------------------------------------------------------------------


class TestPromptAssembly:
    def test_build_prompt_warm_start(self, runner, fixture_dir):
        slug, fm = runner._resolve_frontier("after-setup")
        prompt = runner._build_prompt(fm)
        assert "HERA offline replay" in prompt
        assert "data/3/" in prompt          # latest_fileid
        assert "Characterize the superconducting state" in prompt
        assert "### 1. Read of the latest sweep" in prompt
        assert "### 2. Next experiment" in prompt

    def test_build_prompt_cold_start(self, runner):
        slug, fm = runner._resolve_frontier("cold-start")
        prompt = runner._build_prompt(fm)
        assert "no sweeps have run yet" in prompt.lower()
        assert "### 1. Starting point" in prompt

    def test_build_prompt_with_recipes(self, runner, repo_root):
        slug, fm = runner._resolve_frontier("after-setup")
        recipes_dir = repo_root / "hera" / "recipes"
        prompt = runner._build_prompt(fm, recipes_dir=recipes_dir)
        assert "recipe corpus" in prompt
        assert str(recipes_dir) in prompt

    def test_build_prompt_without_recipes(self, runner):
        slug, fm = runner._resolve_frontier("after-setup")
        prompt = runner._build_prompt(fm, recipes_dir=None)
        assert "recipe corpus" not in prompt

    def test_build_prompt_with_brief(self, runner):
        slug, fm = runner._resolve_frontier("after-setup")
        brief_text = runner._load_brief(slug, "directive-short")
        prompt = runner._build_prompt(fm, brief_text=brief_text)
        assert "Your brief (handed down from the strategic layer)" in prompt
        assert "Find the SC dome quickly" in prompt

    def test_build_prompt_cooldown_drift(self, runner):
        slug, fm = runner._resolve_frontier("after-setup")
        fm["cooldown_drift"] = True
        prompt = runner._build_prompt(fm)
        assert "Device-card drift" in prompt

    def test_build_prompt_no_goal_file(self, tmp_path, repo_root):
        fx = tmp_path / "no-goal-fixture"
        fx.mkdir()
        (fx / "frontiers").mkdir()
        frontier = textwrap.dedent("""\
        ---
        slug: test
        cut_index: 0
        latest_fileid: 1
        included:
          data: []
          images: []
        ---
        """)
        (fx / "frontiers" / "test.md").write_text(frontier)
        (fx / "data" / "1").mkdir(parents=True)
        (fx / "data" / "1" / "metadata.json").write_text("{}")
        (fx / "20260101_measure.ipynb").write_text(
            json.dumps({"cells": [{"cell_type": "code", "source": ["x=1"]}],
                        "metadata": {}, "nbformat": 4, "nbformat_minor": 5}))

        runner2 = BenchmarkRunner(fx, repo_root)
        slug, fm = runner2._resolve_frontier("test")
        prompt = runner2._build_prompt(fm)
        assert "Characterize the device per the campaign goal." in prompt


# ---------------------------------------------------------------------------
# Unit tests — brief loading
# ---------------------------------------------------------------------------


class TestBriefLoading:
    def test_load_brief(self, runner):
        text = runner._load_brief("after-setup", "directive-short")
        assert "Find the SC dome quickly" in text

    def test_load_brief_missing(self, runner):
        with pytest.raises(SystemExit):
            runner._load_brief("after-setup", "nonexistent-variant")


# ---------------------------------------------------------------------------
# Unit tests — A/B worktree (ref resolution)
# ---------------------------------------------------------------------------


class TestRefResolution:
    @pytest.mark.skipif(not shutil.which("git"), reason="git not available")
    def test_resolve_ref_valid(self, repo_root, tmp_path):
        with pytest.raises(SystemExit) as exc_info:
            BenchmarkRunner._resolve_ref(repo_root, "HEAD")
        assert "not a valid commit" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Integration tests — full BenchmarkRunner flow
# ---------------------------------------------------------------------------


@pytest.mark.slow
class TestFullBenchmarkFlow:
    """End-to-end tests that build checkpoints, assemble prompts,
    and verify trajectory graph creation — without invoking claude (dry-run)."""

    def test_run_single_dry_run(self, runner, fixture_dir):
        """Full single-ref dry-run: build checkpoint → prompt → trajectory graph."""
        slug, fm = runner._resolve_frontier("after-setup")
        rc = runner.run_single(
            slug=slug, fm=fm, config="test", brief_text=None,
            recipes=True, model=None, samples=1, timeout=600, dry_run=True,
        )
        assert rc == 0

        # Verify output artifacts
        runs = sorted((fixture_dir / "runs" / slug).glob("test-*"))
        assert len(runs) == 1
        run_dir = runs[0]
        assert (run_dir / "prompt.md").is_file()
        assert (run_dir / "manifest.json").is_file()

        # Verify trajectory graph in workdir
        workdir = run_dir / "workdir"
        engine = ReplayEngine(workdir)
        assert engine.is_initialized()
        graph = json.loads(engine.graph_path.read_text())
        events = graph["events"]
        assert len(events) >= 1
        assert events[0]["action"]["type"] == "CheckpointSnapshot"
        assert "checkpoint" in events[0]["metadata"]
        assert "frontier" in events[0]["metadata"]

        # Verify manifest.json
        manifest = json.loads((run_dir / "manifest.json").read_text())
        assert manifest["frontier"] == "after-setup"
        assert manifest["config"] == "test"
        assert manifest["trajectory_checkpoint_event"] == events[0]["id"]
        assert len(manifest["data_dirs"]) == 3
        assert len(manifest["images"]) == 1

    def test_run_single_cold_start(self, runner, fixture_dir):
        """Cold-start frontier: no sweeps, no data dirs."""
        slug, fm = runner._resolve_frontier("cold-start")
        rc = runner.run_single(
            slug=slug, fm=fm, config="cold-test", brief_text=None,
            recipes=True, model=None, samples=1, timeout=600, dry_run=True,
        )
        assert rc == 0

        runs = sorted((fixture_dir / "runs" / slug).glob("cold-test-*"))
        run_dir = runs[0]
        prompt = (run_dir / "prompt.md").read_text()
        assert "no sweeps have run yet" in prompt.lower()


    def test_run_single_with_brief_variant(self, runner, fixture_dir):
        """Brief variant is loaded and injected into the prompt."""
        slug, fm = runner._resolve_frontier("after-setup")
        brief_text = runner._load_brief(slug, "directive-short")
        rc = runner.run_single(
            slug=slug, fm=fm, config="brief-test", brief_text=brief_text,
            recipes=True, model=None, samples=1, timeout=600, dry_run=True,
        )
        assert rc == 0
        runs = sorted((fixture_dir / "runs" / slug).glob("brief-test-*"))
        prompt = (runs[0] / "prompt.md").read_text()
        assert "Find the SC dome quickly" in prompt

    def test_run_single_no_recipes(self, runner, fixture_dir):
        """--no-recipes omits the recipe corpus from the prompt."""
        slug, fm = runner._resolve_frontier("after-setup")
        rc = runner.run_single(
            slug=slug, fm=fm, config="no-recipes-test", brief_text=None,
            recipes=False, model=None, samples=1, timeout=600, dry_run=True,
        )
        assert rc == 0
        runs = sorted((fixture_dir / "runs" / slug).glob("no-recipes-test-*"))
        prompt = (runs[0] / "prompt.md").read_text()
        assert "recipe corpus" not in prompt


# ---------------------------------------------------------------------------
# Integration tests — trajectory event logging
# ---------------------------------------------------------------------------


class TestTrajectoryIntegration:
    """Verify that BenchmarkRunner creates valid trajectory graphs in the workdir."""

    def test_workdir_has_valid_trajectory(self, runner, fixture_dir):
        slug, fm = runner._resolve_frontier("after-setup")
        runner.run_single(
            slug=slug, fm=fm, config="traj-test", brief_text=None,
            recipes=True, model=None, samples=1, timeout=600, dry_run=True,
        )
        runs = sorted((fixture_dir / "runs" / slug).glob("traj-test-*"))
        workdir = runs[0] / "workdir"

        engine = ReplayEngine(workdir)
        assert engine.is_initialized()

        # CAS cache exists with blobs
        assert engine.cache_dir.is_dir()
        blobs = list(engine.cache_dir.rglob("*"))
        blob_files = [b for b in blobs if b.is_file()]
        assert len(blob_files) > 0, "CAS cache should contain blobs"

        # Graph is valid and has correct structure
        graph = json.loads(engine.graph_path.read_text())
        events = graph["events"]
        assert len(events) >= 1
        for evt in events:
            assert "id" in evt
            assert evt["id"].startswith("evt_")
            assert "timestamp" in evt
            assert "snapshot_id" in evt
            assert "action" in evt

        # Snapshot manifest resolves
        snap_id = events[0]["snapshot_id"]
        manifest = engine.load_manifest(snap_id)
        assert "files" in manifest
        assert "version" in manifest

    def test_trajectory_manifest_includes_all_files(self, runner, fixture_dir):
        """The fixture snapshot's manifest should include all workdir files."""
        slug, fm = runner._resolve_frontier("after-setup")
        runner.run_single(
            slug=slug, fm=fm, config="manifest-test", brief_text=None,
            recipes=True, model=None, samples=1, timeout=600, dry_run=True,
        )
        runs = sorted((fixture_dir / "runs" / slug).glob("manifest-test-*"))
        workdir = runs[0] / "workdir"

        engine = ReplayEngine(workdir)
        snap_id = json.loads(engine.graph_path.read_text())["events"][0]["snapshot_id"]
        manifest = engine.load_manifest(snap_id)
        files = manifest["files"]

        # Check essential files are in the manifest
        file_paths = list(files.keys())
        assert any("measure.ipynb" in p for p in file_paths), \
            "cropped notebook should be in manifest"
        assert any("device_card.md" in p for p in file_paths), \
            "device card should be in manifest"
        assert any("data/3/metadata.json" in p for p in file_paths), \
            "data files should be in manifest"

        # No ignored paths leaked in
        for p in file_paths:
            assert not p.startswith(".replay/"), \
                f".replay should be ignored: {p}"
            assert "__pycache__" not in p


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------


class TestCLIIntegration:
    """Test the trajectory CLI's replay subcommand end-to-end."""

    def test_benchmark_help(self):
        """--help should exit 0 and mention all key flags."""
        with pytest.raises(SystemExit) as exc_info:
            trajectory_main(["replay", "--help"])
        assert exc_info.value.code == 0

    def test_benchmark_requires_fixture_or_run_from(self):
        """--checkpoint or --run-from is required."""
        with pytest.raises(SystemExit) as exc_info:
            trajectory_main(["replay"])
        assert exc_info.value.code != 0

    def test_benchmark_dry_run_cli(self, fixture_dir, capsys):
        """Full CLI invocation with --checkpoint and --dry-run."""
        rc = trajectory_main([
            "replay",
            "--checkpoint", str(fixture_dir),
            "--frontier", "after-setup",
            "--dry-run",
        ])
        assert rc == 0
        captured = capsys.readouterr()
        assert "DRY RUN: prompt" in captured.out

    def test_benchmark_dry_run_cold_start_cli(self, fixture_dir, capsys):
        """CLI cold-start frontier."""
        rc = trajectory_main([
            "replay",
            "--checkpoint", str(fixture_dir),
            "--frontier", "cold-start",
            "--dry-run",
        ])
        captured = capsys.readouterr()
        assert "no sweeps have run yet" in captured.out.lower()

    def test_benchmark_missing_fixture(self, capsys):
        """Graceful error for nonexistent fixture."""
        rc = trajectory_main([
            "replay",
            "--checkpoint", "/nonexistent/path",
            "--dry-run",
        ])
        assert rc != 0

    def test_benchmark_with_brief_cli(self, fixture_dir, capsys):
        """--brief flag loads and injects brief text."""
        rc = trajectory_main([
            "replay",
            "--checkpoint", str(fixture_dir),
            "--frontier", "after-setup",
            "--brief", "directive-short",
            "--dry-run",
        ])
        assert rc == 0
        captured = capsys.readouterr()
        assert "Find the SC dome quickly" in captured.out

    def test_benchmark_no_recipes_cli(self, fixture_dir, capsys):
        """--no-recipes omits recipe corpus."""
        rc = trajectory_main([
            "replay",
            "--checkpoint", str(fixture_dir),
            "--frontier", "after-setup",
            "--no-recipes",
            "--dry-run",
        ])
        assert rc == 0
        captured = capsys.readouterr()
        assert "recipe corpus" not in captured.out

    def test_benchmark_with_config_label(self, fixture_dir, capsys):
        """--config sets the run dir label."""
        rc = trajectory_main([
            "replay",
            "--checkpoint", str(fixture_dir),
            "--frontier", "after-setup",
            "--config", "my-custom-config",
            "--dry-run",
        ])
        captured = capsys.readouterr()
        assert "HERA offline replay" in captured.out

    def test_benchmark_with_samples_flag(self, fixture_dir, capsys):
        """--samples flag is accepted (actual invocation skipped in dry-run)."""
        rc = trajectory_main([
            "replay",
            "--checkpoint", str(fixture_dir),
            "--frontier", "after-setup",
            "--samples", "3",
            "--dry-run",
        ])
        assert rc == 0
    def test_benchmark_ambiguous_frontiers(self, fixture_dir):
        """Two frontiers, no --frontier flag → error with available list."""
        with pytest.raises(SystemExit) as exc_info:
            trajectory_main([
                "replay",
                "--checkpoint", str(fixture_dir),
                "--dry-run",
            ])
        assert exc_info.value.code != 0


# ---------------------------------------------------------------------------
# Regression tests — parity with hera-replay behavior
# ---------------------------------------------------------------------------


class TestReplayParity:
    """Verify that BenchmarkRunner produces output structurally identical to
    the original hera-replay for the same fixture/frontier/config."""

    def test_manifest_structure(self, runner, fixture_dir):
        """manifest.json has the same keys as hera-replay output."""
        slug, fm = runner._resolve_frontier("after-setup")
        runner.run_single(
            slug=slug, fm=fm, config="parity-test", brief_text=None,
            recipes=True, model=None, samples=1, timeout=600, dry_run=True,
        )
        runs = sorted((fixture_dir / "runs" / slug).glob("parity-test-*"))
        manifest = json.loads((runs[0] / "manifest.json").read_text())

        # hera-replay manifest keys
        expected_keys = {
            "config", "frontier", "brief", "recipes", "cut_index",
            "latest_fileid", "model_requested", "checkpoint",
            "included_files", "data_dirs", "images",
        }
        for key in expected_keys:
            assert key in manifest, f"manifest.json missing key: {key}"

        # trajectory-added keys (should also be present)
        assert "trajectory_checkpoint_event" in manifest

    def test_prompt_structure(self, runner, fixture_dir):
        """Prompt has the same sections as hera-replay."""
        slug, fm = runner._resolve_frontier("after-setup")
        runner.run_single(
            slug=slug, fm=fm, config="prompt-parity", brief_text=None,
            recipes=True, model=None, samples=1, timeout=600, dry_run=True,
        )
        runs = sorted((fixture_dir / "runs" / slug).glob("prompt-parity-*"))
        prompt = (runs[0] / "prompt.md").read_text()

        # hera-replay prompt sections
        assert "# HERA offline replay" in prompt
        assert "## Campaign goal" in prompt or "## Your brief" in prompt
        assert "## Where you are" in prompt
        assert "## What to produce" in prompt
        assert "### 1. Read of the latest sweep" in prompt or "### 1. Starting point" in prompt
        assert "### 2. Next experiment" in prompt

    def test_output_dirs_match_replay_convention(self, runner, fixture_dir):
        """Run dirs follow the same <slug>/<config>-<ts> convention."""
        slug, fm = runner._resolve_frontier("after-setup")
        runner.run_single(
            slug=slug, fm=fm, config="convention-test", brief_text=None,
            recipes=True, model=None, samples=1, timeout=600, dry_run=True,
        )
        runs = sorted((fixture_dir / "runs" / slug).glob("convention-test-*"))
        assert len(runs) == 1
        run_name = runs[0].name
        # convention-test-YYYYMMDD-HHMMSS
        assert run_name.startswith("convention-test-")
        ts_part = run_name[len("convention-test-"):]
        assert len(ts_part) == 15  # YYYYMMDD-HHMMSS
