"""Pink LC scraper worker — tails the pink fridge's LabVIEW logs to InfluxDB.

Usage:
    python -m workers.pink_scraper --family FP
    python -m workers.pink_scraper --family TC

Port of the legacy publisher on the pink PC
(``C:\\Users\\dggla\\LC_scrapper\\logs_publisher.py``, a fork of the
toploader's): same measurement name, metric names, units, and
timestamps, wrapped in the worker stdout protocol so the launcher can
manage it. Deliberately preserved quirks:

- Every metric is tagged ``unit=mbar`` — including AVS temperatures.
- ``PC`` (not ``Pc``), ``PT on``, ``PT current`` metric names.
- The pink FP.vi log has 34 columns (two PT blocks); the legacy column
  map has 27, so only the first 24 (through ``PT current``) are
  published and the PT2 block is dropped.
- FP: log files are picked by lexical filename sort, and the dedup
  timestamp is queried once at startup (sentinel P1) and never
  advances — fully byte-exact with legacy.

One deliberate break from byte-exact (operator ruling, 2026-07-15):
the legacy lexical sort tails the AVS ``_9`` file, which stalls for
hours while the logger actively writes ``_0``–``_8`` — the TC feed
went dark for the duration. TC instead tails whichever ``logAVS`` file
was written most recently (per-file read positions, dedup timestamp
advancing past each published row so file switches never re-publish).
Same metrics, names, and units; strictly fresher rows.

The FP.vi tool logs to C:\\avs-47 (``[hardware] lc_logs_folder``):
``logFP___<ts>.dat`` (pressures/gauges, ~60s lines) and eleven
``LogAVS___<ts>[_N].dat`` files (AVS-47 resistances/temperatures,
~45s cadence with occasional multi-hour gaps).

Stdout protocol:
    [init] ...          initialization diagnostics
    [ready]             after first successful line published
    [data] {...}        all metrics from latest line as JSON
    [error] ...         bad lines, write failures, etc.
"""

import argparse
import fnmatch
import json
import os
import sys
import time
from datetime import UTC, datetime, timedelta

from core import Tag, emit
from core.config import load_pink_config
from core.influx import setup_influx, write_point

MEASUREMENT = "LC_scrapper"  # InfluxDB measurement name (legacy spelling)
POLL_INTERVAL = 5

# Legacy column maps, verbatim from the pink logs_publisher.py.
COLUMNS_FP = [
    "#Date", "P1", "P2", "P3", "P4", "P5", "P6", "P7",
    "Flow", "PC", "MG0", "MG1", "MG2", "MG3", "MG4", "MG5",
    "PT on", "W_in", "W_out", "He", "Oil", "P_low", "P_high", "PT current",
    "State0", "State1", "State2",
]

COLUMNS_TC = [
    "Date1", "Date2",
    "R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9",
    "T0", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9",
    "I0", "I1", "I2", "I3",
]


class FamilyConfig:
    def __init__(self, name, columns, glob_pattern, sentinel, skip,
                 first_data_timeout, tail_freshest=False):
        self.name = name
        self.columns = columns
        self.glob_pattern = glob_pattern
        self.sentinel = sentinel  # metric for the startup dedup query
        self.skip = skip  # predicate: column name -> not published
        self.first_data_timeout = first_data_timeout
        # False: legacy lexical filename sort, fixed dedup timestamp.
        # True: freshest mtime, per-file positions, advancing dedup.
        self.tail_freshest = tail_freshest


def _fp_skip(col: str) -> bool:
    return col == "#Date" or "State" in col or "Status" in col


def _tc_skip(col: str) -> bool:
    return col in ("Date1", "Date2")


FAMILIES = {
    "FP": FamilyConfig(
        name="FP",
        columns=COLUMNS_FP,
        glob_pattern="logFP*.dat",
        sentinel="P1",
        skip=_fp_skip,
        first_data_timeout=120,  # ~60s line cadence
    ),
    "TC": FamilyConfig(
        name="TC",
        columns=COLUMNS_TC,
        glob_pattern="logAVS*.dat",
        sentinel="R0",
        skip=_tc_skip,
        first_data_timeout=300,  # ~45s cadence in the freshest file
        tail_freshest=True,
    ),
}


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


def _matching_logs(logs_folder, glob_pattern):
    """Case-insensitive name match (Windows glob semantics — the AVS
    files are named ``LogAVS...`` against a ``logAVS*`` pattern)."""
    try:
        names = os.listdir(logs_folder)
    except OSError:
        return []
    pattern = glob_pattern.lower()
    return [
        os.path.join(logs_folder, n)
        for n in names
        if fnmatch.fnmatch(n.lower(), pattern)
    ]


def _detect_latest_log(logs_folder, glob_pattern):
    """Find the current log file the way the legacy publisher does:
    lexical sort on the filename timestamp segment."""
    log_files = _matching_logs(logs_folder, glob_pattern)
    log_files.sort(key=lambda x: x.split("__")[-1].split(".")[0])
    if not log_files:
        return None
    return log_files[-1]


def _detect_freshest_log(logs_folder, glob_pattern):
    """Find the most recently written log file (mtime)."""
    log_files = _matching_logs(logs_folder, glob_pattern)
    freshest = None
    freshest_mtime = None
    for path in log_files:
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            continue
        if freshest_mtime is None or mtime > freshest_mtime:
            freshest, freshest_mtime = path, mtime
    return freshest


def _is_data_line(line, family):
    """Replicate the legacy per-family header/data gating."""
    if family.name == "FP":
        return not line.startswith("#")
    # TC: header lines start with "Date1"; data lines with "20".
    return line.startswith("20")  # Hey fix this in 2100 (sic)


def _parse_line(line, family):
    """Parse a tab-delimited log line. Returns (timestamp, metrics_dict) or raises.

    Timestamp handling is verbatim legacy: the naive local-time stamp in
    column 0 is converted to UTC via .astimezone().
    """
    components = line.strip().split("\t")
    timestamp = datetime.strptime(components[0], "%Y-%m-%d %H:%M:%S")
    timestamp = timestamp.astimezone(UTC)

    metrics = {}
    for col in family.columns:
        if family.skip(col):
            continue
        idx = family.columns.index(col)
        if idx >= len(components):
            continue
        metrics[col] = (float(components[idx]), "mbar")

    return timestamp, metrics


def _process_line(line, family, last_timestamp, write_api, org, bucket):
    """Process a single log line. Returns the line's timestamp if metrics
    were published, else None."""
    try:
        timestamp, metrics = _parse_line(line, family)
    except Exception as e:
        emit(Tag.ERROR, f"Parse failed: {e} | line: {line.strip()[:80]}")
        return None

    if timestamp <= last_timestamp:
        return None

    published = False
    for metric_name, (value, unit) in metrics.items():
        try:
            write_point(
                write_api, org, bucket, MEASUREMENT,
                metric_name, value, unit, timestamp=timestamp,
            )
            published = True
        except Exception as e:
            emit(Tag.ERROR, f"InfluxDB write failed for {metric_name}: {e}")

    if not published:
        return None

    data = {}
    for metric_name, (value, unit) in metrics.items():
        data[metric_name] = f"{value} {unit}"
    emit(Tag.DATA, json.dumps(data))

    return timestamp


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", required=True, choices=["FP", "TC"])
    parser.add_argument(
        "--timeout", type=int, default=None,
        help="Seconds to wait for first data before exiting; 0 waits forever "
             "(default: per family)",
    )
    args = parser.parse_args()

    family = FAMILIES[args.family]
    timeout = args.timeout if args.timeout is not None else family.first_data_timeout
    config = load_pink_config()
    logs_folder = config.hardware.lc_logs_folder

    try:
        emit(Tag.INIT, f"Pink LC Scraper {family.name}")
        emit(Tag.INIT, f"Logs folder: {logs_folder}")

        client, write_api, org, bucket = setup_influx(config.influxdb)

        # Legacy semantics: queried once, never advanced during the run.
        last_timestamp = _get_last_timestamp(client, bucket, family.sentinel)
        emit(Tag.INIT, f"Resuming from {last_timestamp}")

        detect = _detect_freshest_log if family.tail_freshest else _detect_latest_log
        latest = detect(logs_folder, family.glob_pattern)
        if latest is None:
            emit(Tag.ERROR, f"No log files found matching {family.glob_pattern} in {logs_folder}")
            sys.exit(1)
    except Exception as e:
        emit(Tag.ERROR, f"Startup failed: {e}")
        raise

    current_file = None
    file_pos = 0
    positions = {}  # tail_freshest only: per-file resume positions
    ready_fired = False
    emit(Tag.WAITING)
    waiting_since = time.monotonic()

    while True:
        # Timeout if no data published yet
        if timeout and not ready_fired and time.monotonic() - waiting_since > timeout:
            emit(Tag.ERROR, f"Timed out waiting for data ({timeout}s)")
            sys.exit(1)

        latest = detect(logs_folder, family.glob_pattern)
        if latest is None:
            time.sleep(POLL_INTERVAL)
            continue

        if latest != current_file:
            if family.tail_freshest:
                # Files are written concurrently; remember where we left
                # off so switching back never re-reads (the advancing
                # dedup timestamp guards re-publishing regardless).
                if current_file is not None:
                    positions[current_file] = file_pos
                file_pos = positions.get(latest, 0)
            else:
                # Legacy rotation: drain the old file's tail, then start
                # the new file from the top.
                if current_file is not None:
                    try:
                        final_size = os.path.getsize(current_file)
                        if final_size > file_pos:
                            with open(current_file, "r") as f:
                                f.seek(file_pos)
                                for line in f:
                                    if _is_data_line(line, family):
                                        _process_line(
                                            line, family, last_timestamp,
                                            write_api, org, bucket,
                                        )
                    except Exception as e:
                        emit(Tag.ERROR, f"Error reading old file: {e}")
                file_pos = 0

            emit(Tag.INIT, f"Tailing {latest}")
            current_file = latest

        # Read new lines
        try:
            with open(current_file, "r") as f:
                f.seek(file_pos)
                for line in f:
                    if not _is_data_line(line, family):
                        continue
                    published_ts = _process_line(
                        line, family, last_timestamp,
                        write_api, org, bucket,
                    )
                    if published_ts is not None:
                        if family.tail_freshest:
                            last_timestamp = max(last_timestamp, published_ts)
                        if not ready_fired:
                            ready_fired = True
                            emit(Tag.READY)
                file_pos = f.tell()
        except Exception as e:
            emit(Tag.ERROR, f"Error reading log: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
