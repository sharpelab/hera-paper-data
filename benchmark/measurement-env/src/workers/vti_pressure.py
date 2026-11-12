"""VTI probe-space pressure worker (Terranova 906A).

Polls the Terranova 906A gauge controller over its serial port and publishes
the probe-space pressure to InfluxDB (measurement "vti", metric "probe space
pressure", unit "Torr" — the metric names and units Grafana reads). No
logfiles: the measurement kernel never reads this value back.

The Terranova 906A is one of three VTI monitor instruments the measurement
kernel never touches, so polling it costs the kernel nothing. The contended
magnet field readback lives in workers.vti_magnet.

Stdout protocol (owned by core.poller):
    [init] ...          initialization diagnostics
    [waiting]           connected, waiting for first read
    [ready]             first read published
    [data] {...}        pressure as JSON + _summary
    [error] ...         non-fatal errors (read glitches, InfluxDB write fails)

Reads config from vti.toml in the repo root.

Usage:
    python -m workers.vti_pressure [--dry-run]
"""

from __future__ import annotations

import argparse
import math

from qcodes.instrument import Instrument

from core import Tag, emit
from core.config import load_vti_config
from core.influx import setup_influx, write_point
from core.poller import run
from drivers.Terranova_906A import Terranova_906A

MEASUREMENT = "vti"
METRIC = "probe space pressure"
UNIT = "Torr"
READ_INTERVAL = 30  # seconds between reads


class Terranova906ASource:
    """The Terranova 906A gauge controller over its serial port."""

    name = "Terranova 906A"

    def __init__(self, addr):
        self.addr = addr
        self.inst = None

    def connect(self) -> None:
        emit(Tag.INIT, f"Connecting to Terranova 906A at {self.addr}")
        self.inst = Terranova_906A("terranova_worker", self.addr)

    def close(self) -> None:
        Instrument.close_all()
        self.inst = None

    def read(self) -> float:
        return float(self.inst.pressure())


class FakeSource:
    """Synthetic pressure for --dry-run (no hardware)."""

    name = "Terranova 906A (dry run)"

    def __init__(self):
        self.i = 0

    def connect(self) -> None:
        pass

    def close(self) -> None:
        pass

    def read(self) -> float:
        self.i += 1
        return 1.2e-4 * (1 + 0.1 * math.sin(self.i / 3.0))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="VTI probe-space pressure worker (Terranova 906A)")
    parser.add_argument("--dry-run", action="store_true",
                        help="synthetic readings, no hardware / no InfluxDB")
    args = parser.parse_args(argv)

    if args.dry_run:
        emit(Tag.INIT, "DRY RUN — synthetic readings, no hardware / no InfluxDB")
        source = FakeSource()
        influx = None
    else:
        try:
            config = load_vti_config()
            source = Terranova906ASource(config.hardware.terranova_addr)
            influx = setup_influx(config.influxdb)
        except Exception as e:
            emit(Tag.ERROR, f"Startup failed: {e}")
            raise

    def publish(value: float, cycle: int) -> dict:
        if influx is not None:
            _client, write_api, org, bucket = influx
            try:
                write_point(write_api, org, bucket, MEASUREMENT, METRIC, value, UNIT)
            except Exception as e:
                emit(Tag.ERROR, f"InfluxDB write failed ({METRIC}): {e}")
        formatted = f"{value:.2e} Torr"
        return {METRIC: formatted, "_summary": formatted}

    run(source, interval=READ_INTERVAL, publish=publish)


if __name__ == "__main__":
    main()
