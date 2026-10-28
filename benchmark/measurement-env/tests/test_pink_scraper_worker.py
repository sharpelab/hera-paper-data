"""The pink scraper must publish byte-identical points to the legacy publisher.

The worker replaces ``logs_publisher.py`` on the pink PC, whose Grafana
dashboards and history key on the exact metric names, units, and file
selection the legacy script produced. These tests pin the quirks that
must survive the port (see the module docstring of workers.pink_scraper):
the legacy column maps (``PC``, ``PT on``, dropped PT2 block), the
everything-is-mbar unit tag, and the header/data line gating per family —
plus TC's one sanctioned deviation, tailing the freshest file by mtime
instead of the legacy lexical sort that strands the feed on ``_9``.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime

from workers.pink_scraper import (
    FAMILIES,
    _detect_freshest_log,
    _detect_latest_log,
    _is_data_line,
    _parse_line,
    _process_line,
)

FP = FAMILIES["FP"]
TC = FAMILIES["TC"]


def _tab_line(timestamp: str, n_values: int) -> str:
    """A log line where column i carries the value float(i)."""
    return "\t".join([timestamp] + [f"{i}.0" for i in range(1, n_values)]) + "\n"


class _StubWriteApi:
    def __init__(self):
        self.records = []

    def write(self, *, bucket, org, record):
        self.records.append(record)


# --- Column maps ------------------------------------------------------------


def test_fp_publishes_legacy_metric_set_all_mbar():
    # The real pink logFP has 34 columns (two PT blocks); the legacy map
    # covers 27, so exactly the first 24 (through "PT current") publish.
    _ts, metrics = _parse_line(_tab_line("2026-07-13 12:07:56", 34), FP)
    expected = {
        "P1": 1.0, "P2": 2.0, "P3": 3.0, "P4": 4.0, "P5": 5.0,
        "P6": 6.0, "P7": 7.0, "Flow": 8.0, "PC": 9.0,
        "MG0": 10.0, "MG1": 11.0, "MG2": 12.0, "MG3": 13.0,
        "MG4": 14.0, "MG5": 15.0,
        "PT on": 16.0, "W_in": 17.0, "W_out": 18.0, "He": 19.0,
        "Oil": 20.0, "P_low": 21.0, "P_high": 22.0, "PT current": 23.0,
    }
    assert {m: v for m, (v, _u) in metrics.items()} == expected
    assert {u for _v, u in metrics.values()} == {"mbar"}


def test_tc_publishes_legacy_metric_set_all_mbar():
    # 26 columns: Date1, Date2, R0-R9, T0-T9, I0-I3. Yes, temperatures
    # and excitations are tagged mbar — that is what the dashboards key on.
    _ts, metrics = _parse_line(_tab_line("2026-07-15 16:56:43", 26), TC)
    expected = (
        {f"R{i}": 2.0 + i for i in range(10)}
        | {f"T{i}": 12.0 + i for i in range(10)}
        | {f"I{i}": 22.0 + i for i in range(4)}
    )
    assert {m: v for m, (v, _u) in metrics.items()} == expected
    assert {u for _v, u in metrics.values()} == {"mbar"}


def test_truncated_line_publishes_only_indexable_columns():
    # Legacy wraps each column lookup in try/except and moves on.
    _ts, metrics = _parse_line(_tab_line("2026-07-13 12:07:56", 10), FP)
    assert set(metrics) == {"P1", "P2", "P3", "P4", "P5", "P6", "P7", "Flow", "PC"}


def test_timestamp_is_naive_local_converted_to_utc():
    ts, _metrics = _parse_line(_tab_line("2026-07-13 12:07:56", 34), FP)
    assert ts.tzinfo is UTC
    expected = datetime.strptime("2026-07-13 12:07:56", "%Y-%m-%d %H:%M:%S").astimezone(UTC)
    assert ts == expected


def test_family_modes():
    # FP stays fully byte-exact (legacy file sort, fixed dedup timestamp);
    # TC tails the freshest file so its feed doesn't strand on _9.
    assert not FP.tail_freshest
    assert TC.tail_freshest
    assert FP.first_data_timeout == 120
    assert TC.first_data_timeout == 300


# --- Line gating ------------------------------------------------------------


def test_fp_line_gating_skips_hash_headers():
    assert not _is_data_line("#Date\tP1\tP2\n", FP)
    assert _is_data_line("2026-07-13 12:07:56\t1.0\n", FP)


def test_tc_line_gating_requires_year_prefix():
    assert not _is_data_line("Date1\tDate2\tR0\n", TC)
    assert not _is_data_line("#\n", TC)
    assert _is_data_line("2026-07-15 16:56:43\t1.0\n", TC)


# --- File selection ---------------------------------------------------------


def test_avs_selection_matches_case_insensitively_and_picks_freshest(tmp_path):
    # Real files are "LogAVS..." against the legacy "logAVS*" pattern
    # (Windows glob is case-insensitive). The freshest-by-mtime pick must
    # beat the legacy lexical sort's _9 favorite: the logger writes the
    # per-channel files on its own schedule, and _9 can stall for hours.
    names = (
        ["LogAVS___2026-07-10-21-48-15.dat"]
        + [f"LogAVS___2026-07-10-21-48-15_{i}.dat" for i in range(10)]
        + ["logFP___2026-07-13-12-07-56.dat", "unrelated.txt"]
    )
    for n in names:
        (tmp_path / n).touch()
    stale = 1_700_000_000
    for n in names:
        os.utime(tmp_path / n, (stale, stale))
    fresh = tmp_path / "LogAVS___2026-07-10-21-48-15_4.dat"
    os.utime(fresh, (stale + 100, stale + 100))

    picked = _detect_freshest_log(str(tmp_path), TC.glob_pattern)
    assert picked is not None
    assert picked.endswith("LogAVS___2026-07-10-21-48-15_4.dat")

    # ...while the legacy selector (still used by FP) would strand on _9.
    assert _detect_latest_log(str(tmp_path), TC.glob_pattern).endswith("_9.dat")


def test_fp_selection_picks_newest_rotation(tmp_path):
    for n in (
        "logFP___2026-07-06-09-00-00.dat",
        "logFP___2026-07-13-12-07-56.dat",
        "LogAVS___2026-07-10-21-48-15_3.dat",
    ):
        (tmp_path / n).touch()
    picked = _detect_latest_log(str(tmp_path), FP.glob_pattern)
    assert picked is not None
    assert picked.endswith("logFP___2026-07-13-12-07-56.dat")


def test_selection_handles_missing_folder_and_no_matches(tmp_path):
    assert _detect_latest_log(str(tmp_path / "nope"), FP.glob_pattern) is None
    assert _detect_latest_log(str(tmp_path), FP.glob_pattern) is None


# --- Publishing -------------------------------------------------------------


def test_process_line_writes_legacy_line_protocol():
    api = _StubWriteApi()
    old = datetime(2020, 1, 1, tzinfo=UTC)
    assert _process_line(_tab_line("2026-07-13 12:07:56", 34), FP, old, api, "dgg", "016_pink")

    by_metric = {}
    for record in api.records:
        lp = record.to_line_protocol()
        measurement_tags = lp.split(" value=")[0]
        by_metric[measurement_tags] = lp
    # The exact wire bytes the dashboards were built against.
    assert "LC_scrapper,metric=PC,unit=mbar" in by_metric
    assert by_metric["LC_scrapper,metric=PC,unit=mbar"].startswith(
        "LC_scrapper,metric=PC,unit=mbar value=9"
    )
    assert r"LC_scrapper,metric=PT\ on,unit=mbar" in by_metric
    assert len(api.records) == 23


def test_process_line_dedups_against_startup_timestamp():
    api = _StubWriteApi()
    future = datetime(2030, 1, 1, tzinfo=UTC)
    assert not _process_line(_tab_line("2026-07-13 12:07:56", 34), FP, future, api, "o", "b")
    assert api.records == []


def test_process_line_survives_garbage():
    api = _StubWriteApi()
    old = datetime(2020, 1, 1, tzinfo=UTC)
    assert not _process_line("not a log line at all\n", FP, old, api, "o", "b")
    assert api.records == []
