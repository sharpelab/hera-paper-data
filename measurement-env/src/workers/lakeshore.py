"""Lakeshore 335 temperature worker (VTI rig).

Single persistent GPIB master on the LS335. Polls sample (KRDG? A) and
vaporizer (KRDG? B) temperatures plus heater range/power on a fixed cadence
and fans each reading out to BOTH InfluxDB (measurement "vti", matching the
legacy logger's metric names) and tab-delimited local logfiles that
``sharpelab_nb.thermometry.temperature_from_logfiles`` reads.

Logfile columns (mirrors the AVS workers so the default value_index=-3 picks
kelvin, and the col-0 unix timestamp drives staleness/dead-worker detection)::

    unix \t ctime \t sensor \t kelvin \t status \t

Stdout protocol:
    [init] ...          initialization diagnostics
    [ready]             first reading published
    [data] {...}        sample/vaporizer T + heater state as JSON (+ _summary)
    [error] ...         non-fatal errors (read glitches, InfluxDB write fails)

Reads config from vti.toml in the repo root.

Usage:
    python -m workers.lakeshore [--dry-run]
"""

import argparse
import json
import math
import time
from pathlib import Path

from core import Tag, emit
from core.influx import setup_influx, write_point
from core.config import load_vti_config
from drivers.Lakeshore_335 import Lakeshore_335

MEASUREMENT = "vti"
READ_INTERVAL = 5  # seconds between GPIB polls / logfile appends
INFLUX_EVERY = 6  # write InfluxDB every Nth cycle (= 30 s, the legacy cadence)

# (logfile name, KRDG/SRDG input letter, influx metric prefix, driver attrs)
INPUTS = (
    ("VTI_sample", "A", "sample", "sample_temperature", "sample_range", "sample_power"),
    ("VTI_vaporizer", "B", "vaporizer", "vaporizer_temperature", "vaporizer_range", "vaporizer_power"),
)


def format_log_line(t_unix: int, t_str: str, sensor: float, kelvin: float, status: str) -> str:
    """One tab-delimited logfile line; kelvin lands at split index -3."""
    return f"{t_unix}\t{t_str}\t{sensor:>12.6g}\t{kelvin:>10.5f}\t{status}\t\n"


def write_log(log_dir: Path, name: str, t_unix: int, t_str: str,
              sensor: float, kelvin: float, status: str) -> None:
    """Append a reading to {log_dir}/{name}.txt."""
    with open(log_dir / f"{name}.txt", "a") as f:
        f.write(format_log_line(t_unix, t_str, sensor, kelvin, status))


def _read_input(heater, letter, temp_attr, range_attr, power_attr):
    """Read (kelvin, sensor, range, power) for one LS335 input."""
    kelvin = getattr(heater, temp_attr)()
    sensor = float(heater.ask(f"SRDG? {letter}"))
    rng = getattr(heater, range_attr)()
    power = getattr(heater, power_attr)()
    return kelvin, sensor, rng, power


def _fake_input(letter, i):
    """Synthetic reading for --dry-run (no GPIB)."""
    base = 1.30 if letter == "A" else 1.42
    kelvin = base + 0.02 * math.sin(i / 5.0)
    sensor = 1000.0 + 50.0 * math.sin(i / 5.0)
    return kelvin, sensor, 0, 0.0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Lakeshore 335 worker (VTI)")
    parser.add_argument("--dry-run", action="store_true",
                        help="synthetic readings, no GPIB / no InfluxDB")
    args = parser.parse_args(argv)

    config = load_vti_config()
    log_dir = Path(config.hardware.temperature_log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    heater = None
    write_api = org = bucket = None
    try:
        if args.dry_run:
            emit(Tag.INIT, "DRY RUN — synthetic readings, no GPIB / no InfluxDB")
        else:
            emit(Tag.INIT, f"Connecting to Lakeshore 335 at {config.hardware.lakeshore_gpib}")
            heater = Lakeshore_335("l335_worker", config.hardware.lakeshore_gpib)
            _client, write_api, org, bucket = setup_influx(config.influxdb)
    except Exception as e:
        emit(Tag.ERROR, f"Startup failed: {e}")
        raise

    emit(Tag.INIT, f"Logfiles: {log_dir}")

    first = True
    i = 0
    while True:
        i += 1
        t_unix = int(time.time())
        t_str = time.ctime(t_unix)

        data: dict[str, object] = {}
        summary_temp = None
        ok = True

        for name, letter, prefix, temp_attr, range_attr, power_attr in INPUTS:
            try:
                if args.dry_run:
                    kelvin, sensor, rng, power = _fake_input(letter, i)
                else:
                    kelvin, sensor, rng, power = _read_input(
                        heater, letter, temp_attr, range_attr, power_attr,
                    )
            except Exception as e:
                emit(Tag.ERROR, f"{prefix} read failed: {e}")
                ok = False
                continue

            if prefix == "sample":
                summary_temp = kelvin
            data[f"{prefix} T"] = f"{kelvin:.3f} K"
            data[f"{prefix} heater"] = f"range {rng}, {power:.1f}%"

            try:
                write_log(log_dir, name, t_unix, t_str, sensor, kelvin, f"R{rng}")
            except Exception as e:
                emit(Tag.ERROR, f"Log write failed ({name}): {e}")

            if not args.dry_run and (i - 1) % INFLUX_EVERY == 0:
                try:
                    write_point(write_api, org, bucket, MEASUREMENT, f"{prefix} temperature", kelvin, "K")
                    write_point(write_api, org, bucket, MEASUREMENT, f"{prefix} heater range", float(rng), "")
                    write_point(write_api, org, bucket, MEASUREMENT, f"{prefix} heater power", power, "%")
                except Exception as e:
                    emit(Tag.ERROR, f"InfluxDB write failed ({prefix}): {e}")

        if first and ok:
            emit(Tag.READY)
            first = False

        if summary_temp is not None:
            data["_summary"] = f"sample {summary_temp:.3f} K"
        emit(Tag.DATA, json.dumps(data))

        time.sleep(READ_INTERVAL)


if __name__ == "__main__":
    main()
