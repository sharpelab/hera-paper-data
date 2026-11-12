"""VTI auxiliary monitor worker.

Combines the three uncontended monitor instruments the legacy "Grafana logger"
held (`influx_VTI.ipynb`) into one poller: He level (AMI 1700), probe-space
pressure (Terranova 906A), and the Lakeshore 218 magnet/gm temperatures. None
of these are touched by the measurement kernel, so a single process is safe.
The contended magnet field readback is a SEPARATE worker (workers.vti_magnet).

Each reading fans out to InfluxDB only (measurement "vti", matching the legacy
logger's metric names + units so Grafana is unbroken). No logfiles — unlike the
Lakeshore 335 worker, the kernel never reads these back via fp().

Instrument connection is all-or-nothing (fail-hard): every bus is attempted so
all failures get logged, but if ANY is down at startup the worker exits
non-zero rather than running degraded. A silently-dropped instrument means a
dark Grafana metric no one notices (this is exactly how a busy pressure-gauge
port went unseen once). Per-cycle read failures, by contrast, are transient —
logged and retried next cycle, not fatal.

Stdout protocol:
    [init] ...          initialization diagnostics
    [waiting]           instruments connected, waiting for first read
    [ready]             first read published
    [data] {...}        all live metrics as JSON (+ _summary)
    [error] ...         non-fatal errors (read glitches, InfluxDB write fails)

Reads config from vti.toml in the repo root.

Usage:
    python -m workers.vti_aux [--dry-run]
"""

import argparse
import json
import math
import sys
import time

from core import Tag, emit
from core.influx import setup_influx, write_point
from core.config import load_vti_config
from drivers.AMI_1700 import AMI_1700
from drivers.Lakeshore_218 import Lakeshore_218
from drivers.Terranova_906A import Terranova_906A

MEASUREMENT = "vti"
READ_INTERVAL = 30  # seconds between reads
DATA_TIMEOUT = 60  # max seconds to wait for first data after [waiting]


class InstrumentConnectError(RuntimeError):
    """One or more monitor instruments failed to connect at startup."""


def _connect_instruments(hw):
    """Connect every monitor instrument. Returns the list of
    (metric, unit, read_fn) tuples on full success.

    Fail-hard: all instruments are attempted so every failure is logged, but if
    any fails to connect an InstrumentConnectError naming them is raised. The
    caller must not run degraded — see the module docstring."""
    readings = []
    failures = []

    try:
        emit(Tag.INIT, f"Connecting to AMI 1700 at {hw.ami1700_addr}")
        ami = AMI_1700("ami1700_worker", hw.ami1700_addr)
        readings.append(("He level", "in", ami.He_level))
    except Exception as e:
        emit(Tag.ERROR, f"AMI 1700 connect failed: {e}")
        failures.append(f"AMI 1700 ({hw.ami1700_addr})")

    try:
        emit(Tag.INIT, f"Connecting to Terranova 906A at {hw.terranova_addr}")
        terranova = Terranova_906A("terranova_worker", hw.terranova_addr)
        readings.append(("probe space pressure", "Torr", terranova.pressure))
    except Exception as e:
        emit(Tag.ERROR, f"Terranova 906A connect failed: {e}")
        failures.append(f"Terranova 906A ({hw.terranova_addr})")

    try:
        emit(Tag.INIT, f"Connecting to Lakeshore 218 at {hw.lakeshore218_gpib}")
        l218 = Lakeshore_218("l218_worker", hw.lakeshore218_gpib)
        readings.append(("magnet temperature", "K", l218.magnet_temperature))
        readings.append(("gm temperature", "K", l218.gm_temperature))
    except Exception as e:
        emit(Tag.ERROR, f"Lakeshore 218 connect failed: {e}")
        failures.append(f"Lakeshore 218 ({hw.lakeshore218_gpib})")

    if failures:
        raise InstrumentConnectError("; ".join(failures))

    return readings


def _fake_readings(i):
    """Synthetic readings for --dry-run (no hardware)."""
    return [
        ("He level", "in", lambda: 18.0 + 0.5 * math.sin(i / 7.0)),
        ("probe space pressure", "Torr", lambda: 1.2e-4 * (1 + 0.1 * math.sin(i / 3.0))),
        ("magnet temperature", "K", lambda: 3.9 + 0.05 * math.sin(i / 5.0)),
        ("gm temperature", "K", lambda: 40.0 + 0.5 * math.sin(i / 5.0)),
    ]


def _format_value(metric, value):
    """Human-readable value+unit for the launcher data panel."""
    if metric == "He level":
        return f"{value:.2f} in"
    if metric == "probe space pressure":
        return f"{value:.2e} Torr"
    return f"{value:.3f} K"


def main(argv=None):
    parser = argparse.ArgumentParser(description="VTI auxiliary monitor worker")
    parser.add_argument("--dry-run", action="store_true",
                        help="synthetic readings, no hardware / no InfluxDB")
    args = parser.parse_args(argv)

    write_api = org = bucket = None
    if args.dry_run:
        emit(Tag.INIT, "DRY RUN — synthetic readings, no hardware / no InfluxDB")
        readings = _fake_readings(0)
    else:
        config = load_vti_config()
        try:
            readings = _connect_instruments(config.hardware)
        except InstrumentConnectError as e:
            emit(Tag.ERROR, f"Instrument connect failed, exiting: {e}")
            sys.exit(1)
        try:
            _client, write_api, org, bucket = setup_influx(config.influxdb)
        except Exception as e:
            emit(Tag.ERROR, f"Startup failed: {e}")
            raise

    emit(Tag.WAITING)
    waiting_since = time.monotonic()
    first = True
    i = 0
    while True:
        if first and time.monotonic() - waiting_since > DATA_TIMEOUT:
            emit(Tag.ERROR, f"Timed out waiting for data ({DATA_TIMEOUT}s)")
            sys.exit(1)

        i += 1
        if args.dry_run:
            readings = _fake_readings(i)

        data: dict[str, object] = {}
        he_level = None
        ok = True
        for metric, unit, read_fn in readings:
            try:
                value = float(read_fn())
            except Exception as e:
                emit(Tag.ERROR, f"{metric} read failed: {e}")
                ok = False
                continue

            if metric == "He level":
                he_level = value
            data[metric] = _format_value(metric, value)

            if not args.dry_run:
                try:
                    write_point(write_api, org, bucket, MEASUREMENT, metric, value, unit)
                except Exception as e:
                    emit(Tag.ERROR, f"InfluxDB write failed ({metric}): {e}")

        if first and ok:
            emit(Tag.READY)
            first = False

        if he_level is not None:
            data["_summary"] = f"He {he_level:.1f} in"
        emit(Tag.DATA, json.dumps(data))

        time.sleep(READ_INTERVAL)


if __name__ == "__main__":
    main()
