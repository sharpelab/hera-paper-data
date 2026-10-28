"""Read temperatures from Lakeshore log files on the fridge PC.

The fridge control software (e.g. Lakeshore monitor) continuously
appends tab-delimited lines to log files.  Each line has the format::

    date\ttime\tvalue\tunit\tstatus\t...

We tail-read the last line and extract the temperature from the third-
to-last column (``content[-3]``).
"""

from __future__ import annotations

import os
import time
import warnings
from collections.abc import Sequence

import qcodes


class StaleThermometryWarning(UserWarning):
    """A thermometry logfile has stopped advancing (dead worker / wrong probe)."""


def _read_last_line(path: str, *, retries: int = 5) -> list[str]:
    """Tail-read a tab-delimited log file and return its last line's fields.

    Parameters
    ----------
    path : str
        Absolute path to the log file (on the machine running Python).
    retries : int
        Number of attempts when the file is momentarily unreadable
        (e.g. being written to by another process).
    """
    content: list[str] = []
    remaining = retries
    while len(content) == 0 and remaining > 0:
        with open(path, "rb") as f:
            try:
                f.seek(-2, os.SEEK_END)
                while f.read(1) != b"\n":
                    f.seek(-2, os.SEEK_CUR)
                content = f.readline().decode().split("\t")
            except OSError:
                time.sleep(0.005)
                remaining -= 1
    if remaining == 0:
        raise TimeoutError(
            f"Failed to read temperature from {path} after {retries} retries"
        )
    return content


def _read_last_field(path: str, *, field_index: int = -3, retries: int = 5) -> float:
    """Tail-read a tab-delimited log file and return one float field.

    ``field_index`` indexes into the tab-split columns of the last line.
    """
    return float(_read_last_line(path, retries=retries)[field_index])


def _read_last_lines(path: str, n: int = 2, *, block: int = 8192) -> list[list[str]]:
    """Tail-read up to the last ``n`` non-empty lines, tab-split."""
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(max(0, size - block))
        chunk = f.read().decode(errors="replace")
    lines = [ln for ln in chunk.splitlines() if ln.strip()]
    return [ln.split("\t") for ln in lines[-n:]]


def assert_thermometry_live(
    name: str,
    paths: str | Sequence[str],
    *,
    max_age: float,
    max_period: float | None = None,
    ts_index: int = 0,
) -> str:
    """Bring-up liveness gate on worker logfiles — raise, don't warn.

    Gates the **freshest** candidate (the other probe's file is legitimately
    stale): its last line must be younger than ``max_age`` seconds (dead or
    hung worker), and, when ``max_period`` is given, the spacing of its last
    two lines must not exceed it (a live worker at the wrong cadence, e.g. a
    legacy publisher). Prints the passing readback and returns the path.

    Complements `temperature_from_logfiles`, whose per-get staleness is a
    deliberately non-fatal warning sized for mid-sweep reads — this is the
    hard gate for the setup cell, run before anything trusts a T readback.
    """
    candidates = [paths] if isinstance(paths, str) else list(paths)
    now = time.time()
    best: tuple[float, float | None, str] | None = None  # (age, period, path)
    errors: list[str] = []
    for p in candidates:
        try:
            lines = _read_last_lines(p)
            ts = float(lines[-1][ts_index])
            age = now - ts
            period = ts - float(lines[-2][ts_index]) if len(lines) > 1 else None
        except (OSError, ValueError, IndexError) as e:
            errors.append(f"{os.path.basename(p)}: {e}")
            continue
        if best is None or age < best[0]:
            best = (age, period, p)
    if best is None:
        raise TimeoutError(
            f"{name}: no readable thermometry logfile in {candidates} ({errors})"
        )
    age, period, path = best
    base = os.path.basename(path)
    if age > max_age:
        raise RuntimeError(
            f"{name}: freshest logfile ({base}) is {age:.0f}s old "
            f"(gate {max_age:.0f}s) — worker dead or hung; fix before measuring"
        )
    if max_period is not None and period is not None and period > max_period:
        raise RuntimeError(
            f"{name}: {base} writes every {period:.0f}s (gate {max_period:.0f}s) "
            f"— wrong worker cadence; redeploy the worker"
        )
    detail = f", period {period:.0f}s" if period is not None else ""
    print(f"{name}: {base} live — age {age:.0f}s{detail}")
    return path


def temperature_from_logfile(
    name: str,
    path: str,
    *,
    unit: str = "K",
    label: str | None = None,
) -> qcodes.Parameter:
    """Create a QCoDeS Parameter that reads temperature from a log file.

    Parameters
    ----------
    name : str
        QCoDeS parameter name (e.g. ``"T_probe"``).
    path : str
        Absolute path to the tab-delimited log file.
    unit : str
        Unit string for the parameter.
    label : str | None
        Human-readable label.  Defaults to *name*.
    """
    return qcodes.Parameter(
        name,
        unit=unit,
        label=label or name,
        get_cmd=lambda: _read_last_field(path),
    )


def temperature_from_logfiles(
    name: str,
    paths: str | Sequence[str],
    *,
    unit: str = "K",
    label: str | None = None,
    stale_after: float = 300.0,
    value_index: int = -3,
    ts_index: int = 0,
) -> qcodes.Parameter:
    """QCoDeS Parameter that reads T from whichever logfile is freshest.

    Each candidate logfile carries its own measurement timestamp in column
    ``ts_index`` (a unix time written by the AVS workers).  On every get we
    tail-read each candidate, pick the one whose last line is most recent, and
    return its temperature (column ``value_index``).  This auto-skips a dead
    worker or the wrong-probe logfile, which otherwise sits frozen at a
    plausible value that ``assert T < base`` cannot catch.

    Staleness is **non-fatal**: if even the freshest candidate is older than
    ``stale_after`` seconds, we emit a one-time :class:`StaleThermometryWarning`
    (once per stale episode, so it does not spam a per-point sweep) and still
    return the value.  A hard error is raised only when no candidate is
    readable at all (a config error, not the routine stale case).

    Parameters
    ----------
    name : str
        QCoDeS parameter name (e.g. ``"T"``).
    paths : str | Sequence[str]
        One path or a list of candidate paths (e.g. both probe logfiles).
    stale_after : float
        Age in seconds beyond which the freshest read is flagged stale.
    """
    candidates = [paths] if isinstance(paths, str) else list(paths)
    state = {"warned": False}

    def _get() -> float:
        best: tuple[float, float, str] | None = None  # (age, value, path)
        now = time.time()
        for p in candidates:
            try:
                fields = _read_last_line(p)
                value = float(fields[value_index])
                age = now - float(fields[ts_index])
            except (OSError, TimeoutError, ValueError, IndexError):
                continue
            if best is None or age < best[0]:
                best = (age, value, p)
        if best is None:
            raise TimeoutError(
                f"{name}: no readable thermometry logfile in {candidates}"
            )
        age, value, path = best
        if age > stale_after:
            if not state["warned"]:
                warnings.warn(
                    f"{name}: freshest logfile ({os.path.basename(path)}) is "
                    f"{age:.0f}s old (>{stale_after:.0f}s) — dead worker / wrong "
                    f"probe? T may be stale",
                    StaleThermometryWarning,
                    stacklevel=2,
                )
                state["warned"] = True
        else:
            state["warned"] = False
        return value

    return qcodes.Parameter(name, unit=unit, label=label or name, get_cmd=_get)
