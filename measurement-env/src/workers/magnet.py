"""AMI Model 430 magnet field worker.

Reads magnetic field (Tesla) via TCP/IP and publishes to InfluxDB.
Strictly read-only on the instrument — it polls field and never drives.

Usage:
    python -m workers.magnet                  # toploader
    python -m workers.magnet --rig pink

Stdout protocol:
    [init] ...          initialization diagnostics
    [waiting]           connected, waiting for first read
    [ready]             first read published
    [data] {...}        field as JSON + _summary
    [error] ...         non-fatal errors
"""

import argparse
import json
import sys
import time

from core import Tag, emit
from core.config import load_config, load_pink_config
from core.influx import setup_influx, write_point

# Per-rig InfluxDB measurement name. Toploader keeps its historical
# "AVS_bridge" (see TODO.md re: migrating to AMI430); pink starts clean.
RIGS = {
    "toploader": (load_config, "AVS_bridge"),
    "pink": (load_pink_config, "AMI430"),
}
READ_INTERVAL = 30  # seconds between reads
DATA_TIMEOUT = 60  # max seconds to wait for first data after [waiting]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rig", choices=sorted(RIGS), default="toploader")
    args = parser.parse_args()
    loader, measurement = RIGS[args.rig]

    config = loader()
    hw = config.hardware

    try:
        emit(Tag.INIT, "AMI430 Magnet")
        emit(Tag.INIT, f"Address: {hw.ami430_addr}")
        from qcodes.instrument_drivers.american_magnetics import AMIModel430
        mag = AMIModel430("magnet", address=hw.ami430_addr)
        emit(Tag.INIT, "AMI430 connected")

        _client, write_api, org, bucket = setup_influx(config.influxdb)
    except Exception as e:
        emit(Tag.ERROR, f"Startup failed: {e}")
        raise

    emit(Tag.WAITING)
    waiting_since = time.monotonic()
    first = True

    while True:
        if first and time.monotonic() - waiting_since > DATA_TIMEOUT:
            emit(Tag.ERROR, f"Timed out waiting for data ({DATA_TIMEOUT}s)")
            sys.exit(1)

        try:
            field_T = mag.field()
        except Exception as e:
            emit(Tag.ERROR, f"AMI430 read failed: {e}")
            time.sleep(READ_INTERVAL)
            continue

        if first:
            emit(Tag.READY)
            first = False

        try:
            write_point(write_api, org, bucket, measurement, "magnetic field", field_T, "Tesla")
        except Exception as e:
            emit(Tag.ERROR, f"InfluxDB write failed: {e}")

        data = {
            "_summary": f"{field_T:.4f} T",
            "magnetic field": f"{field_T:.4f} T",
        }
        emit(Tag.DATA, json.dumps(data))
        time.sleep(READ_INTERVAL)


if __name__ == "__main__":
    main()
