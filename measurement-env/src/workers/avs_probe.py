"""AVS-47B probe temperature worker.

Single-channel measurement via GPIB. Parameters set at launch via CLI args.

Usage:
    python -m workers.avs_probe --probe 1 --channel 3 --excitation 1

Stdout protocol:
    [init] ...          initialization diagnostics
    [waiting]           connected, waiting for first measurement
    [ready]             first measurement published
    [data] {...}        measurement as JSON (resistance + temperature + _summary)
    [error] ...         non-fatal errors
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

from core import Tag, emit
from core.avs import connect_gpib, format_temp, wait_opc
from core.config import load_config
from core.influx import setup_influx, write_point
from workers.avs_calibration import SENSORS_PROBE1, SENSORS_PROBE2

MEASUREMENT = "AVS_bridge"
MEASURE_INPUT = 1
OPC_TIMEOUT = 30
DATA_TIMEOUT = 60

_SHORT_NAMES = {
    "3K_low": "3K",
    "Still": "Still",
    "50mK": "50mK",
    "MixingCh_low": "MixCh",
    "MixingCh_high": "MixCh_hi",
    "Magnet": "Mag",
}


def _write_log(log_dir, probe, name, t_unix, t_str, ohms, kelvin):
    """Append a line to the local temperature log file."""
    log_path = log_dir / f"Probe{probe}_{name}.txt"
    with open(log_path, "a") as f:
        f.write(f"{t_unix}\t{t_str}\t{ohms:>10.2f}\t{kelvin:>10.5f}\tIdle\t\n")


def _measure_probe(avs, channel, excitation, averages):
    """Single-channel measurement. Returns (avg_ohms, std_ohms)."""
    wait_opc(avs, timeout=OPC_TIMEOUT)

    # Query current device state
    current_str = avs.query("MUX ?; EXC ?; INP ?").strip()
    match = re.search(r"MUX (\d);EXC (\d);INP (\d)", current_str)

    if match:
        cur_mux, cur_exc, cur_inp = map(int, match.group(1, 2, 3))
        need_reset = (
            cur_mux != channel
            or cur_exc != excitation
            or cur_inp != MEASURE_INPUT
        )
    else:
        need_reset = True

    if need_reset:
        avs.clear()
        time.sleep(0.1)
        avs.write(
            f"REM 1;MUX {channel};EXC {excitation};"
            f"INP {MEASURE_INPUT};REM 0"
        )

    # Start averaging measurement
    avs.write(f"REM 1;AVE {averages};REM 0")
    wait_opc(avs, timeout=OPC_TIMEOUT)

    # Read result
    resp = avs.query("REM 1;AVE?;STD?;REM 0").strip()
    avg_str, std_str = resp.split(";")
    avg = float(avg_str.split()[-1])
    std = float(std_str.split()[-1])

    return avg, std


def main():
    parser = argparse.ArgumentParser(description="AVS probe temperature worker")
    parser.add_argument(
        "--probe", type=int, choices=[1, 2], default=1,
        help="Probe number: 1=straight, 2=rotator",
    )
    parser.add_argument(
        "--channel", type=int, choices=range(6), default=3,
        help="Channel index 0-5",
    )
    parser.add_argument(
        "--excitation", type=int, choices=[1, 2, 3], default=1,
        help="Excitation level",
    )
    parser.add_argument(
        "--averages", type=int, default=10,
        help="Samples to average per reading",
    )
    parser.add_argument(
        "--sleep", type=int, default=15,
        help="Seconds between measurements",
    )
    args = parser.parse_args()

    sensors = SENSORS_PROBE1 if args.probe == 1 else SENSORS_PROBE2
    name, cal_fn = sensors[args.channel]
    metric_name = f"P{args.probe}_{name}"
    short = _SHORT_NAMES.get(name, name)

    config = load_config()
    hw = config.hardware
    log_dir = Path(hw.temperature_log_dir)

    try:
        emit(Tag.INIT, f"AVS Probe (Probe {args.probe}, Ch {args.channel} {name}, EXC {args.excitation})")
        rm, avs = connect_gpib(hw.avs_probe_gpib)
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
            avg, std = _measure_probe(avs, args.channel, args.excitation, args.averages)
        except TimeoutError as e:
            emit(Tag.ERROR, f"Measurement timeout: {e}")
            time.sleep(args.sleep)
            continue
        except Exception as e:
            emit(Tag.ERROR, f"Measurement failed: {e}")
            try:
                avs.close()
            except Exception:
                pass
            try:
                rm, avs = connect_gpib(hw.avs_probe_gpib)
            except Exception as e2:
                emit(Tag.ERROR, f"Reconnect failed: {e2}")
                sys.exit(1)
            time.sleep(args.sleep)
            continue

        if first:
            emit(Tag.READY)
            first = False

        kelvin = cal_fn(avg)

        try:
            write_point(write_api, org, bucket, MEASUREMENT, metric_name, avg, "ohms")
            write_point(write_api, org, bucket, MEASUREMENT, metric_name, kelvin, "kelvin")
        except Exception as e:
            emit(Tag.ERROR, f"InfluxDB write failed: {e}")

        try:
            _write_log(log_dir, args.probe, name, t_unix, t_str, avg, kelvin)
        except Exception as e:
            emit(Tag.ERROR, f"Log write failed: {e}")

        data = {
            "_summary": f"P{args.probe} {short}: {format_temp(kelvin)}",
            metric_name: f"{format_temp(kelvin)} ({avg:.1f} \u03a9)",
        }
        emit(Tag.DATA, json.dumps(data))
        time.sleep(args.sleep)


if __name__ == "__main__":
    main()
