"""VTI Lakeshore 218 worker (magnet + gearbox-motor thermometry).

Polls the Lakeshore 218 monitor over GPIB for the magnet and gm temperatures
and publishes both to InfluxDB (measurement "vti", metrics "magnet
temperature" and "gm temperature", unit "K" — the metric names and units
Grafana reads). No logfiles: the measurement kernel never reads these values
back.

The Lakeshore 218 is one of three VTI monitor instruments the measurement
kernel never touches, so polling it costs the kernel nothing. The contended
magnet field readback lives in workers.vti_magnet.

Stdout protocol (owned by core.poller):
    [init] ...          initialization diagnostics
    [waiting]           connected, waiting for first read
    [ready]             first read published
    [data] {...}        both temperatures as JSON + _summary
    [error] ...         non-fatal errors (read glitches, InfluxDB write fails)

Reads config from vti.toml in the repo root.

Usage:
    python -m workers.vti_l218 [--dry-run]
"""

from __future__ import annotations

import argparse
import math

from qcodes.instrument import Instrument

from core import Tag, emit
from core.config import load_vti_config
from core.influx import setup_influx, write_point
from core.poller import run
from drivers.Lakeshore_218 import Lakeshore_218

MEASUREMENT = "vti"
MAGNET_METRIC = "magnet temperature"
GM_METRIC = "gm temperature"
UNIT = "K"
READ_INTERVAL = 30  # seconds between reads


class Lakeshore218Source:
    """The Lakeshore 218 monitor over GPIB; one read yields both channels."""

    name = "Lakeshore 218"

    def __init__(self, addr):
        self.addr = addr
        self.inst = None

    def connect(self) -> None:
        emit(Tag.INIT, f"Connecting to Lakeshore 218 at {self.addr}")
        self.inst = Lakeshore_218("l218_worker", self.addr)

    def close(self) -> None:
        Instrument.close_all()
        self.inst = None

    def read(self) -> tuple[float, float]:
        return (float(self.inst.magnet_temperature()),
                float(self.inst.gm_temperature()))


class FakeSource:
    """Synthetic temperatures for --dry-run (no hardware)."""

    name = "Lakeshore 218 (dry run)"

    def __init__(self):
        self.i = 0

    def connect(self) -> None:
        pass

    def close(self) -> None:
        pass

    def read(self) -> tuple[float, float]:
        self.i += 1
        return (3.9 + 0.05 * math.sin(self.i / 5.0),
                40.0 + 0.5 * math.sin(self.i / 5.0))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="VTI Lakeshore 218 magnet/gm temperature worker")
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
            source = Lakeshore218Source(config.hardware.lakeshore218_gpib)
            influx = setup_influx(config.influxdb)
        except Exception as e:
            emit(Tag.ERROR, f"Startup failed: {e}")
            raise

    def publish(readings: tuple[float, float], cycle: int) -> dict:
        magnet_T, gm_T = readings
        if influx is not None:
            _client, write_api, org, bucket = influx
            for metric, value in ((MAGNET_METRIC, magnet_T), (GM_METRIC, gm_T)):
                try:
                    write_point(write_api, org, bucket, MEASUREMENT, metric,
                                value, UNIT)
                except Exception as e:
                    emit(Tag.ERROR, f"InfluxDB write failed ({metric}): {e}")
        return {
            MAGNET_METRIC: f"{magnet_T:.3f} K",
            GM_METRIC: f"{gm_T:.3f} K",
            "_summary": f"magnet {magnet_T:.3f} K",
        }

    run(source, interval=READ_INTERVAL, publish=publish)


if __name__ == "__main__":
    main()
