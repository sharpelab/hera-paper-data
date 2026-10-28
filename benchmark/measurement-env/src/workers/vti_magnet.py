"""VTI magnet field worker (FastBi1K5).

Reads the magnetic field (Tesla) from the CAEN ELS FAST-PS 1K5 supply over its
raw TCP socket and publishes to InfluxDB (measurement "vti", metric
"magnetic field", matching the legacy logger). Read-only — never ramps.

SECOND-READER NOTE: the measurement kernel reads ``magnet.field()`` over its own
socket (heavily, during sweeps). This worker is therefore a second reader on the
same supply. It is NOT new risk — the legacy "Grafana logger" already held a
second FastBi socket and read the field every 20s alongside live sweeps, so the
supply already tolerates worker-socket + kernel-socket concurrently; this worker
is a like-for-like replacement of that reader. Coexistence is confirmed at
deploy (verify a live kernel field read still succeeds with this worker running),
not forced out-of-band. Kept SEPARATE from the aux worker so the operator can
stop just the field poller if it ever fights a sweep.

Stdout protocol (owned by core.poller):
    [init] ...          initialization diagnostics
    [waiting]           connected, waiting for first read
    [ready]             first read published
    [data] {...}        field as JSON + _summary
    [error] ...         non-fatal errors

Reads config from vti.toml in the repo root.

Usage:
    python -m workers.vti_magnet [--dry-run]
"""

import argparse
import math

from core import Tag, emit
from core.influx import setup_influx, write_point
from core.config import load_vti_config
from core.poller import run
from drivers.FastBi1K5 import FastBi1K5

MEASUREMENT = "vti"
READ_INTERVAL = 30  # seconds between reads


class Magnet:
    """FastBi1K5 field readback over its raw TCP socket."""

    name = "FastBi1K5"

    def __init__(self, host: str):
        self._host = host
        self._magnet = None

    def connect(self) -> None:
        emit(Tag.INIT, f"Address: {self._host}")
        self._magnet = FastBi1K5("fastbi_worker", self._host)

    def close(self) -> None:
        try:
            self._magnet.close()  # guards a missing socket itself
        except Exception as e:
            emit(Tag.ERROR, f"FastBi1K5 close failed: {e}")
        self._magnet = None

    def read(self) -> float:
        return float(self._magnet.field())


class FakeMagnet:
    """Synthetic field for --dry-run: no hardware, no socket."""

    name = "FastBi1K5 (dry run)"

    def __init__(self):
        self._i = 0

    def connect(self) -> None:
        emit(Tag.INIT, "DRY RUN — synthetic readings, no hardware / no InfluxDB")

    def close(self) -> None:
        pass

    def read(self) -> float:
        self._i += 1
        return 2.0 * math.sin(self._i / 11.0)


def _data(field_T: float) -> dict[str, object]:
    return {
        "_summary": f"{field_T:.4f} T",
        "magnetic field": f"{field_T:.4f} T",
    }


def make_publish(write_api, org, bucket):
    """Build the (field, cycle) -> [data] payload callable."""

    def publish(field_T: float, cycle: int) -> dict[str, object]:
        try:
            write_point(write_api, org, bucket, MEASUREMENT, "magnetic field", field_T, "T")
        except Exception as e:
            emit(Tag.ERROR, f"InfluxDB write failed: {e}")
        return _data(field_T)

    return publish


def dry_publish(field_T: float, cycle: int) -> dict[str, object]:
    """--dry-run publish: the same payload, no InfluxDB."""
    return _data(field_T)


def main(argv=None):
    parser = argparse.ArgumentParser(description="VTI magnet field worker (FastBi1K5)")
    parser.add_argument("--dry-run", action="store_true",
                        help="synthetic readings, no hardware / no InfluxDB")
    args = parser.parse_args(argv)

    if args.dry_run:
        source = FakeMagnet()
        publish = dry_publish
    else:
        try:
            config = load_vti_config()
            source = Magnet(config.hardware.fastbi_host)
            _client, write_api, org, bucket = setup_influx(config.influxdb)
        except Exception as e:
            emit(Tag.ERROR, f"Startup failed: {e}")
            raise
        publish = make_publish(write_api, org, bucket)

    run(source, interval=READ_INTERVAL, publish=publish)


if __name__ == "__main__":
    main()
