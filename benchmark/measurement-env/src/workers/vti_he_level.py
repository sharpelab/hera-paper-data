"""VTI helium level worker (AMI 1700).

Polls the AMI 1700 level meter for the dewar's helium level and publishes it to
InfluxDB (measurement "vti", metric "He level", unit "in" — the metric names
and units Grafana reads). No logfiles: the measurement kernel never reads this
value back.

The AMI 1700 is one of three VTI monitor instruments the measurement kernel
never touches, so polling it costs the kernel nothing. The contended magnet
field readback lives in workers.vti_magnet.

Stdout protocol (owned by core.poller):
    [init] ...          initialization diagnostics
    [waiting]           connected, waiting for first read
    [ready]             first read published
    [data] {...}        He level as JSON + _summary
    [error] ...         non-fatal errors (read glitches, InfluxDB write fails)

Reads config from vti.toml in the repo root.

Usage:
    python -m workers.vti_he_level [--dry-run]
"""

from __future__ import annotations

import argparse
import math

from qcodes.instrument import Instrument

from core import Tag, emit
from core.config import load_vti_config
from core.influx import setup_influx, write_point
from core.poller import run
from drivers.AMI_1700 import AMI_1700

MEASUREMENT = "vti"
METRIC = "He level"
UNIT = "in"
READ_INTERVAL = 30  # seconds between reads


class Ami1700Source:
    """The AMI 1700 level meter over its raw TCP socket."""

    name = "AMI 1700"

    def __init__(self, addr):
        self.addr = addr
        self.inst = None

    def connect(self) -> None:
        emit(Tag.INIT, f"Connecting to AMI 1700 at {self.addr}")
        self.inst = AMI_1700("ami1700_worker", self.addr)

    def close(self) -> None:
        Instrument.close_all()
        self.inst = None

    def read(self) -> float:
        return float(self.inst.He_level())


class FakeSource:
    """Synthetic level for --dry-run (no hardware)."""

    name = "AMI 1700 (dry run)"

    def __init__(self):
        self.i = 0

    def connect(self) -> None:
        pass

    def close(self) -> None:
        pass

    def read(self) -> float:
        self.i += 1
        return 18.0 + 0.5 * math.sin(self.i / 7.0)


def main(argv=None):
    parser = argparse.ArgumentParser(description="VTI helium level worker (AMI 1700)")
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
            source = Ami1700Source(config.hardware.ami1700_addr)
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
        return {METRIC: f"{value:.2f} in", "_summary": f"He {value:.1f} in"}

    run(source, interval=READ_INTERVAL, publish=publish)


if __name__ == "__main__":
    main()
