"""core.poller: the stdout protocol and the error policy for hardware workers.

The driver owns everything a worker would otherwise re-implement badly:
fail-hard on the startup connect, [waiting]/[ready]/[data] ordering,
close-and-reconnect on every read failure, a consecutive-failure budget,
and the first-data timeout. Publish is deliberately unguarded — a bug there
must crash the worker rather than be logged as a hardware fault.
"""

from __future__ import annotations

import json

import pytest

from core import poller


class Halt(BaseException):
    """Stops the endless loop from inside a fake. Not an Exception, so the
    driver's `except Exception` guards can never swallow it."""


class FakeSource:
    """Scripted single instrument; records the call order."""

    def __init__(self, reads, *, name="X", connect_errors=None, close_error=None):
        self.name = name
        self.calls: list[str] = []
        self._reads = list(reads)
        self._connect_errors = list(connect_errors or [])
        self._close_error = close_error

    def connect(self) -> None:
        self.calls.append("connect")
        if self._connect_errors:
            error = self._connect_errors.pop(0)
            if error is not None:
                raise error

    def close(self) -> None:
        self.calls.append("close")
        if self._close_error is not None:
            raise self._close_error

    def read(self):
        self.calls.append("read")
        if not self._reads:
            raise Halt("script exhausted")
        value = self._reads.pop(0)
        if isinstance(value, Exception):
            raise value
        return value


class FakeSleep:
    """Records every interval; optionally advances a FakeClock by it."""

    def __init__(self, clock=None):
        self.calls: list[float] = []
        self._clock = clock

    def __call__(self, seconds: float) -> None:
        self.calls.append(seconds)
        if self._clock is not None:
            self._clock.advance(seconds)


class FakeClock:
    def __init__(self, now: float = 0.0):
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class Publisher:
    """Stand-in for a worker's publish(); records (readings, cycle)."""

    def __init__(self):
        self.calls: list[tuple] = []

    def __call__(self, readings, cycle: int) -> dict:
        self.calls.append((readings, cycle))
        return {"_summary": f"cycle {cycle}", "value": readings}

    @property
    def cycles(self) -> list[int]:
        return [cycle for _, cycle in self.calls]


def drive(capsys, source, *, expect, publish=None, interval=1.0,
          sleep=None, clock=None):
    """Run the driver to completion; returns (emitted lines, the exception).

    run() never returns, so every call ends in an exception — SystemExit
    from the driver's own error policy, or Halt from an exhausted fake.
    """
    with pytest.raises(expect) as excinfo:
        poller.run(
            source,
            interval=interval,
            publish=publish if publish is not None else Publisher(),
            sleep=sleep if sleep is not None else FakeSleep(),
            clock=clock if clock is not None else FakeClock(),
        )
    out = capsys.readouterr().out
    return [line for line in out.splitlines() if line], excinfo.value


def data_payloads(lines: list[str]) -> list[dict]:
    return [json.loads(line[len("[data] "):])
            for line in lines if line.startswith("[data] ")]


# --- Happy path -----------------------------------------------------------


def test_happy_path_protocol_and_cycle_index(capsys):
    source = FakeSource([{"t": 1}, {"t": 2}, {"t": 3}])
    publish = Publisher()
    sleep = FakeSleep()

    lines, _ = drive(capsys, source, expect=Halt, publish=publish,
                     interval=2.5, sleep=sleep)

    assert lines[0] == "[init] Connecting to X"
    assert lines[1] == "[waiting]"
    assert lines[2] == "[ready]"
    assert [line.split(" ", 1)[0] for line in lines[3:]] == ["[data]"] * 3
    assert data_payloads(lines) == [
        {"_summary": "cycle 0", "value": {"t": 1}},
        {"_summary": "cycle 1", "value": {"t": 2}},
        {"_summary": "cycle 2", "value": {"t": 3}},
    ]
    assert publish.cycles == [0, 1, 2]
    assert source.calls == ["connect", "read", "read", "read", "read"]
    assert sleep.calls == [2.5, 2.5, 2.5]


def test_ready_precedes_first_data_only_once(capsys):
    source = FakeSource([{"t": 1}, {"t": 2}])

    lines, _ = drive(capsys, source, expect=Halt)

    assert lines.count("[ready]") == 1
    assert lines.index("[ready]") < lines.index(
        next(line for line in lines if line.startswith("[data] ")))


# --- Startup --------------------------------------------------------------


def test_startup_connect_failure_exits(capsys):
    source = FakeSource([{"t": 1}], connect_errors=[RuntimeError("no device")])

    lines, exc = drive(capsys, source, expect=SystemExit)

    assert exc.code == 1
    assert lines == [
        "[init] Connecting to X",
        "[error] Startup failed: no device",
    ]
    assert source.calls == ["connect"]


# --- Read failure and recovery -------------------------------------------


def test_read_failure_reconnects_and_resets_the_counter(capsys):
    source = FakeSource([
        {"t": 1},
        RuntimeError("boom one"),
        {"t": 2},
        RuntimeError("boom two"),
        {"t": 3},
    ])
    publish = Publisher()

    lines, _ = drive(capsys, source, expect=Halt, publish=publish)

    assert lines == [
        "[init] Connecting to X",
        "[waiting]",
        "[ready]",
        '[data] {"_summary": "cycle 0", "value": {"t": 1}}',
        "[error] X read failed (1/10): boom one",
        "[init] Reconnected to X",
        '[data] {"_summary": "cycle 1", "value": {"t": 2}}',
        # A good read resets the budget, so the second fault is (1/10) again.
        "[error] X read failed (1/10): boom two",
        "[init] Reconnected to X",
        '[data] {"_summary": "cycle 2", "value": {"t": 3}}',
    ]
    assert source.calls == [
        "connect", "read",
        "read", "close", "connect", "read",
        "read", "close", "connect", "read",
        "read",
    ]
    assert source.calls.count("close") == 2
    assert publish.cycles == [0, 1, 2]


def test_close_failure_is_logged_and_the_loop_continues(capsys):
    source = FakeSource([RuntimeError("boom"), {"t": 1}],
                        close_error=OSError("port stuck"))

    lines, _ = drive(capsys, source, expect=Halt)

    assert lines == [
        "[init] Connecting to X",
        "[waiting]",
        "[error] X read failed (1/10): boom",
        "[error] X close failed: port stuck",
        "[init] Reconnected to X",
        "[ready]",
        '[data] {"_summary": "cycle 0", "value": {"t": 1}}',
    ]


# --- The failure budget ---------------------------------------------------


def test_read_failing_every_cycle_gives_up_after_max_failures(capsys):
    source = FakeSource([RuntimeError("dead")] * poller.MAX_FAILURES)
    sleep = FakeSleep()

    lines, exc = drive(capsys, source, expect=SystemExit, interval=3.0,
                       sleep=sleep)

    assert exc.code == 1
    # Startup connect, then read/close/reconnect for each of the first nine
    # failures; the tenth read exits before it can close.
    assert source.calls == (
        ["connect"] + ["read", "close", "connect"] * 9 + ["read"]
    )
    # A successful reconnect does not clear the budget — only a good read does.
    assert [line for line in lines if line.startswith("[error]")] == [
        f"[error] X read failed ({n}/10): dead" for n in range(1, 11)
    ] + ["[error] X: giving up after 10 consecutive failures"]
    assert lines.count("[init] Reconnected to X") == 9
    assert "[ready]" not in lines
    assert data_payloads(lines) == []
    assert sleep.calls == [3.0] * 9


def test_reconnect_failures_count_toward_the_budget(capsys):
    source = FakeSource(
        [RuntimeError("dead")],
        connect_errors=[None] + [OSError("no route")] * 9,
    )

    lines, exc = drive(capsys, source, expect=SystemExit)

    assert exc.code == 1
    assert source.calls == ["connect", "read", "close"] + ["connect"] * 9
    assert [line for line in lines if line.startswith("[error]")] == [
        "[error] X read failed (1/10): dead",
    ] + [
        f"[error] X reconnect failed ({n}/10): no route" for n in range(2, 11)
    ] + ["[error] X: giving up after 10 consecutive failures"]


# --- First-data timeout ---------------------------------------------------


def test_data_timeout_exits_before_the_failure_budget(capsys):
    clock = FakeClock()
    sleep = FakeSleep(clock)
    interval = poller.DATA_TIMEOUT / 2
    source = FakeSource([RuntimeError("nothing yet")] * poller.MAX_FAILURES)

    lines, exc = drive(capsys, source, expect=SystemExit, interval=interval,
                       sleep=sleep, clock=clock)

    assert exc.code == 1
    assert lines[-1] == f"[error] Timed out waiting for data ({poller.DATA_TIMEOUT}s)"
    # Three sleeps of half the timeout each: the check is strictly greater-than,
    # so the cycle that lands exactly on the timeout still runs.
    assert clock.now == pytest.approx(1.5 * poller.DATA_TIMEOUT)
    assert source.calls.count("read") == 3
    assert "[ready]" not in lines


def test_timeout_does_not_fire_once_data_has_arrived(capsys):
    clock = FakeClock()
    sleep = FakeSleep(clock)
    source = FakeSource([{"t": 1}, {"t": 2}])

    lines, _ = drive(capsys, source, expect=Halt,
                     interval=poller.DATA_TIMEOUT * 10, sleep=sleep, clock=clock)

    assert clock.now > poller.DATA_TIMEOUT
    assert not [line for line in lines if line.startswith("[error]")]
    assert len(data_payloads(lines)) == 2


# --- Publish is not guarded ----------------------------------------------


def test_publish_exception_propagates(capsys):
    source = FakeSource([{"t": 1}])

    def publish(readings, cycle):
        raise ValueError("bad payload")

    lines, _ = drive(capsys, source, expect=ValueError, publish=publish)

    # The bug surfaces as a traceback, not as a hardware error line.
    assert lines == ["[init] Connecting to X", "[waiting]"]
    assert source.calls == ["connect", "read"]


def test_data_timeout_is_a_run_parameter(capsys):
    """A worker whose first read is a long scan raises its own budget."""
    clock = FakeClock()
    sleep = FakeSleep(clock)
    source = FakeSource([TimeoutError("scan")] * poller.MAX_FAILURES, name="AVS")
    with pytest.raises(SystemExit):
        poller.run(source, interval=100, publish=Publisher(), data_timeout=250,
                   sleep=sleep, clock=clock)

    lines = [line for line in capsys.readouterr().out.splitlines() if line]
    assert lines[-1] == "[error] Timed out waiting for data (250s)"
    assert clock.now == pytest.approx(300)
    assert source.calls.count("read") == 3
