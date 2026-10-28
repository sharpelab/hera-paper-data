"""Tests for nb.py output rendering — specifically error-output handling.

These exercise the `_print_output` renderer used by `nb cells --outputs`.
The error branch is the one that mattered for the 2026-06-14 QC0426 session:
before the fix, an errored cell rendered as `[error: no data]` and dropped
the traceback, forcing agents to hand-parse the raw .ipynb to recover it.
"""

from __future__ import annotations

from tools.nb import _print_output, _strip_ansi, cmd_cells


def test_strip_ansi_removes_color_codes() -> None:
    colored = "\x1b[0;31mValueError\x1b[0m: bad"
    assert _strip_ansi(colored) == "ValueError: bad"


def test_error_output_renders_ename_evalue_and_traceback(capsys) -> None:
    out = {
        "output_type": "error",
        "ename": "ValueError",
        "evalue": "bad input",
        "traceback": [
            "\x1b[0;31m---------------------------------------------------------------------------\x1b[0m",
            "\x1b[0;31mValueError\x1b[0m                  Traceback (most recent call last)",
            "Cell \x1b[0;32mIn[5]\x1b[0m, line 1",
            "\x1b[0;31mValueError\x1b[0m: bad input",
        ],
    }
    _print_output(3, 0, out)
    captured = capsys.readouterr().out
    # Header carries ename: evalue.
    assert "[error] ValueError: bad input" in captured
    # Traceback body is rendered, not dropped.
    assert "Traceback (most recent call last)" in captured
    assert "Cell In[5], line 1" in captured
    # ANSI escapes are stripped for terminal readability.
    assert "\x1b[" not in captured
    # The old broken behavior must not recur.
    assert "no data" not in captured


def test_error_output_without_traceback_still_shows_header(capsys) -> None:
    out = {"output_type": "error", "ename": "KeyError", "evalue": "'k'"}
    _print_output(1, 0, out)
    captured = capsys.readouterr().out
    assert "[error] KeyError: 'k'" in captured
    assert "no data" not in captured


def test_error_output_with_string_traceback(capsys) -> None:
    """Defensive: some kernels emit traceback as a single string, not a list."""
    out = {
        "output_type": "error",
        "ename": "RuntimeError",
        "evalue": "boom",
        "traceback": "line one\nline two",
    }
    _print_output(0, 0, out)
    captured = capsys.readouterr().out
    assert "[error] RuntimeError: boom" in captured
    assert "line one" in captured
    assert "line two" in captured


def test_error_output_missing_ename_evalue_falls_back(capsys) -> None:
    out = {"output_type": "error", "traceback": ["just a trace"]}
    _print_output(0, 0, out)
    captured = capsys.readouterr().out
    assert "[error]" in captured
    assert "just a trace" in captured


def test_stream_output_unaffected(capsys) -> None:
    """Regression guard: the error branch sits before the stream/data paths."""
    out = {"output_type": "stream", "name": "stdout", "text": "hello\n"}
    _print_output(0, 0, out)
    captured = capsys.readouterr().out
    assert "[stream:stdout]" in captured
    assert "hello" in captured


def _html_progress_output() -> dict:
    """One sweep-progress-bar display_data output as stored under RTC: a
    text/html bar plus the `<IPython.core.display.HTML object>` text/plain
    placeholder nb renders."""
    return {
        "output_type": "display_data",
        "data": {
            "text/html": "<div>42% [00:10<00:14, 6.8it/s]</div>",
            "text/plain": "<IPython.core.display.HTML object>",
        },
    }


def test_cells_collapses_progress_bar_spam(capsys) -> None:
    """A run of identical progress-bar outputs collapses to one block instead
    of dumping thousands of `<IPython.core.display.HTML object>` lines."""
    nb = {
        "cells": [
            {
                "cell_type": "code",
                "source": "s.sweep(...)",
                "outputs": [_html_progress_output() for _ in range(500)],
            }
        ]
    }
    cmd_cells(nb, "0", show_outputs=True)
    captured = capsys.readouterr().out
    # The placeholder is shown once, under a collapse header naming the count.
    assert "(×500 identical, collapsed)" in captured
    assert captured.count("<IPython.core.display.HTML object>") == 1
    # And the per-output headers for the collapsed run are gone.
    assert "--- out 1 ---" not in captured


def test_cells_keeps_short_runs_and_distinct_outputs(capsys) -> None:
    """Runs below the threshold, and distinct outputs, render per-output."""
    nb = {
        "cells": [
            {
                "cell_type": "code",
                "source": "x",
                "outputs": [
                    {"output_type": "stream", "name": "stdout", "text": "a\n"},
                    {"output_type": "stream", "name": "stdout", "text": "b\n"},
                    _html_progress_output(),
                    _html_progress_output(),
                ],
            }
        ]
    }
    cmd_cells(nb, "0", show_outputs=True)
    captured = capsys.readouterr().out
    # Two distinct streams + a 2-long run (< threshold) all render in full.
    assert "--- out 0 ---" in captured
    assert "--- out 3 ---" in captured
    assert "collapsed" not in captured
