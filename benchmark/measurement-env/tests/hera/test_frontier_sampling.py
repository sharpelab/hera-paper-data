from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

FRONTIER = (
    Path(__file__).resolve().parents[2]
    / "hera/evaluations/frontier"
)
sys.path.insert(0, str(FRONTIER))

import sample  # noqa: E402
from sample import check_model_usage  # noqa: E402


PINNED = "claude-haiku-4-5-20251001"


def test_model_usage_accepts_only_the_pinned_model():
    observed, matches = check_model_usage(PINNED, {PINNED: {"inputTokens": 1}})

    assert observed == [PINNED]
    assert matches is True


@pytest.mark.parametrize(
    "usage",
    [
        None,
        {},
        {"claude-fable-5-1": {}},
        {PINNED: {}, "claude-fable-5-1": {}},
    ],
)
def test_model_usage_rejects_missing_different_or_extra_models(usage):
    _, matches = check_model_usage(PINNED, usage)

    assert matches is False


def test_model_usage_tolerates_the_cli_haiku_helper_next_to_an_opus_pin():
    _, matches = check_model_usage("claude-opus-5", {"claude-opus-5": {}, PINNED: {}})
    assert matches is True
    _, matches = check_model_usage("claude-opus-5", {PINNED: {}})  # helper alone: the agent never ran on Opus
    assert matches is False


def test_run_claude_can_resume_once_and_preserve_attempt_artifact(tmp_path, monkeypatch):
    payload = json.dumps({
        "is_error": False,
        "session_id": "session-1",
        "modelUsage": {PINNED: {"inputTokens": 1}},
        "result": "fixed",
    })
    seen = {}

    def fake_run(cmd, **kwargs):
        seen["cmd"] = cmd
        seen["kwargs"] = kwargs
        return SimpleNamespace(returncode=0, stdout=payload, stderr="")

    monkeypatch.setattr(sample.subprocess, "run", fake_run)
    result = sample.run_claude(
        tmp_path,
        "fix it",
        "hera-tactical",
        PINNED,
        30,
        ["Read"],
        resume="session-1",
        artifact="transcript-attempt-2.json",
    )

    assert seen["cmd"][-2:] == ["--resume", "session-1"]
    assert seen["kwargs"]["input"] == "fix it"
    assert result["model_usage_matches"] is True
    assert (tmp_path / "transcript-attempt-2.json").read_text() == payload
    assert (tmp_path / "claude-stderr-attempt-2.json").exists()


def test_one_sample_gives_one_api_repair_and_reports_only_final_result(tmp_path, monkeypatch):
    notebook = tmp_path / "measure.ipynb"
    notebook.write_text(json.dumps({"cells": [
        {"cell_type": "markdown", "source": [], "metadata": {}} for _ in range(42)
    ]}))
    (tmp_path / "fork.json").write_text(json.dumps({
        "notebooks": {"measure": {"file": notebook.name}},
        "cuts": {"measure": 41},
    }))
    calls = []
    cells = [
        "s = async_station(meas_config)\ns.runnow()",
        """s = async_station(meas_config)
s.ramp(k_bg.volt, -1.7627656435567625)
s.ramp(dc205_volt, -2.278022859037)
s.sweep(magnet.mag, np.linspace(0, 4, 501), delay=1.0)
""",
    ]

    def fake_claude(fork_dir, prompt, agent, model, timeout_s, allowed, effort, **kwargs):
        calls.append({"prompt": prompt, **kwargs})
        nb = json.loads(notebook.read_text())
        nb["cells"].append({"cell_type": "code", "source": cells[len(calls) - 1].splitlines(True),
                            "metadata": {"hera": {"appended_at": f"attempt-{len(calls)}"}}})
        notebook.write_text(json.dumps(nb))
        artifact = kwargs["artifact"]
        (fork_dir / artifact).write_text("{}")
        (fork_dir / artifact.replace("transcript", "claude-stderr")).write_text("")
        return {"model_usage_matches": True, "models": [PINNED], "expected_model": PINNED,
                "session_id": "session-1", "total_cost_usd": 0.1, "wall_s": 1.0, "num_turns": 1}

    monkeypatch.setattr(sample, "run_claude", fake_claude)
    monkeypatch.setattr(sample, "wait_for_flush", lambda *args, **kwargs: None)
    grades = iter([
        {"status": "unexecutable", "ok": None, "exec_error": "AttributeError: Mock object has no attribute 'runnow'",
         "repairable_api_error": True, "stdout_tail": "", "own_assert": None, "kind": "spot", "n_columns": 1,
         "B_rows": 0, "B_range_T": None, "n_cm2": [0.0]},
        {"status": "graded", "ok": True, "exec_error": None, "repairable_api_error": False, "stdout_tail": "",
         "own_assert": None, "kind": "spot", "n_columns": 1, "B_rows": 501, "B_range_T": [0.0, 4.0], "n_cm2": [-5e12]},
    ])
    monkeypatch.setattr(sample.grade_mod, "grade_cell", lambda *a, **k: next(grades))
    experiment = {
        "cuts": {"measure": 41}, "prompt": "prompt.md", "agent": "hera-tactical",
        "timeout_s": 30, "effort": "medium", "allowed_tools": ["Read"],
        "calibration": {
            "c_tg_F_per_m2": 1.7027e-3, "c_bg_F_per_m2": 2.2004e-3,
            "n_offset_cm2": -1.581e11, "top_gate_params": ["dc205_volt"],
            "back_gate_params": ["k_2400.volt"], "magnet_params": ["magnet.mag"],
        },
    }

    result = sample.one_sample(experiment, "full", 0, tmp_path,
                               {"recipes_md_count": 24}, model=PINNED)

    assert len(calls) == 2
    assert calls[0].get("resume") is None
    assert calls[1]["resume"] == "session-1"
    assert "no attribute 'runnow'" in calls[1]["prompt"]
    assert result["claude"]["attempts"] == 2
    assert result["grade"]["status"] == "graded"
    assert result["grade"]["ok"] is True
    assert "runnow" not in (tmp_path / "tool_call.py").read_text()


def test_one_sample_forwards_the_manifest_grader(tmp_path, monkeypatch):
    notebook = tmp_path / "measure.ipynb"
    notebook.write_text(json.dumps({"cells": [
        {"cell_type": "markdown", "source": [], "metadata": {}}
    ]}))
    (tmp_path / "fork.json").write_text(json.dumps({
        "notebooks": {"measure": {"file": notebook.name}},
        "cuts": {"measure": 0},
    }))
    seen = {}

    def fake_claude(fork_dir, prompt, agent, model, timeout_s, allowed, effort, **kwargs):
        nb = json.loads(notebook.read_text())
        nb["cells"].append({"cell_type": "code", "source": ["gate_sweep()\n"], "metadata": {}})
        notebook.write_text(json.dumps(nb))
        (fork_dir / kwargs["artifact"]).write_text("{}")
        (fork_dir / kwargs["artifact"].replace("transcript", "claude-stderr")).write_text("")
        return {"model_usage_matches": True, "models": [PINNED], "expected_model": PINNED,
                "session_id": "session-1", "total_cost_usd": 0.1, "wall_s": 1.0, "num_turns": 1}

    def fake_grade_cell(*args, **kwargs):
        seen.update(kwargs)
        return {"status": "graded", "ok": True}

    monkeypatch.setattr(sample, "run_claude", fake_claude)
    monkeypatch.setattr(sample, "wait_for_flush", lambda *args, **kwargs: None)
    monkeypatch.setattr(sample.grade_mod, "grade_cell", fake_grade_cell)
    experiment = {
        "cuts": {"measure": 0}, "cell_prompt": "prompt-cell.md", "agent": "hera-tactical",
        "timeout_s": 30, "calibration": {}, "grader": "sc_cut", "rig": {"readings": {}},
    }

    result = sample.one_sample(experiment, "full", 0, tmp_path,
                               {"recipes_md_count": 24}, model=PINNED)

    assert result["grade"]["ok"] is True
    assert seen["grader"] == "sc_cut"
    assert seen["exp"] is experiment



def test_run_claude_requests_structured_output_and_preserves_artifact(tmp_path, monkeypatch):
    plan = {"rationale": "next", "recipe": "sdh-spot-check", "ops": []}
    payload = json.dumps({
        "is_error": False,
        "session_id": "session-1",
        "modelUsage": {PINNED: {"inputTokens": 1}},
        "structured_output": plan,
    })
    seen = {}

    def fake_run(cmd, **kwargs):
        seen["cmd"] = cmd
        seen["kwargs"] = kwargs
        return SimpleNamespace(returncode=0, stdout=payload, stderr="")

    monkeypatch.setattr(sample.subprocess, "run", fake_run)
    result = sample.run_claude(
        tmp_path, "propose", "hera-tactical", PINNED, 30, ["Read"],
        schema={"type": "object"}, resume="session-1", artifact="transcript-attempt-2.json",
    )

    assert "--json-schema" in seen["cmd"]
    assert seen["cmd"][-2:] == ["--resume", "session-1"]
    assert seen["kwargs"]["input"] == "propose"
    assert result["proposal"] == plan
    assert result["model_usage_matches"] is True
    assert (tmp_path / "transcript-attempt-2.json").read_text() == payload


def test_json_mode_repairs_only_validation_and_reports_final_plan(tmp_path, monkeypatch):
    experiment = yaml.safe_load((FRONTIER / "experiments/qc0426-sdh-m41.yaml").read_text())
    valid = {
        "rationale": "Resolve oscillations.",
        "recipe": "sdh-spot-check",
        "ops": [
            {"op": "ramp", "param": "k_bg.volt", "setpoint": -1.763},
            {"op": "ramp", "param": "dc205_volt", "setpoint": -2.278},
            {"op": "sweep", "param": "magnet.mag",
             "setpoints": {"kind": "linspace", "start": 0.0, "stop": 4.0, "num": 501},
             "delay": 2.2},
        ],
    }
    invalid = json.loads(json.dumps(valid))
    invalid["ops"][0]["param"] = "invented.volt"
    calls = []

    def fake_claude(fork_dir, prompt, agent, model, timeout_s, allowed, effort, **kwargs):
        calls.append({"prompt": prompt, **kwargs})
        return {
            "model_usage_matches": True, "models": [PINNED], "session_id": "session-1",
            "total_cost_usd": 0.1, "wall_s": 1.0, "num_turns": 1,
            "proposal": invalid if len(calls) == 1 else valid,
        }

    monkeypatch.setattr(sample, "run_claude", fake_claude)
    result = sample.one_sample(experiment, "full", 0, tmp_path,
                               {"recipes_md_count": 24}, model=PINNED, mode="json")

    assert len(calls) == 2
    assert calls[0].get("resume") is None
    assert calls[1]["resume"] == "session-1"
    assert "invented.volt" in calls[1]["prompt"]
    assert "scorer" not in calls[1]["prompt"].lower()
    assert result["claude"]["attempts"] == 2
    assert result["grade"]["status"] == "graded"
    assert result["grade"]["ok"] is True
    assert json.loads((tmp_path / "proposal.json").read_text()) == valid
