"""Usage-limit evidence (`hera.replay.quota`): which signals mark an item as ended by the
plan's quota, and which never do. No limit has been hit in a replay yet, so the shapes
are the CLIs' documented ones."""

from __future__ import annotations

import json

from hera.replay import quota


def test_a_rejected_rate_limit_event_names_its_window_and_reset():
    ev = [{"type": "rate_limit_event", "rate_limit_info": {"status": "rejected", "rateLimitType": "seven_day",
                                                          "resetsAt": 1790305776}}]
    assert quota.evidence(ev) == {"category": "weekly_limit", "source": "rate_limit_event",
                                  "message": "seven_day rejected", "reset_at": "2026-09-25T03:09:36+00:00"}


def test_allowed_rate_limit_events_are_not_evidence():
    for status in ("allowed", "allowed_warning"):
        assert quota.evidence([{"type": "rate_limit_event", "rate_limit_info": {"status": status}}]) is None


def test_claude_usage_limit_results():
    spent = quota.evidence([{"type": "result", "is_error": True, "result": "Claude AI usage limit reached|1790305776"}])
    assert spent["category"] == "usage_limit" and spent["source"] == "result" and spent["reset_at"].startswith("2026-09-25")
    window = quota.evidence([{"type": "result", "is_error": True,
                              "result": "You've hit your limit · resets 5pm (America/Los_Angeles)"}])
    assert window["category"] == "session_window"  # "resets 5pm" has no H:MM for the parser; reset_at stays None


def test_codex_failures_and_rollout_limits():
    failed = quota.evidence([{"type": "turn.failed", "error": {"message": "429 Too Many Requests"}}])
    assert failed["category"] == "rate_limit" and failed["source"] == "turn.failed"
    top = quota.evidence([{"type": "error", "message": "You've hit your usage limit. Weekly limit reached."}])
    assert top["category"] == "weekly_limit"
    rl = {"primary": {"used_percent": 100.0, "window_minutes": 10080, "resets_at": 1790305776},
          "rate_limit_reached_type": "primary"}
    assert quota.evidence([], rate_limits=rl)["source"] == "rollout"
    assert quota.evidence([], rate_limits={**rl, "rate_limit_reached_type": None}) is None


def test_stderr_counts_and_the_agents_own_words_never_do():
    assert quota.evidence([], stderr="API Error: 429 rate_limit_error")["source"] == "stderr"
    agent = [{"type": "assistant", "message": {"content": [{"type": "text", "text": "usage limit reached; 429"}]}},
             {"type": "result", "is_error": False, "result": "weekly limit reached, rate limited"}]
    assert quota.evidence(agent) is None
    assert quota.evidence([{"type": "result", "is_error": True, "result": "Connection reset by peer"}]) is None
    assert quota.evidence([{"type": "item.completed", "item": {"type": "error", "message": "hooks require trust"}}]) is None


def test_quota_masks_only_failed_endings():
    block = {"category": "rate_limit"}
    assert [quota.status(s, block) for s in ("error", "stall", "timeout")] == ["quota"] * 3
    assert [quota.status(s, block) for s in ("ok", "no_stop", "max_turns", "interrupted", "model_mismatch")] == \
        ["ok", "no_stop", "max_turns", "interrupted", "model_mismatch"]
    assert quota.status("error", None) == "error"


# ---------------------------------------------------------------- readings and the report
def _rle(five, seven, status="allowed", overage=False):
    return {"type": "rate_limit_event", "rate_limit_info": {
        "status": status, "isUsingOverage": overage, "rateLimitType": "five_hour",
        "unifiedWindows": {"five_hour": {"utilization": five, "resetsAt": 1790098800},
                           "seven_day": {"utilization": seven, "resetsAt": 1790424000}}}}


def test_a_claude_rate_limit_event_is_a_reading_per_window():
    r = quota.claude_reading(_rle(0.12, 0.14))
    assert r == {"runner": "claude", "status": "allowed", "overage": False, "windows": {
        "five_hour": {"used": 0.12, "resets_at": "2026-09-22T17:40:00+00:00"},
        "seven_day": {"used": 0.14, "resets_at": "2026-09-26T12:00:00+00:00"}}}
    assert quota.claude_reading({"type": "assistant"}) is None


def test_stream_and_rollout_readings_keep_only_changes(tmp_path):
    t = tmp_path / "transcript.jsonl"
    t.write_text("".join(json.dumps(e) + "\n" for e in (_rle(0.12, 0.14), _rle(0.12, 0.14), _rle(0.13, 0.14))))
    assert [r["windows"]["five_hour"]["used"] for r in quota.claude_readings(t)] == [0.12, 0.13]
    rollout = tmp_path / "rollout.jsonl"
    tc = lambda used, ts: {"timestamp": ts, "type": "event_msg", "payload": {"type": "token_count", "rate_limits": {  # noqa: E731
        "primary": {"used_percent": used, "window_minutes": 10080, "resets_at": 1790305776},
        "secondary": None, "credits": {"balance": "0"}, "plan_type": "prolite", "rate_limit_reached_type": None}}}
    rollout.write_text("".join(json.dumps(e) + "\n" for e in (tc(64.0, "a"), tc(64.0, "b"), tc(65.0, "c"))))
    rs = quota.codex_readings(rollout)
    assert [(r["t"], r["windows"]["seven_day"]["used"], r["plan"]) for r in rs] == [("a", 0.64, "prolite"), ("c", 0.65, "prolite")]


def test_the_report_shows_the_latest_reading_and_a_burn_rate_per_model(tmp_path):
    log = tmp_path / "quota.jsonl"
    for used0, used1, cost in ((0.10, 0.12, 4.0), (0.12, 0.15, 5.0), (0.15, 0.16, 2.0)):
        rs = [quota.claude_reading(_rle(used0, 0.2)), quota.claude_reading(_rle(used1, 0.2))]
        quota.append(log, quota.item_lines(rs, runner="claude", model="claude-fable-5", cost_usd=cost,
                                           source={"run_dir": "r", "sample": "00"}, job="j"))
    rates = quota.burn_rates([json.loads(line) for line in log.read_text().splitlines()])
    assert sorted(round(r, 3) for r in rates[("claude", "five_hour", "claude-fable-5")]) == [0.5, 0.5, 0.6]
    assert rates[("claude", "seven_day", "claude-fable-5")] == [0.0, 0.0, 0.0]
    out = quota.report(log)
    assert "claude: latest reading" in out and "five_hour    16%" in out and "median 0.50" in out and "n=3" in out
    assert quota.report(tmp_path / "none.jsonl").startswith("no readings yet")
