"""Leiden QCS heater worker — the repo's first command-taking worker.

Owns the QCS (via the MCC DAQ) and does three things:
  - polls channel readback and publishes to stdout/InfluxDB;
  - executes operator commands arriving as JSON lines on **stdin**;
  - never changes an output except on an explicit command (no auto-zero,
    no ramps — see docs/plans/QCS_HEATER_CONTROL.md).

Stdout protocol (docs/worker-architecture.md):
    [init] ...          initialization diagnostics
    [ready]             first successful status read
    [data] {...}        per-channel state + read_at + last_cmd result
    [error] ...         non-fatal errors

Stdin commands (one JSON object per line):
    {"cmd": "set_current", "channel": 3, "ua": 5000}
    {"cmd": "set_on", "channel": 3, "on": true}

Every command is answered by a fresh [data] line whose "last_cmd" field
carries {cmd, channel, ok, detail} — rejections are never silent. On stdin
EOF the worker keeps polling (the launcher owns stopping it). Exits non-zero
after MAX_CONSECUTIVE_FAILURES failed polls so the launcher shows died/red.

Usage:
    python -m workers.qcs_heater [--sim]

--sim runs against an in-memory fake QCS (no hardware, no InfluxDB) so the
panel can be exercised on the dev box.
"""

from __future__ import annotations

import argparse
import json
import queue
import sys
import threading
import time
from datetime import datetime, timezone

from core import Tag, emit
from core.config import load_config
from core.influx import setup_influx, write_point
from drivers.leiden_qcs import (
    QCS_V1_MAP,
    LeidenQcs,
    McculwIO,
    QcsError,
    QcsMap,
)

MEASUREMENT = "QCS"
POLL_INTERVAL = 5  # seconds between readback polls
INFLUX_EVERY = 6  # write InfluxDB every Nth poll (= 30 s), plus on commands
MAX_CONSECUTIVE_FAILURES = 5


# --- Simulation (dev-box panel exercise; no hardware, no InfluxDB) --------

# Same shape as the real map (see drivers.leiden_qcs.QCS_V1_MAP); validated
# is irrelevant in sim.
SIM_MAP = QcsMap(
    channels=dict(QCS_V1_MAP.channels),
    ranges=QCS_V1_MAP.ranges,
    ao_range=QCS_V1_MAP.ao_range,
    validated=True,
)


class _SimIO:
    """In-memory MCC stand-in mimicking the QCS's actual readback: the
    status bit reports whether current flows, i.e. the channel's DAC is
    above 0 V — so panel lamps behave like the real instrument."""

    def __init__(self) -> None:
        self.port_byte = 0
        self.aout: dict[int, float] = {}

    def board_name(self) -> str:
        return "SIM-3101"

    def a_out_volts(self, channel: int, volts: float) -> None:
        self.aout[channel] = volts

    def config_port_out(self) -> None:
        pass

    def config_bit_in(self, bit: int) -> None:
        pass

    def d_out_port(self, byte: int) -> None:
        self.port_byte = byte

    def d_in_port(self) -> int:
        return self.port_byte

    def d_bit_in(self, bit: int) -> bool:
        return self.aout.get(bit // 2, 0.0) > 0.0


# --- Command handling -----------------------------------------------------


def _stdin_reader(cmd_q: queue.Queue[str]) -> None:
    """Feed stdin lines into the queue; ends quietly on EOF."""
    for line in sys.stdin:
        line = line.strip()
        if line:
            cmd_q.put(line)


def handle_command(qcs: LeidenQcs, line: str) -> dict:
    """Execute one command line; always returns a last_cmd dict."""
    try:
        cmd = json.loads(line)
        name = cmd["cmd"]
        channel = qcs.resolve(cmd["channel"])  # number or name ("MC")
    except (QcsError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        return {"cmd": "?", "ok": False, "detail": f"bad command {line!r}: {e}"}

    result = {"cmd": name, "channel": channel}
    try:
        if name == "set_current":
            requested = float(cmd["ua"])
            clamped = qcs.clamp(channel, requested)
            state = qcs.set_current(channel, requested)
            result["ok"] = True
            detail = f"{state.set_ua:g} µA ({state.range_name})"
            if clamped != requested:
                detail += f" — clamped from {requested:g}"
            result["detail"] = detail
        elif name == "set_on":
            on = bool(cmd["on"])
            state = qcs.set_on(channel, on)
            # Report readback without declaring failure on mismatch — the
            # status output may settle slower than our immediate re-read
            # (bring-up will tell); the lamp follows the next poll either way.
            result["ok"] = True
            detail = f"commanded {'on' if on else 'off'}"
            if state.on is None:
                detail += "; readback unavailable"
            elif state.on != on:
                detail += f"; readback still {'on' if state.on else 'off'}"
            result["detail"] = detail
        else:
            result["ok"] = False
            result["detail"] = f"unknown cmd {name!r}"
    except Exception as e:
        # Broad on purpose: mcculw raises ULError (plain Exception) and IO
        # faults raise OSError — a hardware-failed command must still come
        # back as a last_cmd result, never escape into the poll loop.
        result["ok"] = False
        result["detail"] = str(e)
    return result


# --- Publishing -----------------------------------------------------------


def data_payload(qcs: LeidenQcs, last_cmd: dict | None,
                 *, allow_stale: bool = False) -> dict:
    """Build the [data] JSON dict from fresh readback.

    With allow_stale=True a readback failure falls back to cached state
    (flagged "readback_failed") instead of raising — used on the command
    path so a last_cmd result always reaches the panel even when the DAQ
    is unreachable. The poll path keeps allow_stale=False so failures
    feed the dead-DAQ counter."""
    stale = False
    try:
        states = qcs.status()
    except Exception:
        if not allow_stale:
            raise
        states = qcs.cached_status()
        stale = True
    read_at = datetime.now(timezone.utc)
    summary_parts = []
    channels = {}
    for ch, s in sorted(states.items()):
        set_str = "?" if s.set_ua is None else f"{s.set_ua:g}"
        flow = "?" if s.on is None else ("ON " + set_str + "µA" if s.on else "off")
        summary_parts.append(f"{s.name} {flow}")
        channels[s.name] = {
            "channel": ch,
            "on": s.on,  # readback (current flowing); None = unknown
            "commanded_on": s.commanded_on,
            "set_ua": s.set_ua,
            "range": s.range_name,
        }
    payload = {
        "_summary": " · ".join(summary_parts),
        "read_at": read_at.isoformat(timespec="seconds"),
        "channels": channels,
    }
    if stale:
        payload["readback_failed"] = True
    if last_cmd is not None:
        payload["last_cmd"] = last_cmd
    return payload


def write_influx(write_api, org, bucket, payload: dict) -> None:
    """Publish per-channel state. `_on` prefers readback (Grafana must not
    show "off" on a physically driven heater after a restart) and falls
    back to commanded state when readback is unknown, so the metric always
    writes and freshness monitoring works. Unknown setpoints are skipped,
    not faked."""
    for name, ch in payload["channels"].items():
        on = ch["on"] if ch["on"] is not None else ch["commanded_on"]
        write_point(write_api, org, bucket, MEASUREMENT, f"{name}_on",
                    1.0 if on else 0.0, "bool")
        if ch["set_ua"] is not None:
            write_point(write_api, org, bucket, MEASUREMENT, f"{name}_current",
                        ch["set_ua"], "uA")


# --- Main loop ------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sim", action="store_true",
                        help="in-memory fake QCS, no hardware/InfluxDB")
    args = parser.parse_args()

    try:
        if args.sim:
            # No config needed: fake hardware, no InfluxDB, default clamps.
            emit(Tag.INIT, "SIM mode: fake QCS, InfluxDB disabled")
            io, qcs_map = _SimIO(), SIM_MAP
            max_ua: dict[str, float] = {}
            write_api = None
        else:
            if not QCS_V1_MAP.validated:
                emit(Tag.INIT, "WARNING: QCS_V1_MAP is unvalidated — bring-up "
                               "checks pending (docs/plans/QCS_HEATER_CONTROL.md)")
            config = load_config()
            board = config.hardware.qcs_board_num
            if board < 0:
                emit(Tag.ERROR, "hardware.qcs_board_num not set in toploader.toml")
                sys.exit(2)
            io, qcs_map = McculwIO(board, QCS_V1_MAP.ao_range), QCS_V1_MAP
            max_ua = {k: float(v) for k, v in config.hardware.qcs_max_ua.items()}

        emit(Tag.INIT, f"DAQ board: {io.board_name()}")
        qcs = LeidenQcs(io, qcs_map, max_ua)
        qcs.configure_io()
        if not args.sim:
            _client, write_api, org, bucket = setup_influx(config.influxdb)
    except SystemExit:
        raise
    except Exception as e:
        emit(Tag.ERROR, f"Startup failed: {e}")
        raise

    cmd_q: queue.Queue[str] = queue.Queue()
    threading.Thread(target=_stdin_reader, args=(cmd_q,), daemon=True).start()

    emit(Tag.INIT, "channels: " + ", ".join(
        f"{ch}={name}" for ch, name in sorted(qcs_map.channels.items())))

    def publish(last_cmd: dict | None, to_influx: bool,
                allow_stale: bool = False) -> None:
        payload = data_payload(qcs, last_cmd, allow_stale=allow_stale)
        emit(Tag.DATA, json.dumps(payload))
        if to_influx and write_api is not None:
            try:
                write_influx(write_api, org, bucket, payload)
            except Exception as e:
                emit(Tag.ERROR, f"InfluxDB write failed: {e}")

    publish(None, to_influx=True)
    emit(Tag.READY)

    failures = 0
    polls = 0
    next_poll = time.monotonic() + POLL_INTERVAL
    while True:
        try:
            line = cmd_q.get(timeout=max(0.0, next_poll - time.monotonic()))
        except queue.Empty:
            line = None

        try:
            if line is not None:
                last_cmd = handle_command(qcs, line)
                if not last_cmd.get("ok"):
                    emit(Tag.ERROR, f"command failed: {last_cmd['detail']}")
                # allow_stale: the last_cmd result must reach the panel even
                # if the DAQ is unreachable for the follow-up readback.
                publish(last_cmd, to_influx=True, allow_stale=True)
            elif time.monotonic() >= next_poll:
                next_poll = time.monotonic() + POLL_INTERVAL
                polls += 1
                publish(None, to_influx=(polls % INFLUX_EVERY == 0))
            failures = 0
        except Exception as e:
            failures += 1
            emit(Tag.ERROR, f"poll failed ({failures}/{MAX_CONSECUTIVE_FAILURES}): {e}")
            if failures >= MAX_CONSECUTIVE_FAILURES:
                emit(Tag.ERROR, "giving up — hardware unreachable")
                sys.exit(1)
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
