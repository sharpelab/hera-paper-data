"""Lakeshore 335 temperature + heater-state worker (VTI rig).

Single persistent GPIB master on the LS335. Polls each input's temperature
(KRDG?), sensor reading (SRDG?), reading status (RDGST?) and temperature
limit (TLIMIT?) plus each output's heater range (RANGE?), power (HTR?),
setpoint (SETP?) and control mode (OUTMODE?) on a fixed cadence, then sends
``MODE 0`` as the last command of the cycle so the front panel is live
between polls (REN re-asserts remote on every addressed transaction).

Readings fan out to BOTH InfluxDB (measurement "vti") and tab-delimited
local logfiles that ``sharpelab_nb.thermometry.temperature_from_logfiles``
reads. Temperatures go to InfluxDB every INFLUX_EVERY-th cycle; heater state
(range, setpoint, mode, tlimit, reading status — plus power alongside) also
lands immediately on any change, so a range or setpoint command shows up in
Grafana within one poll instead of up to 30 s later.

A temperature is published only while ``RDGST?`` reads 0: a curveless or
faulted input reads 0 K, which must never reach the logfile or InfluxDB as
a temperature. The raw RDGST value goes out as ``<prefix> reading status``
every cycle it is written, so "no temperature" is an explicit state (0 valid;
e.g. 160 = T-over + SU-over with the probe out) rather than a gap, and the
launcher's health check keys on that metric, not on the temperature. Heater
state is published regardless.

Both inputs ride the one GPIB session, so a failure on either input is an
instrument failure: the cycle publishes nothing and the reconnect policy in
``core.poller`` applies.

Logfile columns (mirrors the AVS workers so the default value_index=-3 picks
kelvin, and the col-0 unix timestamp drives staleness/dead-worker detection).
Heater range and power share the status column (``R<range> P<power%>``) so
kelvin stays at split index -3::

    unix \t ctime \t sensor \t kelvin \t R2 P33.5 \t

Stdout protocol:
    [init] ...          initialization diagnostics
    [waiting]           connected, waiting for first read
    [ready]             first reading published
    [data] {...}        sample/vaporizer T + heater state as JSON (+ _summary)
    [error] ...         non-fatal errors (log/InfluxDB write fails, invalid input)

Reads config from vti.toml in the repo root.

Usage:
    python -m workers.lakeshore [--dry-run]
"""

import argparse
import math
import time
from dataclasses import dataclass
from pathlib import Path

from qcodes.instrument import Instrument

from core import Tag, emit
from core.influx import setup_influx, write_point
from core.config import load_vti_config
from core.poller import run
from drivers.Lakeshore_335 import Lakeshore_335

MEASUREMENT = "vti"
READ_INTERVAL = 5  # seconds between GPIB polls / logfile appends
INFLUX_EVERY = 6  # write InfluxDB every Nth cycle (= 30 s, the legacy cadence)

# (logfile name, sensor input letter, heater output number, influx metric prefix)
INPUTS = (
    ("VTI_sample", "A", 1, "sample"),
    ("VTI_vaporizer", "B", 2, "vaporizer"),
)

# OUTMODE? mode field (manual p. 121). Only 0-3 occur on the VTI.
MODE_NAMES = {0: "off", 1: "PID", 2: "zone", 3: "open", 4: "monitor", 5: "warmup"}


@dataclass(frozen=True)
class InputReading:
    """One input/output pair as read in a single poll."""

    kelvin: float
    sensor: float  # ohms (SRDG?)
    rdgst: int  # RDGST? bit field; 0 = valid reading
    range: int  # RANGE? 0 off / 1 low / 2 med / 3 high
    power: float  # HTR? % of full-scale current
    setpoint: float  # SETP? K
    mode: int  # OUTMODE? mode field
    tlimit: float  # TLIMIT? K; 0 = off

    @property
    def valid(self) -> bool:
        return self.rdgst == 0

    @property
    def state(self) -> tuple[int, float, int, float, int]:
        """The delta-triggering subset: range, setpoint, mode, tlimit, rdgst."""
        return (self.range, self.setpoint, self.mode, self.tlimit, self.rdgst)


def format_log_line(t_unix: int, t_str: str, sensor: float, kelvin: float, status: str) -> str:
    """One tab-delimited logfile line; kelvin lands at split index -3."""
    return f"{t_unix}\t{t_str}\t{sensor:>12.6g}\t{kelvin:>10.5f}\t{status}\t\n"


def format_status(rng: int, power: float) -> str:
    """Logfile status column: heater range + power %, space-joined (no new tab)."""
    return f"R{rng} P{power:.1f}"


def write_log(log_dir: Path, name: str, t_unix: int, t_str: str,
              sensor: float, kelvin: float, status: str) -> None:
    """Append a reading to {log_dir}/{name}.txt."""
    with open(log_dir / f"{name}.txt", "a") as f:
        f.write(format_log_line(t_unix, t_str, sensor, kelvin, status))


# Per input/output pair, in response order. Chained with ";" into ONE query per
# poll (manual p. 91: ≤255 chars; the LS335 answers with one ";"-joined line),
# so the poll is a single write/read pair on the bus — one interleave point for
# a second master instead of sixteen, and a consistent snapshot. Verified on the
# rig 2026-09-02: 16 chained ≈ 15 ms vs 67 ms as single queries.
_QUERIES = ("KRDG? {i}", "SRDG? {i}", "RDGST? {i}", "TLIMIT? {i}",
            "RANGE? {o}", "HTR? {o}", "SETP? {o}", "OUTMODE? {o}")

POLL_QUERY = ";".join(q.format(i=letter, o=output)
                      for _name, letter, output, _prefix in INPUTS
                      for q in _QUERIES)
_FIELDS_PER_INPUT = len(_QUERIES)


def _parse_input(fields: list[str]) -> InputReading:
    kelvin, sensor, rdgst, tlimit, rng, power, setpoint, outmode = fields
    return InputReading(
        kelvin=float(kelvin), sensor=float(sensor), rdgst=int(rdgst),
        range=int(rng), power=float(power), setpoint=float(setpoint),
        mode=int(outmode.split(",")[0]), tlimit=float(tlimit),
    )


def parse_poll(response: str) -> dict[str, InputReading]:
    """Split one chained-poll response into both inputs; raise on any mismatch.

    A wrong field count means the answer is not ours (a second GPIB master's
    query interleaved with the poll — seen on the rig 2026-09-02): raising
    hands the cycle to the poll driver's close-and-reconnect path.
    """
    fields = response.split(";")
    expected = _FIELDS_PER_INPUT * len(INPUTS)
    if len(fields) != expected:
        raise ValueError(f"expected {expected} fields, got {len(fields)}: {response!r}")
    return {
        prefix: _parse_input(fields[k * _FIELDS_PER_INPUT:(k + 1) * _FIELDS_PER_INPUT])
        for k, (_name, _letter, _output, prefix) in enumerate(INPUTS)
    }


def _fake_input(letter: str, i: int) -> InputReading:
    """Synthetic reading for --dry-run (no GPIB)."""
    base = 1.30 if letter == "A" else 1.42
    kelvin = base + 0.02 * math.sin(i / 5.0)
    sensor = 1000.0 + 50.0 * math.sin(i / 5.0)
    return InputReading(kelvin, sensor, rdgst=0, range=0, power=0.0,
                        setpoint=0.0, mode=1, tlimit=320.0)


class Ls335Source:
    """The LS335 as the poll driver sees it: one session, both inputs."""

    name = "Lakeshore 335"

    def __init__(self, gpib: str):
        self.gpib = gpib
        self.inst = None

    def connect(self) -> None:
        emit(Tag.INIT, f"Connecting to Lakeshore 335 at {self.gpib}")
        self.inst = Lakeshore_335("l335_worker", self.gpib)

    def close(self) -> None:
        # qcodes: tolerates a dead session and clears the name registry, so the
        # next connect() can claim "l335_worker" again.
        Instrument.close_all()
        self.inst = None

    def read(self) -> dict[str, InputReading]:
        """Both inputs, keyed by metric prefix; any GPIB failure raises.

        ``MODE 0`` (local, panel unlocked) is the last command of every cycle:
        every addressed transaction re-asserts remote, so set-once does not
        work. Never MODE 2 (panel lockout).
        """
        readings = parse_poll(self.inst.ask(POLL_QUERY))
        self.inst.write("MODE 0")
        return readings


class FakeLs335Source:
    """--dry-run stand-in: synthetic readings, no GPIB."""

    name = "Lakeshore 335 (dry run)"

    def __init__(self):
        self.cycle = 0

    def connect(self) -> None:
        emit(Tag.INIT, "DRY RUN — synthetic readings, no GPIB / no InfluxDB")

    def close(self) -> None:
        pass

    def read(self) -> dict[str, InputReading]:
        self.cycle += 1
        return {prefix: _fake_input(letter, self.cycle)
                for _name, letter, _output, prefix in INPUTS}


def _fmt_tlimit(tlimit: float) -> str:
    """0 = off (the factory default, and the hazard state)."""
    return "off" if tlimit == 0 else f"{tlimit:.0f} K"


class LakeshorePublisher:
    """Fans one cycle out to the logfiles and InfluxDB, returns the [data] payload.

    Logfiles get every cycle (valid readings only); InfluxDB gets temperatures
    every INFLUX_EVERY-th cycle and heater state on that cadence *and* on any
    change. Each write is guarded on its own, so a full disk cannot cost the
    Influx point and a dead Influx cannot cost the logfile the measurement
    kernel reads.
    """

    def __init__(self, log_dir: Path, influx: tuple | None):
        self.log_dir = log_dir
        self.influx = influx
        self._last_state: dict[str, tuple] = {}  # prefix -> state
        self._invalid: set[str] = set()  # prefixes currently reading invalid

    def _write_points(self, prefix: str, points: list[tuple[str, float, str]]) -> None:
        write_api, org, bucket = self.influx
        try:
            for metric, value, unit in points:
                write_point(write_api, org, bucket, MEASUREMENT, metric, value, unit)
        except Exception as e:
            emit(Tag.ERROR, f"InfluxDB write failed ({prefix}): {e}")

    def _note_validity(self, prefix: str, r: InputReading) -> None:
        """One [error] per transition into (and out of) an invalid reading."""
        if r.valid and prefix in self._invalid:
            self._invalid.discard(prefix)
            emit(Tag.INIT, f"{prefix} input valid again (RDGST 0)")
        elif not r.valid and prefix not in self._invalid:
            self._invalid.add(prefix)
            emit(Tag.ERROR, f"{prefix} input invalid (RDGST {r.rdgst}): "
                            f"temperature not logged until it clears")

    def __call__(self, readings: dict[str, InputReading], cycle: int) -> dict[str, object]:
        t_unix = int(time.time())
        t_str = time.ctime(t_unix)
        batch = cycle % INFLUX_EVERY == 0

        data: dict[str, object] = {}

        for name, letter, _output, prefix in INPUTS:
            r = readings[prefix]
            self._note_validity(prefix, r)

            data[f"{prefix} T"] = f"{r.kelvin:.3f} K" if r.valid else f"INVALID (RDGST {r.rdgst})"
            data[f"{prefix} heater"] = (
                f"range {r.range}, {r.power:.1f}%, {MODE_NAMES.get(r.mode, f'mode {r.mode}')}")
            data[f"{prefix} setpoint"] = f"{r.setpoint:.3f} K"
            data[f"tlimit {letter.lower()}"] = _fmt_tlimit(r.tlimit)

            if r.valid:
                try:
                    write_log(self.log_dir, name, t_unix, t_str, r.sensor, r.kelvin,
                              format_status(r.range, r.power))
                except Exception as e:
                    emit(Tag.ERROR, f"Log write failed ({name}): {e}")

            changed = self._last_state.get(prefix) != r.state
            self._last_state[prefix] = r.state

            if self.influx is not None and (batch or changed):
                points: list[tuple[str, float, str]] = []
                if batch and r.valid:
                    points.append((f"{prefix} temperature", r.kelvin, "K"))
                points += [
                    (f"{prefix} heater range", float(r.range), ""),
                    (f"{prefix} heater power", r.power, "%"),
                    (f"{prefix} setpoint", r.setpoint, "K"),
                    (f"{prefix} control mode", float(r.mode), ""),
                    (f"tlimit {letter.lower()}", r.tlimit, "K"),
                    (f"{prefix} reading status", float(r.rdgst), ""),
                ]
                self._write_points(prefix, points)

        data["_summary"] = summarize(readings)
        return data


SHORT_NAMES = {"sample": "sam", "vaporizer": "vap"}  # status row only


def _fmt_temp(r: InputReading, digits: int) -> str:
    return f"{r.kelvin:.{digits}f}K" if r.valid else "INVALID"


def summarize(readings: dict[str, InputReading]) -> str:
    """Status-row headline. Loops with the heater on lead as one HEATING
    phrase (temperature→setpoint power%, one decimal); the rest follow as
    bare temperatures (three decimals — cold-side precision matters).
    Setpoints, ranges, tlimit and the RDGST value live in the data rows."""
    heating, idle = [], []
    for _name, _letter, _output, prefix in INPUTS:
        r, short = readings[prefix], SHORT_NAMES[prefix]
        if r.range > 0:
            heating.append(f"{short} {_fmt_temp(r, 1)}→{r.setpoint:g}K {r.power:.0f}%")
        else:
            idle.append(f"{short} {_fmt_temp(r, 3)}")
    parts = (["HEATING " + ", ".join(heating)] if heating else []) + idle
    return " · ".join(parts)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Lakeshore 335 worker (VTI)")
    parser.add_argument("--dry-run", action="store_true",
                        help="synthetic readings, no GPIB / no InfluxDB")
    args = parser.parse_args(argv)

    try:
        config = load_vti_config()
        log_dir = Path(config.hardware.temperature_log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        emit(Tag.INIT, f"Logfiles: {log_dir}")

        if args.dry_run:
            source = FakeLs335Source()
            influx = None
        else:
            source = Ls335Source(config.hardware.lakeshore_gpib)
            _client, write_api, org, bucket = setup_influx(config.influxdb)
            influx = (write_api, org, bucket)
    except Exception as e:
        emit(Tag.ERROR, f"Startup failed: {e}")
        raise

    run(source, interval=READ_INTERVAL,
        publish=LakeshorePublisher(log_dir, influx))


if __name__ == "__main__":
    main()
