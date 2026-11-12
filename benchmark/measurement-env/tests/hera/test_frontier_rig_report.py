"""Rig reconstruction validity: replayed setup-cell errors vs the experiment's expectations."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hera/evaluations/frontier"))

from fakerig import classify_setup_errors  # noqa: E402

HISTORY = {"cell": 33, "error": "RuntimeError: k_2400 state mismatch \u2014 no writes made.\n  rangei = 1.05e-06 (want 1e-06)"}
GAP = {"cell": 12, "error": "AttributeError: type object 'NonCallableMagicMock' has no attribute '_VOLT_TO_N'"}


def test_expected_history_is_not_unexpected():
    # the real message is multi-line: the match must cross newlines
    unexpected, missing = classify_setup_errors([HISTORY], [{"match": r"RuntimeError: .*rangei"}])
    assert unexpected == [] and missing == []


def test_fake_rig_gap_is_unexpected():
    unexpected, _ = classify_setup_errors([HISTORY, GAP], [{"match": r"RuntimeError: .*rangei"}])
    assert unexpected == [GAP]


def test_expectation_that_never_fired_is_missing():
    unexpected, missing = classify_setup_errors([], [{"match": r"RuntimeError: .*rangei", "cell": 33}])
    assert unexpected == [] and len(missing) == 1


def test_cell_ordinal_narrows_the_match():
    unexpected, missing = classify_setup_errors([HISTORY], [{"match": "RuntimeError", "cell": 99}])
    assert unexpected == [HISTORY] and len(missing) == 1


def test_no_errors_no_expectations_is_clean():
    assert classify_setup_errors([], []) == ([], [])
