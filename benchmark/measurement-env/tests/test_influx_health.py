"""Multi-metric freshness: filter, CSV parse, AND semantics, panel display.

A worker owning several instruments is healthy only while every one of its
metrics is being written. A dark instrument returns no row rather than an old
one, so it can only be caught by comparing the names requested against the
names returned — that seam, and the four states a panel renders off it.

Pure functions and a hand-built poller: no network, no GUI.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from gui.influx_health import (
    InfluxHealthPoller,
    _metric_filter,
    _parse_last_writes,
    fetch_last_writes,
)

THRESHOLD = 90


def _poller(metrics, last_writes=None, error=None):
    p = InfluxHealthPoller(
        "https://example.invalid", "token", "dgg", "vti", "vti",
        metrics, THRESHOLD,
    )
    if last_writes is not None:
        p.last_writes = last_writes
    p.error = error
    return p


def _ago(seconds):
    return datetime.now(timezone.utc) - timedelta(seconds=seconds)


# --- filter ---------------------------------------------------------------


def test_filter_lists_every_metric():
    assert _metric_filter(("He level", "magnet temperature")) == (
        'contains(value: r.metric, set: ["He level", "magnet temperature"])'
    )


def test_filter_of_one_metric_still_uses_contains():
    assert _metric_filter(("temp",)) == 'contains(value: r.metric, set: ["temp"])'


# --- CSV parse ------------------------------------------------------------


def test_parse_reads_columns_by_header_position():
    # metric ahead of _time: positions must come from the header, not from a
    # hardcoded index.
    body = (
        "#datatype,string,long,string,dateTime:RFC3339\r\n"
        ",result,table,metric,_time\r\n"
        ",_result,0,He level,2026-09-01T16:52:55Z\r\n"
        ",_result,1,magnet temperature,2026-09-01T16:52:50Z\r\n"
    )
    got = _parse_last_writes(body)
    assert got["He level"] == datetime(2026, 9, 1, 16, 52, 55, tzinfo=timezone.utc)
    assert got["magnet temperature"] == datetime(2026, 9, 1, 16, 52, 50, tzinfo=timezone.utc)


def test_parse_reseats_columns_on_a_second_header():
    body = (
        ",result,table,_time,metric\r\n"
        ",_result,0,2026-09-01T16:52:55Z,He level\r\n"
        "\r\n"
        ",result,table,metric,_time\r\n"
        ",_result,1,magnet temperature,2026-09-01T16:52:50Z\r\n"
    )
    assert set(_parse_last_writes(body)) == {"He level", "magnet temperature"}


def test_parse_of_empty_response_is_empty():
    assert _parse_last_writes("\r\n") == {}


def test_parse_omits_metrics_that_had_no_rows():
    body = ",result,table,_time,metric\r\n,_result,0,2026-09-01T16:52:55Z,He level\r\n"
    assert set(_parse_last_writes(body)) == {"He level"}


# --- fetch seam: requested names vs returned names ------------------------


def test_fetch_returns_none_for_a_metric_with_no_rows(monkeypatch):
    """The mechanism: a dark instrument becomes an explicit None."""
    body = ",result,table,_time,metric\r\n,_result,0,2026-09-01T16:52:55Z,He level\r\n"

    class _Resp:
        def read(self):
            return body.encode()

    monkeypatch.setattr("gui.influx_health.urlopen", lambda req, timeout=10: _Resp())

    got = fetch_last_writes(
        "https://example.invalid", "token", "dgg", "vti", "vti",
        ("He level", "probe space pressure"), 180,
    )
    assert set(got) == {"He level", "probe space pressure"}
    assert got["He level"] == datetime(2026, 9, 1, 16, 52, 55, tzinfo=timezone.utc)
    assert got["probe space pressure"] is None


# --- AND semantics --------------------------------------------------------


def test_all_metrics_fresh_is_healthy():
    p = _poller(("a", "b"), {"a": _ago(5), "b": _ago(10)})
    assert p.stale_metrics == []
    assert p.fresh


def test_one_stale_metric_fails_the_panel():
    p = _poller(("a", "b"), {"a": _ago(5), "b": _ago(500)})
    assert p.stale_metrics == ["b"]
    assert not p.fresh


def test_metric_with_no_write_counts_as_stale():
    p = _poller(("a", "b"), {"a": _ago(5), "b": None})
    assert p.stale_metrics == ["b"]
    assert not p.fresh


def test_stale_metrics_are_reported_in_config_order():
    p = _poller(("a", "b", "c"), {"a": None, "b": _ago(5), "c": _ago(500)})
    assert p.stale_metrics == ["a", "c"]


def test_a_poller_starts_stale_before_its_first_query():
    assert _poller(("a", "b")).stale_metrics == ["a", "b"]


# --- display: the four panel states ---------------------------------------


def test_display_error_wins_over_a_known_timestamp():
    shown = _poller(("a",), {"a": _ago(5)}, error="connection refused").display()
    assert (shown.text, shown.summary, shown.ok) == ("error", "error", False)


def test_display_all_fresh_shows_time_and_age():
    shown = _poller(("a", "b"), {"a": _ago(10), "b": _ago(30)}).display()
    assert shown.ok
    assert shown.text.endswith("(10s ago)")  # newest write across the metrics
    assert shown.summary == ""


def test_display_stale_dates_from_the_stale_metric_not_the_healthy_one():
    # "a" is healthy at 10s; the panel must show b's 2h age, never a's.
    shown = _poller(("a", "b"), {"a": _ago(10), "b": _ago(7200)}).display()
    assert not shown.ok
    assert shown.text.endswith("— stale: b")
    assert "(2h ago)" in shown.text
    assert "(10s ago)" not in shown.text
    assert shown.summary == "stale: b"


def test_display_stale_dates_from_the_oldest_stale_metric():
    shown = _poller(("a", "b"), {"a": _ago(7200), "b": _ago(300)}).display()
    assert "(2h ago)" in shown.text
    assert shown.summary == "stale: a, b"


def test_display_no_write_in_window():
    shown = _poller(("a", "b"), {"a": None, "b": None}).display()
    assert (shown.text, shown.summary, shown.ok) == (
        "no data: a, b", "no data: a, b", False,
    )


def test_display_mixes_a_dark_metric_with_a_stale_one():
    # One never wrote, one wrote long ago: name both, date it from the only
    # stale metric that has a timestamp.
    shown = _poller(("a", "b"), {"a": None, "b": _ago(7200)}).display()
    assert "(2h ago)" in shown.text
    assert shown.summary == "stale: a, b"
