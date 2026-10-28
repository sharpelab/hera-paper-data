"""The Codex runner's pure pieces: the exec argv, the marker guard's settle rule, the
rollout parse and token/cost mapping, the status reading, the case-file rules, the
exec-time config render, and the stop hook port."""

from __future__ import annotations

import base64
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from hera.replay import codex, container
from hera.replay.case import load_case
from hera.replay.errors import CutError

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / "hera/docker/codex-hook.py"
CONFIG_SCRIPT = REPO / "hera/docker/codex-config.py"
CASES = REPO / "hera/replay/cases"


# ------------------------------------------------------------------ argv
def test_exec_args_renders_then_execs_codex_on_stdin():
    argv = codex.exec_args("docker", "c1", session_dir="/home/hera/measurements/z/s", model="gpt-5.6-sol", effort="medium")
    assert argv[:6] == ["docker", "exec", "-i", "-w", "/home/hera/measurements/z/s", "c1"]
    assert argv[6:8] == ["/bin/sh", "-c"]
    inner = argv[8]
    assert inner.startswith(f"python3 {codex.CONFIG_SCRIPT} && exec codex exec --json")
    assert "--dangerously-bypass-approvals-and-sandbox --dangerously-bypass-hook-trust" in inner
    assert "-m gpt-5.6-sol" in inner and "'model_reasoning_effort=\"medium\"'" in inner
    assert "'model_reasoning_summary=\"detailed\"'" in inner
    assert inner.endswith(" -")


# ------------------------------------------------------------------ the marker guard
def _guard(tmp_path, record, **kw):
    marker = tmp_path / "episode-stop.json"
    if record is not None:
        marker.write_text(json.dumps(record))
    t = [0.0]
    g = codex.marker_guard(marker, clock=lambda: t[0], **kw)
    return g, marker, t


def test_guard_is_quiet_without_a_marker(tmp_path):
    g, marker, _ = _guard(tmp_path, None)
    assert g() is None
    marker.write_text(json.dumps({"tool": "nb-collab", "command": "nb-collab execute-cell m_measure.ipynb x"}))
    assert g() == "stop_marker"


def test_guard_waits_for_the_append_to_land(tmp_path):
    g, marker, t = _guard(tmp_path, {"tool": "nb-collab", "command": "nb-collab append m_measure.ipynb --execute"})
    assert g() is None
    t[0] = 30
    assert g() is None
    marker.write_text(json.dumps({"tool": "nb-collab", "command": "nb-collab append m_measure.ipynb --execute",
                                  "append_landed": {"cell_ids": ["a"]}}))
    # Landed is not saved: JupyterLab writes the RTC append to disk on a debounce.
    assert g() is None
    t[0] = 30 + codex.SAVE_GRACE_S
    assert g() == "stop_marker"


def test_guard_caps_an_append_that_never_lands(tmp_path):
    g, _, t = _guard(tmp_path, {"tool": "nb-collab", "command": "nb-collab append m_measure.ipynb --execute"})
    assert g() is None
    t[0] = codex.APPEND_SETTLE_S + 1
    assert g() == "stop_marker"


def test_guard_gives_a_watch_first_handoff_its_grace(tmp_path):
    g, _, t = _guard(tmp_path, {"tool": "hera-watch", "command": "hera-watch data --next --follow"})
    assert g() is None
    t[0] = codex.WATCH_GRACE_S - 1
    assert g() is None
    t[0] = codex.WATCH_GRACE_S + 1
    assert g() == "stop_marker"


# ------------------------------------------------------------------ the rollout
def _rollout(tmp_path, thread="01a0", lines=None):
    d = tmp_path / "codex-home" / "sessions" / "2026" / "09" / "22"
    d.mkdir(parents=True)
    p = d / f"rollout-2026-09-22T08-44-48-{thread}.jsonl"
    rows = lines if lines is not None else [
        {"type": "session_meta", "payload": {"id": thread, "cli_version": "0.155.1"}},
        {"type": "turn_context", "payload": {"model": "gpt-5.6-sol", "effort": "medium"}},
        {"type": "response_item", "payload": {"type": "message", "role": "developer"}},
        {"type": "response_item", "payload": {"type": "message", "role": "assistant"}},
        {"type": "response_item", "payload": {"type": "custom_tool_call", "name": "exec", "input": "x"}},
        {"type": "token_usage_record", "payload": {"usage": {"input_tokens": 100, "cached_input_tokens": 60},
                                                    "thread_token_usage": {"input_tokens": 100, "cached_input_tokens": 60, "output_tokens": 10}}},
        {"type": "response_item", "payload": {"type": "message", "role": "assistant"}},
        {"type": "token_usage_record", "payload": {"thread_token_usage": {"input_tokens": 300, "cached_input_tokens": 250,
                                                                          "cache_write_input_tokens": 0, "output_tokens": 40,
                                                                          "reasoning_output_tokens": 12}}},
    ]
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return p


def test_parse_rollout_reads_model_effort_version_and_the_last_thread_usage(tmp_path):
    p = _rollout(tmp_path)
    r = codex.parse_rollout(p)
    assert r["cli_version"] == "0.155.1" and r["models"] == ["gpt-5.6-sol"] and r["efforts"] == ["medium"]
    assert r["assistant_messages"] == 2 and r["exec_items"] == 1 and r["token_records"] == 2
    assert r["tokens"]["input_tokens"] == 300 and r["entries"] == 8


def test_find_rollout_prefers_the_thread(tmp_path):
    _rollout(tmp_path, thread="aaaa")
    d = tmp_path / "codex-home" / "sessions" / "2026" / "09" / "23"
    d.mkdir(parents=True)
    (d / "rollout-2026-09-23T00-00-00-bbbb.jsonl").write_text("")
    assert str(codex.find_rollout(tmp_path / "codex-home", "aaaa")).endswith("-aaaa.jsonl")
    assert str(codex.find_rollout(tmp_path / "codex-home", "zzzz")).endswith("-bbbb.jsonl")
    assert codex.find_rollout(tmp_path / "nowhere", None) is None


def test_tokens_follow_claude_vocabulary_with_uncached_input():
    t = codex.tokens_of({"input_tokens": 300, "cached_input_tokens": 250, "cache_write_input_tokens": 5,
                         "output_tokens": 40, "reasoning_output_tokens": 12})
    assert t == {"input": 50, "cache_read": 250, "cache_creation": 5, "output": 40}
    assert codex.tokens_of(None) == {"input": 0, "cache_read": 0, "cache_creation": 0, "output": 0}


def test_cost_prices_from_the_table():
    prices = {"asof": "2026-09-22", "models": {"gpt-5.6-sol": {"input": 4.0, "cached": 0.4, "output": 20.0}}}
    tokens = {"input": 1_000_000, "cache_read": 1_000_000, "cache_creation": 0, "output": 100_000}
    assert codex.cost_usd(tokens, "gpt-5.6-sol", prices) == pytest.approx(4.0 + 0.4 + 2.0)
    assert codex.cost_usd(tokens, "gpt-unknown", prices) is None
    live = codex.load_prices()
    assert {"gpt-6-astra", "gpt-5.6-sol"} <= set(live["models"]) and live["asof"]


def test_collect_reads_the_stream_then_the_rollout(tmp_path):
    _rollout(tmp_path)
    (tmp_path / "codex-home" / "hook-log.jsonl").write_text('{"a":1}\n{"b":2}\n')
    events = [
        {"type": "hera.codex_config", "prompt_sha256": "p", "auth": "file"},
        {"type": "thread.started", "thread_id": "01a0"},
        {"type": "turn.started"},
        {"type": "item.started", "item": {"type": "command_execution", "command": "/bin/bash -lc date"}},
        {"type": "item.completed", "item": {"type": "command_execution", "command": "/bin/bash -lc date", "exit_code": 0}},
        {"type": "item.completed", "item": {"type": "agent_message", "text": "DONE"}},
    ]
    killed = codex.collect(tmp_path, events, pinned_model="gpt-5.6-sol", image_version="0.155.1")
    assert killed["tokens_source"] == "rollout" and killed["tokens"]["input"] == 50 and killed["result"] is None
    assert killed["model"]["observed"] == ["gpt-5.6-sol"] and killed["effort_observed"] == ["medium"]
    assert killed["codex_version"] == {"image": "0.155.1", "observed": "0.155.1"}
    assert killed["turns"]["tool_calls"] == 1 and killed["turns"]["commands_completed"] == 1
    assert killed["turns"]["api_messages"] == 2 and killed["turns"]["assistant_events"] == 1
    assert killed["hook_events"] == 2 and killed["config"] == {"prompt_sha256": "p", "auth": "file"}
    assert killed["rollout"]["path"].startswith("codex-home/sessions/") and killed["cost_usd"] > 0
    done = codex.collect(tmp_path, events + [{"type": "turn.completed", "usage": {"input_tokens": 1000, "cached_input_tokens": 900, "output_tokens": 5}}],
                         pinned_model="gpt-5.6-sol", image_version="0.155.1")
    assert done["tokens_source"] == "stream" and done["tokens"] == {"input": 100, "cache_read": 900, "cache_creation": 0, "output": 5}
    assert done["result"]["subtype"] == "turn.completed" and done["result"]["is_error"] is False


# ------------------------------------------------------------------ status
def _rec(**kw):
    base = {"guard": None, "error": None, "returncode": 0, "effort": "medium", "effort_observed": ["medium"],
            "stop": {"tool": "nb-collab"}, "result": {"subtype": "turn.completed", "is_error": False, "error": None}}
    base.update(kw)
    return base


def test_status_stop_marker_is_ok_when_the_marker_exists():
    assert codex.status(_rec(guard="stop_marker", returncode=137, result=None)) == "ok"
    assert codex.status(_rec(guard="stop_marker", stop=None, result=None)) == "no_stop"


def test_status_other_guards_and_results():
    assert codex.status(_rec(guard="timeout", result=None)) == "timeout"
    assert codex.status(_rec()) == "ok"
    assert codex.status(_rec(stop=None)) == "no_stop"
    r = _rec(result=None, returncode=1)
    assert codex.status(r) == "error" and "without a turn.completed" in r["error"]
    r = _rec(result={"subtype": "turn.failed", "is_error": True, "error": {"message": "429"}})
    assert codex.status(r) == "error" and "turn.failed" in r["error"]
    assert codex.status(_rec(effort_observed=["low"])) == "model_mismatch"


def test_scrub_secrets_removes_the_token_file(tmp_path):
    (tmp_path / "codex-home").mkdir()
    (tmp_path / "codex-home" / "auth.json").write_text("{}")
    assert codex.scrub_secrets(tmp_path) == ["auth.json"]
    assert not (tmp_path / "codex-home" / "auth.json").exists()
    assert codex.scrub_secrets(tmp_path) == []


# ------------------------------------------------------------------ the credential
def _auth(refresh: str) -> bytes:
    return json.dumps({"auth_mode": "chatgpt", "tokens": {"refresh_token": refresh, "access_token": f"at-{refresh}"}}).encode()


def _given(refresh: str) -> dict:
    return {"HERA_CODEX_AUTH_JSON": base64.b64encode(_auth(refresh)).decode("ascii")}


def _episode_auth(tmp_path, refresh: str) -> Path:
    ep = tmp_path / "ep"
    (ep / "codex-home").mkdir(parents=True)
    (ep / "codex-home" / "auth.json").write_bytes(_auth(refresh))
    return ep


def test_a_rotated_token_is_written_back_while_the_host_holds_the_one_given(tmp_path):
    host = tmp_path / "home" / "auth.json"
    host.parent.mkdir()
    host.write_bytes(_auth("r1"))
    ep = _episode_auth(tmp_path, "r2")
    assert codex.write_back_auth(ep, _given("r1"), host) == "written"
    assert host.read_bytes() == _auth("r2") and oct(host.stat().st_mode & 0o777) == "0o600"
    assert codex.write_back_auth(ep, _given("r1"), host) == "unchanged"


def test_write_back_leaves_an_unrotated_token_and_a_host_that_moved_on(tmp_path):
    host = tmp_path / "auth.json"
    host.write_bytes(_auth("r3"))
    assert codex.write_back_auth(_episode_auth(tmp_path, "r1"), _given("r1"), host) == "unchanged"
    assert codex.write_back_auth(tmp_path / "ep", _given("r0"), host) == "conflict"
    assert host.read_bytes() == _auth("r3")
    assert codex.write_back_auth(tmp_path / "ep", {"CODEX_API_KEY": "k"}, host) is None


def test_the_credential_refuses_a_copy_of_the_operators_login(tmp_path, monkeypatch):
    monkeypatch.delenv("CODEX_API_KEY", raising=False)
    harness, operator = tmp_path / "harness" / "auth.json", tmp_path / "operator"
    harness.parent.mkdir()
    operator.mkdir()
    monkeypatch.setattr(container, "CODEX_AUTH_FILE", harness)
    monkeypatch.setenv("CODEX_HOME", str(operator))
    harness.write_bytes(_auth("r1"))
    (operator / "auth.json").write_bytes(_auth("r1"))
    with pytest.raises(container.DockerError, match="shares its refresh token"):
        container.credential_env("codex")
    (operator / "auth.json").write_bytes(_auth("r9"))
    assert base64.b64decode(container.credential_env("codex")["HERA_CODEX_AUTH_JSON"]) == _auth("r1")


# ------------------------------------------------------------------ the case file
def _write_case(tmp_path, **override):
    raw = yaml.safe_load((CASES / "vti02-fan-design-sol-corpus.yaml").read_text())
    raw["source"] = str(CASES / raw["source"])
    raw["mask"] = str(CASES / raw["mask"])
    raw["fresh"]["brief"] = str(CASES / raw["fresh"]["brief"])
    raw.update(override)
    p = tmp_path / "case.yaml"
    p.write_text(yaml.safe_dump(raw))
    return p


def test_codex_case_carries_no_allowlist_and_no_turn_cap(tmp_path):
    c = load_case(_write_case(tmp_path))
    assert c.runner == "codex" and c.allowed_tools is None and c.max_turns is None
    assert c.model == "gpt-5.6-sol" and c.effort == "high"


def test_codex_case_refuses_the_claude_only_keys(tmp_path):
    with pytest.raises(CutError, match="allowed_tools has no meaning"):
        load_case(_write_case(tmp_path, allowed_tools=["Bash"]))
    raw = yaml.safe_load(_write_case(tmp_path).read_text())
    raw["run"]["max_turns"] = 120
    p = tmp_path / "case2.yaml"
    p.write_text(yaml.safe_dump(raw))
    with pytest.raises(CutError, match="max_turns has no meaning"):
        load_case(p)


def test_runner_must_be_known(tmp_path):
    with pytest.raises(CutError, match="runner must be one of"):
        load_case(_write_case(tmp_path, runner="pi"))


def test_claude_cases_still_need_both_keys():
    c = load_case(CASES / "vti02-fan-design-fable-corpus.yaml")
    assert c.runner == "claude" and c.max_turns == 120 and c.allowed_tools


@pytest.mark.parametrize("name", ["sol-corpus", "sol-none", "astra-corpus", "astra-none"])
def test_the_four_codex_arms_load(name):
    c = load_case(CASES / f"vti02-fan-design-{name}.yaml")
    assert c.runner == "codex" and c.grader == "fan-design" and c.start == "fresh"
    assert c.condition == ("full" if name.endswith("corpus") else "none")


# ------------------------------------------------------------------ the exec-time render
def test_config_render_writes_the_prompt_as_developer_instructions(tmp_path):
    prompt = tmp_path / "hera_tactical.md"
    prompt.write_text("---\nname: hera-tactical\ndescription: x\n---\n\n# HERA tactical\n\nBody `code`.\n")
    notes = tmp_path / "codex-notes.md"
    notes.write_text("# Harness notes (Codex)\n- one\n")
    home = tmp_path / "home"
    script = tmp_path / "codex-config.py"
    script.write_text(CONFIG_SCRIPT.read_text()
                      .replace('PROMPT = "/home/hera/measurement_env/hera/hera_tactical.md"', f'PROMPT = "{prompt}"')
                      .replace('NOTES = "/opt/hera/codex-notes.md"', f'NOTES = "{notes}"'))
    env = {"CODEX_HOME": str(home), "HERA_CODEX_AUTH_JSON": "eyJhIjogMX0=", "PATH": ""}
    p = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, env=env)
    assert p.returncode == 0, p.stderr
    out = json.loads(p.stdout)
    assert out["type"] == "hera.codex_config" and out["auth"] == "file"
    config = (home / "config.toml").read_text()
    assert config.startswith("developer_instructions = '''\n# Harness notes (Codex)\n- one\n\n\n# HERA tactical")
    assert "name: hera-tactical" not in config
    assert 'inherit = "all"' in config and 'web_search = "disabled"' in config and "multi_agent = false" in config
    import tomllib
    parsed = tomllib.loads(config)
    assert parsed["developer_instructions"].endswith("Body `code`.\n") and parsed["features"]["multi_agent"] is False
    hooks = json.loads((home / "hooks.json").read_text())
    assert hooks["hooks"]["PreToolUse"][0]["matcher"] == "^Bash$"
    assert (home / "auth.json").read_text() == '{"a": 1}' and oct((home / "auth.json").stat().st_mode & 0o777) == "0o600"
    p = subprocess.run([sys.executable, str(script)], capture_output=True, text=True,
                       env={"CODEX_HOME": str(tmp_path / "home2"), "CODEX_API_KEY": "sk", "PATH": ""})
    assert json.loads(p.stdout)["auth"] == "api_key" and not (tmp_path / "home2" / "auth.json").exists()


def test_config_render_refuses_a_prompt_with_a_toml_literal_terminator(tmp_path):
    prompt = tmp_path / "p.md"
    prompt.write_text("x ''' y\n")
    notes = tmp_path / "n.md"
    notes.write_text("n\n")
    script = tmp_path / "codex-config.py"
    script.write_text(CONFIG_SCRIPT.read_text()
                      .replace('PROMPT = "/home/hera/measurement_env/hera/hera_tactical.md"', f'PROMPT = "{prompt}"')
                      .replace('NOTES = "/opt/hera/codex-notes.md"', f'NOTES = "{notes}"'))
    p = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, env={"CODEX_HOME": str(tmp_path / "h"), "PATH": ""})
    assert p.returncode != 0 and "'''" in p.stderr


# ------------------------------------------------------------------ the hook port
def _run_hook(payload: dict, cwd: Path) -> subprocess.CompletedProcess:
    payload = {"cwd": str(cwd), "hook_event_name": "PreToolUse", **payload}
    return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload), capture_output=True, text=True,
                          cwd=cwd, env={"CODEX_HOME": str(cwd), "PATH": ""})


def test_codex_hook_passes_everything_before_the_marker_and_logs(tmp_path):
    p = _run_hook({"tool_name": "Bash", "tool_input": {"command": "nb-collab append m_measure.ipynb --code-file a.py"}, "tool_use_id": "exec-1"}, tmp_path)
    assert p.returncode == 0 and p.stdout == ""
    assert json.loads((tmp_path / "hook-log.jsonl").read_text())["tool_use_id"] == "exec-1"


def test_codex_hook_denies_without_the_unsupported_keys(tmp_path):
    (tmp_path / "episode-stop.json").write_text('{"tool": "nb-collab", "invocation": "nb-collab execute-cell m_measure.ipynb x"}')
    out = json.loads(_run_hook({"tool_name": "Bash", "tool_input": {"command": "ls"}}, tmp_path).stdout)
    assert out == {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                          "permissionDecisionReason": "episode complete"}}


def test_codex_hook_passes_one_measure_append_after_a_watch(tmp_path):
    marker = tmp_path / "episode-stop.json"
    marker.write_text('{"tool": "hera-watch", "invocation": "hera-watch"}')
    append = {"tool_name": "Bash", "tool_input": {"command": "nb-collab append m_measure.ipynb \\\n  --code-file fan.py --execute"}, "tool_use_id": "exec-a"}
    assert json.loads(_run_hook({"tool_name": "Bash", "tool_input": {"command": "nb-collab append --help"}}, tmp_path).stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"
    p = _run_hook(append, tmp_path)
    assert p.returncode == 0 and p.stdout == ""
    assert json.loads(marker.read_text())["append_pass"] == "exec-a"
    assert json.loads(_run_hook(append, tmp_path).stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"
