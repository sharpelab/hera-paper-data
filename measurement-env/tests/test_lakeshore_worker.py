"""The lakeshore worker's logfile must round-trip through the kernel reader.

The worker writes tab-delimited lines; the measurement kernel reads them back
via sharpelab_nb.thermometry.temperature_from_logfiles. These two formats are
coupled by column layout (unix at col 0, kelvin at col -3) — this test pins
that contract so a worker-side format change can't silently break the kernel.
"""

from __future__ import annotations

import time
import warnings

import pytest

from sharpelab_nb.thermometry import StaleThermometryWarning, temperature_from_logfiles
from workers.lakeshore import format_log_line


def _write(path, t_unix, kelvin, *, sensor=1234.5, status="R0"):
    # The tail reader walks back to the newline preceding the last line, so a
    # real (always multi-line) logfile is needed — write a prior reading too.
    prior = format_log_line(t_unix - 30, time.ctime(t_unix - 30), sensor, kelvin, status)
    last = format_log_line(t_unix, time.ctime(t_unix), sensor, kelvin, status)
    path.write_text(prior + last)


def test_logfile_roundtrips_through_temperature_from_logfiles(tmp_path):
    log = tmp_path / "VTI_sample.txt"
    _write(log, int(time.time()), 1.2345)

    T = temperature_from_logfiles("T_sample", [str(log)])
    assert T() == pytest.approx(1.2345)


def test_freshest_candidate_is_chosen(tmp_path):
    now = int(time.time())
    stale = tmp_path / "VTI_stale.txt"
    fresh = tmp_path / "VTI_fresh.txt"
    _write(stale, now - 10_000, 9.999)
    _write(fresh, now, 1.500)

    T = temperature_from_logfiles("T_sample", [str(stale), str(fresh)])
    assert T() == pytest.approx(1.500)


def test_stale_logfile_warns_but_returns_value(tmp_path):
    log = tmp_path / "VTI_sample.txt"
    _write(log, int(time.time()) - 10_000, 1.2345)

    T = temperature_from_logfiles("T_sample", [str(log)], stale_after=300.0)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        value = T()
    assert value == pytest.approx(1.2345)
    assert any(issubclass(w.category, StaleThermometryWarning) for w in caught)
