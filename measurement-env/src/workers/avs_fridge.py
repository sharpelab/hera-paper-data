"""AVS-47B fridge temperature worker.

Scans all 6 fridge channels via GPIB and publishes to InfluxDB.
Persistent connections — opened once at startup.

Usage:
    python -m workers.avs_fridge

Stdout protocol:
    [init] ...          initialization diagnostics
    [waiting]           connected, waiting for first scan to complete
    [ready]             first scan published
    [data] {...}        all channels as JSON (resistance + temperature + _summary)
    [error] ...         non-fatal errors
"""

import json
import sys
import time
from pathlib import Path

from core import Tag, emit
from core.avs import connect_gpib, format_temp, wait_opc
from core.config import load_config
from core.influx import setup_influx, write_point
from workers.avs_calibration import SENSORS_FRIDGE

MEASUREMENT = "AVS_bridge"
SCAN_INTERVAL = 120  # seconds between scans
DATA_TIMEOUT = 400  # max seconds to wait for first data after [waiting]


def _fridge_scan(avs, channels=(0, 1, 2, 3, 4, 5)):
    """Scan all channels. Yields (channel, avg_ohms, std_ohms)."""
    wait_opc(avs)

    # Configure scan range and per-channel settings
    avs.write(
        f"REM 1;FCH {channels[0]};LCH {channels[-1]};"
        "SCI 600;ETC 0;TCP 30;ARN 1;REM 0"
    )
    for ch in channels:
        avs.write(f"REM 1;SCP {ch};EXC 3;SDY 5;CNT 10;REM 0")

    # Start scan and wait
    avs.write("REM 1;SCN 0;REM 0")
    wait_opc(avs)

    # Read results
    for ch in channels:
        resp = avs.query(f"REM 1;SCR {ch};AVE?;STD?;REM 0").strip()
        avg_str, std_str = resp.split(";")
        avg = float(avg_str.split()[-1])
        std = float(std_str.split()[-1])
        yield ch, avg, std


def _write_log(log_dir, name, t_unix, t_str, ohms, kelvin):
    """Append a line to the local temperature log file."""
    log_path = log_dir / f"Fridge_{name}.txt"
    with open(log_path, "a") as f:
        f.write(f"{t_unix}\t{t_str}\t{ohms:>10.2f}\t{kelvin:>10.5f}\tIdle\t\n")


def main():
    config = load_config()
    hw = config.hardware
    log_dir = Path(hw.temperature_log_dir)

    try:
        emit(Tag.INIT, "AVS Fridge")
        rm, avs = connect_gpib(hw.avs_fridge_gpib)

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

        t_unix = int(time.time())
        t_str = time.ctime(t_unix)

        try:
            results = list(_fridge_scan(avs))
        except TimeoutError as e:
            emit(Tag.ERROR, f"Scan timeout: {e}")
            time.sleep(SCAN_INTERVAL)
            continue
        except Exception as e:
            emit(Tag.ERROR, f"Scan failed: {e}")
            try:
                avs.close()
            except Exception:
                pass
            try:
                rm, avs = connect_gpib(hw.avs_fridge_gpib)
            except Exception as e2:
                emit(Tag.ERROR, f"Reconnect failed: {e2}")
                sys.exit(1)
            time.sleep(SCAN_INTERVAL)
            continue

        if first:
            emit(Tag.READY)
            first = False

        data = {}
        summary_temp = None
        for ch, ohms, std in results:
            name, cal_fn = SENSORS_FRIDGE[ch]
            kelvin = cal_fn(ohms)

            data[name] = f"{format_temp(kelvin)} ({ohms:.1f} Ω)"

            if name == "MixingCh_low":
                summary_temp = kelvin

            try:
                write_point(write_api, org, bucket, MEASUREMENT, name, ohms, "ohms")
                write_point(write_api, org, bucket, MEASUREMENT, name, kelvin, "kelvin")
            except Exception as e:
                emit(Tag.ERROR, f"InfluxDB write failed ({name}): {e}")

            try:
                _write_log(log_dir, name, t_unix, t_str, ohms, kelvin)
            except Exception as e:
                emit(Tag.ERROR, f"Log write failed ({name}): {e}")

        if summary_temp is not None:
            data["_summary"] = f"MixCh: {format_temp(summary_temp)}"

        emit(Tag.DATA, json.dumps(data))
        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    main()
