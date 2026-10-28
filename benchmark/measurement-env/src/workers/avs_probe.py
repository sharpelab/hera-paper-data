"""AVS-47B probe temperature worker.

Single-channel measurement over GPIB; probe / channel / excitation are fixed
at launch via CLI args (the launcher's probe panel picks them). Publishes
resistance + temperature to InfluxDB (measurement "AVS_bridge", metric
"P<probe>_<sensor>") and to the local temperature logfile the measurement
kernel reads back.

The temperature metric's name follows the selection, so the launcher's
freshness guard keys on "probe status" instead: written every cycle whatever
probe/channel is selected, 0 = the read was valid (the Lakeshore 335 RDGST
convention). `[health.avs_probe]` lists that metric.

Usage:
    python -m workers.avs_probe --probe 1 --channel 3 --excitation 1

Stdout protocol (owned by core.poller):
    [init] ...          initialization diagnostics
    [waiting]           connected, waiting for the first measurement
    [ready]             first measurement published
    [data] {...}        measurement as JSON (temperature + resistance) + _summary
    [error] ...         non-fatal errors (measurement glitches, write fails)

Reads config from toploader.toml in the repo root.
"""

import argparse
import re
import time
from pathlib import Path

from core import Tag, emit
from core.avs import connect_gpib, format_temp, wait_opc
from core.config import load_config
from core.influx import setup_influx, write_point
from core.poller import run
from workers.avs_calibration import SENSORS_PROBE1, SENSORS_PROBE2

MEASUREMENT = "AVS_bridge"
STATUS_METRIC = "probe status"
STATUS_VALID = 0
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


class ProbeBridge:
    """The probe AVS-47B over a persistent GPIB session, one channel."""

    name = "AVS-47B probe"

    def __init__(self, gpib_addr: str, channel: int, excitation: int, averages: int):
        self._addr = gpib_addr
        self._channel = channel
        self._excitation = excitation
        self._averages = averages
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

    def read(self) -> tuple[float, float]:
        return _measure_probe(self._avs, self._channel, self._excitation,
                              self._averages)


def make_publish(write_api, org, bucket, log_dir: Path, probe: int, name: str,
                 cal_fn):
    """Build the ((avg_ohms, std_ohms), cycle) -> [data] payload callable."""
    metric_name = f"P{probe}_{name}"
    short = _SHORT_NAMES.get(name, name)

    def publish(readings: tuple[float, float], cycle: int) -> dict[str, object]:
        avg, _std = readings
        t_unix = int(time.time())
        t_str = time.ctime(t_unix)
        kelvin = cal_fn(avg)

        try:
            write_point(write_api, org, bucket, MEASUREMENT, metric_name, avg, "ohms")
            write_point(write_api, org, bucket, MEASUREMENT, metric_name, kelvin, "kelvin")
            write_point(write_api, org, bucket, MEASUREMENT, STATUS_METRIC,
                        STATUS_VALID, "status")
        except Exception as e:
            emit(Tag.ERROR, f"InfluxDB write failed: {e}")

        try:
            _write_log(log_dir, probe, name, t_unix, t_str, avg, kelvin)
        except Exception as e:
            emit(Tag.ERROR, f"Log write failed: {e}")

        return {
            "_summary": f"P{probe} {short}: {format_temp(kelvin)}",
            metric_name: f"{format_temp(kelvin)} ({avg:.1f} Ω)",
        }

    return publish


def main(argv=None):
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
    args = parser.parse_args(argv)

    sensors = SENSORS_PROBE1 if args.probe == 1 else SENSORS_PROBE2
    name, cal_fn = sensors[args.channel]

    try:
        config = load_config()
        _client, write_api, org, bucket = setup_influx(config.influxdb)
    except Exception as e:
        emit(Tag.ERROR, f"Startup failed: {e}")
        raise

    hw = config.hardware
    emit(Tag.INIT, f"AVS Probe (Probe {args.probe}, Ch {args.channel} {name}, "
                   f"EXC {args.excitation})")
    run(
        ProbeBridge(hw.avs_probe_gpib, args.channel, args.excitation, args.averages),
        interval=args.sleep,
        publish=make_publish(write_api, org, bucket, Path(hw.temperature_log_dir),
                             args.probe, name, cal_fn),
        data_timeout=DATA_TIMEOUT,
    )


if __name__ == "__main__":
    main()
