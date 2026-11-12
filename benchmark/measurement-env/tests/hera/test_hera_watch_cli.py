"""CLI-level tests for tools.hera_watch — the argument/timeout plumbing.

The engine (hera.watch) is covered by test_watch.py; here we pin the CLI's
foreground-safe-vs-follow timeout resolution and the --next / arm-before-run
wiring, capturing the kwargs handed to watch() rather than running it.
"""

import json
from pathlib import Path

import pytest

from tools import hera_watch


def _write_run(d: Path):
    d.mkdir(parents=True)
    (d / "metadata.json").write_text(json.dumps({
        "version": 2,
        "comments": ["test"],
        "columns": ["mag", "sr1_X", "sr1_P"],
        "measurement_config": {"sr1": "a-b"},
        "type": "1D",
        "fast_params": ["mag"],
        "fast_setpoints": [[0.0, 1.0]],
        "start_time": 1000.0,
    }))
    (d / "data.tsv").write_text("0.0\t1e-6\t0.0\n")


@pytest.fixture
def capture_watch(monkeypatch):
    """Replace watch() with a recorder; returns the captured kwargs dict."""
    captured = {}

    def fake_watch(model, **kwargs):
        captured["model"] = model
        captured.update(kwargs)
        return 0

    monkeypatch.setattr(hera_watch, "watch", fake_watch)
    return captured


def test_timeout_default_is_bounded(tmp_path, capture_watch):
    # Foreground-safe default: 570s, below the harness's ~600s shell cap.
    _write_run(tmp_path / "3")
    assert hera_watch.main([str(tmp_path / "3")]) == 0
    assert capture_watch["timeout"] == 570.0


def test_follow_flag_lifts_deadline(tmp_path, capture_watch):
    _write_run(tmp_path / "3")
    assert hera_watch.main([str(tmp_path / "3"), "--follow"]) == 0
    assert capture_watch["timeout"] is None


def test_explicit_timeout_passthrough(tmp_path, capture_watch):
    _write_run(tmp_path / "3")
    assert hera_watch.main([str(tmp_path / "3"), "--timeout", "120"]) == 0
    assert capture_watch["timeout"] == 120.0


def test_follow_overrides_explicit_timeout(tmp_path, capture_watch):
    _write_run(tmp_path / "3")
    assert hera_watch.main([str(tmp_path / "3"), "--timeout", "120", "--follow"]) == 0
    assert capture_watch["timeout"] is None


def test_next_latches_the_new_run(tmp_path, monkeypatch, capture_watch):
    # --next snapshots existing runs and latches the next one to appear, even
    # with a prior run present (the 2nd+-run case). The new run dir does not
    # exist when armed; wait_for_next_run materializes it (as the sweep would).
    data = tmp_path / "data"
    _write_run(data / "5")          # a prior run already present

    def fake_wait_next(data_dir, **kwargs):
        new = Path(data_dir) / "6"
        _write_run(new)
        return new

    monkeypatch.setattr(hera_watch, "wait_for_next_run", fake_wait_next)
    assert hera_watch.main(["--next", str(data)]) == 0
    assert capture_watch["model"].path.name == "6"


def test_next_times_out_when_no_new_run(tmp_path, monkeypatch, capsys):
    # wait_for_next_run returns None on timeout -> CLI exits 2 so the agent can
    # ping the operator (no watch() reached).
    data = tmp_path / "data"
    _write_run(data / "5")
    monkeypatch.setattr(hera_watch, "wait_for_next_run", lambda *a, **k: None)
    rc = hera_watch.main(["--next", str(data), "--wait-start", "0.001"])
    assert rc == 2
    assert "no new run appeared" in capsys.readouterr().err


def test_watch_gets_flushing_emit(tmp_path, capture_watch):
    # Bug 2: --follow block-buffered stdout, hiding per-row digests mid-run.
    # The CLI must hand watch() the line-flushing emit (not bare print).
    _write_run(tmp_path / "3")
    assert hera_watch.main([str(tmp_path / "3"), "--follow"]) == 0
    assert capture_watch["emit"] is hera_watch._flush_print


def test_missing_dir_times_out(tmp_path, capsys):
    # Tiny wait-start with an instant poll: the deadline trips on the first
    # poll since the target never appears. No watch() should be reached.
    rc = hera_watch.main([str(tmp_path / "nope"), "--wait-start", "0.001",
                          "--poll", "0"])
    assert rc == 2
    assert "did not appear" in capsys.readouterr().err


def test_guard_thresholds_default(tmp_path, capture_watch):
    _write_run(tmp_path / "3")
    assert hera_watch.main([str(tmp_path / "3")]) == 0
    model = capture_watch["model"]
    assert model.fs_warn == 0.90
    assert model.leak_excess_warn == 100e-12


def test_guard_thresholds_override(tmp_path, capture_watch):
    _write_run(tmp_path / "3")
    assert hera_watch.main([str(tmp_path / "3"),
                            "--fs-warn", "0.8",
                            "--leak-excess-warn", "5e-11"]) == 0
    model = capture_watch["model"]
    assert model.fs_warn == 0.8
    assert model.leak_excess_warn == 5e-11
