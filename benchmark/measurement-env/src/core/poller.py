"""Single-instrument poll driver: owns the stdout protocol and the error policy.

A worker supplies a Source (connect/close/read for one instrument) and a
publish callable (side effects such as InfluxDB and logfiles; returns the
[data] payload). run() does the rest: connect fail-hard, [waiting]/[ready]/
[data], close-and-reconnect on any read failure, exit non-zero after
MAX_FAILURES consecutive failed cycles. One instrument per worker by design:
a dead instrument is a dead worker, which the launcher shows as red.
"""

from __future__ import annotations

import json
import sys
import time
from typing import Callable, NoReturn, Protocol, TypeVar

from core import Tag, emit

R = TypeVar("R")

MAX_FAILURES = 10  # consecutive failed cycles (read or reconnect) before exit
DATA_TIMEOUT = 60  # seconds from [waiting] to the first successful read


class Source(Protocol[R]):
    """One instrument, as the driver sees it."""

    name: str  # e.g. "AMI 1700"; used in log lines

    def connect(self) -> None:
        """Open the instrument; raise on failure."""
        ...

    def close(self) -> None:
        """Tear down; must not raise (the driver also guards it)."""
        ...

    def read(self) -> R:
        """One poll; raise on any I/O failure."""
        ...


# (readings, cycle) -> [data] payload, including an optional "_summary"
Publish = Callable[[R, int], dict[str, object]]


def run(
    source: Source[R],
    *,
    interval: float,
    publish: Publish[R],
    data_timeout: float = DATA_TIMEOUT,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
) -> NoReturn:
    """Poll `source` forever, publishing each reading. Never returns.

    `data_timeout` is the budget from [waiting] to the first successful read;
    a worker whose first read is itself a long scan (the AVS fridge bridge
    takes ~210 s) raises it. `sleep` and `clock` are injectable for tests only.
    """
    emit(Tag.INIT, f"Connecting to {source.name}")
    try:
        source.connect()
    except Exception as e:
        emit(Tag.ERROR, f"Startup failed: {e}")
        sys.exit(1)

    emit(Tag.WAITING)
    waiting_since = clock()
    first = True
    cycle = 0
    failures = 0
    connected = True

    def count_failure(kind: str, error: Exception) -> None:
        """Emit a failure with its running count; exit once the limit is hit."""
        nonlocal failures
        failures += 1
        emit(Tag.ERROR,
             f"{source.name} {kind} failed ({failures}/{MAX_FAILURES}): {error}")
        if failures >= MAX_FAILURES:
            emit(Tag.ERROR,
                 f"{source.name}: giving up after {failures} consecutive failures")
            sys.exit(1)

    while True:
        if first and clock() - waiting_since > data_timeout:
            emit(Tag.ERROR, f"Timed out waiting for data ({data_timeout}s)")
            sys.exit(1)

        if not connected:
            try:
                source.connect()
            except Exception as e:
                count_failure("reconnect", e)
                sleep(interval)
                continue
            connected = True
            emit(Tag.INIT, f"Reconnected to {source.name}")
            continue

        try:
            readings = source.read()
        except Exception as e:
            count_failure("read", e)
            try:
                source.close()
            except Exception as close_error:
                emit(Tag.ERROR, f"{source.name} close failed: {close_error}")
            connected = False
            sleep(interval)
            continue
        failures = 0

        data = publish(readings, cycle)
        if first:
            emit(Tag.READY)
            first = False
        emit(Tag.DATA, json.dumps(data))
        cycle += 1
        sleep(interval)
