"""`hera-replay run` / `summarize` without a docker daemon or a model: docker is
replaced at `container._docker`, the resumed claude at `container.subprocess.Popen`
with a fake agent that edits the episode the way a real one does."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import signal
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from hera.replay import container, main, run as run_mod
from hera.replay.case import load_case
from hera.replay.errors import CutError
from hera.replay.materialize import STUBS
from hera.replay.summarize import render, rows, write_summary
from tests.hera.replay_fixture import SID, make_archive

REAL_POPEN = subprocess.Popen
IMAGE_ID = "sha256:" + "ab" * 32
META = {"corpus_sha": "abcdef1234567890abcdef1234567890abcdef12", "condition": "full", "strip": [], "claude_version": "2.1.273"}
OVERLAY_META = {**META, "corpus_sha": "12fa296" + "b" * 33, "harness_sha": "8bf4e7d" + "c" * 33,
                "prompt_source": "corpus", "corpus_paths": ["hera/recipes", "hera/crops", "hera/models"]}
CUT_CELL = {"id": "cccc0001", "cell_type": "code", "metadata": {"hera": {"appended_at": "2026-01-01T12:00:30+00:00"}}, "source": "print('fan')", "outputs": [], "execution_count": None}


def event(type_, **kw):
    return json.dumps({"type": type_, **kw}) + "\n"


def assistant(msg_id, model, blocks, usage):
    return event("assistant", message={"id": msg_id, "model": model, "role": "assistant", "content": blocks, "usage": usage})


def stream(model="claude-sonnet-5", subtype="success", cost=0.5):
    """Two API messages, one of them split over two events, so usage is summed per message."""
    u1 = {"input_tokens": 2, "cache_creation_input_tokens": 100, "cache_read_input_tokens": 1000, "output_tokens": 10}
    u2 = {"input_tokens": 2, "cache_creation_input_tokens": 5, "cache_read_input_tokens": 1100, "output_tokens": 20}
    lines = [
        event("system", subtype="init", claude_code_version="2.1.273", model=model, session_id=SID),
        assistant("msg_1", model, [{"type": "text", "text": "Picking back up."}], u1),
        assistant("msg_1", model, [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "nb-collab append x_measure.ipynb --code-file f.py"}}], u1),
        event("user", message={"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "appended code @ 5 id=cccc0001"}]}),
        assistant("msg_2", model, [{"type": "tool_use", "id": "t2", "name": "Bash", "input": {"command": "nb-collab execute-cell x_measure.ipynb cccc0001"}}], u2),
    ]
    if subtype is not None:
        lines.append(event("result", subtype=subtype, is_error=subtype != "success", num_turns=2, duration_ms=1234,
                           total_cost_usd=cost, stop_reason="end_turn", modelUsage={model: {"costUSD": cost}},
                           usage={"input_tokens": 4, "cache_creation_input_tokens": 105, "cache_read_input_tokens": 2100, "output_tokens": 900}))
    return lines


class FakeAgent:
    """Stands in for `docker exec … claude -p`: edits the episode dir like the real
    agent, then plays a canned stream."""

    def __init__(self, hera_data: Path, *, lines, marker=True, block=False, delete_notebook=False, fresh=False,
                 cell_source=None):
        self.fresh = fresh
        self.cell = CUT_CELL if cell_source is None else {**CUT_CELL, "source": cell_source}
        self.prompts: dict[str, str] = {}
        self.hera_data = hera_data
        self.lines = lines
        self.marker = marker
        self.block = block
        self.delete_notebook = delete_notebook
        self.calls: list[list[str]] = []

    def __call__(self, cmd, **kw):
        # `subprocess` is one module: the harness's own git calls go to the real Popen.
        if cmd[0] != "docker":
            return REAL_POPEN(cmd, **kw)
        self.calls.append(cmd)
        env = kw["env"]
        assert "CLAUDECODE" not in env and not any(k.startswith("CLAUDE_") for k in env)
        name = next(a for a in cmd if a.startswith("hera-replay-"))
        case, sid = name[len("hera-replay-"):].rsplit("-", 3)[0], name.rsplit("-", 1)[1]
        (ep,) = list(self.hera_data.glob(f"replay/runs/{case}/*/episodes/{sid}"))
        session = ep / "session"
        nb_path = session / "x_measure.ipynb"
        nb = json.loads(nb_path.read_text())
        nb["cells"].append(self.cell)
        nb["cells"][0]["source"] = "# Measure (edited)"
        nb_path.write_text(json.dumps(nb))
        if self.delete_notebook:
            nb_path.unlink()
        (session / "hera_scratch" / "fan2.py").write_text("print('fan')\n")
        with (session / "notifications.jsonl").open("a") as fh:
            fh.write(json.dumps({"argv": ["hi"]}) + "\n")
        if self.marker == "hera-watch":
            (session / "episode-stop.json").write_text(json.dumps({
                "timestamp": "2026-01-01T12:00:31+00:00", "tool": "hera-watch", "command": "hera-watch data --next",
                "invocation": "hera-watch", "cell_ids": [], "tool_use_id": None}))
        elif self.marker:
            (session / "episode-stop.json").write_text(json.dumps({
                "timestamp": "2026-01-01T12:00:31+00:00", "tool": "Bash", "command": "nb-collab execute-cell x_measure.ipynb cccc0001",
                "invocation": "nb-collab execute-cell x_measure.ipynb cccc0001", "cell_ids": ["cccc0001"], "tool_use_id": "t2"}))
        if self.fresh:
            # A new instance: the CLI makes its own project dir and session jsonl.
            assert list((ep / "claude-projects").iterdir()) == []
            workdir = cmd[cmd.index("-w") + 1]
            jsonl = ep / "claude-projects" / workdir.replace("/", "-") / f"{cmd[cmd.index('--session-id') + 1]}.jsonl"
            jsonl.parent.mkdir()
        else:
            (jsonl,) = list((ep / "claude-projects").glob("*/*.jsonl"))
        with jsonl.open("a") as fh:
            for i in range(3):
                fh.write(json.dumps({"type": "assistant", "uuid": f"new-{i}"}) + "\n")
        return _Proc(self.lines, self.block, lambda text: self.prompts.__setitem__(sid, text))


class _Blocking:
    def __iter__(self):
        return self

    def __next__(self):
        time.sleep(1000)


class _Proc:
    def __init__(self, lines, block, on_prompt=lambda text: None):
        self.stdin = _Sink(on_prompt)
        self.stdout = _Blocking() if block else iter(lines)
        self.killed = False

    def wait(self, timeout=None):
        return 0

    def kill(self):
        self.killed = True


class _Sink:
    def __init__(self, on_prompt):
        self.on_prompt = on_prompt

    def write(self, text):
        self.on_prompt(text)

    def close(self):
        pass


class FakeDocker:
    def __init__(self, leftovers=(), jl_ready=True, meta=META):
        self.calls: list[list[str]] = []
        self.leftovers = leftovers
        self.jl_ready = jl_ready
        self.meta = meta

    def __call__(self, args, *, stdin_text=None, timeout=None, check=True):
        self.calls.append(args)
        out = ""
        if args[0] == "ps":
            out = "".join(f"{n}\n" for n in self.leftovers)
        elif args[0] == "exec" and not self.jl_ready:
            return subprocess.CompletedProcess(args, 1, stdout="", stderr="connection refused")
        elif args[0] == "version":
            out = json.dumps({"Client": {"Version": "29.8.0"}, "Server": {"Version": "29.8.0"}})
        elif args[:2] == ["image", "inspect"]:
            out = IMAGE_ID + "\n"
        elif args[:3] == ["run", "--rm", "--entrypoint"]:
            out = json.dumps(self.meta)
        elif args[:2] == ["run", "-d"]:
            out = "cid\n"
        elif args[0] == "inspect":
            out = "true\n"
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")

    def of(self, verb):
        return [a for a in self.calls if a[0] == verb]


@pytest.fixture
def setup(tmp_path, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "tok-secret")
    monkeypatch.setenv("HERA_DATA", str(tmp_path / "data"))
    root, b = make_archive(tmp_path / "2026-01-01-dev-session")
    case_path = tmp_path / "cases" / "dev-fan.yaml"
    case_path.parent.mkdir()
    case_path.write_text(yaml.safe_dump({
        "case": "dev-fan", "source": "../2026-01-01-dev-session",
        "cut": {"transcript": f"{SID}.jsonl", "at": b.uuids["cut"]},
        "corpus": {"sha": "abcdef1", "condition": "full"},
        "run": {"model": "claude-sonnet-5", "effort": "medium", "n": 2, "timeout_s": 60, "stall_s": 30, "max_turns": 60},
        "allowed_tools": ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "ScheduleWakeup", "Monitor"],
        "grader": None,
        "resume": {"close": "Signature confirmed. Designing the fan now.", "prompt": "Carry on."},
    }))
    docker = FakeDocker()
    monkeypatch.setattr(container, "_docker", docker)
    return {"root": root, "b": b, "case": case_path, "docker": docker, "hera_data": tmp_path / "data", "monkeypatch": monkeypatch}


def install_agent(setup, **kw):
    agent = FakeAgent(setup["hera_data"], **kw)
    setup["monkeypatch"].setattr(container.subprocess, "Popen", agent)
    return agent


def run_dir_of(setup, case="dev-fan"):
    (d,) = list(setup["hera_data"].glob(f"replay/runs/{case}/*"))
    return d


def test_run_cuts_once_copies_per_sample_and_archives_each_episode(setup, capsys):
    agent = install_agent(setup, lines=stream())
    assert main(["run", str(setup["case"]), "--parallel", "2"]) == 0
    rd = run_dir_of(setup)
    run = json.loads((rd / "run.json").read_text())
    assert run["schema"] == "hera-replay-run/1" and run["n"] == 2 and run["parallel"] == 2
    assert run["image"] == {"tag": "hera-agent:abcdef1-full", "id": IMAGE_ID, "metadata": META}
    assert run["episode_source"]["mode"] == "cut" and run["episode_source"]["cut"]["uuid"] == setup["b"].uuids["cut"]
    assert run["episode_source"]["corpus_reads"] == {"mode": "archived"}
    assert run["credential"] == "CLAUDE_CODE_OAUTH_TOKEN" and "tok-secret" not in (rd / "run.json").read_text()
    assert run["harness"]["git_head"] and run["harness"]["code_hash"] and run["statuses"] == {"00": "ok", "01": "ok"}

    # The cut is pristine; each sample consumed its own copy.
    cut = rd / "cut"
    assert not (cut / "session" / "episode-stop.json").exists()
    assert "run" not in json.loads((cut / "episode.json").read_text())
    assert len(json.loads((cut / "session" / "x_measure.ipynb").read_text())["cells"]) == 4
    assert len(agent.calls) == 2 and len(setup["docker"].of("run")) == 1 + 2  # metadata cat + two containers

    for sid in ("00", "01"):
        ep = rd / "episodes" / sid
        for f in ("transcript.jsonl", "claude-stderr.txt", "harness.log", "appended_cells.json", "session/notifications.jsonl"):
            assert (ep / f).exists(), f
        assert (ep / "transcript.jsonl").read_text().splitlines(keepends=True) == stream()
        rec = json.loads((ep / "episode.json").read_text())["run"]
        assert rec["status"] == "ok" and rec["sample"] == sid and rec["container"] == f"hera-replay-dev-fan-{rd.name}-{sid}"
        assert rec["stop"]["cell_ids"] == ["cccc0001"] and rec["cost_usd"] == 0.5
        assert rec["model"] == {"pinned": "claude-sonnet-5", "observed": ["claude-sonnet-5"]}
        assert rec["claude_version"] == {"image": "2.1.273", "observed": "2.1.273"}
        assert rec["tokens"] == {"input": 4, "cache_creation": 105, "cache_read": 2100, "output": 900} and rec["tokens_source"] == "result"
        assert rec["turns"] == {"num_turns": 2, "api_messages": 2, "assistant_events": 3, "tool_calls": 2, "events": 6}
        assert rec["session_jsonl"]["entries_after"] == rec["session_jsonl"]["entries_before"] + 3
        assert rec["notebooks"]["x_measure.ipynb"] == {"cells_before": 4, "cells_after": 5, "appended": ["cccc0001"], "modified": ["t1"]}
        assert rec["notebooks"]["x_ana.ipynb"]["appended"] == [] and rec["cells_appended"] == 1 and rec["notifications"] == 1
        appended = json.loads((ep / "appended_cells.json").read_text())
        assert appended["x_measure.ipynb"]["appended"] == [CUT_CELL]
        assert appended["x_measure.ipynb"]["modified"][0]["after"] == "# Measure (edited)"
        # Provenance: the verbatim argv with the token redacted, and the clock.
        drun = rec["docker"]["run"]
        assert drun[:3] == ["docker", "run", "-d"]
        assert "CLAUDE_CODE_OAUTH_TOKEN=<redacted>" in drun and "tok-secret" not in json.dumps(rec)
        assert f"{ep / 'session'}:/home/hera/measurements/zack/20260101-dev" in drun
        assert f"{ep / 'mnt'}:/home/hera/measurements" in drun and f"{ep / 'claude-projects'}:/home/hera/.claude/projects" in drun
        assert f"{ep / 'tmp'}:/tmp" in drun and (ep / "tmp").is_dir() and rec["outputs"]["tmp"] == "tmp"
        assert all(f"{ep / 'stubs' / s}:/home/hera/.local/bin/{s}:ro" in drun for s in STUBS)
        assert "HERA_JL_PORT=8899" in drun and f"HERA_FAKETIME=-{rec['faketime_s']}" in drun
        assert "TZ=America/Los_Angeles" in drun
        assert drun[-1] == "hera-agent:abcdef1-full"
        dexec = rec["docker"]["exec"]
        assert dexec[:3] == ["docker", "exec", "-i"] and rec["container"] in dexec
        assert f"HERA_FAKE_OFFSET_MS={rec['faketime_s'] * 1000}" in dexec and "BUN_OPTIONS=--preload /opt/hera/fakedate.js" in dexec
        for flag, value in (("--model", "claude-sonnet-5"), ("--effort", "medium"), ("--max-turns", "60"), ("--resume", SID),
                            ("--allowedTools", "Bash,Read,Write,Edit,Glob,Grep,ScheduleWakeup,Monitor")):
            assert dexec[dexec.index(flag) + 1] == value
        assert dexec[-2] == "--allowedTools"
        # Untouched files carry the cut timestamp; the faketime offset is now − cut.
        cut_epoch = datetime.fromisoformat(rec["started_at"]).timestamp() - rec["faketime_s"]
        assert abs((ep / "session" / "rig_card.md").stat().st_mtime - cut_epoch) < 2
        assert setup["docker"].of("stop").count(["stop", "-t", str(container.STOP_TIMEOUT_S), rec["container"]]) >= 1
        assert ["rm", "-f", rec["container"]] in setup["docker"].of("rm")

    rs = rows(rd)
    assert [r["sample"] for r in rs] == ["00", "01"] and all(r["status"] == "ok" and r["cells_appended"] == 1 for r in rs)
    assert rs[0]["stop"] == "nb-collab execute-cell x_measure.ipynb cccc0001"
    csv_text = (rd / "summary.csv").read_text()
    assert csv_text.startswith("sample,model,status,cost_usd,turns,tool_calls,wall_s,cells_appended,stop_cell_sweeps,stop\n00,claude-sonnet-5,ok,0.5,2,2,")
    out = capsys.readouterr().out
    assert "2 episodes: ok 2" in out and "cost: $1.00 over 2 priced episodes" in out


def test_n_override_and_source_dir_is_never_written(setup):
    install_agent(setup, lines=stream())
    before = sorted(p.relative_to(setup["root"]).as_posix() for p in setup["root"].rglob("*"))
    assert main(["run", str(setup["case"]), "--n", "1"]) == 0
    rd = run_dir_of(setup)
    assert sorted(p.name for p in (rd / "episodes").iterdir()) == ["00"]
    assert sorted(p.relative_to(setup["root"]).as_posix() for p in setup["root"].rglob("*")) == before


def test_model_and_effort_override_the_case(setup):
    install_agent(setup, lines=stream(model="claude-opus-5"))
    assert main(["run", str(setup["case"]), "--n", "1", "--model", "claude-opus-5", "--effort", "high"]) == 0
    rd = run_dir_of(setup)
    run = json.loads((rd / "run.json").read_text())
    assert run["override"] == {"model": "claude-opus-5", "effort": "high"}
    assert run["case"]["run"]["model"] == "claude-sonnet-5" and run["case"]["run"]["effort"] == "medium"
    assert "model=claude-opus-5 override=" in (rd / "harness.log").read_text()
    rec = json.loads((rd / "episodes" / "00" / "episode.json").read_text())["run"]
    assert rec["status"] == "ok"  # the pinned model moved with the override, so the run is not a mismatch
    assert rec["model"] == {"pinned": "claude-opus-5", "observed": ["claude-opus-5"]} and rec["effort"] == "high"
    dexec = rec["docker"]["exec"]
    assert dexec[dexec.index("--model") + 1] == "claude-opus-5" and dexec[dexec.index("--effort") + 1] == "high"


def test_model_override_alone_keeps_the_case_effort(setup):
    install_agent(setup, lines=stream(model="claude-opus-5"))
    assert main(["run", str(setup["case"]), "--n", "1", "--model", "claude-opus-5"]) == 0
    rd = run_dir_of(setup)
    assert json.loads((rd / "run.json").read_text())["override"] == {"model": "claude-opus-5"}
    rec = json.loads((rd / "episodes" / "00" / "episode.json").read_text())["run"]
    assert rec["status"] == "ok" and rec["effort"] == "medium"
    assert rec["docker"]["exec"][rec["docker"]["exec"].index("--effort") + 1] == "medium"


def test_an_unoverridden_run_records_no_override(setup):
    install_agent(setup, lines=stream())
    assert main(["run", str(setup["case"]), "--n", "1"]) == 0
    assert "override" not in json.loads((run_dir_of(setup) / "run.json").read_text())


def test_an_unknown_effort_is_refused_before_any_container(setup):
    install_agent(setup, lines=stream())
    with pytest.raises(SystemExit):
        main(["run", str(setup["case"]), "--effort", "turbo"])
    with pytest.raises(CutError, match="effort must be one of"):
        run_mod.run_case(load_case(setup["case"]), n=1, parallel=1, hera_data=setup["hera_data"], effort="turbo")
    assert not (setup["hera_data"] / "replay" / "runs").exists()


@pytest.mark.parametrize("guard, limits", [("stall", {"stall_s": 0.05}), ("timeout", {"timeout_s": 0.05, "stall_s": 60})])
def test_guards_stop_the_container_and_record_the_status(setup, guard, limits):
    install_agent(setup, lines=(), block=True)
    case = load_case(setup["case"])
    case = type(case)(**{**case.__dict__, **limits, "n": 1})
    rd = run_mod.run_case(case, n=None, parallel=1, hera_data=setup["hera_data"])
    rec = json.loads((rd / "episodes" / "00" / "episode.json").read_text())["run"]
    assert rec["status"] == guard and rec["guard"] == guard and rec["result"] is None and rec["cost_usd"] is None
    assert rec["stop"]["cell_ids"] == ["cccc0001"]  # the agent got there; the stream did not
    assert rec["turns"]["api_messages"] == 0 and rec["tokens_source"] == "assistant_events"
    assert f"guard: {guard}" in (rd / "episodes" / "00" / "harness.log").read_text()
    assert rows(rd)[0]["cost_usd"] is None and "cost: $0.00 over 0 priced" in render(rd)


@pytest.mark.parametrize("guard, limits", [("stall", {"stall_s": 0.05}), ("timeout", {"timeout_s": 0.05, "stall_s": 60})])
def test_a_sweep_cell_landed_before_a_guard_is_landed_unexecuted(setup, guard, limits):
    install_agent(setup, lines=(), block=True, marker=False, cell_source="s.megasweep(magnet.field, B, k_tg.volt, V)")
    case = load_case(setup["case"])
    case = type(case)(**{**case.__dict__, **limits, "n": 1})
    rd = run_mod.run_case(case, n=None, parallel=1, hera_data=setup["hera_data"])
    rec = json.loads((rd / "episodes" / "00" / "episode.json").read_text())["run"]
    assert rec["status"] == "landed_unexecuted" and rec["guard"] == guard and rec["sweep_cell_appended"] is True


@pytest.mark.parametrize("kw, status", [
    (dict(lines=stream(subtype="error_max_turns"), marker=False), "max_turns"),
    (dict(lines=stream(subtype="error_max_turns"), marker=False, cell_source="s.sweep(k_tg.volt, V)"), "landed_unexecuted"),
    (dict(lines=stream(), marker=False), "no_stop"),
    (dict(lines=stream(model="claude-sonnet-4-5")), "model_mismatch"),
    (dict(lines=stream(), marker="hera-watch"), "ok"),
    (dict(lines=stream(subtype=None)), "error"),
    (dict(lines=stream(subtype="error_during_execution")), "error"),
    (dict(lines=[*stream(subtype=None), event("result", subtype="success", is_error=True,
                                              result="Claude AI usage limit reached|1790305776")]), "quota"),
    (dict(lines=[*stream(subtype=None), event("rate_limit_event", rate_limit_info={"status": "rejected",
                                                                                   "rateLimitType": "five_hour"})]), "quota"),
    (dict(lines=[event("rate_limit_event", rate_limit_info={"status": "allowed_warning"}), *stream()]), "ok"),
])
def test_episode_statuses(setup, kw, status):
    install_agent(setup, **kw)
    assert main(["run", str(setup["case"]), "--n", "1"]) == 0
    rec = json.loads((run_dir_of(setup) / "episodes" / "00" / "episode.json").read_text())["run"]
    assert rec["status"] == status
    if status in ("error", "quota"):
        assert rec["error"]
    assert (rec["quota"] is not None) == (status == "quota")
    if status == "model_mismatch":
        assert rec["model"]["observed"] == ["claude-sonnet-4-5"]
    if kw.get("marker") == "hera-watch":
        assert rows(run_dir_of(setup))[0]["stop"] == "hera-watch"


def test_harness_failure_is_recorded_and_the_container_removed(setup, monkeypatch):
    install_agent(setup, lines=stream())
    monkeypatch.setattr(container, "wait_for_jupyter", lambda *a, **k: (_ for _ in ()).throw(container.DockerError("JL never came up")))
    assert main(["run", str(setup["case"]), "--n", "1"]) == 0
    rd = run_dir_of(setup)
    rec = json.loads((rd / "episodes" / "00" / "episode.json").read_text())["run"]
    assert rec["status"] == "error" and rec["error"] == "DockerError: JL never came up"
    assert ["rm", "-f", rec["container"]] in setup["docker"].of("rm")
    assert "JL never came up" in (rd / "episodes" / "00" / "harness.log").read_text()


def test_failure_text_never_carries_the_token(setup, monkeypatch):
    """subprocess.TimeoutExpired quotes the whole docker argv, token included."""
    install_agent(setup, lines=stream())

    def hang(args):
        raise subprocess.TimeoutExpired(cmd=["docker", *args], timeout=300)

    monkeypatch.setattr(container, "start_container", hang)
    assert main(["run", str(setup["case"]), "--n", "1"]) == 0
    rd = run_dir_of(setup)
    rec = json.loads((rd / "episodes" / "00" / "episode.json").read_text())["run"]
    assert rec["status"] == "error" and rec["error"].startswith("TimeoutExpired: Command") and "<redacted>" in rec["error"]
    for f in (rd / "episodes" / "00" / "episode.json", rd / "episodes" / "00" / "harness.log", rd / "harness.log", rd / "run.json"):
        assert "tok-secret" not in f.read_text(), f


def test_collection_failure_is_recorded_and_the_run_completes(setup):
    install_agent(setup, lines=stream(), delete_notebook=True)
    assert main(["run", str(setup["case"]), "--n", "2"]) == 0
    rd = run_dir_of(setup)
    rec = json.loads((rd / "episodes" / "00" / "episode.json").read_text())["run"]
    assert rec["status"] == "error" and "x_measure.ipynb is gone" in rec["error"]
    assert rec["cost_usd"] is None and rec["cells_appended"] is None
    assert json.loads((rd / "run.json").read_text())["statuses"] == {"00": "error", "01": "error"}
    assert [r["status"] for r in rows(rd)] == ["error", "error"] and (rd / "summary.csv").exists()


def interrupt_self(after_s):
    threading.Timer(after_s, lambda: os.kill(os.getpid(), signal.SIGINT)).start()


def test_sigint_stops_in_flight_episodes_and_cancels_queued_ones(setup):
    install_agent(setup, lines=(), block=True)
    before = signal.getsignal(signal.SIGINT)
    interrupt_self(0.3)
    assert main(["run", str(setup["case"]), "--n", "2"]) == 130
    assert signal.getsignal(signal.SIGINT) is before
    rd = run_dir_of(setup)
    run = json.loads((rd / "run.json").read_text())
    assert run["interrupted"] is True and run["statuses"] == {"00": "interrupted", "01": "cancelled"}
    rec = json.loads((rd / "episodes" / "00" / "episode.json").read_text())["run"]
    assert rec["status"] == "interrupted" and rec["guard"] == "interrupted" and rec["result"] is None
    assert ["stop", "-t", str(container.STOP_TIMEOUT_S), rec["container"]] in setup["docker"].of("stop")
    assert ["rm", "-f", rec["container"]] in setup["docker"].of("rm")
    assert not (rd / "episodes" / "01").exists()
    assert [r["status"] for r in rows(rd)] == ["interrupted"]
    assert "SIGINT: stopping the run" in (rd / "harness.log").read_text()


def test_sigterm_during_jupyter_wait_is_interrupted_and_cleaned_up(setup, monkeypatch):
    install_agent(setup, lines=stream())
    setup["docker"].jl_ready = False
    threading.Timer(0.3, lambda: os.kill(os.getpid(), signal.SIGTERM)).start()
    assert main(["run", str(setup["case"]), "--n", "1"]) == 130
    rd = run_dir_of(setup)
    rec = json.loads((rd / "episodes" / "00" / "episode.json").read_text())["run"]
    assert rec["status"] == "interrupted" and rec["error"] == "DockerError: interrupted before JupyterLab was ready"
    assert ["rm", "-f", rec["container"]] in setup["docker"].of("rm")


def test_run_refuses_while_replay_containers_exist(setup):
    install_agent(setup, lines=stream())
    setup["docker"].leftovers = ("hera-replay-dev-fan-20260916T000000-00",)
    with pytest.raises(SystemExit, match=r"containers from another run exist .*hera-replay-dev-fan-20260916T000000-00"):
        main(["run", str(setup["case"])])
    assert not (setup["hera_data"] / "replay" / "runs").exists()


def test_precut_episode_is_copied_and_stays_unconsumed(setup):
    install_agent(setup, lines=stream())
    assert main(["cut", str(setup["root"]), "--at", setup["b"].uuids["cut"], "--dest", str(setup["hera_data"] / "pre")]) == 0
    case = yaml.safe_load(setup["case"].read_text())
    del case["source"], case["cut"]
    case["episode"] = str(setup["hera_data"] / "pre")
    case["case"] = "dev-pre"
    baseline = setup["hera_data"] / "pre" / "session" / ".claude" / "measure_cells.json"
    expected = json.loads(baseline.read_text())
    baseline.unlink()  # an episode dir cut before the baseline existed
    setup["case"].write_text(yaml.safe_dump(case))
    assert main(["run", str(setup["case"]), "--n", "1"]) == 0
    rd = run_dir_of(setup, "dev-pre")
    assert not (rd / "cut").exists()
    assert json.loads((rd / "run.json").read_text())["episode_source"]["mode"] == "precut"
    assert "run" not in json.loads((setup["hera_data"] / "pre" / "episode.json").read_text())
    assert not (setup["hera_data"] / "pre" / "session" / "episode-stop.json").exists()
    assert json.loads((rd / "episodes" / "00" / "episode.json").read_text())["run"]["status"] == "ok"
    assert json.loads((rd / "episodes" / "00" / "session" / ".claude" / "measure_cells.json").read_text()) == expected
    assert not baseline.exists()
    case["corpus"]["reads"] = "corpus"
    case["case"] = "dev-pre-corpus"
    setup["case"].write_text(yaml.safe_dump(case))
    with pytest.raises(SystemExit, match="corpus.reads applies at cut time"):
        main(["run", str(setup["case"]), "--n", "1"])


def test_run_refuses_a_mismatched_image_or_transcript(setup, monkeypatch):
    install_agent(setup, lines=stream())
    case = yaml.safe_load(setup["case"].read_text())
    case["cut"]["transcript"] = "other.jsonl"
    setup["case"].write_text(yaml.safe_dump(case))
    with pytest.raises(SystemExit, match="cut.transcript is other.jsonl"):
        main(["run", str(setup["case"])])
    case["cut"]["transcript"] = f"{SID}.jsonl"
    case["corpus"]["condition"] = "none"
    setup["case"].write_text(yaml.safe_dump(case))
    with pytest.raises(SystemExit, match="was built for .*/full, case pins abcdef1/none"):
        main(["run", str(setup["case"])])
    assert not (setup["hera_data"] / "replay" / "runs").exists()
    case["corpus"]["condition"] = "full"
    case["cut"]["at"] = setup["b"].uuids["post-cut-call"]
    setup["case"].write_text(yaml.safe_dump(case))
    with pytest.raises(SystemExit, match="not a tool_result"):
        main(["run", str(setup["case"])])
    assert list((setup["hera_data"] / "replay" / "runs").glob("*/*")) == []  # a failed cut leaves no run dir


def _overlay_case(setup, **corpus):
    case = yaml.safe_load(setup["case"].read_text())
    case["corpus"] = {"sha": "12fa296", "condition": "full", **corpus}
    setup["case"].write_text(yaml.safe_dump(case))
    return case


def test_run_resolves_the_overlay_image_a_corpus_case_names(setup):
    _overlay_case(setup, harness="8bf4e7d", prompt="corpus")
    setup["docker"].meta = OVERLAY_META
    install_agent(setup, lines=stream())
    assert main(["run", str(setup["case"]), "--n", "1"]) == 0
    run = json.loads((run_dir_of(setup) / "run.json").read_text())
    tag = "hera-agent:8bf4e7d.c12fa296p-full"
    assert run["image"] == {"tag": tag, "id": IMAGE_ID, "metadata": OVERLAY_META}
    assert [a for a in setup["docker"].calls if a[:2] == ["image", "inspect"]][0][-1] == tag
    # Both shas and the prompt source read straight off the case block, no tag parsing.
    assert run["case"]["corpus"] == {"sha": "12fa296", "condition": "full", "harness": "8bf4e7d", "prompt": "corpus"}


def test_run_refuses_an_image_built_on_another_harness_or_prompt(setup):
    _overlay_case(setup, harness="8bf4e7d")
    setup["docker"].meta = OVERLAY_META
    install_agent(setup, lines=stream())
    with pytest.raises(SystemExit, match="with corpus prompts, case pins 8bf4e7d/harness"):
        main(["run", str(setup["case"])])
    setup["docker"].meta = {**OVERLAY_META, "prompt_source": "harness", "harness_sha": "0000000" + "c" * 33}
    with pytest.raises(SystemExit, match="was built on harness 0000000"):
        main(["run", str(setup["case"])])
    assert not (setup["hera_data"] / "replay" / "runs").exists()


def test_case_file_validation(tmp_path, monkeypatch):
    good = {
        "case": "x", "source": "${HERA_REPO}/notes/s", "cut": {"transcript": "a.jsonl", "at": "9e2f2705-fd95-4c6b-acad-33b27d01bcfc"},
        "corpus": {"sha": "8bf4e7d", "condition": "full"},
        "run": {"model": "claude-sonnet-5", "effort": "medium", "n": 5, "timeout_s": 1800, "stall_s": 600, "max_turns": 60},
        "allowed_tools": ["Bash"],
        "grader": None,
        "resume": {"close": "Signature confirmed.", "prompt": "Carry on."},
    }
    p = tmp_path / "c.yaml"

    def check(mutate, match):
        d = json.loads(json.dumps(good))
        mutate(d)
        p.write_text(yaml.safe_dump(d))
        with pytest.raises(CutError, match=match):
            load_case(p)

    monkeypatch.delenv("HERA_REPO", raising=False)
    check(lambda d: None, r"\$\{HERA_REPO\} is not set")
    monkeypatch.setenv("HERA_REPO", "/repo")
    p.write_text(yaml.safe_dump(good))
    c = load_case(p)
    assert c.source == Path("/repo/notes/s") and c.n == 5 and c.allowed_tools == ("Bash",) and c.timeout_s == 1800.0
    check(lambda d: d.__delitem__("allowed_tools"), r"missing \['allowed_tools'\]")
    check(lambda d: d.__setitem__("max_repairs", 1), r"unknown \['max_repairs'\]")
    check(lambda d: d["run"].__setitem__("effort", "extreme"), "run.effort must be one of")
    check(lambda d: d["run"].__setitem__("n", "5"), "run.n must be int")
    check(lambda d: d["run"].__delitem__("stall_s"), r"run: missing \['stall_s'\]")
    check(lambda d: d.__setitem__("episode", "/x"), "exactly one of source \\+ cut")
    check(lambda d: d["corpus"].__setitem__("sha", "main"), "corpus.sha must be a hex sha")
    check(lambda d: d["corpus"].__setitem__("harness", "HEAD"), "corpus.harness must be a hex sha")
    check(lambda d: d["corpus"].__setitem__("vintage", "june"), r"corpus: missing \[\], unknown \['vintage'\]")
    check(lambda d: d["corpus"].__setitem__("prompt", "june"), "corpus.prompt must be one of")
    check(lambda d: d["corpus"].__setitem__("prompt", "corpus"), "it needs corpus.harness")
    check(lambda d: d["corpus"].__setitem__("reads", "june"), "corpus.reads must be one of")
    check(lambda d: d["cut"].__setitem__("at", "841"), "cut.at must be an entry uuid")
    check(lambda d: d.__setitem__("allowed_tools", []), "allowed_tools must be a non-empty list")
    check(lambda d: d.__setitem__("case", "a b"), "case must be a")
    check(lambda d: d.__delitem__("resume"), "exactly one of resume .* or fresh .*, got none")
    check(lambda d: d.__setitem__("fresh", {"brief": "b.md"}), r"exactly one of resume .*, got \['resume', 'fresh'\]")
    check(lambda d: d["resume"].__setitem__("close", ""), "resume.close must be one non-empty line")
    check(lambda d: d["resume"].__setitem__("prompt", "a\nb"), "resume.prompt must be one non-empty line")
    p.write_text(yaml.safe_dump(good))
    assert (load_case(p).resume_close, load_case(p).resume_prompt) == ("Signature confirmed.", "Carry on.")
    plain = load_case(p)
    assert (plain.corpus_sha, plain.harness_sha, plain.prompt_source, plain.read_source) == ("8bf4e7d", None, "harness", "archived")
    overlay = json.loads(json.dumps(good))
    overlay["corpus"] = {"sha": "12fa296", "condition": "full", "harness": "8bf4e7d", "prompt": "corpus", "reads": "corpus"}
    p.write_text(yaml.safe_dump(overlay))
    c = load_case(p)
    assert (c.corpus_sha, c.harness_sha, c.prompt_source, c.read_source) == ("12fa296", "8bf4e7d", "corpus", "corpus")
    d = json.loads(json.dumps(good))
    del d["source"], d["cut"]
    d["episode"] = "pre/ep"
    p.write_text(yaml.safe_dump(d))
    assert load_case(p).episode == (tmp_path / "pre" / "ep").resolve()


def test_case_file_start_and_session_validation(tmp_path):
    (tmp_path / "b.md").write_text("# brief\n\nline two\n")
    (tmp_path / "empty.md").write_text("\n")
    good = {
        "case": "x", "session": {"dir": "built/20241230-RPL10", "ts": "2024-12-30T14:05:00-08:00", "user": "aaron"},
        "corpus": {"sha": "8bf4e7d", "condition": "full"},
        "run": {"model": "claude-sonnet-5", "effort": "medium", "n": 5, "timeout_s": 1800, "stall_s": 600, "max_turns": 60},
        "allowed_tools": ["Bash"], "grader": None, "fresh": {"brief": "b.md"},
    }
    p = tmp_path / "c.yaml"

    def check(mutate, match):
        d = json.loads(json.dumps(good))
        mutate(d)
        p.write_text(yaml.safe_dump(d))
        with pytest.raises(CutError, match=match):
            load_case(p)

    p.write_text(yaml.safe_dump(good))
    c = load_case(p)
    assert (c.start, c.brief_path, c.brief_text) == ("fresh", tmp_path / "b.md", "# brief\n\nline two\n")
    assert (c.resume_close, c.resume_prompt, c.source, c.episode) == (None, None, None, None)
    assert c.session == tmp_path / "built" / "20241230-RPL10" and c.session_user == "aaron"
    assert c.session_ts == datetime.fromisoformat("2024-12-30T14:05:00-08:00")
    # An unquoted YAML timestamp arrives as a datetime; the raw block stays JSON-serializable for run.json.
    p.write_text(yaml.safe_dump(good).replace("'2024-12-30T14:05:00-08:00'", "2024-12-30T14:05:00-08:00"))
    c = load_case(p)
    assert c.session_ts == datetime.fromisoformat("2024-12-30T14:05:00-08:00") and json.dumps(c.raw)
    check(lambda d: d["fresh"].__setitem__("brief", "nope.md"), "fresh.brief not found")
    check(lambda d: d["fresh"].__setitem__("brief", "empty.md"), "fresh.brief is empty")
    check(lambda d: d["fresh"].__setitem__("mask", True), r"fresh: missing \[\], unknown \['mask'\]")
    check(lambda d: d["corpus"].__setitem__("reads", "corpus"), "a fresh start stages none")
    check(lambda d: d["session"].__setitem__("ts", "2024-12-30T14:05:00"), "session.ts must carry a UTC offset")
    check(lambda d: d["session"].__setitem__("ts", "yesterday"), "session.ts must be an ISO timestamp")
    check(lambda d: d["session"].__setitem__("user", "a/b"), "session.user must be a")
    check(lambda d: d["session"].__setitem__("at", "x"), r"session: missing \[\], unknown \['at'\]")
    check(lambda d: d.__setitem__("episode", "/x"), r"got \['episode', 'session'\]")

    def to_resume(d):
        del d["fresh"]
        d["resume"] = {"close": "Done.", "prompt": "Carry on."}
    check(to_resume, "a hand-built session has no transcript to resume")


BRIEF = "# dev / rig — session brief (picked up in progress)\n\nGoal: test.\nSecond line.\n"


def _fresh_case(setup, **changes):
    (setup["case"].parent / "briefs").mkdir(exist_ok=True)
    (setup["case"].parent / "briefs" / "dev-fan.md").write_text(BRIEF)
    case = yaml.safe_load(setup["case"].read_text())
    del case["resume"]
    case["fresh"] = {"brief": "briefs/dev-fan.md"}
    case.update(changes)
    setup["case"].write_text(yaml.safe_dump(case))
    return case


def test_fresh_start_sends_the_brief_and_stages_no_transcript(setup):
    agent = install_agent(setup, lines=stream(), fresh=True)
    _fresh_case(setup, case="dev-fresh")
    assert main(["run", str(setup["case"]), "--n", "2"]) == 0
    rd = run_dir_of(setup, "dev-fresh")
    run = json.loads((rd / "run.json").read_text())
    sha = hashlib.sha256(BRIEF.encode()).hexdigest()
    assert run["start"] == {"mode": "fresh", "first_message": {
        "source": str(setup["case"].parent / "briefs" / "dev-fan.md"), "sha256": sha, "lines": 4}}
    assert "prompt" not in run and "resume" not in run and "corpus_reads" not in run["episode_source"]
    cut = json.loads((rd / "cut" / "episode.json").read_text())
    assert cut["container"]["transcript"] is None and cut["resume"] is None
    assert list((rd / "cut" / "claude-projects").iterdir()) == []
    original = (setup["root"] / "hera_session.md").read_text()
    session_ids = set()
    for sid, cmd in zip(("00", "01"), agent.calls):
        ep = rd / "episodes" / sid
        assert agent.prompts[sid] == BRIEF == (ep / "session" / "hera_session.md").read_text()
        assert (ep / "session" / "hera_session.md").stat().st_mtime == (ep / "session" / "rig_card.md").stat().st_mtime
        assert "--resume" not in cmd
        session_id = cmd[cmd.index("--session-id") + 1]
        session_ids.add(session_id)
        rec = json.loads((ep / "episode.json").read_text())["run"]
        assert rec["status"] == "ok" and "prompt" not in rec
        assert rec["start"] == {"mode": "fresh", "session_id": session_id, "first_message": run["start"]["first_message"]}
        assert rec["session_jsonl"] == {"path": f"claude-projects/-home-hera-measurements-zack-20260101-dev/{session_id}.jsonl",
                                        "entries_before": 0, "entries_after": 3}
        # Neither the archived brief nor the archived agent's turns are anywhere the container mounts.
        mounted = [f for d in ("session", "claude-projects") for f in (ep / d).rglob("*") if f.is_file()]
        assert not any(original in f.read_text(errors="ignore") or SID in f.name for f in mounted)
    assert len(session_ids) == 2
    warm = [a for a in setup["docker"].of("exec") if "/api/sessions" in a[-1]]
    assert len(warm) == 2 and "'zack/20260101-dev/x_measure.ipynb'" in warm[0][-1]


def test_resume_start_is_unchanged_and_opens_no_sessions(setup):
    agent = install_agent(setup, lines=stream())
    assert main(["run", str(setup["case"]), "--n", "1"]) == 0
    cmd = agent.calls[0]
    assert cmd[cmd.index("--resume") + 1] == SID and "--session-id" not in cmd
    assert agent.prompts["00"] == "Carry on."
    assert not [a for a in setup["docker"].of("exec") if "/api/sessions" in a[-1]]
    run = json.loads((run_dir_of(setup) / "run.json").read_text())
    assert run["start"]["mode"] == "resume" and run["start"]["first_message"]["source"] == "resume.prompt"
    assert run["prompt"] == "Carry on." and run["episode_source"]["corpus_reads"]["mode"] == "archived"


def test_a_resume_cut_bundle_runs_fresh_without_its_transcript(setup):
    install_agent(setup, lines=stream(), fresh=True)
    pre = setup["hera_data"] / "pre"
    assert main(["cut", str(setup["root"]), "--at", setup["b"].uuids["cut"], "--dest", str(pre)]) == 0
    case = _fresh_case(setup, case="dev-pre-fresh", episode=str(pre))
    del case["source"], case["cut"]
    setup["case"].write_text(yaml.safe_dump(case))
    assert main(["run", str(setup["case"]), "--n", "1"]) == 0
    ep = run_dir_of(setup, "dev-pre-fresh") / "episodes" / "00"
    assert not list((ep / "claude-projects").glob(f"*/{SID}.jsonl"))
    assert list((pre / "claude-projects").glob(f"*/{SID}.jsonl"))


def test_a_fresh_cut_bundle_refuses_a_resume_case(setup, capsys):
    _fresh_case(setup)
    pre = setup["hera_data"] / "pre"
    assert main(["cut", "--case", str(setup["case"]), "--dest", str(pre)]) == 0
    assert "fresh — no transcript staged" in capsys.readouterr().out
    case = yaml.safe_load(setup["case"].read_text())
    del case["source"], case["cut"], case["fresh"]
    case.update(episode=str(pre), resume={"close": "Done.", "prompt": "Carry on."})
    setup["case"].write_text(yaml.safe_dump(case))
    with pytest.raises(SystemExit, match="nothing to resume"):
        main(["run", str(setup["case"])])


def test_hand_built_session_runs_fresh(setup, tmp_path):
    install_agent(setup, lines=stream(), fresh=True)
    built = tmp_path / "built" / "20241230-RPL10"
    (built / "hera_scratch").mkdir(parents=True)
    (built / "hera_session.md").write_text("# the brief the builder left\n")
    (built / "rig_card.md").write_text("# Rig card\n")
    (built / "x_measure.ipynb").write_text((setup["root"] / "x_measure.ipynb").read_text())
    case = _fresh_case(setup, case="rpl10", session={"dir": str(built), "ts": "2024-12-30T14:05:00-08:00", "user": "aaron"})
    del case["source"], case["cut"]
    setup["case"].write_text(yaml.safe_dump(case))
    assert main(["run", str(setup["case"]), "--n", "1"]) == 0
    rd = run_dir_of(setup, "rpl10")
    run = json.loads((rd / "run.json").read_text())
    assert run["episode_source"]["mode"] == "session"
    assert run["episode_source"]["cut"] == {"source": str(built), "transcript": None, "timestamp": "2024-12-30T14:05:00-08:00"}
    ep = rd / "episodes" / "00"
    episode = json.loads((ep / "episode.json").read_text())
    assert episode["container"]["session_dir"] == "/home/hera/measurements/aaron/20241230-RPL10"
    assert episode["run"]["status"] == "ok"
    assert (ep / "session" / "hera_session.md").read_text() == BRIEF
    assert (ep / "session" / ".claude" / "episode_stop.py").exists() and all((ep / "stubs" / s).exists() for s in STUBS)
    assert json.loads((ep / "session" / ".claude" / "measure_cells.json").read_text()) == {
        "x_measure.ipynb": [c["id"] for c in json.loads((built / "x_measure.ipynb").read_text())["cells"]]}
    ts = datetime.fromisoformat("2024-12-30T14:05:00-08:00").timestamp()
    assert (ep / "session" / "rig_card.md").stat().st_mtime == ts
    assert not (built / ".claude").exists()  # the source dir is never written
    (built / ".claude").mkdir()
    case["case"] = "rpl10-again"
    setup["case"].write_text(yaml.safe_dump(case))
    with pytest.raises(SystemExit, match="the episode's stop hook goes there"):
        main(["run", str(setup["case"]), "--n", "1"])
    assert list((setup["hera_data"] / "replay" / "runs" / "rpl10-again").glob("*")) == []  # a failed bundle leaves no run dir


def test_stop_cell_sweeps_tells_an_acquisition_from_a_prep_cell():
    def appended(*cells):
        return {"x_measure.ipynb": {"appended": [{"id": i, "cell_type": k, "source": src} for i, k, src in cells], "modified": []},
                "x_ana.ipynb": {"appended": [{"id": "ana1", "cell_type": "code", "source": "s.sweep(a, b)"}], "modified": []}}

    prep = ("p1", "code", "cal = GateCalibration(1, 2)\nprint(cal)")
    fan = ("f1", "code", ["s = async_station(mc)\n", "s.megasweep(magnet.mag, B, k_tg.volt, V)\n"])
    note = ("m1", "markdown", "## we will s.sweep( later")
    f = run_mod._stop_cell_sweeps
    assert f({"cell_ids": ["p1"]}, appended(note, prep, fan)) is False   # the prep cell was handed off; the fan never ran
    assert f({"cell_ids": ["f1"]}, appended(note, prep, fan)) is True
    assert f({"cell_ids": []}, appended(prep, fan)) is True              # a watch names no cell: any appended measure cell
    assert f({"cell_ids": []}, appended(prep)) is False
    assert f({"cell_ids": []}, appended(("w1", "code", "s.watch(max_duration=600)"))) is True
    assert f({"cell_ids": ["gone"]}, appended(prep)) is None and f({"cell_ids": []}, appended(note)) is None
    assert f(None, appended(fan)) is None


def test_summarize_cli_rewrites_summary_csv(setup, capsys):
    install_agent(setup, lines=stream())
    assert main(["run", str(setup["case"]), "--n", "1"]) == 0
    rd = run_dir_of(setup)
    (rd / "summary.csv").unlink()
    assert main(["summarize", str(rd)]) == 0
    assert (rd / "summary.csv").exists() and write_summary(rd) == rd / "summary.csv"
    assert "1 episodes: ok 1" in capsys.readouterr().out
    with pytest.raises(SystemExit, match="no run.json"):
        main(["summarize", str(setup["hera_data"])])


def test_container_helpers(monkeypatch):
    assert container.image_tag("8bf4e7d251f6", "full") == "hera-agent:8bf4e7d-full"
    assert container.image_tag("8bf4e7d251f6", "none", corpus_sha="12fa296b5d3a") == "hera-agent:8bf4e7d.c12fa296-none"
    assert container.image_tag("8bf4e7d251f6", "full", corpus_sha="12fa296b5d3a", corpus_prompt=True) == \
        "hera-agent:8bf4e7d.c12fa296p-full"
    assert container.redact(["-e", "CLAUDE_CODE_OAUTH_TOKEN=abc", "-e", "HOME=/home/hera", "ANTHROPIC_API_KEY=k"]) == \
        ["-e", "CLAUDE_CODE_OAUTH_TOKEN=<redacted>", "-e", "HOME=/home/hera", "ANTHROPIC_API_KEY=<redacted>"]
    monkeypatch.setattr(container, "_docker", lambda args, **k: subprocess.CompletedProcess(args, 1, "", "no such image"))
    with pytest.raises(container.DockerError, match=r"hera/docker/build\.sh 8bf4e7d full"):
        container.resolve_image("8bf4e7d", "full")
    with pytest.raises(container.DockerError,
                       match=r"hera/docker/build\.sh 8bf4e7d --corpus 12fa296 --corpus-prompt full"):
        container.resolve_image("8bf4e7d", "full", corpus_sha="12fa296", corpus_prompt=True)
    monkeypatch.delenv("CLAUDE_CODE_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(container, "OAUTH_TOKEN_FILE", Path("/nonexistent/token"))
    with pytest.raises(container.DockerError, match="no Claude credential"):
        container.credential_env()
    assert os.getuid() >= 0


def test_a_codex_run_reads_the_credential_per_episode_and_keeps_a_rotated_token(setup, tmp_path, monkeypatch):
    """The CLI spends its refresh token when it refreshes; the next episode must start from
    the rotated one, which the harness writes back before scrubbing the episode's copy."""
    host = tmp_path / "codex-home" / "auth.json"
    host.parent.mkdir()
    auth = lambda r: json.dumps({"tokens": {"refresh_token": r}}).encode()  # noqa: E731
    host.write_bytes(auth("r0"))
    monkeypatch.setattr(container, "CODEX_AUTH_FILE", host)
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "operator"))
    monkeypatch.delenv("CODEX_API_KEY", raising=False)
    case = yaml.safe_load(setup["case"].read_text())
    del case["allowed_tools"], case["run"]["max_turns"]
    setup["case"].write_text(yaml.safe_dump({**case, "runner": "codex"}))
    agent = install_agent(setup, lines=[])
    given = []

    def rotating(cmd, **kw):
        if cmd[0] == "docker":
            name = next(a for a in cmd if a.startswith("hera-replay-"))
            run = next(c for c in setup["docker"].of("run") if name in c)
            env = next(a for a in run if a.startswith("HERA_CODEX_AUTH_JSON="))
            r = json.loads(base64.b64decode(env.split("=", 1)[1]))["tokens"]["refresh_token"]
            given.append(r)
            (ep,) = list(setup["hera_data"].glob(f"replay/runs/dev-fan/*/episodes/{name.rsplit('-', 1)[1]}"))
            (ep / "codex-home" / "auth.json").write_bytes(auth(f"r{int(r[1:]) + 1}"))
        return agent(cmd, **kw)

    monkeypatch.setattr(container.subprocess, "Popen", rotating)
    main(["run", str(setup["case"])])
    rd = run_dir_of(setup)
    assert given == ["r0", "r1"] and host.read_bytes() == auth("r2")
    for sid in ("00", "01"):
        rec = json.loads((rd / "episodes" / sid / "episode.json").read_text())["run"]
        assert rec["auth_writeback"] == "written" and rec["secrets_removed"] == ["auth.json"]
        assert "HERA_CODEX_AUTH_JSON=<redacted>" in rec["docker"]["run"]
