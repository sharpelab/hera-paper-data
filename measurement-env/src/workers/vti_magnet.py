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

Stdout protocol:
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
import json
import math
import sys
import time

from core import Tag, emit
from core.influx import setup_influx, write_point
from core.config import load_vti_config
from drivers.FastBi1K5 import FastBi1K5

MEASUREMENT = "vti"
READ_INTERVAL = 30  # seconds between reads
DATA_TIMEOUT = 60  # max seconds to wait for first data after [waiting]


def main(argv=None):
    parser = argparse.ArgumentParser(description="VTI magnet field worker (FastBi1K5)")
    parser.add_argument("--dry-run", action="store_true",
                        help="synthetic readings, no hardware / no InfluxDB")
    args = parser.parse_args(argv)

    magnet = None
    write_api = org = bucket = None
    if args.dry_run:
        emit(Tag.INIT, "DRY RUN — synthetic readings, no hardware / no InfluxDB")
    else:
        config = load_vti_config()
        try:
            emit(Tag.INIT, f"Connecting to FastBi1K5 at {config.hardware.fastbi_host}")
            magnet = FastBi1K5("fastbi_worker", config.hardware.fastbi_host)
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
        try:
            if args.dry_run:
                field_T = 2.0 * math.sin(i / 11.0)
            else:
                field_T = float(magnet.field())
        except Exception as e:
            emit(Tag.ERROR, f"FastBi1K5 read failed: {e}")
            time.sleep(READ_INTERVAL)
            continue

        if first:
            emit(Tag.READY)
            first = False

        if not args.dry_run:
            try:
                write_point(write_api, org, bucket, MEASUREMENT, "magnetic field", field_T, "T")
            except Exception as e:
                emit(Tag.ERROR, f"InfluxDB write failed: {e}")

        emit(Tag.DATA, json.dumps({
            "_summary": f"{field_T:.4f} T",
            "magnetic field": f"{field_T:.4f} T",
        }))
        time.sleep(READ_INTERVAL)


if __name__ == "__main__":
    main()
