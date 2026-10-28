"""AMI Model 430 magnet field worker.

Reads magnetic field (Tesla) via TCP/IP and publishes to InfluxDB.
Strictly read-only on the instrument — it polls field and never drives.

Per rig it can also publish the magnet's control state — the AMI430
``STATE?`` code (ramping / holding / paused / quench detected / ...) and the
quench flag — so a stalled or quenched ramp is visible in Grafana, not just
a field that stopped moving. Two extra queries per cycle on a connection the
measurement kernel may share; enabled where that cost is known to be fine.

Usage:
    python -m workers.magnet                  # toploader (field only)
    python -m workers.magnet --rig pink       # field + control state

Stdout protocol (owned by core.poller):
    [init] ...          initialization diagnostics
    [waiting]           connected, waiting for first read
    [ready]             first read published
    [data] {...}        field (+ state) as JSON + _summary
    [error] ...         non-fatal errors
"""

import argparse
from typing import NamedTuple

from qcodes.instrument import Instrument
from qcodes.instrument_drivers.american_magnetics import AMIModel430

from core import Tag, emit
from core.config import load_config, load_pink_config
from core.influx import setup_influx, write_point
from core.poller import run

READ_INTERVAL = 30  # seconds between reads

# AMI430 STATE? reply codes (the instrument's table; the qcodes driver maps
# them to these names). Published as the numeric code so Grafana can
# threshold on it; the name goes to the panel.
STATE_CODES = {
    "ramping": 1,
    "holding": 2,
    "paused": 3,
    "manual up": 4,
    "manual down": 5,
    "zeroing current": 6,
    "quench detected": 7,
    "at zero current": 8,
    "heating switch": 9,
    "cooling switch": 10,
}


class Rig(NamedTuple):
    loader: object
    measurement: str  # per-rig InfluxDB measurement name
    with_state: bool  # also publish ramping state + quench flag


# Toploader keeps its historical "AVS_bridge" measurement (see TODO.md re:
# migrating to AMI430) and field only until the extra queries' cost on the
# kernel-shared connection is characterized; pink starts clean with state.
RIGS = {
    "toploader": Rig(load_config, "AVS_bridge", with_state=False),
    "pink": Rig(load_pink_config, "AMI430", with_state=True),
}


class Reading(NamedTuple):
    field_T: float
    state: str | None = None  # STATE_CODES key, None when not polled
    quenched: bool | None = None


class Magnet:
    """AMI 430 field (and optionally control state) readback over TCP/IP."""

    name = "AMI430"

    def __init__(self, address: str, *, with_state: bool = False):
        self._address = address
        self._with_state = with_state
        self._mag = None

    def connect(self) -> None:
        emit(Tag.INIT, f"Address: {self._address}")
        self._mag = AMIModel430("magnet", address=self._address)
        emit(Tag.INIT, "AMI430 connected")

    def close(self) -> None:
        # close_all() tolerates a dead VISA session and clears the qcodes name
        # registry, so a reconnect can re-instantiate under the same name.
        Instrument.close_all()
        self._mag = None

    def read(self) -> Reading:
        field_T = float(self._mag.field())
        if not self._with_state:
            return Reading(field_T)
        return Reading(field_T, str(self._mag.ramping_state()),
                       bool(self._mag.is_quenched()))


def make_publish(write_api, org, bucket, measurement):
    """Build the (Reading, cycle) -> [data] payload callable for one rig."""

    def publish(reading: Reading, cycle: int) -> dict[str, object]:
        field_T = reading.field_T
        points = [("magnetic field", field_T, "Tesla")]
        data: dict[str, object] = {
            "_summary": f"{field_T:.4f} T",
            "magnetic field": f"{field_T:.4f} T",
        }
        if reading.state is not None:
            code = STATE_CODES.get(reading.state, -1)
            quenched = bool(reading.quenched)
            points.append(("ramping state", float(code), "state"))
            points.append(("quenched", 1.0 if quenched else 0.0, "status"))
            data["ramping state"] = f"{reading.state} ({code})"
            data["quenched"] = "YES" if quenched else "no"
            data["_summary"] = (f"{field_T:.4f} T "
                                f"{'QUENCH' if quenched else reading.state}")
        try:
            for metric, value, unit in points:
                write_point(write_api, org, bucket, measurement, metric, value, unit)
        except Exception as e:
            emit(Tag.ERROR, f"InfluxDB write failed: {e}")
        return data

    return publish


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--rig", choices=sorted(RIGS), default="toploader")
    args = parser.parse_args(argv)
    rig = RIGS[args.rig]

    try:
        config = rig.loader()
        _client, write_api, org, bucket = setup_influx(config.influxdb)
    except Exception as e:
        emit(Tag.ERROR, f"Startup failed: {e}")
        raise

    run(
        Magnet(config.hardware.ami430_addr, with_state=rig.with_state),
        interval=READ_INTERVAL,
        publish=make_publish(write_api, org, bucket, rig.measurement),
    )


if __name__ == "__main__":
    main()
