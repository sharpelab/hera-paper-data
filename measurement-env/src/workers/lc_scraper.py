"""LC scraper worker — tails LabVIEW log files and publishes to InfluxDB.

Usage:
    python -m workers.lc_scraper --family FP
    python -m workers.lc_scraper --family PT

The FP.vi LabVIEW tool writes tab-delimited log files to a folder
(default C:\\LC Data\\Data). Files rotate every ~7 days. This worker
tails the most recent file, detects rotation, and publishes each
metric to InfluxDB.

Stdout protocol:
    [init] ...          initialization diagnostics
    [ready]             after first successful line published
    [data] {...}        all metrics from latest line as JSON
    [error] ...         bad lines, write failures, etc.
"""

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from glob import glob
from pathlib import Path

from core import Tag, emit
from core.config import load_config
from core.influx import setup_influx, write_point

MEASUREMENT = "LC_scrapper"  # InfluxDB measurement name (legacy spelling)
POLL_INTERVAL = 5
DATA_INTERVAL = 60  # LabVIEW writes a new log line every ~60s


# --- Family definitions ---

COLUMNS_FP = [
    "#Date", "P1", "P2", "P3", "P4", "P5", "P6", "P7",
    "Flow", "Pc", "MG0", "MG1", "MG2", "MG3", "MG4", "MG5",
    "State0", "State1", "State2", "FP Status", "MG Status",
]

COLUMNS_PT = [
    "#Date",
    "PT1.ON", "PT1.W_in", "PT1.W_out", "PT1.He", "PT1.Oil",
    "PT1.P_low", "PT1.P_high", "PT1.I_mtr",
    "PT2.ON", "PT2.W_in", "PT2.W_out", "PT2.He", "PT2.Oil",
    "PT2.P_low", "PT2.P_high", "PT2.I_mtr",
    "PT3.ON", "PT3.W_in", "PT3.W_out", "PT3.He", "PT3.Oil",
    "PT3.P_low", "PT3.P_high", "PT3.I_mtr",
    "PT4.ON", "PT4.W_in", "PT4.W_out", "PT4.He", "PT4.Oil",
    "PT4.P_low", "PT4.P_high", "PT4.I_mtr",
    "PT1.Status", "PT2.Status", "PT3.Status", "PT4.Status",
]

# Which columns to skip (metadata, not metrics)
_SKIP_FP = {"#Date", "State0", "State1", "State2", "FP Status", "MG Status"}
_SKIP_PT = {"#Date"}

# Only publish PT1 metrics (the toploader's single pulse tube)
_PT1_ONLY = {c for c in COLUMNS_PT if c.startswith("PT1.") and not c.endswith(".ON")}


@dataclass
class FamilyConfig:
    name: str
    columns: list[str]
    glob_pattern: str
    skip: set[str]
    publish: set[str] | None  # None = publish all non-skipped
    sentinel: str  # metric for dedup timestamp query
    default_unit: str | None = None  # fallback unit; None = every metric must match a suffix
    units: dict[str, str] = field(default_factory=dict)


FAMILIES = {
    "FP": FamilyConfig(
        name="FP",
        columns=COLUMNS_FP,
        glob_pattern="logFP*.dat",
        skip=_SKIP_FP,
        publish=None,
        sentinel="P1",
        default_unit="mbar",
    ),
    "PT": FamilyConfig(
        name="PT",
        columns=COLUMNS_PT,
        glob_pattern="logPT*.dat",
        skip=_SKIP_PT,
        publish=_PT1_ONLY,
        sentinel="PT1.Status",
        units={
            "W_in": "celsius",
            "W_out": "celsius",
            "He": "celsius",
            "Oil": "celsius",
            "P_low": "psi",
            "P_high": "psi",
            "I_mtr": "amps",
            "Status": "status",
        },
    ),
}


def _unit_for_metric(family: FamilyConfig, metric: str) -> str:
    """Determine unit for a metric based on family config."""
    for suffix, unit in family.units.items():
        if metric.endswith(suffix):
            return unit
    if family.default_unit is not None:
        return family.default_unit
    raise ValueError(f"No unit mapping for metric {metric!r} in family {family.name!r}")


def _get_last_timestamp(client, bucket, sentinel, n_days_back=7):
    """Query InfluxDB for the last published timestamp of the sentinel metric."""
    query = f'''
    from(bucket: "{bucket}")
    |> range(start: -{n_days_back}d)
    |> filter(fn: (r) => r["_measurement"] == "{MEASUREMENT}" and r["metric"] == "{sentinel}")
    |> last()
    |> keep(columns: ["_time"])
    '''
    try:
        result = client.query_api().query(query)
        return result[0].records[0].values["_time"]
    except Exception:
        return datetime.now(UTC) - timedelta(days=1)


def _detect_latest_log(logs_folder, glob_pattern):
    """Find the most recent log file by filename timestamp."""
    log_files = sorted(
        glob(os.path.join(logs_folder, glob_pattern)),
        key=lambda x: x.split("__")[-1].split(".")[0],
    )
    if not log_files:
        return None
    return log_files[-1]


def _parse_line(line, family):
    """Parse a tab-delimited log line. Returns (timestamp, metrics_dict) or raises."""
    components = line.strip().split("\t")
    timestamp = datetime.strptime(components[0], "%Y-%m-%d %H:%M:%S")
    timestamp = timestamp.astimezone(UTC)

    metrics = {}
    for col in family.columns:
        if col in family.skip:
            continue
        if family.publish is not None and col not in family.publish:
            continue
        idx = family.columns.index(col)
        if idx >= len(components):
            continue
        value = components[idx]
        unit = _unit_for_metric(family, col)
        metrics[col] = (float(value), unit)

    return timestamp, metrics


def _process_line(line, family, last_timestamp, write_api, org, bucket):
    """Process a single log line. Returns new timestamp on success, None on skip/error."""
    try:
        timestamp, metrics = _parse_line(line, family)
    except Exception as e:
        emit(Tag.ERROR, f"Parse failed: {e} | line: {line.strip()[:80]}")
        return None

    if timestamp <= last_timestamp:
        return None

    try:
        for metric_name, (value, unit) in metrics.items():
            write_point(
                write_api, org, bucket, MEASUREMENT,
                metric_name, value, unit, timestamp=timestamp,
            )
    except Exception as e:
        emit(Tag.ERROR, f"InfluxDB write failed: {e}")
        return None

    # Emit data with string values including units
    data = {}
    for metric_name, (value, unit) in metrics.items():
        data[metric_name] = f"{value} {unit}"
    emit(Tag.DATA, json.dumps(data))

    return timestamp


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", required=True, choices=["FP", "PT"])
    parser.add_argument(
        "--timeout", type=int, default=2 * DATA_INTERVAL,
        help="Seconds to wait for first data before exiting (default: 2 * DATA_INTERVAL)",
    )
    args = parser.parse_args()

    family = FAMILIES[args.family]
    config = load_config()
    logs_folder = config.hardware.lc_logs_folder

    try:
        emit(Tag.INIT, f"LC Scraper {family.name}")
        emit(Tag.INIT, f"Logs folder: {logs_folder}")

        client, write_api, org, bucket = setup_influx(config.influxdb)

        last_timestamp = _get_last_timestamp(client, bucket, family.sentinel)
        emit(Tag.INIT, f"Resuming from {last_timestamp}")

        latest = _detect_latest_log(logs_folder, family.glob_pattern)
        if latest is None:
            emit(Tag.ERROR, f"No log files found matching {family.glob_pattern} in {logs_folder}")
            sys.exit(1)
    except Exception as e:
        emit(Tag.ERROR, f"Startup failed: {e}")
        raise

    current_file = None
    file_pos = 0
    ready_fired = False
    emit(Tag.WAITING)
    waiting_since = time.monotonic()

    while True:
        # Timeout if no data published yet
        if not ready_fired and time.monotonic() - waiting_since > args.timeout:
            emit(Tag.ERROR, f"Timed out waiting for data ({args.timeout}s)")
            sys.exit(1)

        try:
            latest = _detect_latest_log(logs_folder, family.glob_pattern)
        except Exception as e:
            emit(Tag.ERROR, f"Log detection failed: {e}")
            time.sleep(POLL_INTERVAL)
            continue

        if latest is None:
            time.sleep(POLL_INTERVAL)
            continue

        # File rotation
        if latest != current_file:
            if current_file is not None:
                # Read remaining lines from old file
                try:
                    final_size = os.path.getsize(current_file)
                    if final_size > file_pos:
                        with open(current_file, "r") as f:
                            f.seek(file_pos)
                            for line in f:
                                _process_line(
                                    line, family, last_timestamp,
                                    write_api, org, bucket,
                                )
                except Exception as e:
                    emit(Tag.ERROR, f"Error reading old file: {e}")

            emit(Tag.INIT, f"Tailing {latest}")
            current_file = latest
            file_pos = 0

        # Read new lines
        try:
            with open(current_file, "r") as f:
                f.seek(file_pos)
                for line in f:
                    if line.startswith("#"):
                        continue
                    result = _process_line(
                        line, family, last_timestamp,
                        write_api, org, bucket,
                    )
                    if result is not None:
                        last_timestamp = result
                        if not ready_fired:
                            ready_fired = True
                            emit(Tag.READY)
                file_pos = f.tell()
        except Exception as e:
            emit(Tag.ERROR, f"Error reading log: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
