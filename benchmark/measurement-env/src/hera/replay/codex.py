"""The Codex CLI as the episode agent (`runner: codex` in the case file).

What differs from `claude -p`, and where it is handled:
- the prompt is `developer_instructions` in `$CODEX_HOME/config.toml`, rendered inside
  the container by `hera/docker/codex-config.py` right before `codex exec` (so the
  image's prompt, corpus overlay included, is the one used);
- the stop hook (`hera/docker/codex-hook.py`) denies commands but cannot end the turn,
  so the run loop polls the marker (`marker_guard`) and stops the container once the
  handoff has landed;
- the `--json` stream carries tokens only; model, effort, version and per-response
  usage come from the rollout Codex writes under `codex-home/` (the `claude-projects/`
  analogue), and cost is priced from `prices.toml`;
- there is no `--max-turns` and no tool allowlist: the case file forbids both keys.
"""

from __future__ import annotations

import base64
import fcntl
import json
import os
import shlex
import tempfile
import time
import tomllib
from pathlib import Path

from hera.replay import quota
from hera.replay.container import refresh_token

RUNNERS = ("claude", "codex")
CODEX_HOME = "/home/hera/.codex"
CONFIG_SCRIPT = "/opt/hera/codex-config.py"
LAST_MESSAGE = "/tmp/last-message.txt"
PRICES = Path(__file__).with_name("prices.toml")
CONFIG_EVENT = "hera.codex_config"
# The stub writes `append_landed` once the real tool has returned; a watch armed
# first may still be followed by the append the hook lets through.
APPEND_SETTLE_S = 60.0
WATCH_GRACE_S = 120.0
SAVE_GRACE_S = 5.0  # JupyterLab writes an RTC append to disk on a save debounce; a kill inside it drops the cells
TOKEN_KEYS = {"input": "input_tokens", "cache_read": "cached_input_tokens",
              "cache_creation": "cache_write_input_tokens", "output": "output_tokens"}


def exec_args(docker: str, name: str, *, session_dir: str, model: str, effort: str) -> list[str]:
    """`docker exec` argv for one Codex turn: render `$CODEX_HOME`, then `codex exec` with
    the brief on stdin. `/bin/sh` rather than bash so the render and the CLI start
    without the wrapper's faketime; Codex's own shells go through the wrapper."""
    inner = (f"python3 {CONFIG_SCRIPT} && exec codex exec --json --skip-git-repo-check "
             f"--dangerously-bypass-approvals-and-sandbox --dangerously-bypass-hook-trust "
             f"-C {shlex.quote(session_dir)} -m {shlex.quote(model)} "
             f"-c {shlex.quote(f'model_reasoning_effort={json.dumps(effort)}')} "
             f"-c {shlex.quote('model_reasoning_summary="detailed"')} -o {LAST_MESSAGE} -")
    return [docker, "exec", "-i", "-w", session_dir, name, "/bin/sh", "-c", inner]


def marker_guard(marker: Path, *, append_settle_s: float = APPEND_SETTLE_S, watch_grace_s: float = WATCH_GRACE_S,
                 save_grace_s: float = SAVE_GRACE_S, clock=time.monotonic):
    """A guard for `container.stream_claude`: `stop_marker` once the episode's handoff has
    settled. An `nb-collab append` handoff settles `save_grace_s` after its `append_landed`
    is recorded (cap `append_settle_s`); a watch armed first waits `watch_grace_s` for the
    append the hook lets through; any other handoff (execute-cell, exec-all, wait) settles
    at once."""
    marker = Path(marker)
    seen: list[float] = []
    landed: list[float] = []

    def check() -> str | None:
        if not marker.exists():
            return None
        now = clock()
        if not seen:
            seen.append(now)
        try:
            rec = json.loads(marker.read_text(encoding="utf-8") or "{}")
        except json.JSONDecodeError:
            return None
        command = rec.get("command") or ""
        if "append_landed" in rec:
            if not landed:
                landed.append(now)
            return "stop_marker" if now - landed[0] >= save_grace_s else None
        if rec.get("tool") == "hera-watch":
            wait = watch_grace_s
        elif command.startswith("nb-collab append"):
            wait = append_settle_s
        else:
            return "stop_marker"
        return "stop_marker" if now - seen[0] > wait else None

    return check


# ------------------------------------------------------------------ what the run produced
def find_rollout(codex_home: Path, thread_id: str | None) -> Path | None:
    files = sorted(Path(codex_home).glob("sessions/*/*/*/rollout-*.jsonl"))
    if thread_id:
        files = [f for f in files if f.name.endswith(f"-{thread_id}.jsonl")] or files
    return files[-1] if files else None


def parse_rollout(path: Path) -> dict:
    """Model, effort and version as Codex recorded them, the assistant-message and
    tool-call counts, and the last thread-wide token usage."""
    out: dict = {"cli_version": None, "models": set(), "efforts": set(), "assistant_messages": 0,
                 "exec_items": 0, "token_records": 0, "tokens": None, "entries": 0, "rate_limits": None}
    with Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            out["entries"] += 1
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            t, p = d.get("type"), d.get("payload") or {}
            if t == "session_meta":
                out["cli_version"] = p.get("cli_version")
            elif t == "turn_context":
                if p.get("model"):
                    out["models"].add(p["model"])
                if p.get("effort"):
                    out["efforts"].add(p["effort"])
            elif t == "response_item":
                kind = p.get("type")
                if kind == "message" and p.get("role") == "assistant":
                    out["assistant_messages"] += 1
                elif kind in ("custom_tool_call", "function_call"):
                    out["exec_items"] += 1
            elif t == "token_usage_record":
                out["token_records"] += 1
                usage = p.get("thread_token_usage") or p.get("usage")
                if usage:
                    out["tokens"] = usage
            elif t == "event_msg" and p.get("type") == "token_count" and p.get("rate_limits"):
                out["rate_limits"] = p["rate_limits"]
    out["models"] = sorted(out["models"])
    out["efforts"] = sorted(out["efforts"])
    return out


def tokens_of(usage: dict | None) -> dict:
    """Codex usage in the record's vocabulary. OpenAI's input_tokens includes the cached
    ones; Claude's does not, and the record follows Claude."""
    u = usage or {}
    tokens = {k: int(u.get(src) or 0) for k, src in TOKEN_KEYS.items()}
    tokens["input"] = max(0, tokens["input"] - tokens["cache_read"])
    return tokens


def load_prices(path: Path = PRICES) -> dict:
    return tomllib.loads(Path(path).read_text(encoding="utf-8"))


def cost_usd(tokens: dict, model: str, prices: dict | None = None) -> float | None:
    prices = load_prices() if prices is None else prices
    table = prices.get("models", {}).get(model)
    if table is None:
        return None
    return round((tokens["input"] * table["input"] + tokens["cache_read"] * table["cached"]
                  + tokens["output"] * table["output"]) / 1e6, 6)


def collect(ep: Path, events: list[dict], *, pinned_model: str, image_version: str | None) -> dict:
    """The Codex half of an episode record: what the stream and the rollout say."""
    ep = Path(ep)
    thread = next((e.get("thread_id") for e in events if e.get("type") == "thread.started"), None)
    turn = next((e for e in reversed(events) if e.get("type") in ("turn.completed", "turn.failed")), None)
    config = next((e for e in events if e.get("type") == CONFIG_EVENT), None)
    commands = [e["item"] for e in events if e.get("type") == "item.started"
                and (e.get("item") or {}).get("type") == "command_execution"]
    completed = sum(1 for e in events if e.get("type") == "item.completed"
                    and (e.get("item") or {}).get("type") == "command_execution")
    errors = [e["item"].get("message") for e in events if e.get("type") == "item.completed"
              and (e.get("item") or {}).get("type") == "error"]
    rollout_path = find_rollout(ep / "codex-home", thread)
    rollout = parse_rollout(rollout_path) if rollout_path else None
    if turn is not None and turn["type"] == "turn.completed":
        tokens, source = tokens_of(turn.get("usage")), "stream"
    elif rollout and rollout["tokens"]:
        tokens, source = tokens_of(rollout["tokens"]), "rollout"
    else:
        tokens, source = tokens_of(None), "none"
    prices = load_prices()
    hook_log = ep / "codex-home" / "hook-log.jsonl"
    return {
        "model": {"pinned": pinned_model, "observed": rollout["models"] if rollout else []},
        "effort_observed": rollout["efforts"] if rollout else [],
        "codex_version": {"image": image_version, "observed": rollout["cli_version"] if rollout else None},
        "result": None if turn is None else {"subtype": turn["type"], "is_error": turn["type"] == "turn.failed",
                                              "error": turn.get("error"), "usage": turn.get("usage")},
        "turns": {"num_turns": None, "api_messages": rollout["assistant_messages"] if rollout else 0,
                  "assistant_events": sum(1 for e in events if e.get("type") == "item.completed"
                                          and (e.get("item") or {}).get("type") == "agent_message"),
                  "tool_calls": len(commands), "commands_completed": completed,
                  "exec_items": rollout["exec_items"] if rollout else 0, "events": len(events)},
        "tokens": tokens,
        "tokens_source": source,
        "cost_usd": cost_usd(tokens, pinned_model, prices),
        "cost_source": {"table": PRICES.name, "asof": prices.get("asof")},
        "rollout": {"path": rollout_path.relative_to(ep).as_posix() if rollout_path else None,
                    "entries": rollout["entries"] if rollout else 0,
                    "token_records": rollout["token_records"] if rollout else 0},
        "config": {k: v for k, v in (config or {}).items() if k != "type"} or None,
        "hook_events": sum(1 for line in hook_log.open(encoding="utf-8") if line.strip()) if hook_log.exists() else 0,
        "stream_errors": errors,
        "clock": {"shells": "faketime", "agent_date": "real"},
        "quota": quota.evidence(events, stderr=_read(ep / "codex-stderr.txt"),
                                rate_limits=rollout["rate_limits"] if rollout else None),
    }


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def status(rec: dict) -> str:
    """The Codex reading of an episode record, after the shared checks."""
    if set(rec.get("effort_observed") or []) - {rec["effort"]}:
        return "model_mismatch"
    if rec["guard"] == "stop_marker":
        return "ok" if rec["stop"] else "no_stop"
    if rec["guard"]:
        return rec["guard"]
    result = rec["result"]
    if result is None:
        rec["error"] = f"codex exited {rec['returncode']} without a turn.completed event"
        return "error"
    if result["is_error"] or rec["returncode"] != 0:
        rec["error"] = f"result {result['subtype']} {result.get('error') or ''}, exit {rec['returncode']}".strip()
        return "error"
    return "ok" if rec["stop"] else "no_stop"


def write_back_auth(ep: Path, credential: dict[str, str], host: Path) -> str | None:
    """A CLI that refreshed its token mid-episode spent the refresh token it was given, so
    the rotated `auth.json` replaces the host credential before the scrub deletes it —
    only while the host still holds the token this episode started from (a compare-and-
    swap under a lock; the rotation that lost the race is logged as `conflict`)."""
    path = Path(ep) / "codex-home" / "auth.json"
    if "HERA_CODEX_AUTH_JSON" not in credential or not path.exists():
        return None
    rotated = path.read_bytes()
    before, after = refresh_token(base64.b64decode(credential["HERA_CODEX_AUTH_JSON"])), refresh_token(rotated)
    if not before or not after or before == after:
        return "unchanged"
    host = Path(host)
    with open(host.with_name(host.name + ".lock"), "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        current = refresh_token(host.read_bytes()) if host.exists() else None
        if current == after:
            return "unchanged"
        if current != before:
            return "conflict"
        fd, tmp = tempfile.mkstemp(dir=host.parent, prefix=".auth-")
        with os.fdopen(fd, "wb") as fh:
            fh.write(rotated)
        os.replace(tmp, host)
    return "written"


def access_expires_at(auth: bytes) -> float | None:
    """The `exp` of the login's access token (epoch seconds); None when unreadable."""
    try:
        token = (json.loads(auth).get("tokens") or {}).get("access_token") or ""
        payload = token.split(".")[1]
        return float(json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))["exp"])
    except (ValueError, IndexError, KeyError, TypeError, AttributeError, UnicodeDecodeError):
        return None


def scrub_secrets(ep: Path) -> list[str]:
    """The token file the render wrote is not part of the archive."""
    removed = []
    auth = Path(ep) / "codex-home" / "auth.json"
    if auth.exists():
        auth.unlink()
        removed.append(auth.name)
    return removed
