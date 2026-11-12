"""AVS-47B fridge temperature worker.

Scans all 6 fridge channels over GPIB (one ~210 s scan per cycle) and
publishes each channel's resistance + temperature to InfluxDB (measurement
"AVS_bridge") and to the local temperature logfiles the measurement kernel
reads back (`temperature_from_logfiles`).

Usage:
    python -m workers.avs_fridge

Stdout protocol (owned by core.poller):
    [init] ...          initialization diagnostics
    [waiting]           connected, waiting for the first scan to complete
    [ready]             first scan published
    [data] {...}        all channels as JSON (temperature + resistance) + _summary
    [error] ...         non-fatal errors (scan glitches, InfluxDB/log write fails)

Reads config from toploader.toml in the repo root.
"""

import time
from pathlib import Path

from core import Tag, emit
from core.avs import connect_gpib, format_temp, wait_opc
from core.config import load_config
from core.influx import setup_influx, write_point
from core.poller import run
from workers.avs_calibration import SENSORS_FRIDGE

MEASUREMENT = "AVS_bridge"
SCAN_INTERVAL = 120  # seconds between scans
DATA_TIMEOUT = 400  # the first scan alone takes ~210 s
CHANNELS = (0, 1, 2, 3, 4, 5)

# (channel, avg_ohms, std_ohms) per channel
Scan = list[tuple[int, float, float]]


def _fridge_scan(avs, channels=CHANNELS):
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


class FridgeBridge:
    """The fridge AVS-47B over a persistent GPIB session; one read = one scan."""

    name = "AVS-47B fridge"

    def __init__(self, gpib_addr: str):
        self._addr = gpib_addr
        self._rm = None
        self._avs = None

    def connect(self) -> None:
        self._rm, self._avs = connect_gpib(self._addr)

    def close(self) -> None:
        try:
            self._avs.close()
        except Exception as e:
            emit(Tag.ERROR, f"{self.name} close failed: {e}")
        self._avs = None

    def read(self) -> Scan:
        return list(_fridge_scan(self._avs))


def make_publish(write_api, org, bucket, log_dir: Path):
    """Build the (scan, cycle) -> [data] payload callable."""

    def publish(results: Scan, cycle: int) -> dict[str, object]:
        t_unix = int(time.time())
        t_str = time.ctime(t_unix)

        data: dict[str, object] = {}
        summary_temp = None
        for ch, ohms, _std in results:
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
        return data

    return publish


def main():
    try:
        config = load_config()
        _client, write_api, org, bucket = setup_influx(config.influxdb)
    except Exception as e:
        emit(Tag.ERROR, f"Startup failed: {e}")
        raise

    hw = config.hardware
    run(
        FridgeBridge(hw.avs_fridge_gpib),
        interval=SCAN_INTERVAL,
        publish=make_publish(write_api, org, bucket, Path(hw.temperature_log_dir)),
        data_timeout=DATA_TIMEOUT,
    )


if __name__ == "__main__":
    main()
