"""Plan quota: usage-limit evidence, and the readings log behind `hera-replay quota`.

Evidence: whether the plan's quota, not the agent, ended an episode or an extraction.
Such an item is recorded as status `quota` — an infrastructure failure, excluded like
`error` but counted apart — with the evidence as its `quota` block. Only the
harness-facing channels are read (rate-limit events, error results, the CLI's stderr,
the Codex rollout's `rate_limits`); what the agent itself wrote never counts.

Readings: every window utilization a job's items report, one JSON line each in the
machine-local log (`hera.replay.jobs.quota_log_path`), plus one `item` line per item
with its first and last reading and its notional cost — the basis of the burn rate.
"""

from __future__ import annotations

import fcntl
import json
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path

from hera.experiment_scheduler import classify_quota

CATEGORIES = frozenset(("exhausted_balance", "weekly_limit", "session_window", "rate_limit"))
# `claude -p` reports a spent plan as "Claude AI usage limit reached|<epoch>", which the
# scheduler's signatures (written for messages that name the reset) miss.
USAGE_LIMIT = re.compile(r"usage limit reached(?:\|(\d{9,11}))?", re.I)
WINDOWS = {"five_hour": "session_window", "seven_day": "weekly_limit"}
STDERR_TAIL = 2000
CODEX_WINDOWS = {300: "five_hour", 10080: "seven_day"}
# Statuses a quota hit presents as; any other ending (ok, no_stop, max_turns, ...) stands.
MASKED = frozenset(("error", "stall", "timeout"))


def evidence(events: list[dict], *, stderr: str = "", rate_limits: dict | None = None) -> dict | None:
    """The first usage-limit signal in a `claude -p` or `codex exec` stream, the CLI's
    stderr tail, or (Codex) the rollout's last `rate_limits`; None when there is none."""
    for e in events:
        info = e.get("rate_limit_info") if e.get("type") == "rate_limit_event" else None
        if info and info.get("status") == "rejected":
            return _block(WINDOWS.get(info.get("rateLimitType"), "session_window"), "rate_limit_event",
                          f"{info.get('rateLimitType')} rejected", info.get("resetsAt"))
    if rate_limits and rate_limits.get("rate_limit_reached_type"):
        primary = rate_limits.get("primary") or {}
        return _block("weekly_limit" if primary.get("window_minutes") == 10080 else "session_window", "rollout",
                      f"rate_limit_reached_type {rate_limits['rate_limit_reached_type']}", primary.get("resets_at"))
    for source, message in [*_messages(events), ("stderr", stderr[-STDERR_TAIL:])]:
        if not message:
            continue
        hit = USAGE_LIMIT.search(message)
        if hit:
            return _block("usage_limit", source, message, int(hit.group(1)) if hit.group(1) else None)
        c = classify_quota(message)
        if c.category in CATEGORIES:
            return _block(c.category, source, c.message, c.reset_at)
    return None


def status(base: str, block: dict | None) -> str:
    """`quota` where the evidence explains a failed ending, else the status as read."""
    return "quota" if block and base in MASKED else base


def _messages(events: list[dict]):
    for e in events:
        t = e.get("type")
        if t == "result" and e.get("is_error"):
            yield "result", str(e.get("result") or "")
        elif t == "turn.failed":
            yield "turn.failed", str((e.get("error") or {}).get("message") or "")
        elif t == "error":
            yield "error", str(e.get("message") or "")
        elif t == "item.completed" and (e.get("item") or {}).get("type") == "error":
            yield "error", str(e["item"].get("message") or "")


def _block(category: str, source: str, message: str, reset) -> dict:
    return {"category": category, "source": source, "message": message[:300], "reset_at": _iso(reset)}


def _iso(reset) -> str | None:
    if reset is None:
        return None
    try:
        return datetime.fromtimestamp(float(reset), timezone.utc).isoformat(timespec="seconds")
    except (TypeError, ValueError, OverflowError, OSError):
        return str(reset)


# ------------------------------------------------------------------ readings
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def claude_reading(ev: dict) -> dict | None:
    """A `rate_limit_event` as a reading: utilization (0–1) and reset per window."""
    info = ev.get("rate_limit_info") if ev.get("type") == "rate_limit_event" else None
    if not info:
        return None
    windows = {k: {"used": w.get("utilization"), "resets_at": _iso(w.get("resetsAt"))}
               for k, w in (info.get("unifiedWindows") or {}).items()}
    if not windows and info.get("rateLimitType"):
        windows = {info["rateLimitType"]: {"used": info.get("utilization"), "resets_at": _iso(info.get("resetsAt"))}}
    return {"runner": "claude", "status": info.get("status"), "overage": info.get("isUsingOverage"), "windows": windows}


def claude_readings(transcript: Path) -> list[dict]:
    """The readings in a `claude -p` stream on disk (an extraction's transcript)."""
    out = []
    for ev in _jsonl(transcript):
        r = claude_reading(ev)
        if r and (not out or out[-1]["windows"] != r["windows"] or out[-1]["status"] != r["status"]):
            out.append(r)
    return out


def codex_readings(rollout: Path) -> list[dict]:
    """The rollout's `rate_limits`, one reading per change, timestamped as Codex wrote them."""
    out = []
    for d in _jsonl(rollout):
        p = d.get("payload") or {}
        rl = p.get("rate_limits") if d.get("type") == "event_msg" and p.get("type") == "token_count" else None
        if not rl:
            continue
        windows = {}
        for w in (rl.get("primary"), rl.get("secondary")):
            if w:
                name = CODEX_WINDOWS.get(w.get("window_minutes"), f"{w.get('window_minutes')}m")
                used = w.get("used_percent")
                windows[name] = {"used": None if used is None else round(used / 100, 4), "resets_at": _iso(w.get("resets_at"))}
        r = {"t": d.get("timestamp"), "runner": "codex", "plan": rl.get("plan_type"),
             "status": "rejected" if rl.get("rate_limit_reached_type") else "allowed",
             "credits": (rl.get("credits") or {}).get("balance"), "windows": windows}
        if not out or out[-1]["windows"] != windows or out[-1]["status"] != r["status"]:
            out.append(r)
    return out


def append(path: Path, lines: list[dict]) -> None:
    """Append lines to the log under an exclusive lock (jobs write it concurrently)."""
    if not lines:
        return
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.write("".join(json.dumps(line, ensure_ascii=False) + "\n" for line in lines))


def item_lines(readings: list[dict], *, runner: str, model: str | None, cost_usd: float | None, source: dict,
               job: str | None) -> list[dict]:
    """One `reading` line per reading and the item's `item` line (first and last windows,
    cost), all tagged with the item's source and job."""
    base = {"runner": runner, "source": source, "job": job}
    lines = [{"t": r.get("t") or now_iso(), "kind": "reading", **base, **{k: v for k, v in r.items() if k != "t"}}
             for r in readings]
    if readings:
        lines.append({"t": now_iso(), "kind": "item", **base, "model": model, "cost_usd": cost_usd,
                      "first": readings[0]["windows"], "last": readings[-1]["windows"]})
    return lines


# ------------------------------------------------------------------ report
def burn_rates(lines: list[dict]) -> dict:
    """Per (runner, window, model): percentage points of the window per notional dollar,
    from each item's first-to-last change inside one window (same reset)."""
    rates: dict = {}
    for line in lines:
        if line.get("kind") != "item" or not line.get("cost_usd"):
            continue
        for window, last in (line.get("last") or {}).items():
            first = (line.get("first") or {}).get(window)
            if not first or first.get("resets_at") != last.get("resets_at") or None in (first.get("used"), last.get("used")):
                continue
            rate = 100 * (last["used"] - first["used"]) / line["cost_usd"]
            rates.setdefault((line["runner"], window, line.get("model")), []).append(rate)
    return rates


def report(path: Path, *, now: datetime | None = None) -> str:
    lines = list(_jsonl(Path(path)))
    if not lines:
        return f"no readings yet ({path})"
    now = now or datetime.now(timezone.utc)
    out = []
    for runner in sorted({ln["runner"] for ln in lines if ln.get("kind") == "reading"}):
        last = None
        for ln in lines:  # the log's order breaks ties between readings stamped in one second
            if ln.get("kind") == "reading" and ln["runner"] == runner and (last is None or ln["t"] >= last["t"]):
                last = ln
        age = (now - datetime.fromisoformat(last["t"].replace("Z", "+00:00"))).total_seconds() / 60
        flags = [f"status {last.get('status')}"] + (["OVERAGE"] if last.get("overage") else []) \
            + ([f"plan {last['plan']}"] if last.get("plan") else [])
        out.append(f"{runner}: latest reading {last['t']} ({age:.0f} min ago), {', '.join(flags)}")
        for window, w in sorted(last["windows"].items()):
            used = "?" if w.get("used") is None else f"{100 * w['used']:.0f}%"
            out.append(f"    {window:10s} {used:>5s}  resets {w.get('resets_at')}")
    rates = burn_rates(lines)
    if rates:
        out.append("burn (percentage points of the window per notional $; each item's change, other use included):")
        for (runner, window, model), rs in sorted(rates.items(), key=lambda kv: tuple(str(x) for x in kv[0])):
            q = statistics.quantiles(rs, n=4) if len(rs) >= 2 else [rs[0]] * 3
            out.append(f"    {runner:6s} {window:10s} {model or '-':28s} median {statistics.median(rs):.2f}  "
                       f"IQR {q[0]:.2f}–{q[2]:.2f}  n={len(rs)}")
    return "\n".join(out)


def _jsonl(path: Path):
    path = Path(path)
    if not path.exists():
        return
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(d, dict):
                yield d
